#!/usr/bin/env python3
"""Assemble the three-model preview and paired reference comparisons."""
import json
from pathlib import Path
import shutil
import os

ROOT = Path(__file__).resolve().parents[1]
SHARED = Path(os.environ.get('LUCY_SHARED_ROOT', ROOT.parent/'lucy-3D/shared')).resolve()
OUT = ROOT/'work/preview'


def main():
    if not (SHARED/'viewer-controls.js').is_file():
        raise SystemExit('Missing Lucy shared controls; set LUCY_SHARED_ROOT.')
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (ROOT/'web').iterdir():
        if f.is_file():
            shutil.copyfile(f, OUT/f.name)
    shutil.copyfile(SHARED/'viewer-controls.js', OUT/'viewer-controls.js')
    shutil.copytree(SHARED/'vendor', OUT/'vendor', dirs_exist_ok=True)
    refs = OUT/'references'
    refs.mkdir(exist_ok=True)
    for f in (ROOT/'references').iterdir():
        if f.suffix in ('.jpg','.png'):shutil.copyfile(f, refs/f.name)
    available = []
    for model in ('1053', '2741', '5471'):
        source = ROOT/'work'/('ibm'+model)/'out'
        if not (source/'report.json').exists():
            continue
        target = OUT/model
        target.mkdir(exist_ok=True)
        for f in source.iterdir():
            if f.suffix in ('.glb','.blend','.obj','.mtl','.png','.json'):
                shutil.copyfile(f, target/f.name)
        available.append(model)
    if not available:
        raise SystemExit('No completed models; run just render first.')
    (OUT/'models.json').write_text(json.dumps(available)+'\n')
    (OUT/'reference').mkdir(exist_ok=True)
    for reference in (ROOT/'references').glob('*.glb'):
        shutil.copyfile(reference,OUT/'reference'/reference.name)
    comparisons=sorted(p.parent for p in (ROOT/'work/comparisons').glob('*/comparison.json'))
    latest={}
    for folder in comparisons:
        model=json.loads((folder/'comparison.json').read_text())['config'].get('model','1053')
        latest[model]=folder
    for model,folder in latest.items():
        target=OUT/('comparison' if model=='1053' else 'comparison-'+model);target.mkdir(exist_ok=True)
        for f in folder.iterdir():
            if f.suffix in ('.png','.glb','.json'):
                shutil.copyfile(f,target/f.name)
    print('Preview: '+str(OUT/'index.html'))


if __name__ == '__main__':
    main()
