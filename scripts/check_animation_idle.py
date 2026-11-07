#!/usr/bin/env python3
"""Exercise playback visibility, idle rendering, pause, and viewport controls."""
import base64
from pathlib import Path
import json
import time
from check_preview import api
session=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1280,800']}}}})['sessionId']
p='/session/'+session
def js(s):return api('POST',p+'/execute/sync',{'script':s,'args':[]})
def settle():time.sleep(.7)
try:
 api('POST',p+'/url',{'url':'http://127.0.0.1:5803/animate.html?model=2741'})
 for _ in range(150):
  if js('return !!window.selectric'):break
  time.sleep(.1)
 assert js('return !!window.selectric')
 settle();a=js('return selectricRenderStats');settle();b=js('return selectricRenderStats')
 assert a['frames']==b['frames'] and not b['pending'],(a,b)
 assert b['pixels']<=b['pixelBudget'],b
 assert js('const a=document.querySelector("#stage").getBoundingClientRect(),b=document.querySelector("#run-program").getBoundingClientRect();return a.bottom<=innerHeight && b.top>=0'), 'Controls and stage must fit together'
 js('document.querySelector("#run-program").click()');time.sleep(.2)
 activeStart=js('return {time:performance.now(),stats:selectricRenderStats}');time.sleep(1)
 activeEnd=js('return {time:performance.now(),stats:selectricRenderStats}')
 activeFPS=(activeEnd['stats']['frames']-activeStart['stats']['frames'])*1000/(activeEnd['time']-activeStart['time'])
 assert activeFPS>=5,activeEnd
 assert activeFPS<=22,activeEnd
 js('document.querySelector("#pause-program").click()');settle()
 a=js('return {pose:selectric.state,stats:selectricRenderStats}');settle();b=js('return {pose:selectric.state,stats:selectricRenderStats}')
 assert a==b,(a,b)
 js('document.querySelector("#pause-program").click()');time.sleep(.25)
 assert js('return !selectricRenderStats.paused')
 js("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
 settle();a=js('return {pose:selectric.state,stats:selectricRenderStats}');settle();b=js('return {pose:selectric.state,stats:selectricRenderStats}')
 assert a==b and not b['stats']['pending'],(a,b)
 js("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));document.querySelector('#stop').click()")
 settle();assert js('return !selectricRenderStats.continuous && !selectricRenderStats.pending')
 # Editing a long program suspends the offscreen stage; Run and view returns.
 js("document.querySelector('details').open=true;document.querySelector('textarea').style.height='1200px';window.scrollTo(0,document.body.scrollHeight)")
 settle();assert js('return !selectricRenderStats.visible && !selectricRenderStats.pending')
 js("document.querySelector('#run-from-editor').click()")
 settle();assert js('return selectricRenderStats.visible && selectric.state.busy')
 js("document.querySelector('#stop').click()")
 settle()
 out=Path('work/animation-browser-check');out.mkdir(parents=True,exist_ok=True)
 (out/'playback-controls.png').write_bytes(base64.b64decode(api('GET',p+'/screenshot')))
 print(json.dumps({'idle':'no scheduled work or renders','pause':'pose and frame count frozen','hidden':'pose and frame count frozen','viewport':'Run and entire stage visible at 1280x800','pixelBudget':b['stats']['pixelBudget'],'fpsLimit':b['stats']['fpsLimit'],'measuredFPS':round(activeFPS,1),'lastRenderMs':round(activeEnd['stats']['lastRenderMs'],1)}))
finally:api('DELETE',p)
