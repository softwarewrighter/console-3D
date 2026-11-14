#!/usr/bin/env python3
"""Copy complete candidate artifacts to an explicitly provisional preview area."""
from pathlib import Path
import json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/preview'
models=[dict(id='3279',name='IBM 3279 graphics terminal',stem='ibm3279',photo='references/ibm3279-photo.jpg',ref='ibm3279-reference.glb',radius=1.9,target='0m .27m .02m',note='Our procedural color terminal and sculpted keyboard. Provisional scale and controls.'),dict(id='029',name='IBM 029 keypunch',stem='ibm029',photo='references/ibm029-photo.jpg',ref='ibm029-reference.glb',radius=3.1,target='0m .65m 0m',note='Columbia-photo refinement: open card route, separate hoppers, raked program window and 49-cap combination keyboard. Shallow rear cabinet leaves operator knee space; detached keyboard has a visible tabletop gap. Scale and hidden details remain approximate.'),dict(id='cor24',name='COR24-TB development board',stem='cor24',photo='references/cor24-photo.jpg',ref='cor24-reference.glb',radius=.16,target='0m .003m 0m',pan=.002,note='Our procedural PCB, FPGA, SRAM, USB socket, switches and headers. Trace artwork and package details are reconstructed.'),dict(id='macbook',name='MacBook Pro M1 Max',stem='macbook',photo='references/macbook-photo.jpg',ref='macbook-reference.glb',radius=.85,target='0m .12m -.015m',note='Our procedural open laptop. Provisional 16-inch envelope, lid angle, ports and keyboard; screen lettering approximate.')]
subprocess.run([sys.executable,str(ROOT/'scripts/make_preview.py')],check=True)
entries=[]
for m in models:
 candidates=sorted((ROOT/'work'/m['stem']).glob('candidate-*/report.json'))
 if not candidates:continue
 source=candidates[-1].parent;target=OUT/'new'/m['id'];target.mkdir(parents=True,exist_ok=True)
 for f in source.glob('*.png'):shutil.copyfile(f,target/f.name)
 shutil.copyfile(source/(m['stem']+'.glb'),target/'model.glb');shutil.copyfile(source/'report.json',target/'report.json')
 m['reference']='reference/'+m.pop('ref');entries.append(m)
(OUT/'new/catalog.json').write_text(json.dumps(entries,indent=2)+'\n')
print('Preview index: http://192.168.1.178:5803/new-models.html')
for m in entries:print('http://192.168.1.178:5803/equipment.html?model='+m['id'])
