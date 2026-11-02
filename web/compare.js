'use strict';
const compact=document.querySelector('#compact'),reference=document.querySelector('#reference');
const requested=new URLSearchParams(location.search).get('model');
const model=['2741','5471'].includes(requested)?requested:'1053';
const folder=model==='1053'?'comparison':'comparison-'+model;
const views={overview:'38deg 67deg 1m',front:'0deg 90deg 1m',left:'-40deg 69deg 1m',right:'40deg 69deg 1m',top:'0deg 3deg 1m',rear:'180deg 75deg 1m'};
let controls,focus=model==='2741',loaded=new Set();
if(model==='2741'){
 document.title='2741 · Reference comparison';
 document.querySelector('.comparison-head p:not(.eyebrow)').textContent='Compare the complete desktop 2741 reference with the compact APL terminal. Both use the loaded-paper configuration. Orbit either model to turn both together; scale remains provisional.';
 document.querySelector('.study:nth-child(2) h2').textContent='Compact IBM 2741 · latest candidate';
 document.querySelector('#reference-stats').textContent='One textured mesh · 144,046 triangles · 6.25 MiB original';
 document.querySelector('#focus').hidden=true;
 document.querySelector('#full').textContent='Complete reference terminal';
 document.querySelector('.evidence p:not(.eyebrow)').textContent='The 2741 comparison uses the complete reference terminal. Sheets show the reference, the compact reconstruction, and silhouette differences under the same cameras and lighting. The reference itself is a reconstruction, so original photos remain the authority for small details.';
}
if(model==='5471'){
 document.title='5471 · Reference comparison';
 document.querySelector('.comparison-head p:not(.eyebrow)').textContent='Compare the IBM 5471 System/3 console with the supplied dense reference. The compact lower case is clean, following the user’s correction and the IBM illustration. The original reference retains its underside anomalies for inspection.';
 document.querySelector('.study:nth-child(2) h2').textContent='Compact IBM 5471 · latest candidate';
 document.querySelector('#reference-stats').textContent='One textured mesh · 146,282 triangles · 5.68 MiB original';
 document.querySelector('#full').textContent='Original reference (with artifacts)';
 document.querySelector('#focus').textContent='Body comparison (artifacts excluded)';
 document.querySelector('.evidence p:not(.eyebrow)').textContent='The diagnostic reference region excludes the known hanging underside. The compact model uses a clean, rounded case like the 2741 and IBM’s 5471 illustration. Control legends follow IBM’s System/3 Components Reference, Figures 8-1 and 8-2.';
}
document.querySelectorAll('a[href^="comparison/"]').forEach(a=>a.href=a.getAttribute('href').replace('comparison/',folder+'/'));
document.querySelector('.sheets img').src=folder+'/compare-front.png';
document.querySelector('a[download]').href='reference/'+(model==='1053'?'ibm1130-superset-reference.glb':'ibm'+model+'-reference.glb');
function synchronize(from,to){
 const o=from.getCameraOrbit(),t=from.getCameraTarget();
 const ratio=focus||model!=='1053'?1:1.65;
 const radius=from===compact?o.radius*ratio:o.radius/ratio;
 to.cameraOrbit=`${o.theta}rad ${o.phi}rad ${radius}m`;
 to.cameraTarget=focus||model!=='1053'?`${t.x}m ${t.y}m ${t.z}m`:to===reference?'0.13m 0.13m 0.10m':'0m 0.10m 0m';
 to.jumpCameraToGoal();
}
function view(name){
 controls.setView(views[name],'0m 0.10m 0m');compact.jumpCameraToGoal();synchronize(compact,reference);
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name));
}
function mode(isFocus){
 focus=isFocus||model==='2741';reference.src=folder+'/'+(focus&&model!=='2741'?'reference-region.glb':'reference-aligned.glb');
 document.querySelector('#reference-title').textContent=model==='2741'?'Supplied reference · complete IBM 2741':model==='5471'?(focus?'Reference · underside artifacts excluded':'Supplied reference · underside artifacts retained'):focus?'Reference · diagnostic printer region':'Supplied reference · full console';
 document.querySelector('#full').classList.toggle('active',!focus||model==='2741');document.querySelector('#focus').classList.toggle('active',focus);
 view('overview');
}
customElements.whenDefined('model-viewer').then(()=>{
 controls=ModelControls.attach(compact,{orbit:views.overview,target:'0m 0.10m 0m',min:.2,max:4,pan:.02,rotateButton:document.querySelector('[data-action="rotate"]')});
 compact.addEventListener('camera-change',()=>synchronize(compact,reference));
 reference.addEventListener('camera-change',e=>{if(e.detail.source==='user-interaction')synchronize(reference,compact);});
 for(const mv of [compact,reference]){
  mv.addEventListener('load',()=>{loaded.add(mv.id);document.querySelector('#compare-status').textContent=loaded.size===2?'Ready · orbit either model to compare':'Loading both models…';synchronize(compact,reference);});
  mv.addEventListener('error',()=>document.querySelector('#compare-status').textContent='Interactive setup failed. Open with just view, using the configured Chromium window.');
 }
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
 document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{controls.actions[b.dataset.action]();compact.jumpCameraToGoal();synchronize(compact,reference);});
 document.querySelector('#full').onclick=()=>mode(false);document.querySelector('#focus').onclick=()=>mode(true);
 compact.src=`${model}/ibm${model}.glb`;mode(false);
 fetch(`${model}/report.json`).then(r=>r.json()).then(r=>document.querySelector('#compact-stats').textContent=`${r.mesh_count} meshes · ${r.triangle_count?.toLocaleString()||'see report'} triangles · ${r.glb_bytes?(r.glb_bytes/1024).toFixed(0)+' KiB':'see report for size'}`);
});
