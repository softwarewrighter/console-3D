'use strict';
const studies = {
  '1053': {heading:'IBM 1053', number:'STUDY 01 / CONSOLE PRINTER', description:'The 1053 console (used on IBM 1130/1800 systems), shown here in its 1130 arrangement. The 1130’s toggle switches were on the printer front cover; the 1800’s were on its large system panel.', accuracy:'Enclosure dimensions are inferred from the photograph. The surrounding 1130 register display is outside this first printer study.', photo:'references/ibm1130-console.jpg', credit:'1053 appearance reference: <a href="https://apaacini.com/IBM-1130_Consola.jpg" target="_blank" rel="noopener">supplied IBM 1130 console photograph</a>. The original image is preserved without edits.'},
  '2741': {heading:'IBM 2741', number:'STUDY 02 / APL TERMINAL', description:'A low-profile ivory terminal with an APL keyboard, exposed Selectric mechanism, and loaded paper. Refined against the supplied desktop reference model and museum photograph.', accuracy:'Desktop shell dimensions are provisional. The IBM manual’s complete desk-terminal envelope is a separate configuration.', photo:'references/ibm2741-terminal.jpg', credit:'2741 photograph: <a href="https://commons.wikimedia.org/wiki/File:IBM_2741_Communications_Terminal.jpg" target="_blank" rel="noopener">Oscar.nierstrasz, June 13, 2015</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>. Original image, unmodified.'},
  '5471': {heading:'IBM 5471', number:'STUDY 03 / SYSTEM/3 CONSOLE', description:'The System/3 printer-keyboard: a rounded light-gray shell, typewriter keys, separate request controls and status indicators, and the shared Selectric mechanism.', accuracy:'The reference’s hanging underside artifacts are excluded. Scale and rear details remain provisional; the keyboard follows IBM’s component manual.', photo:'references/ibm5471-manual-figure.jpg', credit:'5471 illustration: <a href="https://bitsavers.trailing-edge.com/pdf/ibm/system3/GA21-9103-1_System3_ComponentsRef_Nov70.pdf" target="_blank" rel="noopener">IBM System/3 Components Reference, GA21-9103-1, November 1970</a>, printed page 8-1, Figure 8-1 (cropped for display). Keyboard layout: page 8-2, Figure 8-2.'}
};
const cameras = {
 overview:['38deg 57deg 1.05m','0m 0.12m 0m'], front:['0deg 75deg 0.95m','0m 0.12m 0m'],
 left:['-43deg 65deg 1m','0m 0.12m 0m'],right:['43deg 65deg 1m','0m 0.12m 0m'],
 top:['0deg 3deg 0.95m','0m 0.12m 0m'],detail:['24deg 42deg 0.55m','0m 0.14m 0.07m']
};
const mv=document.querySelector('#mv'), still=document.querySelector('#still'), status=document.querySelector('#status');
let current='1053', preset='overview', mode='3d', controls, ready=false, generation=0, webglFailed=false;
function fallback(){
 webglFailed=true;ready=false;mode='render';controls?.dispose();controls=null;
 document.querySelector('[data-mode="3d"]').disabled=true;
 updateMode();
}
window.addEventListener('error',e=>{if(/WebGL|renderer|context|reading 'xr'|getFieldOfView/i.test(e.message||''))fallback();});
window.addEventListener('unhandledrejection',e=>{if(/WebGL|renderer|context|getFieldOfView/i.test(String(e.reason)))fallback();});
// Probe before importing model-viewer. A broken browser GL stack must not
// prevent model selection, still renders, references, or downloads.
const viewerReady=(async()=>{
 try{
  if(new URLSearchParams(location.search).has('renders'))throw new Error('Render-only view');
  const canvas=document.createElement('canvas');
  const gl=canvas.getContext('webgl2');
  if(!gl)throw new Error('WebGL 2 unavailable');
  gl.getExtension('WEBGL_lose_context')?.loseContext();
  await import('./vendor/model-viewer-4.0.0.min.js');
  await customElements.whenDefined('model-viewer');
  return !webglFailed;
 }catch(e){fallback();return false;}
})();
function updateMode(){
 mv.hidden=mode!=='3d';still.hidden=mode==='3d';
 if(mode!=='3d')still.src=mode==='reference'?studies[current].photo:`${current}/${preset}.png`;
 document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',String(b.dataset.mode===mode));});
 document.querySelectorAll('[data-action]').forEach(b=>b.disabled=mode!=='3d'||!ready);
 document.querySelectorAll('[data-preset]').forEach(b=>b.disabled=mode==='reference');
 status.textContent=mode==='reference'?'Original reference':mode==='render'?(webglFailed?'3D unavailable in this browser · Blender render':'Cycles render'):ready?'Ready · drag to inspect':'Loading 3D model…';
 if(mode!=='3d'&&controls)controls.setView(...cameras[preset]);
}
function setPreset(name){
 preset=name;
 document.querySelectorAll('[data-preset]').forEach(b=>b.classList.toggle('active',b.dataset.preset===name));
 if(controls){controls.setView(...cameras[name]);mv.jumpCameraToGoal();}
 updateMode();
}
async function selectModel(id){
 const token=++generation;current=id;ready=false;preset='overview';
 const s=studies[id];
 for(const [selector,value] of [['#model-title',s.heading],['#model-heading',s.heading],['#model-number',s.number],['#description',s.description],['#accuracy',s.accuracy]])document.querySelector(selector).textContent=value;
 document.querySelector('#reference-credit').innerHTML=s.credit;
 mv.alt=`Interactive reconstruction of the ${s.heading}`;
 document.querySelectorAll('[data-model]').forEach(b=>{b.classList.toggle('selected',b.dataset.model===id);b.setAttribute('aria-pressed',String(b.dataset.model===id));});
 for(const [selector,suffix] of [['#download-glb','.glb'],['#download-blend','.blend']])document.querySelector(selector).href=`${id}/ibm${id}${suffix}`;
 document.querySelector('#download-report').href=`${id}/report.json`;
 document.querySelector('#animate-mechanism').href=`animate.html?model=${id}`;
 document.querySelector('#mesh-count').textContent='—';document.querySelector('#dimensions').textContent='—';
 controls?.dispose();
 updateMode();
 const supported=await viewerReady;
 if(token!==generation)return;
 if(supported&&!webglFailed){
  controls=ModelControls.attach(mv,{orbit:cameras.overview[0],target:cameras.overview[1],pan:.02,min:.15,max:3,rotateButton:document.querySelector('[data-action="rotate"]')});
  setPreset('overview');
  const source=`${id}/ibm${id}.glb`, alreadyLoaded=mv.src===source&&mv.loaded;
  mv.src=source;
  if(alreadyLoaded){ready=true;updateMode();}
 }else{mode='render';setPreset('overview');}
 try{
  const response=await fetch(`${id}/report.json`);if(!response.ok)throw new Error('Report not found');
  const report=await response.json();if(token!==generation)return;
  document.querySelector('#mesh-count').textContent=report.mesh_count.toLocaleString();
  document.querySelector('#dimensions').textContent=report.dimensions_m.map(v=>Math.round(v*1000)).join(' × ');
 }catch(e){if(token===generation)status.textContent=e.message;}
}
mv.addEventListener('load',()=>{if(webglFailed||!mv.src.includes(`${current}/ibm${current}.glb`))return;ready=true;updateMode();});
mv.addEventListener('error',fallback);
still.addEventListener('error',()=>{status.textContent='Image unavailable; check the build output.';});
document.querySelectorAll('[data-model]').forEach(b=>b.onclick=()=>selectModel(b.dataset.model));
document.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>setPreset(b.dataset.preset));
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;updateMode();});
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{controls?.actions[b.dataset.action]();if(controls)mv.jumpCameraToGoal();});
fetch('models.json',{cache:'no-store'}).then(r=>r.json()).then(ids=>{
 document.querySelectorAll('[data-model]').forEach(b=>b.disabled=!ids.includes(b.dataset.model));
 if(!ids.length)throw new Error('No built models available');return selectModel(ids[0]);
}).catch(e=>status.textContent=e.message);
