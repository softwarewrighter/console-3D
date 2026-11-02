"""Blender-side paired views. Keep source intact; crop only diagnostic copies.

Run via scripts/compare.py. All transforms and cameras come from one manifest.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
import numpy as np
import hashlib

root = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--')+1:]
candidate = Path(args[0]).resolve()
out = Path(args[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
config_path=Path(args[2]) if len(args)>2 else root/'models/comparison.json'
cfg = json.loads(config_path.read_text())


def render(source, tag, aligned=False, region=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if aligned:
        # Intentional study-only selection. No partial mesh is used in the
        # production asset; source GLB and the full reference viewer stay intact.
        lo, hi = cfg['source_blender_printer_region']['min'], cfg['source_blender_printer_region']['max']
        for o in objects:
            if region:
                import bmesh
                bm = bmesh.new(); bm.from_mesh(o.data)
                outside = [v for v in bm.verts if any((o.matrix_world@v.co)[i] < lo[i] or (o.matrix_world@v.co)[i] > hi[i] for i in range(3))]
                bmesh.ops.delete(bm, geom=outside, context='VERTS')
                bm.to_mesh(o.data); bm.free()
            for v in o.data.vertices:
                v.co = (o.matrix_world@v.co)*cfg['alignment']['scale']+Vector(cfg['alignment']['translation'])
            o.matrix_world.identity()
    if tag in ('reference-full','reference-region'):
        bpy.ops.export_scene.gltf(filepath=str(out/('reference-aligned.glb' if tag=='reference-full' else 'reference-region.glb')))
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    bounds = [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
    scene=bpy.context.scene
    scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU'
    scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.world=bpy.data.worlds.new('comparison world');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    scene.view_settings.exposure=-1.2
    for name, loc, power, size in [('key',(.4,-.7,1.3),100,1),('fill',(-.8,-.2,.7),70,.8),('rim',(.2,.8,1),130,.7)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
        o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc
        o.rotation_euler=(Vector(cfg['aim'])-o.location).to_track_quat('-Z','Y').to_euler()
    results={}
    for view, loc in cfg['views'].items():
        data=bpy.data.cameras.new(view);data.type='ORTHO';data.ortho_scale=cfg['orthographic_scale']
        cam=bpy.data.objects.new('camera '+view,data);scene.collection.objects.link(cam);cam.location=loc
        cam.rotation_euler=(Vector(cfg['aim'])-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
        scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/(tag+'-'+view+'.png'))
        bpy.ops.render.render(write_still=True)
        im=bpy.data.images.load(scene.render.filepath,check_existing=False)
        pixels=np.array(im.pixels[:],dtype=np.float32).reshape((im.size[1],im.size[0],4))
        results[view]=pixels
    return results, {'bounds':bounds,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'mesh_nodes':len(meshes)}


ref, refstats = render(root/cfg['reference'], 'reference-region', True, True)
full, fullstats = render(root/cfg['reference'], 'reference-full', True, False)
model, stats = render(candidate, 'candidate')
metrics={}
for view in cfg['views']:
    # Silhouette statistics apply to the cropped study, not a claim of overall
    # historical accuracy. Transparent hood pixels require a conservative cutoff.
    a=ref[view][...,3]>.5;b=model[view][...,3]>.5
    union=np.logical_or(a,b).sum();intersection=np.logical_and(a,b).sum()
    metrics[view]={'region_silhouette_iou':float(intersection/union) if union else 0,'reference_pixels':int(a.sum()),'candidate_pixels':int(b.sum())}
    # Three aligned images in one artifact: source region, candidate, difference.
    delta=np.zeros_like(ref[view]);delta[...,3]=1
    delta[a&~b,:3]=[.1,.5,1];delta[b&~a,:3]=[1,.25,.08];delta[a&b,:3]=[.2,.24,.26]
    sheet=np.concatenate([ref[view],model[view],delta],axis=1)
    image=bpy.data.images.new('comparison '+view,width=sheet.shape[1],height=sheet.shape[0],alpha=True)
    image.pixels.foreach_set(sheet.ravel());image.filepath_raw=str(out/('compare-'+view+'.png'));image.file_format='PNG';image.save()
stats['glb_bytes']=candidate.stat().st_size
(out/'comparison.json').write_text(json.dumps({'candidate':str(candidate),'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256((root/cfg['reference']).read_bytes()).hexdigest(),'config_path':str(config_path),'config_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),'config':cfg,'reference_full':fullstats,'reference_region':refstats,'candidate_stats':stats,'views':metrics,'warning':'ROI is an imperfect study cut for the 1053; 2741 uses the complete terminal. IoU is a diagnostic, not fidelity proof.'},indent=2)+'\n')
print('COMPARISON_COMPLETE',out)
