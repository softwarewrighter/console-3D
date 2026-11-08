#!/usr/bin/env python3
"""Promote a visually reviewed candidate, with a concrete acceptance reason."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('comparison',type=Path)
p.add_argument('--reason',required=True,help='Feature, evidence, measurement, and remaining mismatch after reviewing all views')
a=p.parse_args()
report=a.comparison.resolve()
r=json.loads(report.read_text())
asset=Path(r['candidate']).resolve()
if hashlib.sha256(asset.read_bytes()).hexdigest()!=r['candidate_sha256']:
    p.error('Candidate changed after comparison; compare it again.')
if hashlib.sha256(Path(r.get('config_path',ROOT/'models/comparison.json')).read_bytes()).hexdigest()!=r['config_sha256']:
    p.error('Camera/alignment manifest changed after comparison; compare again.')
candidate=asset.parent
build=json.loads((candidate/'report.json').read_text())
model=build['model']
stem='trs80' if model=='trs80' else 'ibm'+model
if candidate.parent != ROOT/'work'/stem or not candidate.name.startswith('candidate-'):
    p.error('Expected an unpromoted model candidate directory.')
assert build['glb_round_trip']=='mesh names and bounds passed'
budget=r['config']['budget'];stats=r['candidate_stats']
for field in ('triangles','mesh_nodes','glb_bytes'):
    if stats[field]>budget[field]:p.error(f'{field} budget exceeded: {stats[field]} > {budget[field]}')
for view in r['config']['views']:
    assert (report.parent/('compare-'+view+'.png')).is_file()
for suffix in ('.glb','.blend','.obj','.mtl'):
    assert (candidate/(stem+suffix)).stat().st_size>0
stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
acceptance={'accepted_utc':datetime.now(timezone.utc).isoformat(),'comparison':str(report),'candidate_sha256':r['candidate_sha256'],'reason':a.reason,'budget':budget,'stats':stats,'reviewed_views':list(r['config']['views'])}
(candidate/'acceptance.json').write_text(json.dumps(acceptance,indent=2)+'\n')
current=ROOT/'work'/stem/'out'
if current.exists():current.rename(current.with_name('out-before-accepted-'+stamp))
candidate.rename(current)
subprocess.run([sys.executable,str(ROOT/'scripts/make_preview.py')],check=True)
print('Accepted: '+str(current))
