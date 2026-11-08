#!/usr/bin/env python3
# /// script
# dependencies = ["pillow>=11"]
# ///
"""Original, deterministic TRS-80 print artwork, derived from visible legends."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'textures';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/gnu-free/FreeSansBold.otf'
def font(size):return ImageFont.truetype(FONT,size)
rows=[list('1234567890')+[': *','- =','BREAK'],list('QWERTYUIOP')+['@','↑','↓'],list('ASDFGHJKL')+['; +','ENTER'],['SHIFT']+list('ZXCVBNM')+[', <','. >','/ ?','SHIFT'],['←','SPACE','→']]
keys=[key for row in rows for key in row]+['CLEAR']
im=Image.new('RGBA',(1024,1024));d=ImageDraw.Draw(im)
for i,key in enumerate(keys):
 x=(i%8)*128+64;y=(i//8)*128+64
 d.text((x,y),'' if key=='SPACE' else key,font=font(19 if len(key)>2 else 38),fill=(25,27,26,255) if key=='ENTER' else (238,237,225,255),anchor='mm')
im.save(OUT/'trs80-key-legends.png',optimize=True)
for suffix,title in [('cpu','MICROCOMPUTER\nSYSTEM'),('expansion','EXPANSION\nINTERFACE'),('monitor','VIDEO\nDISPLAY'),('disk','MINI DISK')]:
 im=Image.new('RGB',(256,320),(23,25,25));d=ImageDraw.Draw(im)
 d.rectangle((5,5,250,314),outline=(192,195,185),width=6)
 d.rectangle((18,18,237,81),outline=(150,155,148),width=2)
 d.text((128,49),'Radio Shack',font=font(27),fill=(232,232,219),anchor='mm')
 d.rectangle((18,91,237,148),fill=(202,204,195))
 d.text((128,119),'TRS-80',font=font(31),fill=(30,32,31),anchor='mm')
 d.multiline_text((128,225),title,font=font(23),fill=(230,231,219),anchor='mm',align='center',spacing=8)
 im.save(OUT/('trs80-'+suffix+'-badge.png'),optimize=True)
print('TRS-80 key and badge artwork generated')
