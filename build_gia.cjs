// Mechanical embedding keeps installation to one index.html upload; edit gia/knowledge.json, not generated HTML.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),file=path.join(root,'index.html');
const kb=JSON.parse(fs.readFileSync(path.join(root,'gia/knowledge.json'),'utf8'));
const engine=fs.readFileSync(path.join(root,'gia/engine.js'),'utf8');
let html=fs.readFileSync(file,'utf8');
const start=html.indexOf('function giaAnswer(raw){'),end=html.indexOf('/* ---------------- UI ---------------- */',start);
if(start<0||end<0)throw Error('Gia integration anchors missing');
html=html.slice(0,start)+'function giaAnswer(raw){\n return window.GiaLocked ? window.GiaLocked.answer(raw,window.GIA_APPROVED_KB) : {direct:"I don’t have verified information to answer that accurately, and I don’t want to mislead you.",sources:[]};\n}\n\n'+html.slice(end);
const block='<script id="gia-source-locked">\nwindow.GIA_APPROVED_KB='+JSON.stringify(kb).replace(/</g,'\\u003c')+';\n'+engine+'\n</script>';
html=html.replace(/<script id="gia-source-locked">[\s\S]*?<\/script>/,'');
html=html.replace('</head>',block+'\n</head>');
// Replace the original welcome without touching the avatar data.
html=html.replace(/(<div[^>]*id="chatlog"[^>]*>)[\s\S]*?(?=<\/div>\s*<div class="chatrow")/,'$1<div class="msg bot">Hello! I’m Gia. I answer from reviewed evidence and say when information is not verified.</div>');
const chips=html.indexOf('function giaSuggestedQuestions(){'),chipsEnd=html.indexOf('function giaRefreshChips()',chips);
if(chips<0||chipsEnd<0)throw Error('Suggested question anchors missing');
html=html.slice(0,chips)+'function giaSuggestedQuestions(){return [["Custos record","Who is the Custos?"],["Source audit","Source audit"],["JP requirements","How do I become a JP"]];}\n'+html.slice(chipsEnd);
fs.writeFileSync(file,html);
console.log('Embedded source-locked Gia; legacy answer routing removed.');
