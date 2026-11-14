#!/usr/bin/env python3
"""Check the published 029 evidence page, assets, revised GLB and mobile layout."""
import base64,hashlib,json,time
from pathlib import Path
from urllib.request import urlopen
from check_preview import api
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/029-refinement/browser-check';OUT.mkdir(parents=True,exist_ok=True)
session=api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1500,1100']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];p='/session/'+session

def js(code):return api('POST',p+'/execute/sync',{'script':code,'args':[]})
def wait(code):
 end=time.monotonic()+60
 while time.monotonic()<end:
  if js(code):return
  time.sleep(.1)
 raise AssertionError(code)
try:
 base='http://127.0.0.1:5803/029-comparison/'
 api('POST',p+'/url',{'url':base});wait('return document.images.length>=13 && [...document.images].every(i=>i.complete&&i.naturalWidth>0)')
 assert js('return document.querySelectorAll(".triptych figure").length')==9
 (OUT/'desktop.png').write_bytes(base64.b64decode(api('GET',p+'/screenshot')))
 report=json.load(urlopen(base+'measurements.json'));assert hashlib.sha256(urlopen(base+'after.glb').read()).hexdigest()==report['after_sha256']
 assert hashlib.sha256(urlopen(base+'before.glb').read()).hexdigest()==report['before_sha256']
 # Both framed render pairs must use the same pixel dimensions as their photos.
 assert js('return [...document.querySelectorAll("section")].filter(s=>s.querySelector(".overlay")).every(s=>{const a=[...s.querySelectorAll(".triptych img")];return a.every(i=>i.naturalWidth===a[0].naturalWidth&&i.naturalHeight===a[0].naturalHeight)})')
 js('document.querySelector("details").open=true;document.querySelector("input[type=range]").value=35;document.querySelector("input[type=range]").dispatchEvent(new Event("input"))')
 assert js('return document.querySelector(".overlay img:last-child").style.opacity')=='0.35'
 api('POST',p+'/window/rect',{'width':390,'height':844});assert js('return document.documentElement.scrollWidth<=innerWidth')
 errors=[x for x in api('POST',p+'/log',{'type':'browser'}) if x['level']=='SEVERE'];assert not errors,errors
 (OUT/'report.json').write_text(json.dumps({'images':'13 loaded','triptychs':3,'glb_hashes':'passed','matched_image_dimensions':'passed','overlay':'passed','mobile':'passed','browser_errors':errors},indent=2)+'\n')
 print('029 comparison: photos, 3 triptychs, both GLB hashes, matching dimensions, overlay and mobile passed; no severe browser errors.')
finally:api('DELETE',p)
