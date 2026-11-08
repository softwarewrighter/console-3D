#!/usr/bin/env python3
"""Browser smoke check using a running ChromeDriver (no Python dependencies).

Start the preview on :5803 and chromedriver on :9515 before running this script.
"""
import base64
import json
from pathlib import Path
import time
import sys
from urllib.request import Request, urlopen

BASE = 'http://127.0.0.1:9515'
OUT = Path(__file__).resolve().parents[1]/'work/browser-check'
OUT.mkdir(parents=True, exist_ok=True)


def api(method, path, body=None):
    req = Request(BASE+path, data=None if body is None else json.dumps(body).encode(), method=method, headers={'Content-Type':'application/json'})
    with urlopen(req, timeout=60) as r:
        return json.load(r)['value']


def main():
    session = api('POST','/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--window-size=1440,1100']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    prefix = '/session/'+session

    def js(script, *args):
        return api('POST',prefix+'/execute/sync',{'script':script,'args':list(args)})

    def wait(script, timeout=50):
        until = time.monotonic()+timeout
        while time.monotonic() < until:
            if js(script):
                return
            time.sleep(.25)
        raise AssertionError('Browser condition timed out: '+script)

    def click(selector):
        js('document.querySelector(arguments[0]).click()',selector)

    def shot(name):
        data = api('GET',prefix+'/screenshot')
        (OUT/(name+'.png')).write_bytes(base64.b64decode(data))

    results = []
    try:
        if '--renders-only' in sys.argv:
            api('POST',prefix+'/url',{'url':'http://127.0.0.1:5803/?renders=1'})
            wait("return document.querySelector('#still').complete && document.querySelector('#still').naturalWidth > 0")
            for model in ('2741','5471','trs80','1053'):
                click('[data-model="'+model+'"]')
                wait("return document.querySelector('#still').complete && document.querySelector('#still').naturalWidth > 0")
                assert js("return document.querySelector('#model-heading').textContent") == ('TRS-80 Model I' if model=='trs80' else 'IBM '+model)
                assert js("return document.querySelector('[data-mode=\"3d\"]').disabled")
            click('[data-mode="reference"]')
            wait("return document.querySelector('#still').complete && document.querySelector('#still').naturalWidth > 0")
            assert not [x for x in api('POST',prefix+'/log',{'type':'browser'}) if x['level']=='SEVERE']
            shot('render-fallback')
            (OUT/'fallback-report.json').write_text(json.dumps({'render_only':'both model switches and reference images passed','console':'no severe errors'},indent=2)+'\n')
            print('Render-only fallback: both model switches, reference photo, and browser console passed')
            return
        api('POST',prefix+'/url',{'url':'http://127.0.0.1:5803/'})
        for model in ('1053','2741','5471','trs80','1053'):
            click('[data-model="'+model+'"]')
            wait("return document.querySelector('#status').textContent.startsWith('Ready') && document.querySelector('#mv').loaded")
            assert js("return document.querySelector('#model-heading').textContent") == ('TRS-80 Model I' if model=='trs80' else 'IBM '+model)
            assert js("return document.querySelector('#mv').src").endswith(model+'/'+('trs80' if model=='trs80' else 'ibm'+model)+'.glb')
            assert js("return document.querySelector('#animate-mechanism').hidden") == (model=='trs80')
            click('[data-preset="detail"]')
            assert js("return document.querySelector('#mv').cameraTarget") == ('0m .07m .235m' if model=='trs80' else '0m 0.14m 0.07m')
            time.sleep(.7)
            before = js("return document.querySelector('#mv').getCameraOrbit().radius")
            click('[data-action="zoom-in"]')
            time.sleep(.5)
            after = js("return document.querySelector('#mv').getCameraOrbit().radius")
            assert after < before, {'before':before,'after':after,'orbit':js("return document.querySelector('#mv').cameraOrbit"),'disabled':js("return document.querySelector('[data-action=zoom-in]').disabled")}
            click('[data-action="reset"]')
            click('[data-mode="render"]')
            wait("return document.querySelector('#still').complete && document.querySelector('#still').naturalWidth > 0")
            assert js("return document.querySelector('#mv').hidden")
            click('[data-mode="reference"]')
            wait("return document.querySelector('#still').complete && document.querySelector('#still').naturalWidth > 0")
            click('[data-mode="3d"]')
            assert not js("return document.querySelector('#mv').hidden")
            shot(model+'-desktop')
            results.append(('TRS-80 Model I' if model=='trs80' else 'IBM '+model)+': loaded, camera preset, zoom/reset, render and reference switches passed')
        # Exercise shared keyboard handling after repeated model changes. Exactly
        # one handler should apply a 1.25x zoom-out per key press.
        before = js("return document.querySelector('#mv').getCameraOrbit().radius")
        js("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'s',bubbles:true}))")
        js("document.querySelector('#mv').jumpCameraToGoal()")
        time.sleep(.7)
        after = js("return document.querySelector('#mv').getCameraOrbit().radius")
        assert abs(after/before-1.25) < .02, (before,after)
        results.append('Single shared keyboard listener after model switches passed')
        api('POST',prefix+'/window/rect',{'width':390,'height':844})
        assert js('return document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile horizontal overflow'
        shot('mobile')
        results.append('390px mobile layout: no horizontal overflow')
        errors = [x for x in api('POST',prefix+'/log',{'type':'browser'}) if x['level']=='SEVERE']
        assert not errors, errors
        results.append('Browser console: no severe errors')
        (OUT/'report.json').write_text(json.dumps(results,indent=2)+'\n')
        print('\n'.join(results))
    except Exception:
        shot('failure')
        raise
    finally:
        api('DELETE',prefix)


if __name__ == '__main__':
    main()
