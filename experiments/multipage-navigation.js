/* HJPA multi-page navigation prototype. Intentionally isolated from live main. */
(function(){
'use strict';
const navLinks=[...document.querySelectorAll('nav a[href^="#"],header a[href^="#"]')];
const candidates=navLinks.map(a=>({a,id:decodeURIComponent(a.hash.slice(1)),label:a.textContent.trim()})).filter(x=>x.id&&x.label&&x.label.length<48).map(x=>({...x,target:document.getElementById(x.id)})).filter(x=>x.target&&x.target.tagName.toLowerCase()==='section');
const unique=[...new Map(candidates.map(x=>[x.id,x])).values()];
if(unique.length<3)return; // Do not alter unrecognised layouts.
const root=unique[0].target.parentElement;
if(!unique.every(x=>x.target.parentElement===root))return;
const pageIds=new Set(unique.map(x=>x.id));
const home=unique[0].id;
function show(id){
 const chosen=pageIds.has(id)?id:home;
 unique.forEach(x=>{x.target.hidden=x.id!==chosen;x.a.setAttribute('aria-current',x.id===chosen?'page':'false')});
 document.documentElement.dataset.hjpaPage=chosen;
 history.replaceState(null,'','#'+chosen);
 window.scrollTo({top:0,behavior:'instant'});
}
const nav=document.createElement('nav');nav.setAttribute('aria-label','Website pages');nav.className='hjpa-page-navigation';
nav.innerHTML=unique.map(x=>'<a href="#'+encodeURIComponent(x.id)+'">'+x.label.replaceAll('&','&amp;').replaceAll('<','&lt;')+'</a>').join('');
const css=document.createElement('style');css.textContent='.hjpa-page-navigation{display:flex;gap:8px;overflow-x:auto;padding:10px 12px;background:#0c1b2e;position:sticky;top:0;z-index:75}.hjpa-page-navigation a{flex:none;color:#fff;text-decoration:none;padding:9px 14px;border:1px solid #ffffff40;border-radius:30px;font:600 13px system-ui}.hjpa-page-navigation a[aria-current=page]{background:#d4b86a;color:#111}.hjpa-page-navigation a:focus-visible{outline:3px solid #fff}';
document.head.appendChild(css);root.parentElement.insertBefore(nav,root);
nav.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;e.preventDefault();show(decodeURIComponent(a.hash.slice(1)))});
window.addEventListener('hashchange',()=>show(location.hash.slice(1)));
show(decodeURIComponent(location.hash.slice(1)));
})();
