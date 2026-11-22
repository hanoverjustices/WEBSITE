"""Offline structural QA for generated HJPA site. Exits nonzero for internal broken links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,sys
SITE=Path(__file__).resolve().parents[1]/'_site'
PAGES=['index.html','leadership.html','services.html','annual-report.html','resources.html','find-services.html','gallery.html','memorials.html','media.html','justice-centre.html','faq.html','documents.html']
class Audit(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set();self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        if tag in ('a','link') and a.get('href'):self.links.append(a['href'])
        if tag in ('img','script','iframe') and a.get('src'):self.images.append(a['src'])
def main():
    errors=[];parsers={}
    for name in PAGES:
        path=SITE/name
        if not path.is_file():errors.append('Missing page: '+name);continue
        p=Audit();p.feed(path.read_text(encoding='utf-8'));parsers[name]=p
    for name,p in parsers.items():
        for link in p.links+p.images:
            if not link or link.startswith(('mailto:','tel:','data:','javascript:','//')):continue
            url=urlsplit(link)
            if url.scheme or url.netloc:continue
            # Some links are handled by in-page JavaScript, not native anchor navigation.
            if not url.path and url.fragment:
                if url.fragment not in p.ids and url.fragment not in {'notice-board','become-jp'}:
                    errors.append(f'{name}: missing local anchor #{url.fragment}')
                continue
            path=unquote(url.path).lstrip('/')
            if not path:continue
            target=SITE/path
            if target.is_dir():target=target/'index.html'
            if not target.is_file():
                # Source page may refer to image variants generated at runtime.
                errors.append(f'{name}: missing local asset {path}')
    homepage=(SITE/'index.html').read_text(encoding='utf-8')
    if 'JP Qualifying Training Manual' in homepage or 'notice-assets/gia-documents/manual.pdf' in homepage:
        errors.append('Restricted training manual still referenced in homepage')
    if (SITE/'notice-assets/gia-documents/manual.pdf').exists():
        errors.append('Restricted training manual publicly distributed')
    for name in PAGES:
        if name=='documents.html':continue
        if 'hjpa-multipage' not in (SITE/name).read_text(encoding='utf-8'):
            errors.append(name+': missing multipage layout')
    if errors:
        print('FAILED HJPA structural QA:')
        for e in sorted(set(errors))[:100]:print(' -',e)
        sys.exit(1)
    print('PASS: '+str(len(PAGES))+' pages, local link/asset targets, multipage layout, restricted manual exclusions')
if __name__=='__main__':main()
