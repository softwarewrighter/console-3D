#!/usr/bin/env python3
"""Verify program control against actual exported pivots in Chromium."""
import base64
import json
from pathlib import Path
import sys
import time
from check_preview import api

ROOT=Path(__file__).resolve().parents[1]
models=sys.argv[1:] or ['2741','1053','5471']
OUT=ROOT/'work/animation-browser-check';OUT.mkdir(parents=True,exist_ok=True)
session=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1440,1100']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
prefix='/session/'+session
api('POST',prefix+'/timeouts',{'script':30000})
def js(script,*args):return api('POST',prefix+'/execute/sync',{'script':script,'args':list(args)})
def run(script):
    result=api('POST',prefix+'/execute/async',{'script':"const done=arguments[arguments.length-1];(async()=>{"+script+"})().then(value=>done({ok:true,value}),error=>done({ok:false,error:String(error)}));",'args':[]})
    assert result['ok'],result
    return result.get('value')
def wait(script):
    end=time.monotonic()+45
    while time.monotonic()<end:
        if js(script):return
        time.sleep(.1)
    raise AssertionError('Timed out: '+script)
results=[]
try:
    api('POST',prefix+'/url',{'url':'http://127.0.0.1:5803/animate.html?model='+models[0]})
    for model in models:
        wait('return !!window.selectric')
        if js('return window.selectricModel')!=model:run(f"await window.loadSelectricModel('{model}');")
        assert js('return window.selectricRig.spin.parent===window.selectricRig.tilt && window.selectricRig.tilt.parent===window.selectricRig.carrier')
        run('selectric.reset();')
        geometry=js("""let mesh;selectricRig.spin.traverse(o=>{if(o.isMesh&&!mesh)mesh=o;});
          if(!mesh)throw new Error('No type element geometry under spin pivot');
          window.movingElementMesh=mesh;window.fixedConsoleNode=selectricRig.carrier.parent;
          return {elementX:mesh.matrixWorld.elements[12],fixed:fixedConsoleNode.matrixWorld.toArray()};""")
        run('window.selectric.reset();await window.selectric.select({tilt:12,rotate:65,duration:90});await window.selectric.advance(5,{duration:120});')
        state=js('return {state:selectric.state,x:selectricRig.carrier.position.x,left:selectric.config.left_x_m,pitch:selectric.config.pitch_m,tilt:selectricRig.tilt.rotation.x,spin:selectricRig.spin.rotation.y}')
        assert state['state']['column']==5,state
        assert abs(state['x']-state['left']-5*state['pitch'])<1e-6,state
        assert abs(state['tilt']-.2094395102)<1e-5,state
        # Quaternion rotation is checked, rather than Euler spin beyond 90°.
        assert abs(state['spin']-1.134464014)<1e-5,state
        assert abs(js('return movingElementMesh.matrixWorld.elements[12]')-geometry['elementX']-5*state['pitch'])<1e-6
        assert js('return fixedConsoleNode.matrixWorld.toArray()')==geometry['fixed']
        (OUT/(model+'-selected.png')).write_bytes(base64.b64decode(api('GET',prefix+'/screenshot')))
        run('await selectric.backspace(2,{duration:80});');assert js('return selectric.state.column')==3
        run('await selectric.carriageReturn({duration:150});');assert js('return selectric.state.column')==0
        assert js('return selectric.state.tilt')==12
        js("window.outcome=null;selectric.run([{op:'advance',columns:20,duration:2000},{op:'select',tilt:-15,duration:0}]).then(()=>outcome='completed',e=>outcome=e.name)")
        wait('return selectric.state.column>0.1');js('selectric.stop()');wait("return outcome==='AbortError'")
        stopped=js('return selectric.state.column');time.sleep(.15);assert js('return selectric.state.column')==stopped
        assert js('return selectric.state.tilt')==12
        run('selectric.reset();await selectric.run(JSON.parse(document.querySelector("#program").value));');assert js('return selectric.state.column')==0
        results.append({'model':model,'hierarchy':'passed','tilt_rotate':'passed','advance_backspace_return':'passed','stop_cancels_queue':'passed','demo':'passed'})
    api('POST',prefix+'/window/rect',{'width':390,'height':844})
    assert js('return document.documentElement.scrollWidth<=innerWidth'),'Mobile overflow'
    errors=[x for x in api('POST',prefix+'/log',{'type':'browser'}) if x['level']=='SEVERE']
    assert not errors,errors
    (OUT/'report.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results));print('No severe browser errors; mobile layout passed.')
except Exception:
    (OUT/'failure.png').write_bytes(base64.b64decode(api('GET',prefix+'/screenshot')))
    raise
finally:api('DELETE',prefix)
