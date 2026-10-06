'use strict';
const RUNTIME='https://cdn.jsdelivr.net/pyodide/v0.29.3/full/';
let engine=null;
function status(message) { postMessage({type:'status',message}); }
async function initialize() {
  if(engine) return engine;
  status('Loading Python on your device. The first comparison may take a few seconds…');
  importScripts(RUNTIME+'pyodide.js');
  const pyodide=await loadPyodide({indexURL:RUNTIME});
  const response=await fetch('engine.zip');
  if(!response.ok) throw new Error('Could not download the comparison engine.');
  pyodide.unpackArchive(await response.arrayBuffer(),'zip',{extractDir:'/home/pyodide'});
  await pyodide.runPythonAsync('from mcp_tooldelta.catalog import load_catalog\nfrom mcp_tooldelta.diff import compare\nfrom mcp_tooldelta.render import render\nimport json, os');
  engine=pyodide;
  return engine;
}
self.onmessage=async event=>{
  try {
    const pyodide=await initialize();
    const data=event.data;
    status('Checking input and output compatibility locally…');
    pyodide.FS.writeFile('/tmp/before.json',new Uint8Array(data.before));
    pyodide.FS.writeFile('/tmp/after.json',new Uint8Array(data.after));
    pyodide.globals.set('before_label',data.beforeName);
    pyodide.globals.set('after_label',data.afterName);
    const output=await pyodide.runPythonAsync(`
try:
    baseline = load_catalog('/tmp/before.json')
    candidate = load_catalog('/tmp/after.json')
    report = compare({'tools': list(baseline.values())}, {'tools': list(candidate.values())})
    result = json.dumps({'html': render(report, 'html', before_label, after_label), 'report': report.to_dict()})
finally:
    for path in ('/tmp/before.json', '/tmp/after.json'):
        if os.path.exists(path):
            os.unlink(path)
result
`);
    const result=JSON.parse(output);
    postMessage({type:'result',...result});
  } catch(exception) {
    const message=String(exception.message || exception);
    const lines=message.trim().split('\n');
    postMessage({type:'error',message:lines[lines.length-1] || 'Local comparison failed. Try the offline CLI.'});
  } finally {
    if(engine) {
      // Avoid retaining user catalogs in worker globals between comparisons.
      await engine.runPythonAsync("for key in ('baseline','candidate','report','result','before_label','after_label'):\n    globals().pop(key, None)");
    }
  }
};
