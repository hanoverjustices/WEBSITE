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
 'jp-act-2018.pdf':'https://moj.gov.jm/sites/default/files/2022-07/The%20Justices%20of%20the%20Peace%20Act%2C%202018%20No.%2010.pdf',
 'bail-act-2023.pdf':'https://mlca.gov.jm/wp-content/uploads/2023/12/The-Bail-Act-2023.pdf',
 'jp-application-form.pdf':'https://moj.gov.jm/sites/default/files/2021-06/JP_Application_Form.pdf',
 'bail-regulations.pdf':'https://laws.moj.gov.jm/legislation/subsids/B/The%20Bail%20Act%20%28sub%20leg%29.pdf',
 'constitution.pdf':'https://laws.moj.gov.jm/legislation/statutes/J/Ja%20%28Constitution%29%20Order%20in%20Council%201962_1.pdf',
}
def main():
    records=[]
    for name,url in SOURCES.items():
        target=DEST/name
        row={'filename':name,'sourceUrl':url,'downloaded':False,'status':'not verified'}
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'HJPA-document-library/1.0','Accept':'application/pdf'})
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
