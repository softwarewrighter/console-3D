# /// script
# dependencies = ["pillow>=11"]
# ///
"""Labeled photo / supplied GLB / compact-model sheet. Originals remain intact."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('comparison',type=Path);p.add_argument('--out',type=Path,default=ROOT/'work/preview/pcdual-three-way.png');a=p.parse_args()
folder=a.comparison;report=json.loads((folder/'comparison.json').read_text());stats=report['candidate_stats']
width=1000;height=850;sheet=Image.new('RGB',(width*3,height),(24,31,34));d=ImageDraw.Draw(sheet)
fontfile='/usr/share/fonts/gnu-free/FreeSans.otf';font=ImageFont.truetype(fontfile,30);small=ImageFont.truetype(fontfile,21)
items=[('Original photograph',ROOT/'references/ibmpc-dual-photo.jpg','Unmodified photo; right-hand monitor is cropped in source'),('Supplied detailed GLB',folder/'reference-full-front.png',f"{report['reference_full']['triangles']:,} triangles; approximate reconstructed geometry"),('Our compact Blender model',folder/'candidate-front.png',f"{stats['triangles']:,} triangles / {stats['mesh_nodes']} meshes / {stats['glb_bytes']/1024:.0f} KiB")]
for i,(label,path,note) in enumerate(items):
 x=i*width;d.text((x+22,22),label,font=font,fill=(224,234,234));d.text((x+22,height-50),note,font=small,fill=(168,192,195))
 image=Image.open(path).convert('RGBA');bg=Image.new('RGBA',image.size,(42,49,52,255));bg.alpha_composite(image);tile=ImageOps.contain(bg.convert('RGB'),(width-20,height-140))
 sheet.paste(tile,(x+(width-tile.width)//2,85+(height-140-tile.height)//2));d.line((x,0,x,height),fill=(87,110,115),width=2)
a.out.parent.mkdir(parents=True,exist_ok=True);sheet.save(a.out);sheet.save(a.out.with_suffix('.jpg'),quality=92)
sheet.save(folder/'photo-detailed-compact.png');sheet.save(folder/'photo-detailed-compact.jpg',quality=92)
print(a.out)
