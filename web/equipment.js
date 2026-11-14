'use strict';
(async()=>{
 const entries=await fetch('new/catalog.json',{cache:'no-store'}).then(r=>r.json());
 const requested=new URLSearchParams(location.search).get('model'),entry=entries.find(m=>m.id===requested)||entries[0];
 const mv=document.querySelector('#model'),img=document.querySelector('#image'),status=document.querySelector('#source');
 const base='new/'+entry.id+'/';let mode='render',view='overview',controls;
 document.querySelector('#comparison-link').hidden=entry.id!=='029';
 document.title=entry.name+' · procedural preview';document.querySelector('#title').textContent=entry.name;document.querySelector('#note').textContent=entry.note;
 document.querySelector('#download').href=base+'model.glb';
 const cameras={overview:['35deg 65deg '+entry.radius+'m',entry.target],front:['0deg 75deg '+entry.radius+'m',entry.target],left:['-40deg 65deg '+entry.radius+'m',entry.target],right:['40deg 65deg '+entry.radius+'m',entry.target],top:['0deg 3deg '+entry.radius+'m',entry.target],detail:['20deg 45deg '+entry.radius*.65+'m',entry.target]};
 function update(){
  const interactive=mode==='model'||mode==='reference';img.hidden=interactive;mv.hidden=!interactive;
  document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
  document.querySelectorAll('[data-action]').forEach(b=>b.disabled=!interactive);
  if(!interactive){mv.autoRotate=false;img.src=mode==='photo'?entry.photo:base+view+'.png';status.textContent=mode==='photo'?'SOURCE: original supplied photograph':'SOURCE: our procedural Blender model · '+view;return;}
  const src=mode==='reference'?entry.reference:base+'model.glb';if(mv.getAttribute('src')!==src)mv.src=src;
  controls?.setView(...(mode==='reference'?[`${entry.id==='3279'?180:35}deg 65deg 2.6m`,'0m 0m 0m']:cameras[view]));mv.jumpCameraToGoal();status.textContent=mode==='reference'?'SOURCE: supplied detailed reconstruction · approximate scale':'SOURCE: our compact procedural 3D model';
 }
 await customElements.whenDefined('model-viewer');
 controls=ModelControls.attach(mv,{orbit:cameras.overview[0],target:entry.target,min:.005,max:10,pan:entry.pan||.02,rotateButton:document.querySelector('[data-action="rotate"]')});
 document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;update()});
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{view=b.dataset.view;update()});
 document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>{if(b.dataset.action==='reset')update();else controls.actions[b.dataset.action]();mv.jumpCameraToGoal()});
 mv.addEventListener('error',()=>status.textContent='Interactive render failed. Our Blender renders remain available; use the configured window with just view.');
 fetch(base+'report.json').then(r=>r.json()).then(r=>document.querySelector('#stats').textContent=`${r.triangle_count.toLocaleString()} triangles · ${r.mesh_count} meshes · ${(r.glb_bytes/1024).toFixed(0)} KiB · first-pass geometry`);
 update();
})().catch(e=>document.querySelector('#source').textContent=e.message);
