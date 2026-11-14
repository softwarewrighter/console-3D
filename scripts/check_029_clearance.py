"""Blender geometric checks for the operator's knee bay and detached keyboard."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];new=Path(args[0]);old=Path(args[1]);out=Path(args[2])
def rays(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path.resolve()));bpy.context.view_layer.update();scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();hits=[]
 for x in (-.50,-.25,0,.25,.50):
  for z in (.22,.40,.60,.70):
   hit=scene.ray_cast(deps,Vector((x,-.37,z)),Vector((0,1,0)),distance=.54)
   if hit[0]:hits.append({'x':x,'z':z,'object':hit[4].name,'point':list(hit[1])})
 return hits
old_hits=rays(old);new_hits=rays(new);assert old_hits,'Baseline should demonstrate blocked knee space';assert not new_hits,new_hits
head_names=['029 structural head enclosure','029 left stacker and curved guides','029 central punch and read stations','029 program drum cover','029 right card hopper and throat']
def points(names):
 result=[]
 for name in names:
  root=bpy.data.objects.get(name);assert root,name
  for obj in root.children_recursive:
   if obj.type=='MESH':result.extend(obj.matrix_world@v.co for v in obj.data.vertices)
 return result
head=points(head_names);keyboard=points(['029 combination keyboard and operator switches'])
gap=min(v.y for v in head)-max(v.y for v in keyboard);assert gap>.03,gap
feet=min(v.z for v in keyboard);assert abs(feet-.7825)<.001,feet
report={'baseline_blocked_rays':len(old_hits),'corrected_blocked_rays':len(new_hits),'sampled_clear_depth_m':.54,'model_desktop_depth_m':.76,'model_cabinet_depth_m':.19,'nominal_open_depth_m':.57,'nominal_open_fraction':.75,'keyboard_to_head_gap_m':gap,'keyboard_feet_bottom_m':feet,'note':'Model design clearances, not independently measured historical specifications.'}
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
