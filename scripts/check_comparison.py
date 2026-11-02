#!/usr/bin/env python3
"""Exercise both GLBs under synchronized orbit in the real comparison viewer."""
import base64
import json
from pathlib import Path
import time
import sys
from check_preview import api

ROOT=Path(__file__).resolve().parents[1]
MODEL=sys.argv[1] if len(sys.argv)>1 else '1053'
OUT=ROOT/('work/comparison-browser-check-'+MODEL);OUT.mkdir(parents=True,exist_ok=True)


def main():
    session=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1500,1100','--disable-background-timer-throttling','--disable-renderer-backgrounding']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    prefix='/session/'+session
    def js(script,*args):return api('POST',prefix+'/execute/sync',{'script':script,'args':list(args)})
    def wait(script,seconds=60):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if js(script):return
            time.sleep(.2)
        raise AssertionError('Timed out: '+script)
    def shot(name):
        (OUT/(name+'.png')).write_bytes(base64.b64decode(api('GET',prefix+'/screenshot')))
    try:
        api('POST',prefix+'/url',{'url':'http://127.0.0.1:5803/compare.html?model='+MODEL})
        wait("return document.querySelector('#compact').loaded && document.querySelector('#reference').loaded")
        shot('full-reference')
        if MODEL!='2741':
            js("document.querySelector('#focus').click()")
            wait("return document.querySelector('#reference').loaded && document.querySelector('#reference').src.includes('region')")
        results=[]
        for yaw in (0,45,90,135,180,225,270,315):
            state=js("""const c=document.querySelector('#compact'),r=document.querySelector('#reference');
              c.cameraOrbit=`${arguments[0]}deg 67deg 1m`;c.jumpCameraToGoal();
              c.dispatchEvent(new CustomEvent('camera-change',{detail:{source:'user-interaction'}}));
              const a=c.getCameraOrbit(),b=r.getCameraOrbit();return {yaw:arguments[0],compact:[a.theta,a.phi,a.radius],reference:[b.theta,b.phi,b.radius]};""",yaw)
            wait("const c=document.querySelector('#compact'),r=document.querySelector('#reference');const a=c.getCameraOrbit(),b=r.getCameraOrbit();const goal="+str(yaw)+"*Math.PI/180;return Math.abs(Math.atan2(Math.sin(a.theta-goal),Math.cos(a.theta-goal)))<.003 && Math.abs(a.theta-b.theta)<.003")
            state=js("const a=document.querySelector('#compact').getCameraOrbit(),b=document.querySelector('#reference').getCameraOrbit();return {yaw:arguments[0],compact:[a.theta,a.phi,a.radius],reference:[b.theta,b.phi,b.radius]}",yaw)
            assert max(abs(a-b) for a,b in zip(state['compact'],state['reference']))<.003,state
            shot('yaw-'+str(yaw).zfill(3))
            results.append(state)
        # Orbiting the reference must also move the compact model.
        js("const r=document.querySelector('#reference');r.cameraOrbit='-28deg 50deg .9m';r.jumpCameraToGoal()")
        wait("return Math.abs(document.querySelector('#reference').getCameraOrbit().theta+28*Math.PI/180)<.003")
        js("document.querySelector('#reference').dispatchEvent(new CustomEvent('camera-change',{detail:{source:'user-interaction'}}))")
        wait("return Math.abs(document.querySelector('#compact').getCameraOrbit().theta+28*Math.PI/180)<.003")
        js("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'s',bubbles:true}));document.querySelector('#compact').jumpCameraToGoal()")
        api('POST',prefix+'/window/rect',{'width':390,'height':844})
        assert js('return document.documentElement.scrollWidth<=innerWidth'),'Mobile horizontal overflow'
        shot('mobile')
        errors=[x for x in api('POST',prefix+'/log',{'type':'browser'}) if x['level']=='SEVERE']
        assert not errors,errors
        (OUT/'report.json').write_text(json.dumps({'rotations':results,'reverse_sync':'passed','mobile_overflow':False,'browser_errors':errors},indent=2)+'\n')
        print('Both GLBs loaded; eight matched rotations; reverse orbit sync; mobile layout; no severe console errors.')
    except Exception:
        shot('failure')
        raise
    finally:api('DELETE',prefix)


if __name__=='__main__':main()
