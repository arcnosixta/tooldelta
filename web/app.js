'use strict';
const byId = id => document.getElementById(id);
const LIMIT = 8 * 1024 * 1024;
let files = {before:null,after:null};
let worker = null, busy = false, timer = null, currentHtml = null, currentJson = null, reportUrl = null, generation=0;
const tabs = [...document.querySelectorAll('[data-example]')];
const notes = {
  sample:'A fictional workspace update: a required argument, a tighter limit, a wider response enum, and changed behavior hints.',
  filesystem:'Actual tools/list snapshots of the official MCP Filesystem Server, 2025.1.14 → 2026.8.31. Only catalog discovery was performed; no filesystem tools were called.',
  custom:'Choose complete saved tools/list results from one MCP server. Arrays, {tools: […]}, and JSON-RPC {result: {tools: […]}} are accepted.'
};
function error(message) { byId('error').textContent=message; byId('error').hidden=false; }
function clearError() { byId('error').hidden=true; byId('error').textContent=''; }
function setBusy(value) { busy=value; byId('compare').disabled=value; byId('load-sample').disabled=value; byId('cancel').hidden=!value; for(const side of ['before','after']) byId(side+'-file').disabled=value; }
function stop(message) { generation++; if(worker) worker.terminate(); worker=null; clearTimeout(timer); setBusy(false); byId('status').textContent=message || ''; }
function selectExample(example) {
  if(busy) stop('Comparison cancelled.');
  clearError(); byId('status').textContent='';
  for(const tab of tabs) { const selected=tab.dataset.example===example; tab.classList.toggle('active',selected); tab.setAttribute('aria-pressed',String(selected)); }
  byId('compare-form').hidden=example!=='custom';
  byId('example-note').textContent=notes[example];
  if(example==='filesystem') {
    const link=document.createElement('a'); link.href='https://github.com/arcnosixta/tooldelta/tree/main/examples/filesystem'; link.textContent=' Provenance and captured catalogs.';
    byId('example-note').append(link);
  }
  if(example!=='custom') {
    byId('report').removeAttribute('srcdoc'); byId('report').src=(example==='sample'?'sample.html':'filesystem.html')+'?embed=1';
    byId('open-report').href=example==='sample'?'sample.html':'filesystem.html'; byId('open-report').hidden=false;
    byId('report-label').textContent=example==='sample'?'Guided example · 4 breaking · 3 review · 3 info':'Official filesystem server · actual version update';
    byId('download-html').hidden=true; byId('download-json').hidden=true;
  }
}
for(const tab of tabs) tab.addEventListener('click',()=>selectExample(tab.dataset.example));
for(const side of ['before','after']) byId(side+'-file').addEventListener('change',event=>{
  files[side]=event.target.files[0] || null;
  byId(side+'-name').textContent=files[side]?files[side].name+' · '+Math.ceil(files[side].size/1024)+' KiB':'No file selected';
  clearError();
});
byId('load-sample').addEventListener('click',async()=>{
  const request=++generation; setBusy(true);
  try {
    clearError();
    const loaded={};
    for(const side of ['before','after']) {
      const response=await fetch('examples/'+side+'.json'); if(!response.ok) throw new Error('Could not load the example catalogs.');
      const file=new File([await response.text()],side+'.json',{type:'application/json'});
      loaded[side]=file;
    }
    if(request!==generation) return;
    for(const side of ['before','after']) {
      const file=loaded[side]; files[side]=file;
      const transfer=new DataTransfer(); transfer.items.add(file); byId(side+'-file').files=transfer.files;
      byId(side+'-name').textContent=file.name+' · '+Math.ceil(file.size/1024)+' KiB';
    }
    byId('status').textContent='Sample catalogs loaded. Compare to run the Python engine in your browser.';
  } catch(exception) { if(request===generation) error(exception.message); }
  finally { if(request===generation) setBusy(false); }
});
function ensureWorker() {
  if(worker) return worker;
  worker=new Worker('worker.js');
  worker.onmessage=event=>{
    const data=event.data;
    if(data.type==='status') { byId('status').textContent=data.message; return; }
    clearTimeout(timer); setBusy(false);
    if(data.type==='error') { byId('status').textContent=''; error(data.message); return; }
    if(data.type==='result') {
      currentHtml=data.html; currentJson=data.report;
      byId('report').removeAttribute('src'); byId('report').srcdoc=currentHtml.replace('<body>','<body class="embedded">');
      const s=data.report.summary;
      byId('report-label').textContent='Your comparison · '+s.breaking+' breaking · '+s.review+' review · '+s.info+' info';
      if(reportUrl) URL.revokeObjectURL(reportUrl);
      reportUrl=URL.createObjectURL(new Blob([currentHtml],{type:'text/html'}));
      byId('open-report').href=reportUrl; byId('open-report').hidden=false;
      byId('download-html').hidden=false; byId('download-json').hidden=false;
      byId('status').textContent='Comparison complete. Your catalog contents stayed on this device.';
    }
  };
  worker.onerror=()=>{ stop(''); error('The browser runtime could not start. Retry, or use the offline Python CLI.'); };
  return worker;
}
byId('compare-form').addEventListener('submit',async event=>{
  event.preventDefault(); if(busy) return; clearError();
  if(!files.before || !files.after) { error('Choose both a baseline and a candidate catalog.'); return; }
  if(files.before.size>LIMIT || files.after.size>LIMIT) { error('Each catalog must be at most 8 MiB.'); return; }
  const request=++generation;
  setBusy(true); byId('status').textContent='Preparing local comparison…';
  try {
    const before=await files.before.arrayBuffer(), after=await files.after.arrayBuffer();
    if(request!==generation) return;
    timer=setTimeout(()=>{ stop(''); error('Comparison timed out. Try smaller catalogs or the offline CLI.'); },120000);
    ensureWorker().postMessage({before,after,beforeName:files.before.name,afterName:files.after.name},[before,after]);
  } catch(exception) { if(request===generation) { stop(''); error(exception.message); } }
});
byId('cancel').addEventListener('click',()=>stop('Comparison cancelled. You can select files and try again.'));
function download(content,type,name) { const url=URL.createObjectURL(new Blob([content],{type})); const link=document.createElement('a'); link.href=url; link.download=name; document.body.append(link); link.click(); link.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000); }
byId('download-html').addEventListener('click',()=>download(currentHtml,'text/html','tooldelta-report.html'));
byId('download-json').addEventListener('click',()=>download(JSON.stringify(currentJson,null,2),'application/json','tooldelta-report.json'));
byId('copy-command').addEventListener('click',async()=>{
  try { await navigator.clipboard.writeText('python -m mcp_tooldelta demo'); byId('copy-command').textContent='Copied'; }
  catch(_) { byId('copy-command').textContent='Select to copy'; }
});
