# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Deterministic printed legends, not photographic textures. uv run this file."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'textures';OUT.mkdir(exist_ok=True)
font_file='/usr/share/fonts/gnu-free/FreeSansBold.otf'
font=ImageFont.truetype(font_file,38)
image=Image.new('RGBA',(2048,512),(0,0,0,0));d=ImageDraw.Draw(image)
def xy(x,z):return ((x/.552+.5)*2048,(.155-z)/.143*512)
for bit in range(16):
    d.text(xy(-.143+bit*.024,.134),str(bit),font=font,fill=(238,237,220,255),anchor='mm')
for x in (-.155,-.059,.037,.133,.229):
    d.line([xy(x,.117),xy(x,.141)],fill=(238,237,220,255),width=3)
image.save(OUT/'1053-fascia-print.png',optimize=True)

image=Image.new('RGB',(2048,64),(180,188,182));d=ImageDraw.Draw(image)
font=ImageFont.truetype(font_file,21)
for i in range(131):
    x=18+i/130*(2048-36)
    d.line([(x,3),(x,23 if i%5==0 else 15)],fill=(17,22,24),width=2)
    if i%5==0:d.text((x,45),str(i),font=font,fill=(17,22,24),anchor='mm')
d.line([(0,0),(2047,0),(2047,63),(0,63),(0,0)],fill=(215,220,215),width=2)
image.save(OUT/'1053-carrier-scale.png',optimize=True)
print('Wrote deterministic print textures to '+str(OUT))

image=Image.new('RGBA',(1024,1024),(0,0,0,0));d=ImageDraw.Draw(image)
symbol=ImageFont.truetype('/usr/share/fonts/gnu-free/FreeSans.otf',34)
italic=ImageFont.truetype('/usr/share/fonts/gnu-free/FreeSerifItalic.otf',36)
for i,key in enumerate(json.loads((ROOT/'models/2741-keyboard.json').read_text())['keys']):
    x=(i%8)*128+64;y=(i//8)*128+64
    lines=key['legend'].splitlines()
    if len(lines)==2:
        d.text((x,y-22),lines[0],font=symbol,fill=(231,229,215,255),anchor='mm')
        d.text((x,y+23),lines[1],font=italic,fill=(231,229,215,255),anchor='mm')
    elif lines:
        font=ImageFont.truetype('/usr/share/fonts/gnu-free/FreeSans.otf',23 if len(lines[0])>2 else 36)
        d.text((x,y),lines[0],font=font,fill=(231,229,215,255),anchor='mm')
image.save(OUT/'2741-apl-keyboard.png',optimize=True)

image=Image.new('RGBA',(1024,1024),(0,0,0,0));d=ImageDraw.Draw(image)
for i,key in enumerate(json.loads((ROOT/'models/5471-keyboard.json').read_text())['keys']):
    x=(i%8)*128+64;y=(i//8)*128+64
    lines=key['legend'].splitlines()
    font=ImageFont.truetype(font_file,19 if len(key['legend'])>3 and len(lines)==1 else 34)
    if len(lines)==2:
        for yy,line in zip((y-23,y+23),lines):d.text((x,yy),line,font=font,fill=(235,235,222,255),anchor='mm')
    elif lines:d.text((x,y),lines[0],font=font,fill=(235,235,222,255),anchor='mm')
image.save(OUT/'5471-keyboard.png',optimize=True)

image=Image.new('RGB',(2048,128),(20,24,25));d=ImageDraw.Draw(image)
font=ImageFont.truetype(font_file,24)
for i in range(126):
    x=20+i/125*2008
    d.line([(x,45),(x,68 if i%5==0 else 57)],fill=(180,185,176),width=2)
    if i%5==0:d.text((x,88),str(i),font=font,fill=(200,203,193),anchor='mm')
image.save(OUT/'5471-front-scale.png',optimize=True)

image=Image.new('RGB',(256,512),(28,32,32));d=ImageDraw.Draw(image)
font=ImageFont.truetype(font_file,26)
d.text((128,100),'PROCEED',font=font,fill=(220,222,211),anchor='mm')
d.multiline_text((128,340),'REQUEST\nPENDING',font=font,fill=(220,222,211),anchor='mm',align='center',spacing=10)
image.save(OUT/'5471-indicators.png',optimize=True)

for model,label in [('2741','2741 Communications\nTerminal'),('5471','5471 Printer-Keyboard')]:
    image=Image.new('RGB',(1024,160),(190,193,185));d=ImageDraw.Draw(image)
    d.rectangle((0,0,282,159),fill=(20,23,24))
    d.text((141,78),'IBM',font=ImageFont.truetype(font_file,105),fill=(240,240,231),anchor='mm')
    d.multiline_text((310,35),label,font=ImageFont.truetype(font_file,38),fill=(20,23,24),spacing=6)
    image.save(OUT/(model+'-badge.png'),optimize=True)
