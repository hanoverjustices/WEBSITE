"""Generate both indexes and a deployable allowlisted site. Originals stay untouched."""
from pathlib import Path
from PIL import Image, ImageOps
import hashlib,json,re,subprocess,shutil,datetime,sys
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
    for folder in ['announcements','homepage-slideshow']:
        (out/folder).mkdir()
        for p in (ROOT/folder).iterdir():
            if p.suffix.lower() in EXT:shutil.copyfile(p,out/folder/p.name)
    (out/'.nojekyll').touch()
    print(f'Built {len(notices)} posters and {len(slides)} slideshow images into _site')
if __name__=='__main__':main()
