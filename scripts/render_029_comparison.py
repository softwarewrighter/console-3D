"""Render rejected/corrected GLBs with identical frozen cameras and illumination."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:]
old=Path(args[0]);new=Path(args[1]);out=Path(args[2]);out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'models/029-photo-cameras.json').read_text())
for tag,source in [('before',old),('after',new)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 assert any(d.type=='OPTIX' for d in prefs.devices)
 for d in prefs.devices:d.use=d.type=='OPTIX'
 scene.cycles.device='GPU';scene.view_settings.exposure=-1.2
 scene.world=bpy.data.worlds.new('frozen comparison world');scene.world.use_nodes=True
 scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.28,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.009));floor=bpy.context.object
 mat=bpy.data.materials.new('frozen floor');mat.diffuse_color=(.14,.17,.20,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.14,.17,.20,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;floor.data.materials.append(mat)
 for name,loc,power,size in [('key',(.4,-.7,1.3),100,1),('fill',(-.8,-.2,.7),70,.8),('rim',(.2,.8,1),130,.7)]:
  data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
  obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,0,.1))-obj.location).to_track_quat('-Z','Y').to_euler()
 for view in manifest['views']:
  data=bpy.data.cameras.new('locked '+view['id']);data.type='PERSP';data.lens=view['lens_mm'];data.sensor_width=36;data.sensor_fit='HORIZONTAL'
  cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);cam.location=view['camera_location']
  cam.rotation_euler=Matrix(view['camera_rotation_matrix']).to_euler() if 'camera_rotation_matrix' in view else (Vector(view['camera_target'])-cam.location).to_track_quat('-Z','Y').to_euler()
  scene.camera=cam;scene.render.resolution_x,scene.render.resolution_y=view['size'];scene.render.resolution_percentage=100
  scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/(view['id']+'-'+tag+'.png'));bpy.ops.render.render(write_still=True)
print('029_COMPARISON_RENDER_COMPLETE')
