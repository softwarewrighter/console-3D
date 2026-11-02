#!/usr/bin/env python3
"""Generate through X_eTaL, run bounded Blender, promote only passing outputs."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model', choices=['1053', '2741', '5471', 'all'], default='all', nargs='?')
    p.add_argument('--device', choices=['CPU', 'OPTIX', 'CUDA', 'METAL'], default='CPU')
    p.add_argument('--timeout', type=int, default=600)
    p.add_argument('--candidate-only', action='store_true', help='Keep current passing output; inspect this candidate with scripts/compare.py before promotion')
    a = p.parse_args()
    ext = Path(os.environ.get('XETAL_EXTENSIONS_ROOT', ROOT/'X_eTaL-extensions')).resolve()
    binary = Path(os.environ.get('XETAL_BIN', ext/'target/release/xetal-x')).resolve()
    blender = shutil.which(os.environ.get('BLENDER_BIN', 'blender'))
    needed = [binary, ext/'extensions/blender/lib/Blender.xtl', ext/'extensions/blender/lib/Bpy.xtl']
    missing = [str(f) for f in needed if not f.is_file()]
    if missing:
        p.error('Missing X_eTaL dependencies: '+', '.join(missing)+'. See scripts/setup.sh.')
    if not blender:
        p.error('Blender not found; set BLENDER_BIN.')
    env = os.environ.copy()
    env['XETAL_PATH'] = os.pathsep.join([str(ext/'extensions/blender/lib'), str(ROOT)])
    env['XETAL_EXT_LIB_PATH'] = str(binary.parent)
    env['BLENDER_DEVICE'] = a.device
    for model in (['1053', '2741', '5471'] if a.model == 'all' else [a.model]):
        work = ROOT/'work'/('ibm'+model)
        work.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        candidate = work/('candidate-'+stamp)
        candidate.mkdir()
        env['BLENDER_USER_RESOURCES'] = str(candidate/'blender-user')
        env['XDG_CACHE_HOME'] = str(candidate/'cache')
        with (candidate/'generate.log').open('w') as log:
            subprocess.run([str(binary), '--ext', str(ext/'extensions/blender'), 'run', 'make-ibm'+model+'.xtl'], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
        cmd = [blender, '--background', '--factory-startup', '-noaudio', '--python-exit-code', '1', '--python', str(work/'scene.py'), '--', str(candidate)]
        print('Building IBM '+model+'; log: '+str(candidate/'blender.log'), flush=True)
        with (candidate/'blender.log').open('w') as log:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=a.timeout)
        expected = ['ibm'+model+suffix for suffix in ('.blend','.glb','.obj','.mtl')]+[v+'.png' for v in ('overview','front','left','right','top','detail')]+['report.json']
        for name in expected:
            f = candidate/name
            if not f.is_file() or f.stat().st_size == 0:
                raise RuntimeError('Missing fresh artifact: '+str(f))
        report = json.loads((candidate/'report.json').read_text())
        assert report['glb_round_trip'] == 'mesh names and bounds passed'
        report['xetal_extensions_commit'] = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ext, text=True).strip()
        (candidate/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        shutil.copyfile(work/'scene.py',candidate/'generated-scene.py')
        shutil.copyfile(ROOT/('Ibm'+model+'.xtl'),candidate/('Ibm'+model+'.xtl'))
        if a.candidate_only:
            print('Candidate ready for comparison: '+str(candidate),flush=True)
            continue
        current = work/'out'
        if current.exists():
            current.rename(work/('out-before-'+stamp))
        candidate.rename(current)
        print('Passed: '+str(current), flush=True)
    if not a.candidate_only:
        subprocess.run([sys.executable, str(ROOT/'scripts/make_preview.py')], check=True)


if __name__ == '__main__':
    main()
