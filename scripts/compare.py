#!/usr/bin/env python3
"""Bounded reproducible comparison run; do not overwrite prior comparisons."""
import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=ROOT/'work/ibm1053/out/ibm1053.glb')
p.add_argument('--label',default='candidate')
p.add_argument('--model',choices=['1053','2741','5471','trs80'],default='1053')
a=p.parse_args()
if a.model!='1053' and a.candidate==ROOT/'work/ibm1053/out/ibm1053.glb':
    a.candidate=ROOT/'work'/('trs80' if a.model=='trs80' else 'ibm'+a.model)/'out'/('trs80.glb' if a.model=='trs80' else 'ibm'+a.model+'.glb')
config=ROOT/'models'/('comparison-'+a.model+'.json' if a.model!='1053' else 'comparison.json')
out=ROOT/'work/comparisons'/(datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+a.label)
out.mkdir(parents=True)
env=os.environ.copy();env['BLENDER_USER_RESOURCES']=str(out/'blender-user')
cmd=[os.environ.get('BLENDER_BIN','blender'),'--background','--factory-startup','-noaudio','--python-exit-code','1','--python',str(ROOT/'scripts/compare_models.py'),'--',str(a.candidate.resolve()),str(out),str(config)]
print('Comparison log: '+str(out/'blender.log'),flush=True)
with (out/'blender.log').open('w') as log:
    subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
assert (out/'comparison.json').is_file()
for view in ('front','left','right','top','rear'):
    assert (out/('compare-'+view+'.png')).stat().st_size>0
print('Passed: '+str(out))
