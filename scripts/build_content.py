"""Generate both indexes and a deployable allowlisted site. Originals stay untouched."""
from pathlib import Path
from PIL import Image, ImageOps
import hashlib,json,re,subprocess,shutil,datetime,sys,urllib.request
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'notice-assets'
EXT={'.jpg','.jpeg','.png','.webp'}
def added(path):
    result=subprocess.run(['git','log','--no-renames','--diff-filter=A','--format=%ct','--',str(path.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True)
    times=[int(t) for t in result.stdout.splitlines() if t.isdigit()]
    return min(times) if times else 0

def scan(folder,posters=False):
    rows=[]
    for p in sorted((ROOT/folder).iterdir()):
        if p.suffix.lower() not in EXT:continue
        if p.is_symlink() or not p.is_file():raise ValueError('Only regular image files are supported: '+p.name)
        date=None
        if posters:
            m=re.fullmatch(r'(\d{4}-\d{2}-\d{2}|undated)__(.+)',p.stem)
            if not m:raise ValueError('Rename poster using YYYY-MM-DD__title or undated__title: '+p.name)
            if m[1]!='undated':date=datetime.date.fromisoformat(m[1]).isoformat()
            title=m[2].replace('-',' ').replace('_',' ')
        else:title=p.stem.replace('-',' ').replace('_',' ')
        data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()[:16]
        with Image.open(p) as im:
            im.load();preview=ImageOps.exif_transpose(im).convert('RGB');preview.thumbnail((1100,1700) if posters else (1920,1440))
            name=f'{"poster" if posters else "slide"}-{digest}.webp';preview.save(ASSETS/'generated'/name,'WEBP',quality=88)
        row={'id':hashlib.sha256(p.name.encode()).hexdigest()[:16],'title':title,'filename':p.name,'date':date,'added':added(p),'image':f'notice-assets/generated/{name}','original':quote(folder+'/'+p.name,safe='/')+'?v='+digest}
        rows.append(row)
    # Recent first; simultaneous migrations use event date descending then filename ascending.
    rows.sort(key=lambda r:r['filename'].casefold())
    rows.sort(key=lambda r:r['date'] or '',reverse=True)
    rows.sort(key=lambda r:r['added'],reverse=True)
    return rows

def main():
    generated=ASSETS/'generated'
    if generated.exists():shutil.rmtree(generated)
    generated.mkdir(parents=True)
    notices=scan('announcements',True);slides=scan('homepage-slideshow')
    content={'notices':notices,'slides':slides}
    for filename,data in [('announcements-index.json',notices),('slideshow-index.json',slides)]:
        (ASSETS/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2))
    (ASSETS/'content.js').write_text('window.HJPA_CONTENT='+json.dumps(content,ensure_ascii=False).replace('<','\\u003c')+';\n')
    out=ROOT/'_site'
    if out.exists():shutil.rmtree(out)
    out.mkdir()
    for name in ['index.html','CNAME']:shutil.copyfile(ROOT/name,out/name)
    shutil.copytree(ASSETS,out/'notice-assets')
    # The homepage references historical images through notice-assets/site-images/.
    # Keep the original URLs intact by packaging existing root-level source images.
    site_images=out/'notice-assets'/'site-images'
    site_images.mkdir(parents=True,exist_ok=True)
    for p in ROOT.iterdir():
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in EXT:
            shutil.copyfile(p,site_images/p.name)
    for folder in ['announcements','homepage-slideshow']:
        (out/folder).mkdir()
        for p in (ROOT/folder).iterdir():
            if p.suffix.lower() in EXT:shutil.copyfile(p,out/folder/p.name)
    # Local-first document delivery: all original repository PDF files are published.
    for pdf in ROOT.rglob('*.pdf'):
        if pdf.name.lower()=='manual.pdf' and 'gia-documents' in pdf.parts:
            continue
        if any(part in {'.git','_site','node_modules'} for part in pdf.relative_to(ROOT).parts):
            continue
        if pdf.is_symlink():
            continue
        dest=out/pdf.relative_to(ROOT)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(pdf,dest)
    # Optional official snapshots. Do not make site availability depend on
    # government servers or replace a local PDF with an unverified response.
    official_pdfs={
        'bail.pdf':'https://mlca.gov.jm/wp-content/uploads/2023/12/The-Bail-Act-2023.pdf',
        'jp-act.pdf':'https://moj.gov.jm/sites/default/files/2022-07/The%20Justices%20of%20the%20Peace%20Act%2C%202018%20No.%2010.pdf',
        'jp-application-form.pdf':'https://moj.gov.jm/sites/default/files/2021-06/JP_Application_Form.pdf',
    }
    for filename,url in official_pdfs.items():
        destination=out/filename
        if destination.is_file():
            continue
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'HJPA-Resource-Verification/1.0','Accept':'application/pdf'})
            with urllib.request.urlopen(request,timeout=12) as response:
                data=response.read(18*1024*1024+1)
            if len(data)>18*1024*1024 or not data.lstrip().startswith(b'%PDF-') or len(data)<1500:
                raise ValueError('Response is not a valid PDF')
            destination.write_bytes(data)
        except Exception as exc:
            print(f'WARNING: official snapshot {filename} unavailable; verify its source before publishing: {exc}',file=sys.stderr)
    # Restricted JTI qualifying training manual: no public distribution permission.
    # Remove both the PDF and its extracted contents from the published Gia corpus.
    restricted=out/'notice-assets'/'gia-documents'/'manual.pdf'
    if restricted.exists():
        restricted.unlink()
    homepage=out/'index.html'
    html=homepage.read_text(encoding='utf-8')
    decoder=json.JSONDecoder()
    for prefix in ['window.GIA_APPROVED_KB=','const GIA_KNOWLEDGE_V2=']:
        start=html.find(prefix)
        if start<0:
            raise ValueError('Expected Gia knowledge dataset missing: '+prefix)
        pos=start+len(prefix)
        data,end=decoder.raw_decode(html[pos:])
        def restricted_entry(item):
            if not isinstance(item,dict):return False
            return ('jp qualifying training manual' in str(item.get('title','')).lower()
                    or 'jp qualifying training manual' in str(item.get('document','')).lower()
                    or 'jp-training-manual' in str(item.get('resourceId','')).lower()
                    or 'manual.pdf' in str(item.get('url','')).lower()
                    or str(item.get('documentId','')).lower()=='jp-training-manual')
        if isinstance(data,dict):
            for key,value in list(data.items()):
                if isinstance(value,list):data[key]=[item for item in value if not restricted_entry(item)]
            # Remove manual document metadata and all page excerpts from Gia.
            for key in ['documents','resourceCatalogue','sources','evidence']:
                if isinstance(data.get(key),list):
                    data[key]=[item for item in data[key] if not restricted_entry(item)]
        elif isinstance(data,list):
            data=[item for item in data if not restricted_entry(item)]
        html=html[:pos]+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\\\u003c')+html[pos+end:]
    homepage.write_text(html,encoding='utf-8')
    # Restore the HJPA logo in browser tabs using the same verified local image as the header.
    favicon='notice-assets/site-images/78326aac0c092349df10.png'
    homepage=out/'index.html'
    html=homepage.read_text(encoding='utf-8')
    icon_tags='<link rel="icon" type="image/png" href="/'+favicon+'?v=hjpa-20261122"><link rel="shortcut icon" href="/'+favicon+'?v=hjpa-20261122"><link rel="apple-touch-icon" href="/'+favicon+'?v=hjpa-20261122">'
    # Replace old icon declarations so browsers do not select a stale favicon.
    html=re.sub(r'<link\\b[^>]*\\brel\\s*=\\s*["\\\'](?:shortcut icon|icon|apple-touch-icon)["\\\'][^>]*>', '', html, flags=re.I)
    html=html.replace('</head>',icon_tags+'</head>',1)
    html=html.replace('</body>','<script defer src="/scripts/hjpa-document-reader.js"></script></body>',1)
    homepage.write_text(html,encoding='utf-8')
    # A browsable index of actual local PDFs, rather than links to guessed files.
    local_documents=sorted(p for p in out.rglob('*.pdf') if p.is_file())
    from html import escape as html_escape
    cards=[]
    for pdf in local_documents:
        rel=pdf.relative_to(out).as_posix()
        title=pdf.stem.replace('_',' ').replace('-',' ').strip()
        cards.append('<a class="document-card" href="/'+html_escape(quote(rel,safe='/'))+'"><span>PDF</span><strong>'+html_escape(title)+'</strong><small>Read online or download</small></a>')
    official_references=[
      ('Justices of the Peace Act, 2018 — statute record','https://laws.moj.gov.jm/library/statute/the-justices-of-the-peace-act'),
      ('Justices of the Peace Jurisdiction Act — statute record','https://laws.moj.gov.jm/library/statute/the-justices-of-the-peace-jurisdiction-act'),
      ('Bail Act, 2023 — official PDF','https://mlca.gov.jm/wp-content/uploads/2023/12/The-Bail-Act-2023.pdf'),
      ('JP Application Form — official PDF','https://moj.gov.jm/sites/default/files/2021-06/JP_Application_Form.pdf'),
      ('JP Annual Report and Online Form','https://moj.gov.jm/justice-peace'),
      ('Ministry of Justice Forms Directory','https://moj.gov.jm/forms'),
      ('Laws of Jamaica — check amendments','https://laws.moj.gov.jm/'),
    ]
    for title,url in official_references:
        cards.append('<a class="document-card" href="'+html_escape(url,quote=True)+'" target="_blank" rel="noopener noreferrer"><span>OFFICIAL SOURCE</span><strong>'+html_escape(title)+'</strong><small>Opens issuing authority; check current edition</small></a>')
    document_page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Laws, Forms & Documents | Hanover JPA</title><link rel="icon" href="/notice-assets/site-images/78326aac0c092349df10.png"><style>body{margin:0;background:#f2f5fa;color:#182d4d;font:16px system-ui}header{background:#10274b;color:white;padding:28px max(20px,calc((100vw - 1100px)/2))}header a{color:#f3d68a}main{max-width:1100px;margin:auto;padding:24px 20px 80px}.documents{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}.document-card{display:flex;flex-direction:column;gap:9px;padding:19px;border:1px solid #d9e3f1;background:white;border-radius:14px;box-shadow:0 5px 20px #11284b12;text-decoration:none;color:#182d4d}.document-card span{font-size:11px;font-weight:800;color:#265c99}.document-card strong{font-size:17px}.document-card small{color:#52677f}.document-card:hover,.document-card:focus-visible{outline:2px solid #ba9c54}input{padding:13px;width:min(100%,500px);box-sizing:border-box;border:1px solid #a6b8ce;border-radius:10px;margin:15px 0 25px}footer{max-width:1100px;margin:20px auto;padding:20px;font-size:12px;color:#566}</style></head><body><header><a href="/">← Hanover JPA Home</a><h1>Laws, Forms & Document Library</h1><p>Open available local PDF documents in the interactive reader. Check the issuing authority for current amendments and form revisions.</p></header><main><label for="docFilter">Find a document</label><div><input id="docFilter" type="search" placeholder="Search laws, forms and documents"></div><div class="documents" id="documents">'''+''.join(cards)+'''</div></main><footer>Reference copies are not a substitute for the latest official law or form. Confirm amendments and current requirements with the issuing authority.</footer><script defer src="/scripts/hjpa-document-reader.js"></script><script>document.getElementById('docFilter').addEventListener('input',function(){const q=this.value.toLowerCase();document.querySelectorAll('.document-card').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(q))})</script></body></html>'''
    (out/'documents.html').write_text(document_page,encoding='utf-8')
    # Direct Beginning Concepts service enquiries to its business email, not WhatsApp.
    from urllib.parse import urlencode
    business_email='beginningconcepts.org@gmail.com'
    contact_links={
      'https://wa.me/18765029756?text=I%20would%20like%20to%20report%20an%20issue%20with%20the%20HJPA%20website.': 'mailto:'+business_email+'?'+urlencode({'subject':'HJPA website — report an issue','body':'Hello Beginning Concepts,\\n\\nI would like to report the following issue on the Hanover JPA website:\\n\\nPage/link:\\nIssue:\\n\\nThank you.'}),
      'https://wa.me/18765029756?text=Hi%2C%20I%20would%20like%20a%20website%20like%20the%20HJPA%20website.': 'mailto:'+business_email+'?'+urlencode({'subject':'Website enquiry — Beginning Concepts','body':'Hello Beginning Concepts,\\n\\nI would like to enquire about a website similar to the Hanover JPA website for my organisation.\\n\\nOrganisation:\\nContact details:\\nRequirements:\\n\\nThank you.'}),
    }
    current=homepage.read_text(encoding='utf-8')
    for old,new in contact_links.items():
        current=current.replace(old,new.replace('&','&amp;'))
        current=current.replace(old.replace('&','&amp;'),new.replace('&','&amp;'))
    homepage.write_text(current,encoding='utf-8')
    # Add a nonfloating navigation link without changing existing page structure.
    homepage.write_text(homepage.read_text(encoding='utf-8').replace('</body>','<div style="text-align:center;padding:18px 12px 95px;background:#0c1c32"><a href="/documents.html" style="color:#f2d789;font:700 15px system-ui;text-decoration:underline">Browse Laws, Forms &amp; PDF Library</a></div></body>',1),encoding='utf-8')
    # Publish real, directly addressable pages instead of one giant scroll.
    # Each page retains the original design, interactive scripts and Gia.
    page_sections={
      'index.html':[],
      'leadership.html':['leadership','milestones'],
      'services.html':['services'],
      'annual-report.html':['annual-report'],
      'resources.html':['resources'],
      'find-services.html':['justice-services'],
      'gallery.html':['gallery'],
      'memorials.html':['memorials'],
      'media.html':['media'],
      'justice-centre.html':['centre'],
      'faq.html':['faq'],
    }
    anchor_pages={'home':'index.html','become-jp':'services.html','notice-board':'index.html',
      'leadership':'leadership.html','milestones':'leadership.html','services':'services.html',
      'annual-report':'annual-report.html','resources':'resources.html','justice-services':'find-services.html',
      'gallery':'gallery.html','memorials':'memorials.html','media':'media.html',
      'centre':'justice-centre.html','faq':'faq.html'}
    base_html=homepage.read_text(encoding='utf-8')
    for filename,visible in page_sections.items():
        page=base_html
        for anchor,target in anchor_pages.items():
            page=page.replace('href="#'+anchor+'"','href="/'+target+('#'+anchor if anchor in {'become-jp','notice-board','milestones'} else '')+'"')
        # Hide every other main section while keeping all interactive widgets loaded.
        # The homepage displays its hero and quick-access content only.
        selectors=['main > section.section','main > section.justice-directory','main > section.memorial-section','main > section.navy-section']
        css='main > section:not(.hero){display:none!important}'
        if filename!='index.html':css+='main > section.hero{display:none!important}'
        for section_id in visible:
            css+='main > section#'+section_id+'{display:block!important}'
        # Only show the original main content of this page; header/footer remain.
        page=page.replace('</head>','<style id="hjpa-multipage">'+css+'</style></head>',1)
        if filename!='index.html':
            page=page.replace('<main id="home">','<main id="home"><div style="padding:22px max(16px,5vw);background:#10243e;color:#e8d486;font:700 14px system-ui"><a href="/" style="color:inherit">← Home</a> / '+filename.replace('.html','').replace('-',' ').title()+'</div>',1)
        (out/filename).write_text(page,encoding='utf-8')
    shutil.copytree(ROOT/'scripts',out/'scripts',dirs_exist_ok=True)
    # Fail publishing if key local assets are missing.
    for required in [favicon,'scripts/hjpa-document-reader.js']:
        if not (out/required).is_file():
            raise FileNotFoundError('Required published asset missing: '+required)
    (out/'.nojekyll').touch()
    print(f'Built {len(notices)} posters and {len(slides)} slideshow images into _site')
if __name__=='__main__':main()
