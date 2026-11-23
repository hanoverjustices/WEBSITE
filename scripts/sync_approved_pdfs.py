"""Synchronize explicitly listed public Jamaican JP reference PDFs into the repository.
This is a best-effort ingestion job, not a statement about current law or redistribution rights.
Do not add private training manuals or documents without permission.
"""
from pathlib import Path
import hashlib,json,urllib.request,urllib.error,datetime
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'documents'/'library'
DEST.mkdir(parents=True,exist_ok=True)
SOURCES={
 'jp-jurisdiction.pdf':'https://laws.moj.gov.jm/legislation/statutes/J/The%20Justices%20of%20the%20Peace%20Jurisdiction%20Act.pdf',
 'official-seals-regulations.pdf':'https://laws.moj.gov.jm/legislation/subsids/J/JP%20%28Official%20Seals%29%20Regulations%20LN%2089%20B%20of%202004.pdf',
 'official-seals-act-historical.pdf':'https://laws.moj.gov.jm/legislation/statutes/J/The%20Justices%20of%20the%20Peace%20%28Official%20Seals%29%20Act.pdf',
 'jp-act-2018.pdf':'https://moj.gov.jm/sites/default/files/2022-07/The%20Justices%20of%20the%20Peace%20Act%2C%202018%20No.%2010.pdf',
 'bail-act-2023.pdf':'https://mlca.gov.jm/wp-content/uploads/2023/12/The-Bail-Act-2023.pdf',
 'jp-application-form.pdf':'https://moj.gov.jm/sites/default/files/2021-06/JP_Application_Form.pdf',
 'bail-regulations.pdf':'https://laws.moj.gov.jm/legislation/subsids/B/The%20Bail%20Act%20%28sub%20leg%29.pdf',
 'constitution.pdf':'https://laws.moj.gov.jm/legislation/statutes/J/Ja%20%28Constitution%29%20Order%20in%20Council%201962_1.pdf',
}

# Further public JP references are discovered from the official statute records.
# A statute landing page is never stored as a PDF.
MORE_SOURCES={
 'spirit-licence-act.pdf':'https://laws.moj.gov.jm/library/statute/the-spirit-licence-act',
 'zoso-act.pdf':'https://laws.moj.gov.jm/library/act-of-parliament/law-reform-zones-of-special-operations-special-security-and-community-development-measures',
 'parish-courts-act.pdf':'https://laws.moj.gov.jm/library/act-of-parliament/21-of-2021-the-judicature-parish-courts-act',
 'voluntary-declarations-act.pdf':'https://laws.moj.gov.jm/library/statute/the-voluntary-declarations-act',
 'oaths-act.pdf':'https://laws.moj.gov.jm/library/statute/the-oaths-act',
 'interpretation-act.pdf':'https://laws.moj.gov.jm/library/statute/the-interpretation-act',
 'proceeds-of-crime-act.pdf':'https://laws.moj.gov.jm/library/statute/the-proceeds-of-crime-act',
 'child-diversion-act.pdf':'https://laws.moj.gov.jm/library/statute/the-child-diversion-act-2018',
 'jp-amendment-2021.pdf':'https://laws.moj.gov.jm/library/act-of-parliament/9-of-2021-the-justices-of-the-peace-amendment-act',
 'jp-act-parliament.pdf':'https://laws.moj.gov.jm/library/act-of-parliament/10-2018-the-justices-of-the-peace-act',
 'official-seals-regulations-revised.pdf':'https://laws.moj.gov.jm/library/subsidiary-legislation/the-justices-of-the-peace-official-seals',
}
SOURCES.update(MORE_SOURCES)

from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
class PDFLinks(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag!='a':return
        d=dict(attrs);href=d.get('href','')
        if '.pdf' in href.lower():self.links.append(href)

def resolve_pdf(url):
    if '.pdf' in urlparse(url).path.lower():return url
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 HJPA-document-library'})
    with urllib.request.urlopen(req,timeout=20) as response:
        if 'pdf' in response.headers.get('Content-Type','').lower():return url
        html=response.read(2*1024*1024).decode('utf-8','replace')
    parser=PDFLinks();parser.feed(html)
    if not parser.links:raise ValueError('No direct PDF link found on official statute page')
    return urljoin(url,parser.links[0])

def main():
    records=[]
    for name,url in SOURCES.items():
        target=DEST/name
        row={'filename':name,'sourceUrl':url,'downloaded':False,'status':'not verified'}
        try:
            download_url=resolve_pdf(url)
            row['resolvedPdfUrl']=download_url
            req=urllib.request.Request(download_url,headers={'User-Agent':'HJPA-document-library/1.0','Accept':'application/pdf'})
            with urllib.request.urlopen(req,timeout=20) as response:
                content=response.read(20*1024*1024+1)
            if len(content)>20*1024*1024 or len(content)<1500 or not content.lstrip().startswith(b'%PDF-') or b'%%EOF' not in content[-4096:]:
                raise ValueError('Invalid, incomplete or oversized PDF')
            if not target.exists() or target.read_bytes()!=content:target.write_bytes(content)
            row.update(downloaded=True,status='Downloaded official-source snapshot; check amendments',sha256=hashlib.sha256(content).hexdigest(),size=len(content))
            print('OK',name,len(content))
        except Exception as exc:
            if target.exists() and target.read_bytes().startswith(b'%PDF-'):
                row.update(downloaded=True,status='Existing repository copy; source refresh failed',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),size=target.stat().st_size)
            else:
                row['status']='Unavailable from official source'
            print('WARN',name,str(exc)[:220])
        records.append(row)
    (DEST/'source-manifest.json').write_text(json.dumps({'checkedOn':datetime.date.today().isoformat(),'documents':records},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
