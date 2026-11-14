#!/usr/bin/env python3
"""Verify the four new procedural preview pages and their source switches."""
import time,json,base64
from pathlib import Path
from check_preview import api
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/equipment-browser-check';OUT.mkdir(parents=True,exist_ok=True)
s=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1440,1000']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];p='/session/'+s
api('POST',p+'/timeouts',{'script':30000})
def js(code):return api('POST',p+'/execute/sync',{'script':code,'args':[]})
def wait(code):
 end=time.monotonic()+60
 while time.monotonic()<end:
  if js(code):return
  time.sleep(.15)
 raise AssertionError(code)
results=[]
try:
 api('POST',p+'/url',{'url':'http://127.0.0.1:5803/new-models.html'});wait('return document.querySelectorAll("#cards a").length===4')
 for model in ['3279','029','cor24','macbook']:
  api('POST',p+'/url',{'url':'http://127.0.0.1:5803/equipment.html?model='+model})
  wait('return document.querySelector("#image").complete && document.querySelector("#image").naturalWidth>0')
  assert js('return document.querySelector("#source").textContent.includes("our procedural")')
  js('document.querySelector("[data-mode=model]").click()');wait('return document.querySelector("#model").loaded')
  before=js('return document.querySelector("#model").getCameraOrbit().radius');js('document.querySelector("[data-action=zoom-in]").click()');time.sleep(.3)
  assert js('return document.querySelector("#model").getCameraOrbit().radius')<before
  js('document.querySelector("[data-mode=photo]").click()');wait('return document.querySelector("#image").complete && document.querySelector("#image").naturalWidth>0')
  js('document.querySelector("[data-mode=reference]").click()');wait('return document.querySelector("#model").loaded && document.querySelector("#model").src.includes("reference")')
  js('document.querySelector("[data-mode=render]").click();document.querySelector("[data-view=front]").click()');wait('return document.querySelector("#image").complete && document.querySelector("#image").naturalWidth>0')
  (OUT/(model+'.png')).write_bytes(base64.b64decode(api('GET',p+'/screenshot')))
  results.append({'model':model,'render':'passed','compactGLB':'passed','camera':'passed','photo':'passed','referenceGLB':'passed'})
 api('POST',p+'/window/rect',{'width':390,'height':844});assert js('return document.documentElement.scrollWidth<=innerWidth')
 errors=[x for x in api('POST',p+'/log',{'type':'browser'}) if x['level']=='SEVERE'];assert not errors,errors
 (OUT/'report.json').write_text(json.dumps({'pages':results,'mobile':'passed','errors':errors},indent=2)+'\n');print(json.dumps(results))
finally:api('DELETE',p)
