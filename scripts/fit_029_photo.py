# /// script
# dependencies = ["numpy", "scipy", "pillow>=11"]
# ///
"""Freeze a 029 comparison camera using unchanged tabletop/leg landmarks."""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import least_squares
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
pts={'table_front_left':([-.65,-.38,.7825],[180,310]),'table_front_right':([.65,-.38,.7825],[693,225]),'table_rear_left':([-.65,.38,.7825],[14,198]),'front_left_foot':([-.59,-.30,.005],[191,708]),'front_right_foot':([.59,-.30,.005],[611,592]),'rear_left_foot':([-.59,.30,.005],[64,571])}
size=[700,723];xyz=np.array([p[0] for p in pts.values()]);uv=np.array([p[1] for p in pts.values()]);center=np.array([0,0,.65])
def matrix(v):
 a,e,r=v[:3];ca,sa,ce,se=np.cos(a),np.sin(a),np.cos(e),np.sin(e);R=np.array([[ca,sa,0],[sa*se,-ca*se,-ce],[-sa*ce,ca*ce,-se]]);cr,sr=np.cos(r),np.sin(r);return np.array([[cr,-sr,0],[sr,cr,0],[0,0,1]])@R

def project(v):
 p=(xyz-center)@matrix(v).T+v[3:6];return p[:,:2]/p[:,2:3]*np.exp(v[6])+np.array(size)/2
best=None
for distance in (2,3,5,8):
 v=[-.55,.42,0,0,0,distance,math.log(distance*430)]
 fit=least_squares(lambda v:(project(v)-uv).ravel(),v,bounds=([-1.3,.10,-.15,-3,-3,1,math.log(250)],[1.3,1.3,.15,3,3,15,math.log(20000)]),max_nfev=3000)
 if best is None or np.linalg.norm(fit.fun)<np.linalg.norm(best.fun):best=fit
v=best.x;R=matrix(v)
view={'id':'manual','photo':'references/029-columbia-029b.jpg','source_page':'https://www.columbia.edu/cu/computinghistory/029.html','credit':'IBM 29 Card Punch Reference Manual A24-3332-1, via Columbia University Computing History','size':size,'camera_location':(center-R.T@v[3:6]).tolist(),'camera_rotation_matrix':(R.T@np.diag([1,-1,-1])).tolist(),'lens_mm':float(np.exp(v[6])*36/size[0]),'fit_rms_coordinate_px':float(np.sqrt(np.mean(best.fun**2))),'fit_points':{n:{'model':a,'photo':b,'projected':c.tolist()} for (n,(a,b)),c in zip(pts.items(),project(v))}}
# Museum close-up: deliberately described as approximate framing, not a fitted
# camera, because its table corners and legs are cropped out.
view2={'id':'color','photo':'references/029-columbia-ibm029c.jpg','source_page':'https://www.columbia.edu/cu/computinghistory/029.html','credit':'Color photograph linked by Columbia, original photographer/license unconfirmed','size':[1024,768],'camera_location':[.035,-2.30,1.85],'camera_target':[0,.02,.91],'lens_mm':62,'fit_rms_coordinate_px':None}
manifest={'camera_policy':'Frozen before geometry revision. Manual photo fit uses unchanged tabletop corners and feet only. Interior card stations and keyboard excluded from fit. Color crop uses approximate fixed camera, not a calibrated fit.','uncertainty':'Hand-selected image landmarks, inferred desktop dimensions and unknown distortion; fit is diagnostic, not physical measurement.','views':[view,view2]}
(ROOT/'models/029-photo-cameras.json').write_text(json.dumps(manifest,indent=2)+'\n')
image=Image.open(ROOT/view['photo']).convert('RGB');draw=ImageDraw.Draw(image)
for name,(point,target),pred in zip(pts,pts.values(),project(v)):
 draw.line([tuple(target),tuple(pred)],fill='red',width=2);x,y=target;draw.ellipse((x-3,y-3,x+3,y+3),outline='yellow',width=2);x,y=pred;draw.ellipse((x-2,y-2,x+2,y+2),fill='cyan')
out=ROOT/'work/029-refinement';out.mkdir(exist_ok=True);image.save(out/'camera-fit.jpg')
print('Locked manual camera RMS coordinate error:',view['fit_rms_coordinate_px'])
