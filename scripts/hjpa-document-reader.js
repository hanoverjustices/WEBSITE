/* HJPA document reader: local-first; no changes to existing navigation. */
(function(){
'use strict';
const isPdf=u=>{try{return /\.pdf$/i.test(new URL(u,location.href).pathname)}catch{return false}};
const style=document.createElement('style');
style.textContent='#hjpaPdfReader{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.76);display:none;align-items:center;justify-content:center;padding:12px}#hjpaPdfReader[open]{display:flex}#hjpaPdfReader .hjpa-reader-box{display:flex;flex-direction:column;width:min(1120px,100%);height:min(94dvh,980px);background:#fff;color:#18253b;border-radius:14px;overflow:hidden;box-shadow:0 18px 70px #0008}#hjpaPdfReader .hjpa-reader-head{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:10px 12px;background:#142238;color:white}#hjpaPdfReader .hjpa-reader-head strong{flex:1;min-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#hjpaPdfReader button,#hjpaPdfReader a{font:600 13px system-ui;padding:7px 10px;border:1px solid #9eaab8;border-radius:7px;background:#fff;color:#17263b;text-decoration:none;cursor:pointer}#hjpaPdfReader .hjpa-reader-frame{width:100%;flex:1;border:0;background:#f0f1f3}#hjpaPdfReader .hjpa-reader-status{font:13px system-ui;padding:5px 12px;background:#f6f7f8;color:#394454}@media(max-width:600px){#hjpaPdfReader .hjpa-reader-box{height:95dvh}#hjpaPdfReader .hjpa-reader-head{gap:5px}#hjpaPdfReader button,#hjpaPdfReader a{padding:6px}}';
document.head.appendChild(style);
const modal=document.createElement('section');modal.id='hjpaPdfReader';modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');modal.setAttribute('aria-label','Document reader');
modal.innerHTML='<div class="hjpa-reader-box"><div class="hjpa-reader-head"><strong id="hjpaReaderTitle">Document</strong><button type="button" id="hjpaReaderPrev" aria-label="Previous page">‹</button><span id="hjpaReaderCount">PDF</span><button type="button" id="hjpaReaderNext" aria-label="Next page">›</button><a id="hjpaReaderDownload" download>Download</a><button type="button" id="hjpaReaderClose" aria-label="Close document">✕</button></div><iframe class="hjpa-reader-frame" title="PDF document" id="hjpaReaderFrame"></iframe><div class="hjpa-reader-status" id="hjpaReaderStatus">Use your browser’s PDF controls to zoom, search and print.</div></div>';
document.body.appendChild(modal);
const q=id=>document.getElementById(id),frame=q('hjpaReaderFrame'),count=q('hjpaReaderCount');let page=1,previousFocus=null;
function close(){modal.removeAttribute('open');frame.removeAttribute('src');previousFocus?.focus?.();document.body.style.removeProperty('overflow')}
function open(url,title){previousFocus=document.activeElement;page=1;const absolute=new URL(url,location.href).href;frame.src=absolute+'#page=1&view=FitH';q('hjpaReaderTitle').textContent=title||decodeURIComponent(new URL(absolute).pathname.split('/').pop())||'Document';q('hjpaReaderDownload').href=absolute;count.textContent='Page 1';modal.setAttribute('open','');document.body.style.overflow='hidden';q('hjpaReaderClose').focus()}
q('hjpaReaderClose').onclick=close;
modal.addEventListener('click',e=>{if(e.target===modal)close()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&modal.hasAttribute('open'))close()});
function move(n){page=Math.max(1,page+n);const base=q('hjpaReaderDownload').href;frame.src=base+'#page='+page+'&view=FitH';count.textContent='Page '+page}
q('hjpaReaderPrev').onclick=()=>move(-1);q('hjpaReaderNext').onclick=()=>move(1);
document.addEventListener('click',e=>{const a=e.target.closest?.('a[href]');if(!a||e.defaultPrevented||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||a.hasAttribute('download'))return;const href=a.getAttribute('href');if(!isPdf(href))return;const url=new URL(href,location.href);if(url.origin!==location.origin){return}e.preventDefault();open(url.href,(a.textContent||'').trim())},false);
window.HJPA_openLocalPdf=open;
})();