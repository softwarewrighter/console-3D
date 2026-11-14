# /// script
# dependencies = ["pillow>=11"]
# ///
"""Small original artwork for the 3279 and COR24-TB procedural studies."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'textures';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/gnu-free/FreeSans.otf'
def font(n):return ImageFont.truetype(FONT,n)
im=Image.new('RGB',(1024,768),(12,17,24));d=ImageDraw.Draw(im)
d.text((512,35),'ENGINEERING SUPPORT / FIRST HALF YEAR',font=font(24),fill=(220,211,154),anchor='mm')
base=[3,1,7,18,15,22,12,8,2,4,6,10,16,8,14,5,10,8,2,1,6,15];mid=[6,3,12,24,21,28,16,11,6,8,10,16,21,13,19,10,16,15,7,4,11,19];upper=[9,7,16,29,32,24,29,16,10,12,17,26,18,25,21,17,25,22,13,10,19,23]
xs=[180+i*34 for i in range(len(base))]
for data,col in [(upper,(170,183,82)),(mid,(190,58,25)),(base,(25,91,173))]:d.polygon([(xs[0],670)]+[(x,670-y*17) for x,y in zip(xs,data)]+[(xs[-1],670)],fill=col)
d.line([(170,100),(170,675),(940,675)],fill=(201,196,148),width=2)
for i in range(0,36,5):d.text((151,670-i*17),str(i),font=font(19),fill=(210,203,158),anchor='rm')
for i,x in enumerate(xs):
 if i%3==0:d.text((x,697),str(i+1),font=font(19),fill=(210,203,158),anchor='mm')
for j,(label,col) in enumerate([('AREA 4',(170,183,82)),('AREA 3',(190,58,25)),('AREA 1',(25,91,173))]):
 d.rectangle((28,230+j*34,48,256+j*34),fill=col);d.text((60,240+j*34),label,font=font(19),fill=(213,208,168),anchor='lm')
im.save(OUT/'3279-area-chart.png',optimize=True)
im=Image.new('RGB',(128,80),(28,29,30));d=ImageDraw.Draw(im);d.text((64,40),'IBM',font=font(53),fill=(180,185,183),anchor='mm');im.save(OUT/'3279-badge.png',optimize=True)
im=Image.new('RGB',(1600,900),(43,95,81));d=ImageDraw.Draw(im)
def xy(x,y):return ((x/.09+.5)*1600,(.5-y/.05)*900)
def line(points,col=(22,65,53),w=3):d.line([xy(*p) for p in points],fill=col,width=w,joint='curve')
for i in range(30):
 y=-.011+i*.00065
 line([(-.010,y),(-.001,y),(.008+i*.00024,y+.009),(.025+i*.00016,y+.009),(.031+i*.00016,y+.002)],w=3)
for i in range(16):
 x=-.029+i*.0010
 line([(x,.010),(x,.014+i*.00023),(-.010+i*.0006,.020),(.020+i*.0007,.020)],w=3)
for i in range(14):
 x=-.030+i*.0010;line([(x,-.010),(x,-.017-i*.00020),(-.037-i*.00015,-.017-i*.00020),(-.043,-.018+i*.00065)],w=3)
for i in range(7):line([(-.043,.012-i*.00254),(-.035,.012-i*.00254),(-.030,.007-i*.0012)],w=5)
for ix in range(27):
 for iy in range(13):
  if (ix*13+iy*7)%17==0:
   x=-.040+ix*.003;y=-.021+iy*.0035;px,py=xy(x,y);d.ellipse((px-2,py-2,px+2,py+2),fill=(176,175,121))
d.text(xy(.024,.020),'COR24-TB',font=font(54),fill=(211,231,222));d.text(xy(-.043,-.021),'makerlisp.com',font=font(35),fill=(211,231,222))
for label,x,y in [('U1',-.032,.013),('U2',.027,-.001),('U3',-.022,.021),('S1',-.006,.023),('S2',.012,.023),('J5',.026,-.022),('C17',.002,.005),('C16',.002,-.002),('C15',.002,-.011),('R6',-.005,-.018)]:d.text(xy(x,y),label,font=font(25),fill=(206,223,209))
im.save(OUT/'cor24-top-artwork.png',optimize=True)
im=Image.new('RGB',(512,512),(31,34,38));d=ImageDraw.Draw(im);d.text((256,170),'LATTICE',font=font(64),fill=(123,131,128),anchor='mm');d.multiline_text((256,300),'LCMXO2280C\n5TN144C',font=font(38),fill=(123,131,128),anchor='mm',align='center');im.save(OUT/'cor24-fpga-label.png',optimize=True)
im=Image.new('RGB',(768,384),(20,23,25));d=ImageDraw.Draw(im);d.text((110,190),'ISSI',font=font(90),fill=(158,164,160),anchor='mm');d.multiline_text((460,190),'IS61WV1024\nSRAM',font=font(46),fill=(158,164,160),anchor='mm',align='center');im.save(OUT/'cor24-sram-label.png',optimize=True)
print('Equipment screen and PCB artwork generated')
im=Image.new('RGB',(1024,640),(2,3,4));d=ImageDraw.Draw(im)
# Stylized wireframe APL artwork; exact lettering is a later fidelity pass.
mask=Image.new('L',im.size);md=ImageDraw.Draw(mask);md.text((512,335),'APL',font=font(255),fill=255,anchor='mm')
wire=Image.new('L',im.size);wd=ImageDraw.Draw(wire)
for x in range(100,925,12):wd.line((x,170,x-80,530),fill=200,width=1)
for y in range(160,535,10):wd.line((80,y,945,y+30),fill=200,width=1)
import PIL.ImageChops
wire=PIL.ImageChops.multiply(wire,mask);im.paste((223,231,231),(0,0),wire)
d=ImageDraw.Draw(im);d.text((512,335),'APL',font=font(255),fill=None,stroke_width=2,stroke_fill=(230,236,236),anchor='mm');d.ellipse((607,125,659,180),outline=(225,230,230),width=2)
im.save(OUT/'macbook-apl-screen.png',optimize=True)
im=Image.new('RGB',(128,768),(137,145,151));d=ImageDraw.Draw(im)
for y in range(5,765,8):
 for x in range(5,125,8):d.ellipse((x,y,x+2,y+2),fill=(31,35,38))
im.save(OUT/'macbook-speakers.png',optimize=True)
