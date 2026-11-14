# /// script
# dependencies = ["pillow>=11"]
# ///
"""IBM 029 combination keyboard: 48 numbered caps plus a space bar, Fig. 8."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'textures';OUT.mkdir(exist_ok=True)
# Source-pixel rectangles from Columbia's IBM manual Fig. 8. No regular-grid
# substitution for the asymmetric RESET and LEFT ZERO keys.
keys=[]
def key(name,rect,blue=False,shape=None):keys.append(dict(legend=name,rect=rect,blue=blue,shape=shape))
xs=[233,384,540,691,845,1000,1154,1308,1461,1615,1771,1927]
for x,label in zip(xs,['MULT\nPCH','#\n@',',\n%','$\n*','.\n<','','DUP','−\n-','0\n/','PROG\nONE','REL','PROG\nTWO']):key(label,[x,70,x+106,178],label in ('MULT\nPCH','DUP','PROG\nONE','REL','PROG\nTWO'))
for x,label in zip([268,424,578,733,886,1041,1197,1352,1508,1666,1820],['+\nQ','—\nW',')\nE','¢\nR','0–8–2\nT','†\nY','1\nU','2\nI','3\nO','&\nP','FEED']):key(label,[x,228,x+106,334],label=='FEED')
for x,label in zip([307,465,622,779,936,1093,1250,1408,1566,1720,1876],['A','>\nS',':\nD',';\nF','¬\nG',"'\nH",'4\nJ','5\nK','6\nL','SKIP','REG']):key(label,[x,386,x+106,490],label in ('SKIP','REG'))
for x,label in zip([350,506,663,820,977,1134,1291,1448,1605,1762],['Z','?\nX','C','=\nV','!\nB','(\nN','7\nM','8\n,','9\n.','AUX\nDUP']):key(label,[x,541,x+106,645],label=='AUX\nDUP')
key('NUMERIC',[75,542,301,647],True);key('ALPHA',[1910,536,2158,643],True)
key('ERROR\nRESET',[75,230,263,493],True,[[75,230],[220,230],[220,388],[263,388],[263,493],[75,493]])
key('LEFT\nZERO',[1982,216,2158,481],True,[[1982,216],[2158,216],[2158,481],[2023,481],[2023,322],[1982,322]])
key('SPACE',[327,699,1890,813],True)
assert len(keys)==49,len(keys)
(ROOT/'models/029-keyboard.json').write_text(json.dumps({'source':'Columbia / IBM A24-3332-1 Figure 8, combination keyboard','keys':keys},indent=2)+'\n')
fontpath='/usr/share/fonts/gnu-free/FreeSans.otf'
im=Image.new('RGBA',(1024,1024));d=ImageDraw.Draw(im)
for i,k in enumerate(keys):
 label=k['legend'];x=i%8*128+64;y=i//8*128+64
 if label=='SPACE':continue
 f=ImageFont.truetype(fontpath,19 if len(label.replace('\n',''))>5 else 29)
 d.multiline_text((x,y),label,font=f,fill=(238,242,237,255) if k['blue'] else (35,39,36,255),anchor='mm',align='center',spacing=3)
im.save(OUT/'029-keyboard-legends.png',optimize=True)
im=Image.new('RGB',(1024,128),(31,34,32));d=ImageDraw.Draw(im)
d.rectangle((6,6,1017,121),outline=(154,160,153),width=3)
d.text((155,65),'IBM',font=ImageFont.truetype(fontpath,88),fill=(207,210,200),anchor='mm');d.text((820,67),'29',font=ImageFont.truetype(fontpath,75),fill=(207,210,200),anchor='mm');im.save(OUT/'029-nameplate.png',optimize=True)
im=Image.new('RGB',(800,360),(199,188,153));d=ImageDraw.Draw(im)
f=ImageFont.truetype('/usr/share/fonts/gnu-free/FreeMono.otf',9)
for row in range(12):
 y=45+row*23
 for col in range(80):
  x=18+col*9.6
  if (col*7+row*13)%19<2:d.rectangle((int(x),y,int(x)+3,y+11),fill=(49,52,45))
  else:d.text((x,y),str(row%10),font=f,fill=(131,125,100))
d.text((28,15),'IBM 29 CARD PUNCH',font=ImageFont.truetype(fontpath,14),fill=(75,77,65));im.save(OUT/'029-card.png',optimize=True)
print('49 keycap records and deterministic legends/card artwork generated')
