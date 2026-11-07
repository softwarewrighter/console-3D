import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {FramePump,ActiveClock} from './frame-pump.mjs';
import {SelectricMachine} from './selectric-machine.mjs';

const stage=document.querySelector('#stage'),stageStatus=document.querySelector('#stage-status');
const motionStatus=document.querySelector('#motion-status'),selector=document.querySelector('#machine-model');
const demo=[{op:'select',tilt:-12,rotate:-65,duration:400},{op:'advance',columns:1},{op:'select',tilt:4,rotate:35,duration:250},{op:'advance',columns:1},{op:'select',tilt:12,rotate:120,duration:250},{op:'advance',columns:1},{op:'backspace',columns:1,duration:300},{op:'select',tilt:-4,rotate:-30,duration:250},{op:'advance',columns:1},{op:'advance',columns:8,duration:900},{op:'return',duration:900}];
const program=document.querySelector('#program');program.value=JSON.stringify(demo,null,2);
let machine,modelRoot,rig,generation=0,follow=false;
const scene=new THREE.Scene();scene.background=new THREE.Color('#222c31');
const camera=new THREE.PerspectiveCamera(35,1,.001,20);
let renderer;
try{renderer=new THREE.WebGLRenderer({antialias:false});}catch(e){stageStatus.textContent='Animation rendering unavailable. Run just view-animate from the project directory to open the configured animation window.';throw e;}
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
stage.append(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff,0x39444c,2));
const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(1,2,2);scene.add(light);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=false;orbit.minDistance=.08;orbit.maxDistance=3;
const vector=new THREE.Vector3(),clock=new ActiveClock();
let manualPaused=false,inView=true,pixelBudget=100000;
const pump=new FramePump(()=>{
 if(follow&&rig){rig.carrier.getWorldPosition(vector);const dx=vector.x-orbit.target.x;orbit.target.x+=dx;camera.position.x+=dx;}
 orbit.update(1/pump.fps);renderer.render(scene,camera);
 // Wait for completion so a slow GPU cannot build seconds of queued frames.
 renderer.getContext().finish();
});
Object.defineProperty(window,'selectricRenderStats',{get:()=>({...pump.stats,pixels:renderer.domElement.width*renderer.domElement.height,pixelBudget})});
function activity(){const visible=!document.hidden&&inView;clock.pause('visibility',!visible);clock.pause('manual',manualPaused);pump.activity(visible,manualPaused);document.querySelector('#pause-program').textContent=manualPaused?'Resume':'Pause';}
document.addEventListener('visibilitychange',activity);
new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;activity();}).observe(stage);
orbit.addEventListener('change',()=>pump.invalidate());
stage.addEventListener('pointerdown',()=>stage.focus({preventScroll:true}));
function angle(token){return parseFloat(token)*(token.endsWith('deg')?Math.PI/180:1);}
const adapter={
 getCameraOrbit(){const v=camera.position.clone().sub(orbit.target),r=v.length();return {theta:Math.atan2(v.x,v.z),phi:Math.acos(THREE.MathUtils.clamp(v.y/r,-1,1)),radius:r};},
 getCameraTarget(){return orbit.target.clone();},
 set cameraOrbit(value){const [theta,phi,r]=value.split(/\s+/).map(angle);camera.position.set(orbit.target.x+r*Math.sin(phi)*Math.sin(theta),orbit.target.y+r*Math.cos(phi),orbit.target.z+r*Math.sin(phi)*Math.cos(theta));orbit.update();},
 set cameraTarget(value){const old=orbit.target.clone();orbit.target.set(...value.split(/\s+/).map(parseFloat));camera.position.add(orbit.target.clone().sub(old));orbit.update();},
 get autoRotate(){return orbit.autoRotate;},set autoRotate(value){orbit.autoRotate=value;pump.continuous=value;pump.invalidate();},setAttribute(){},removeAttribute(){}
};
const overview={orbit:'38deg 57deg 1m',target:'0m .11m 0m'};
camera.position.set(.5,.4,.8);orbit.target.set(0,.11,0);orbit.update();
const controls=ModelControls.attach(adapter,{host:stage,orbit:overview.orbit,target:overview.target,min:.08,max:3,pan:.02});
function configTargetX(){return machine.config.left_x_m+machine.config.pitch_m*machine.config.max_column/6;}
function view(name){
 follow=name==='mechanism';adapter.autoRotate=false;
 if(name==='mechanism'&&rig){rig.carrier.getWorldPosition(vector);controls.setView('25deg 32deg .27m',`${vector.x}m ${vector.y}m ${vector.z}m`);}
 else if(name==='typing'&&rig){rig.carrier.getWorldPosition(vector);controls.setView('10deg 45deg .58m',`${configTargetX()}m ${vector.y}m ${vector.z}m`);}
 else if(name==='top')controls.setView('0deg 3deg .85m',overview.target);
 else controls.setView(overview.orbit,overview.target);
}
document.querySelectorAll('[data-camera]').forEach(b=>b.onclick=()=>{if(controls.actions[b.dataset.camera])controls.actions[b.dataset.camera]();else view(b.dataset.camera);});
orbit.addEventListener('start',()=>{follow=false;});
function resize(){const w=stage.clientWidth,h=stage.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setPixelRatio(Math.min(devicePixelRatio,1,Math.sqrt(pixelBudget/(w*h))));renderer.setSize(w,h,false);pump.invalidate();}
new ResizeObserver(resize).observe(stage);
document.querySelector('#render-quality').onchange=e=>{pump.fps=Number(e.target.value);pixelBudget=({12:60000,20:100000,30:220000})[pump.fps];resize();};
function free(root){const geometries=new Set(),materials=new Set(),textures=new Set();root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of (Array.isArray(o.material)?o.material:[o.material]))if(m){materials.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value);}});geometries.forEach(x=>x.dispose());materials.forEach(x=>x.dispose());textures.forEach(x=>x.dispose());}
async function loadModel(model){
 manualPaused=false;activity();const token=++generation;machine?.dispose();machine=null;rig=null;window.selectric=null;
 document.querySelectorAll('[data-motion]').forEach(b=>b.disabled=true);stageStatus.textContent=`Loading IBM ${model}…`;
 if(modelRoot){scene.remove(modelRoot);free(modelRoot);modelRoot=null;}
 const response=await fetch(`${model}/mechanism.json`,{cache:'no-store'});if(!response.ok)throw new Error('Mechanism rig is not built for '+model);
 const config=await response.json(),gltf=await new GLTFLoader().loadAsync(`${model}/ibm${model}.glb`);
 if(token!==generation){free(gltf.scene);return;}
 const nodes=Object.fromEntries(Object.entries(config.nodes).map(([role,name])=>[role,gltf.scene.getObjectByName(name)]));
 if(Object.values(nodes).some(node=>!node)){free(gltf.scene);throw new Error('Missing mechanism pivot');}
 // Animation prioritizes responsive motion: textured diffuse shading avoids the
 // expensive physical/environment shader used by the static inspection viewer.
 const simpleMaterials=new Map();
 gltf.scene.traverse(o=>{if(!o.isMesh)return;const simplify=m=>{if(!simpleMaterials.has(m))simpleMaterials.set(m,new THREE.MeshBasicMaterial({color:m.color,map:m.map,side:m.side,transparent:m.transparent,opacity:m.opacity,alphaTest:m.alphaTest}));return simpleMaterials.get(m);};o.material=Array.isArray(o.material)?o.material.map(simplify):simplify(o.material);});
 for(const original of simpleMaterials.keys())original.dispose();
 modelRoot=gltf.scene;scene.add(modelRoot);rig=nodes;
 const tiltRest=nodes.tilt.quaternion.clone(),spinRest=nodes.spin.quaternion.clone();
 const tiltAxis=new THREE.Vector3(1,0,0),spinAxis=new THREE.Vector3(0,1,0),q=new THREE.Quaternion();
 let previousPose;
 machine=new SelectricMachine(config,pose=>{
  if(previousPose&&Object.keys(pose).every(k=>pose[k]===previousPose[k]))return;previousPose=pose;
  nodes.carrier.position.x=config.left_x_m+pose.column*config.pitch_m;
  nodes.tilt.quaternion.copy(tiltRest).multiply(q.setFromAxisAngle(tiltAxis,THREE.MathUtils.degToRad(pose.tilt)));
  nodes.spin.quaternion.copy(spinRest).multiply(q.setFromAxisAngle(spinAxis,THREE.MathUtils.degToRad(pose.rotate)));
  nodes.carrier.updateMatrixWorld(true);pump.invalidate();
 },{now:()=>clock.now(),requestFrame:cb=>pump.request(cb),cancelFrame:id=>pump.cancel(id),onChange:state=>{document.querySelector('#run-program').disabled=state.busy;document.querySelector('#run-from-editor').disabled=state.busy;document.querySelector('#motion-state').textContent=`Column ${state.column.toFixed(1)} · tilt ${state.tilt.toFixed(1)}° · rotation ${state.rotate.toFixed(1)}°`;}});
 window.selectric=machine;window.selectricRig=nodes;window.selectricModel=model;
 document.querySelector('#mechanism-model').textContent='IBM '+model;selector.value=model;
 document.querySelector('#rig-download').href=`${model}/ibm${model}.glb`;
 stageStatus.textContent=`IBM ${model} · ready`;motionStatus.textContent='Ready';
 document.querySelectorAll('[data-motion]').forEach(b=>b.disabled=false);view('typing');
 return machine;
}
window.loadSelectricModel=loadModel;
async function invoke(action){const owner=machine;if(!owner)return;try{motionStatus.textContent='Running…';await action(owner);if(machine===owner)motionStatus.textContent='Ready';}catch(e){if(machine===owner)motionStatus.textContent=e.name==='AbortError'?'Stopped':e.message;}}
for(const id of ['tilt','spin'])document.querySelector('#'+id).oninput=e=>document.querySelector('#'+id+'-value').textContent=e.target.value+'°';
document.querySelector('#select-pose').onclick=()=>invoke(m=>m.select({tilt:Number(document.querySelector('#tilt').value),rotate:Number(document.querySelector('#spin').value),duration:350}));
document.querySelector('#advance').onclick=()=>invoke(m=>m.advance());
document.querySelector('#backspace').onclick=()=>invoke(m=>m.backspace());
document.querySelector('#return').onclick=()=>invoke(m=>m.carriageReturn());
document.querySelector('#pause-program').onclick=()=>{if(!machine?.state.busy)return;manualPaused=!manualPaused;activity();motionStatus.textContent=manualPaused?'Paused':'Running…';};
document.querySelector('#stop').onclick=()=>{manualPaused=false;activity();machine?.stop();motionStatus.textContent='Stopped';};
document.querySelector('#reset-motion').onclick=()=>{manualPaused=false;activity();machine?.reset();motionStatus.textContent='Ready';};
document.querySelector('#load-demo').onclick=()=>program.value=JSON.stringify(demo,null,2);
function runProgram(){document.querySelector('#workspace').scrollIntoView({block:'start'});manualPaused=false;activity();return invoke(m=>m.run(JSON.parse(program.value)));}
document.querySelector('#run-program').onclick=()=>{document.querySelector('#workspace').scrollIntoView({block:'start'});manualPaused=false;activity();view('typing');return invoke(m=>m.typeContinuously({onPrint:showPrint}));};document.querySelector('#run-from-editor').onclick=runProgram;
selector.onchange=()=>loadModel(selector.value).catch(e=>stageStatus.textContent=e.message);
fetch('mechanisms.json',{cache:'no-store'}).then(r=>r.json()).then(ids=>{
 for(const option of selector.options){option.disabled=!ids.includes(option.value);if(option.disabled)option.textContent+=' (rig not built yet)';}
 if(!ids.length)throw new Error('Build a mechanism-enabled model first.');
 const requested=new URLSearchParams(location.search).get('model');
 return loadModel(ids.includes(requested)?requested:ids.includes('2741')?'2741':ids[0]);
}).catch(e=>stageStatus.textContent=e.message);

const paper=document.querySelector('#printed-paper'),paperContext=paper.getContext('2d');
const sampleText='THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. IBM SELECTRIC 2741 1053 5471. ';
let lastPaper='';
function showPrint(sample){
 const key=`${sample.line}:${sample.count}:${sample.feed.toFixed(2)}`;if(key===lastPaper)return;lastPaper=key;
 paperContext.fillStyle='#f5efd9';paperContext.fillRect(0,0,paper.width,paper.height);
 paperContext.fillStyle='#172020';paperContext.font='18px monospace';
 const columns=Math.floor(machine.config.max_column/3),feed=sample.feed-sample.line;
 for(let row=Math.max(0,sample.line-2);row<=sample.line;row++){
  const count=row===sample.line?sample.count:columns;
  const text=Array.from({length:count},(_,i)=>sampleText[(row*columns+i)%sampleText.length]).join('');
  paperContext.fillText(text,16,96-(sample.line-row+feed)*25);
 }
 document.querySelector('#typing-status').textContent=`13 characters/s · ${sample.count}/${columns} · line ${sample.line+1} · ${sample.phase}`;
}
