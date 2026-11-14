# /// script
# dependencies = ["pillow>=11"]
# ///
"""Original green CRT artwork and IBM PC keyboard legends; no photo projection."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'textures';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/gnu-free/FreeMonoBold.otf'
def font(size):return ImageFont.truetype(FONT,size)
# Model F style 83-key layout: function block, main block, and keypad.
keys=[]
def add(label,x,y,w=1,h=1,tone='ivory'):keys.append(dict(legend=label,x=x,y=y,width=w,height=h,tone=tone))
pitch=.019
for row in range(5):
 for col in range(2):add('F'+str(row*2+col+1),-.218+col*pitch,.046-row*pitch,tone='gray')
rows=[['Esc','1 !','2 @','3 #','4 $','5 %','6 ^','7 &','8 *','9 (','0 )','- _','= +','Bksp'],['Tab','Q','W','E','R','T','Y','U','I','O','P','[ {','] }'],['Ctrl','A','S','D','F','G','H','J','K','L','; :',"\' \'",'Enter'],['Shift','\\ |','Z','X','C','V','B','N','M',', <','. >','/ ?','Shift']]
for row,labels in enumerate(rows):
 for j,label in enumerate(labels):add(label,-.160+j*pitch+(.003 if row==2 else 0),.046-row*pitch,1.05 if label in ('Shift','Enter','Bksp') else .94,tone='gray' if len(label)>3 else 'ivory')
add('Alt',-.151,-.035,1.2,tone='gray');add('Space',-.027,-.035,10.1);add('Caps',.090,-.035,1.1,tone='gray')
for row,labels in enumerate([['Num','Scroll','-'],['7 Home','8 ↑','9 PgUp'],['4 ←','5','6 →'],['1 End','2 ↓','3 PgDn'],['0 Ins','. Del','+']]):
 for j,label in enumerate(labels):add(label,.145+j*pitch,.046-row*pitch,.94,tone='gray' if row==0 else 'ivory')
add('PrtSc',.113,.046,.94,tone='gray');add('*',.113,.027,.94)
# 83 separate physical keycaps; exact wide-key outlines remain provisional.
(ROOT/'models/pcdual-keyboard.json').write_text(json.dumps({'pitch_m':pitch,'keys':keys,'status':'Model F style, photo-led; exact 83-key geometry remains provisional'},indent=2)+'\n')
im=Image.new('RGBA',(1024,2048));d=ImageDraw.Draw(im)
for i,k in enumerate(keys):
 label=k['legend'];lines=label.split(' ',1) if ' ' in label and label!='Space' else [label]
 x=i%8*128+64;y=i//8*128+64
 if label=='Space':continue
 for j,line in enumerate(lines):d.text((x,y+(j-(len(lines)-1)/2)*38),line,font=font(20 if len(line)>3 else 33),fill=(28,31,30,255),anchor='mm')
im.save(OUT/'pcdual-key-legends.png',optimize=True)
im=Image.new('RGB',(256,256),(136,145,138));d=ImageDraw.Draw(im)
d.text((128,86),'IBM',font=font(106),fill=(25,34,35),anchor='mm')
for y in range(35,133,8):d.rectangle((0,y,255,y+2),fill=(136,145,138))
d.text((128,170),'Personal',font=font(28),fill=(25,34,35),anchor='mm');d.text((128,202),'Computer',font=font(28),fill=(25,34,35),anchor='mm')
im.save(OUT/'pcdual-ibm-badge.png',optimize=True)
def finish(im,name):
 glow=im.filter(ImageFilter.GaussianBlur(3));im=Image.blend(glow,im,.84);im.save(OUT/name,optimize=True)
im=Image.new('RGB',(1024,768),(3,12,10));mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
d.text((512,260),'IBM PC',font=font(190),fill=255,anchor='mm')
for y in range(150,360,9):d.rectangle((0,y,1023,y+3),fill=0)
d.text((512,505),'APL',font=font(230),fill=0,stroke_width=3,stroke_fill=255,anchor='mm')
im.paste((43,238,102),(0,0),mask);finish(im,'pcdual-apl-screen.png')
im=Image.new('RGB',(1024,768),(2,10,8));d=ImageDraw.Draw(im)
def point(t,p):
 r=.61*math.sin(t)*(1+.10*math.cos(3*t))*(1+.025*math.cos(5*p));x=r*math.cos(p);y=r*math.sin(p);z=.72*math.cos(t)-.10*math.exp(-t*t/.05)
 # Turn and incline the wireframe so both contour directions read clearly.
 xx=.94*x+.34*y;yy=-.34*x+.94*y;return (512+xx*340,425-(z*.94-yy*.34)*310)
for j in range(19):
 pts=[point(.06+i*(math.pi-.12)/100,j*math.tau/18) for i in range(101)];d.line(pts,fill=(34,237,96),width=2)
for j in range(1,15):d.line([point(j*math.pi/15,i*math.tau/120) for i in range(121)],fill=(34,237,96),width=2)
d.line([(510,219),(513,174),(539,146)],fill=(37,239,101),width=3)
d.line([(514,198),(467,159),(430,135),(403,135),(432,173),(477,198),(514,198)],fill=(37,239,101),width=2)
for t in range(1,5):d.line([(414+t*18,144+t*14),(447+t*14,176+t*6)],fill=(37,239,101),width=1)
d.text((35,30),'3D MODEL',font=font(23),fill=(34,237,96));d.text((800,30),'APPLE.OBJ',font=font(21),fill=(34,237,96))
d.line([(58,650),(188,650),(58,550),(58,650),(350,705)],fill=(20,172,72),width=2)
d.text((38,705),'APPLE.OBJ',font=font(20),fill=(34,237,96));finish(im,'pcdual-apple-screen.png')
print('Generated keyboard, IBM badge, and two CRT artwork textures')
