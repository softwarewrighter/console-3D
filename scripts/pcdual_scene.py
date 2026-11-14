"""Photo-led dual-monitor IBM PC. Front -Y, meters, Z up. See docs/pcdual.md."""
from mathutils import Matrix

def pc_group(name):
    g=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(g);g.parent=bpy.data.objects['IBM PC dual monitor workstation'];return g

def pc_own(g,start):
    bpy.context.view_layer.update()
    for o in PARTS[start:]:world=o.matrix_world.copy();o.parent=g;o.matrix_world=world

def pc_plate(name,loc,w,h,material,angle=math.pi/2):
    rotation=Matrix.Rotation(angle,4,'X')
    return decal(name,[Vector(loc)+rotation@Vector((x,y,0)) for x,y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]],material)

def pc_cable(name,points,radius,material):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=10;data.bevel_depth=radius;data.bevel_resolution=1
    sp=data.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);register(o,material)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')

def pc_round_ring(w,h,y,zc,r=.012):
    pts=[]
    for cx,cz,a in [(w/2-r,zc+h/2-r,0),(-w/2+r,zc+h/2-r,90),(-w/2+r,zc-h/2+r,180),(w/2-r,zc-h/2+r,270)]:
        for j in range(6):
            angle=math.radians(a+j*18);pts.append((cx+r*math.cos(angle),y,cz+r*math.sin(angle)))
    return pts

def pc_monitor(name,at,yaw,screen_name,cream,black,badge):
    g=pc_group(name);start=len(PARTS);w=.370;h=.290
    # Wide CRT face, narrowing behind the tube with a falling roof.
    sections=[(-.125,.370,.290,.151,.016),(-.104,.370,.290,.151,.018),(.095,.344,.268,.148,.023),(.205,.306,.214,.135,.025)]
    n=24;verts=[p for y,sw,sh,zc,r in sections for p in pc_round_ring(sw,sh,y,zc,r)]
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]+[tuple(range(3*n,4*n))]
    shell=mesh(name+' rounded CRT housing',verts,faces,cream)
    for face in shell.data.polygons:face.use_smooth=True
    # Front ring surrounds a real opening; no solid cube behind the glass.
    outer=pc_round_ring(.366,.284,-.128,.151,.014)
    inner=[(x-.019,y,z) for x,y,z in pc_round_ring(.286,.234,-.128,.151,.008)]
    mesh(name+' front cream surround',outer+inner,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],cream)
    # Three-dimensional sloped inner bezel, independently rounded at the glass.
    back=[(x-.019,y,z) for x,y,z in pc_round_ring(.254,.199,-.106,.151,.012)]
    mesh(name+' deep screen bezel',inner+back,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],cream)
    # Textured bowed CRT grid with original schematic screen artwork.
    material=print_material(name+' green phosphor',screen_name)
    bsdf=material.node_tree.nodes.get('Principled BSDF');tex=next(n for n in material.node_tree.nodes if n.type=='TEX_IMAGE')
    material.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Emission Color']);bsdf.inputs['Emission Strength'].default_value=.7;bsdf.inputs['Roughness'].default_value=.27;bsdf.inputs['Coat Weight'].default_value=.28
    verts=[];uv=[];nx=32;nz=24
    for j in range(nz+1):
        v=j/nz;z=(v-.5)*.198
        for i in range(nx+1):
            u=i/nx;x=(u-.5)*.253
            verts.append((x-.019,-.109-.006*(1-(x/.1265)**2)*(1-(z/.099)**2),.151+z));uv.append((u,v))
    faces=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)]
    o=mesh(name+' curved luminous CRT',verts,faces,material);layer=o.data.uv_layers.new()
    for loop in o.data.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
    for face in o.data.polygons:face.use_smooth=True
    pc_plate(name+' IBM badge',(.151,-.130,.249),.022,.026,badge)
    for z in (.123,.090):
        cyl(name+' contrast brightness collar',(.151,-.132,z),.008,.004,black,(0,-1,0),24)
        cyl(name+' contrast brightness knob',(.151,-.135,z),.0055,.009,black,(0,-1,0),24)
        box(name+' knob white index',(.151,-.140,z+.002),(.001,.0005,.004),WHITE,0)
    # Vent rows follow the sloped roof rather than floating over it.
    for row in range(2):
        y=.005+row*.041;roofz=.296-(y+.104)*(.014/.199)
        for i in range(43):box(name+' roof vent',(-.145+i*.0069,y,roofz+.0005),(.0022,.031,.001),black,.0003)
    for side in (-1,1):
        for i in range(11):box(name+' side vent',(side*(.185-(.04+i*.009+.104)*.013/.199),.04+i*.009,.207),(.001,.0025,.025),black,.0002)
        box(name+' rubber foot',(side*.135,-.015,.004),(.035,.12,.008),RUBBER,.002)
    box(name+' rear label',(0,.207,.10),(.095,.001,.038),black,.0003)
    for x in (-.03,.03):cyl(name+' rear cable grommet',(x,.207,.055),.006,.003,black,(0,1,0),16)
    pc_own(g,start);g.location=at;g.rotation_euler.z=math.radians(yaw)
    return g

def pc_key(k,index,atlas,cream,gray,cy):
    x=k['x'];y=cy+k['y'];w=k['width']*.019-.0015;d=.016;angle=math.radians(9)
    basez=.028+(k['y']+.08)*math.tan(angle);center=Vector((x,y,basez));rot=Matrix.Rotation(angle,4,'X')
    verts=[]
    for ww,dd,z in [(w,d,0),(w-.0015,d-.0015,.008),(w-.0035,d-.0035,.011)]:verts += [(u*ww/2,v*dd/2,z) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    verts.append((0,0,.0098));faces=[(3,2,1,0)]+[(r*4+i,r*4+(i+1)%4,(r+1)*4+(i+1)%4,(r+1)*4+i) for r in range(2) for i in range(4)]+[(8+i,8+(i+1)%4,12) for i in range(4)]
    o=mesh('keyboard '+k['legend']+' '+str(index),[center+rot@Vector(v) for v in verts],faces,gray if k['tone']=='gray' else cream,.0004);o['keycap']=True
    o=decal('key legend '+str(index),[center+rot@Vector(v) for v in [(-w/2+.002,-d/2+.002,.0112),(w/2-.002,-d/2+.002,.0112),(w/2-.002,d/2-.002,.0112),(-w/2+.002,d/2-.002,.0112)]],atlas)
    layer=o.data.uv_layers.active
    for loop in o.data.loops:
        u,v=layer.data[loop.index].uv;layer.data[loop.index].uv=((index%8+u)/8,1-(index//8+1-v)/16)

def build_pcdual():
    cream=mat('PC warm beige textured ABS',(.54,.52,.44),.03,.55)
    keycream=mat('PC ivory keycaps',(.71,.69,.59),0,.43);keygray=mat('PC gray modifier keys',(.34,.34,.30),0,.48)
    black=mat('PC black drive and vent interiors',(.008,.012,.012),.04,.53)
    steel=mat('PC chassis powdercoat',(.40,.395,.34),.18,.55)
    badge=print_material('IBM printed metal badges','pcdual-ibm-badge.png')
    atlas=print_material('PC key legend atlas','pcdual-key-legends.png',True)
    g=pc_group('PC system unit');start=len(PARTS)
    box('5150 lower chassis',(0,0,.017),(.500,.410,.024),steel,.002)
    # Separate side/top panels leave room for recessed drive fronts.
    box('5150 left cover',(-.245,0,.082),(.010,.408,.120),cream,.003)
    box('5150 right cover',(.245,0,.082),(.010,.408,.120),cream,.003)
    box('5150 top cover',(0,0,.139),(.490,.408,.010),cream,.003)
    box('5150 rear panel',(0,.202,.080),(.480,.006,.108),steel,.001)
    box('5150 front fascia',(-.171,-.208,.081),(.152,.012,.120),cream,.003)
    for z in (.025,.137):box('5150 drive surround rail',(.073,-.209,z),(.346,.012,.014),cream,.002)
    pc_plate('system IBM badge',(-.204,-.215,.105),.026,.026,badge)
    for i in range(20):box('front vertical ventilation',(-.225+i*.0065,-.215,.049),(.0022,.001,.035),black,.0006)
    for drive,x in enumerate((-.014,.143)):
        box('full height disk drive '+str(drive),(x,-.206,.082),(.152,.014,.092),black,.001)
        box('disk bezel inner relief '+str(drive),(x,-.215,.087),(.142,.003,.064),BLACK,.001)
        box('disk horizontal insertion slot '+str(drive),(x,-.218,.087),(.130,.003,.004),black,.0005)
        box('disk door center hub '+str(drive),(x,-.222,.066),(.023,.012,.023),black,.001)
        box('disk latch handle '+str(drive),(x+.010,-.230,.077),(.050,.006,.007),black,.001)
        cyl('disk activity LED '+str(drive),(x+.052,-.220,.096),.0017,.002,RED,(0,-1,0),12)
        for sx in (-1,1):cyl('disk mounting screw',(x+sx*.067,-.220,.115),.0013,.001,CHROME,(0,-1,0),12)
    for x in (-.212,.212):
        for y in (-.165,.165):box('system rubber foot',(x,y,.005),(.038,.040,.010),RUBBER,.002)
    # Conservative rear detail: PSU grille and five expansion-slot covers.
    for i in range(9):box('PSU rear vent',(.120+i*.008,.206,.084),(.003,.001,.080),black,.0003)
    for i in range(5):box('rear expansion cover',(-.195+i*.021,.206,.082),(.015,.002,.087),CHROME,.0005)
    box('red side power switch',(.251,.113,.090),(.003,.026,.020),RED,.001)
    pc_own(g,start)
    pc_monitor('left APL monitor',(-.015,.015,.153),0,'pcdual-apl-screen.png',cream,black,badge)
    pc_monitor('right graphics monitor',(.505,.030,.008),-10,'pcdual-apple-screen.png',cream,black,badge)
    g=pc_group('detached PC keyboard');start=len(PARTS);cy=-.321
    profile('keyboard sloping case',-.245,.245,[(cy-.100,.009),(cy+.100,.009),(cy+.100,.062),(cy-.100,.026)],cream,.004)
    angle=math.radians(9)
    o=box('keyboard recessed bed',(-.012,cy+.006,.043),(.457,.124,.005),black,.002);o.rotation_euler.x=angle
    for i,k in enumerate(json.loads((ROOT/'models/pcdual-keyboard.json').read_text())['keys']):pc_key(k,i,atlas,keycream,keygray,cy)
    pc_plate('keyboard IBM badge',(-.211,cy+.082,.061),.027,.026,badge,0)
    pc_own(g,start)
    g=pc_group('PC interconnect cables');start=len(PARTS)
    pc_cable('left monitor cable',[(-.04,.22,.20),(-.05,.29,.16),(-.10,.30,.04),(-.12,.21,.07)],.003,black)
    pc_cable('right monitor cable',[(.51,.23,.06),(.45,.29,.02),(.26,.30,.015),(.14,.207,.065)],.003,black)
    # A short visible coil beside the keyboard echoes the supplied photograph.
    points=[(-.225,cy+.10,.035),(-.263,-.195,.027)]
    points += [(-.272+.009*math.cos(i*.5),-.185+i*.0018,.020+.009*math.sin(i*.5)) for i in range(60)]
    points += [(-.245,.04,.025),(-.20,.207,.05)]
    pc_cable('keyboard coiled cable',points,.002,black);pc_own(g,start)
