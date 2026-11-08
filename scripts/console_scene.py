"""Shared Selectric construction appended to the Bpy.xtl-generated scene.

Only finish() adds cameras and lighting. Hardware is exported without a stage.
Dimensions below are provisional photograph proportions, in meters.
"""
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(out)
PARTS = []
FONT = None
font_candidates = [os.environ.get('CONSOLE_FONT', ''), '/usr/share/fonts/gnu-free/FreeSans.otf', '/System/Library/Fonts/Supplemental/Arial Unicode.ttf']
for font_path in font_candidates:
    if font_path and Path(font_path).is_file():
        FONT = bpy.data.fonts.load(font_path)
        break


def mat(name, rgb, metal=0, rough=.4, alpha=1):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, alpha)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Alpha'].default_value = alpha
    if alpha < 1:
        m.surface_render_method = 'DITHERED'
        p.inputs['Transmission Weight'].default_value = 1
        p.inputs['IOR'].default_value = 1.46
    return m


GRAY = mat('1053 warm gray enamel', (.32, .34, .33), .2, .36)
CREAM = mat('2741 warm ivory enamel', (.65, .64, .54), .12, .37)
BLACK = mat('charcoal fascia', (.018, .022, .024), .1, .46)
KEY = mat('graphite keycaps', (.075, .085, .09), .05, .32)
RUBBER = mat('platen rubber', (.014, .017, .019), 0, .75)
BLUE = mat('1053 turquoise blue controls', (.015, .28, .46), .12, .29)
CHROME = mat('satin chrome', (.55, .6, .62), .85, .22)
WHITE = mat('ivory legends', (.88, .87, .78), 0, .45)
GLASS = mat('clear acrylic hood', (.94, .97, .98), 0, .06, .16)
RED = mat('power switch red base', (.44, .012, .012), 0, .4)


def register(o, material):
    o.data.materials.append(material)
    PARTS.append(o)
    return o


def edge(o, radius=.0015, segments=3):
    mod = o.modifiers.new('manufactured edge radii', 'BEVEL')
    mod.width = radius
    mod.segments = segments
    o.modifiers.new('weighted surface normals', 'WEIGHTED_NORMAL')
    return o


def box(name, loc, size, material, bevel=.0015):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    register(o, material)
    return edge(o, bevel) if bevel else o


def cyl(name, loc, radius, length, material, axis=(1, 0, 0), vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=loc)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = Vector(axis).to_track_quat('Z', 'Y').to_euler()
    register(o, material)
    for p in o.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return edge(o, .0005, 2)


def mesh(name, verts, faces, material, bevel=0):
    o = mesh_object(name, verts, faces)  # Bpy.xtl recalculates normals.
    register(o, material)
    return edge(o, bevel) if bevel else o


def profile(name, x0, x1, yz, material, bevel=.002):
    n = len(yz)
    verts = [(x, y, z) for x in (x0, x1) for y, z in yz]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
    return mesh(name, verts, faces, material, bevel)


def text(name, body, loc, size, material=WHITE, rotation=(math.pi/2, 0, 0), align='CENTER'):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = body
    if FONT:
        data.font = FONT
    data.align_x = align
    data.align_y = 'CENTER'
    data.size = size
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rotation
    register(o, material)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH')
    return o


def rod(name, a, b, radius, material, vertices=48):
    a, b = Vector(a), Vector(b)
    return cyl(name, (a+b)/2, radius, (b-a).length, material, b-a,vertices)


def knob(name, x, y, z, material, agile=False):
    cyl(name+' hub', (x, y, z), .018, .026, BLACK)
    if agile:
        # One fluted wheel surface replaces forty overlapping rib cylinders.
        segments=160
        verts=[]
        for dx in (-.0065,.0065):
            for i in range(segments):
                angle=i*math.tau/segments
                r=.0291 if i%4 in (1,2) else .0275
                verts.append((x+dx,y+r*math.cos(angle),z+r*math.sin(angle)))
        faces=[tuple(reversed(range(segments))),tuple(range(segments,2*segments))]
        faces += [(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
        mesh(name+' fluted wheel',verts,faces,material)
        return
    cyl(name+' wheel', (x, y, z), .029, .012, material)
    # Actual fluting around the rim rather than a smooth wheel.
    for i in range(40):
        angle = i*math.tau/40
        cyl(name+f' flute {i:02}', (x, y+.028*math.cos(angle), z+.028*math.sin(angle)), .0011, .013, material, vertices=8)


def mechanism(width, y, z, material, carrier_x=-.055, agile=False, carrier_y=None, knob_sides=(-1,1)):
    if carrier_y is None:carrier_y=y-.053
    span = width-.10
    box('mechanism dark well', (0, y-.015, z-.035), (span+.025, .14, .05), BLACK)
    cyl('rubber platen', (0, y+.025, z), .018, span, RUBBER)
    for side in (-1, 1):
        cyl(f'platen axle {side}', (side*(span/2+.015), y+.025, z), .005, .045, CHROME)
        if side in knob_sides:knob(f'platen knob {side}', side*(width/2+.003), y+.025, z, material,agile)
        box(f'paper bail bracket {side}', (side*(span/2-.005), y+.003, z+.013), (.008, .008, .041), CHROME)
    cyl('paper bail rod', (0, y-.004, z+.023), .002, span-.01, CHROME)
    for x in (-.145, 0, .145):
        cyl(f'paper bail roller {x}', (x, y-.004, z+.023), .006, .014, RUBBER)
    for offset in (-.002, -.025):
        cyl(f'carrier guide rail {offset}', (0, carrier_y+offset, z-.027), .0035, span-.015, CHROME)
    carrier_start=len(PARTS)
    box('type element carrier', (carrier_x, carrier_y-.007, z-.018), (.057, .043, .02), BLACK)
    element_start=len(PARTS)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=(carrier_x, carrier_y, z+.002))
    ball = bpy.context.object
    ball.name = 'Selectric type element'
    ball.scale = (.016, .016, .015)
    register(ball, CHROME)
    cyl('type element cap', (carrier_x, carrier_y, z+.015), .009, .004, BLACK, (0, 0, 1))
    # Fine raised type blocks indicate the element, without inventing legible glyphs.
    for row in range(3):
        for col in range(20):
            a = col*math.tau/20
            r = .015*math.cos((row-1)*.4)
            o = box(f'type slug {row}-{col}', (carrier_x+r*math.cos(a), carrier_y+r*math.sin(a), z+(row-1)*.005), (.002, .002, .0025), BLACK, .0002)
            o.rotation_euler.z = a
    # Keep motion pivots independent of static batching. Rest geometry is
    # unchanged; tilt and spin share the element center, carrier translates X.
    carrier=bpy.data.objects.new('selectric_carrier',None)
    tilt=bpy.data.objects.new('selectric_tilt',None)
    spin=bpy.data.objects.new('selectric_spin',None)
    for node in (carrier,tilt,spin):bpy.context.collection.objects.link(node)
    carrier.location=(carrier_x,carrier_y,z+.002)
    tilt.parent=carrier;spin.parent=tilt
    bpy.context.view_layer.update()
    for index,o in enumerate(PARTS[carrier_start:],start=carrier_start):
        world=o.matrix_world.copy()
        o.parent=spin if index>=element_start else carrier
        o.matrix_world=world
    carrier['mechanism_role']='carrier';tilt['mechanism_role']='tilt';spin['mechanism_role']='spin'


def ruler(y, z, width=.43, front=True):
    box('carrier position scale', (0, y, z), (width, .003, .012), CHROME, .0006)
    for i in range(131):
        x = (i/130-.5)*(width-.008)
        height = .004 if i % 5 == 0 else .002
        box(f'position tick {i:03}', (x, y-.0018, z+.004-height/2), (.00035, .0003, height), BLACK, 0)
        if i % 5 == 0:
            text(f'position numeral {i:03}', str(i), (x, y-.0021, z-.002), .003, BLACK)


def badge(name, body, loc, material=GRAY):
    box(name+' plate', loc, (.099, .0015, .014), CHROME, .0007)
    x, y, z = loc
    box(name+' IBM field', (x-.034, y-.001, z), (.029, .001, .012), BLACK, 0)
    text(name+' IBM', 'IBM', (x-.034, y-.0017, z), .010)
    text(name+' model', body, (x+.015, y-.0017, z), .0047, BLACK)


def print_material(name, filename, transparent=False):
    m=mat(name,(1,1,1),0,.55)
    p=m.node_tree.nodes.get('Principled BSDF')
    tex=m.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(ROOT/'textures'/filename));tex.image.pack()
    m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    if transparent:
        m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha'])
        m.surface_render_method='DITHERED'
    return m


def decal(name, verts, material):
    o=mesh(name,verts,[(0,1,2,3)],material)
    layer=o.data.uv_layers.new()
    uvs=[(0,0),(1,0),(1,1),(0,1)]
    # Bpy's normal recalculation may rotate a polygon's loop order.
    # Anchor UVs to vertex identity, not the current loop sequence.
    for loop in o.data.loops:layer.data[loop.index].uv=uvs[loop.vertex_index]
    return o


def printed_ruler(y,z,tilt,height=.020):
    from mathutils import Matrix
    o=box('carrier scale recessed surround',(0,y+.0008,z),(.438,.004,height+.003),BLACK,.0012)
    o.rotation_euler.x=tilt
    o=box('carrier scale metal frame',(0,y,z),(.43,.003,height),CHROME,.0006)
    o.rotation_euler.x=tilt
    pivot=Vector((0,y,z));rotation=Matrix.Rotation(tilt,4,'X')
    h=height/2-.0008
    verts=[pivot+rotation@Vector((x,-.0018,dz)) for x,dz in [(-.213,-h),(.213,-h),(.213,h),(-.213,h)]]
    decal('carrier scale printed graduations',verts,print_material('black printed scale on aluminum','1053-carrier-scale.png'))


def arrow_legend(name,x,y,z,tilt,direction=1,tab=False):
    from mathutils import Matrix
    rotation=Matrix.Rotation(tilt,4,'X')
    # A simple white outline arrow, faithful to the photographed control symbols.
    points=[(-.005,-.0012),(.001,-.0012),(.001,-.0038),(.006,0),(.001,.0038),(.001,.0012),(-.005,.0012)]
    verts=[Vector((x,y,z))+rotation@Vector((direction*u,0,v)) for u,v in points]
    mesh(name,verts,[tuple(range(len(verts)))],WHITE)
    if tab:
        o=box(name+' tab stop',(x+.008,y,z),(.0009,.0003,.009),WHITE,0);o.rotation_euler.x=tilt


def flat_badge(model,loc,tilt):
    from mathutils import Matrix
    box(model+' badge backing',loc,(.092,.014,.0008),CHROME,.0003).rotation_euler.x=tilt
    rotation=Matrix.Rotation(tilt,4,'X')
    verts=[Vector(loc)+rotation@Vector((x,y,.0006)) for x,y in [(-.046,-.007),(.046,-.007),(.046,.007),(-.046,.007)]]
    decal(model+' printed badge',verts,print_material(model+' printed model plate',model+'-badge.png'))


def build_1053(width, depth):
    # Reference-led pass: low shell, thin ledge, and a fascia tilted back 12.2°.
    # All controls are placed in that same panel frame, rather than guessed in Y.
    tilt = -math.atan2(.031, .143)
    def front_y(z):
        return -.095+(z-.012)*(.031/.143)-.004
    yz = [(-.095, .012), (.13, .012), (.13, .145), (.115, .155), (-.064, .155)]
    cabinet=mat('1053 charcoal gray cabinet enamel',(.09,.105,.105),.18,.43)
    top_paint=mat('1053 satin gray cover ledge',(.21,.23,.22),.20,.38)
    hood_material=mat('1053 lightly smoked clear acrylic',(.60,.66,.66),0,.10,.30)
    hood_material.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.90
    for side in (-1, 1):
        x0, x1 = sorted((side*.28, side*.235))
        o=profile(f'1053 side enclosure {side}', x0, x1, yz, cabinet)
        o.data.materials.append(top_paint)
        for p in o.data.polygons:
            if p.normal.z>.4:p.material_index=1
    o=profile('1053 rear enclosure', -.235, .235, [(.105, .012), (.13, .012), (.13, .145), (.115, .155), (.105, .155)], cabinet)
    o.data.materials.append(top_paint)
    for p in o.data.polygons:
        if p.normal.z>.4:p.material_index=1
    profile('1053 front cover ledge', -.235, .235, [(-.064, .147), (-.064, .155), (-.041, .155), (-.041, .147)], top_paint)
    panel = box('1131 console fascia', (0, -.0805, .0835), (.552, .006, math.hypot(.143,.031)), BLACK, .0015)
    panel.rotation_euler.x = tilt
    # Console switches: explicit states, resting downward as in the reference.
    for bit in range(16):
        x = -.143+bit*.024
        y = front_y(.116)
        cyl(f'data bit {bit:02} bezel', (x, y, .116), .0048, .003, CHROME, (0, -math.cos(tilt), -math.sin(tilt)),vertices=24)
        rod(f'data bit {bit:02} lever', (x, y-.002, .116), (x, y-.015, .102), .0016, CHROME,16)
        rod(f'data bit {bit:02} ivory tip', (x, y-.012, .105), (x, y-.017, .100), .0022, WHITE,16)
    printmat=print_material('1053 white printed switch legends','1053-fascia-print.png',True)
    decal('1053 printed bit numbers and nibble dividers',[(x,front_y(z)-.0005,z) for x,z in [(-.276,.012),(.276,.012),(.276,.155),(-.276,.155)]],printmat)
    o=box('tab set clear bezel', (-.247, front_y(.116), .116), (.022, .008, .031), CHROME);o.rotation_euler.x=tilt
    o=box('blue tab set clear control', (-.247, front_y(.116)-.008, .116), (.018, .009, .024), BLUE);o.rotation_euler.x=tilt
    text('TAB control legend','TAB',(-.247,front_y(.116)-.013,.116),.004,WHITE,(math.pi/2+tilt,0,0))
    printed_ruler(front_y(.085),.085,tilt)
    o=box('1053 three-key recessed bezel',(0,front_y(.035)-.001,.035),(.094,.005,.028),BLACK,.0015);o.rotation_euler.x=tilt
    for name, x, glyph in [('space', -.029, '→'), ('tab', 0, '⇥'), ('return', .029, '←')]:
        o=box('1053 '+name+' key', (x, front_y(.035)-.006, .035), (.027, .018, .022), BLUE, .002);o.rotation_euler.x=tilt
        arrow_legend(name+' key legend',x,front_y(.035)-.016,.035,tilt,-1 if name=='return' else 1,name=='tab')
    mechanism(width, .060, .132, BLUE,agile=True)
    # A thin, hollow formed hood with a front slope and rear paper deflector.
    cover_start = len(PARTS)
    surface = [(-.041, .157), (-.010, .177), (.093, .177), (.116, .198)]
    for j, ((y0, z0), (y1, z1)) in enumerate(zip(surface, surface[1:])):
        o = mesh(f'acrylic hood panel {j}', [(-.233, y0, z0), (.233, y0, z0), (.233, y1, z1), (-.233, y1, z1)], [(0, 1, 2, 3)], hood_material)
        solid = o.modifiers.new('acrylic thickness 2mm', 'SOLIDIFY'); solid.thickness = .002
    for side in (-1, 1):
        mesh(f'acrylic hood end {side}', [(side*.233, y, z) for y, z in surface[:3]]+[(side*.233, .093, .157)], [(0, 1, 2, 3)], hood_material)
    rod('acrylic hood front trim', (-.235, -.041, .157), (.235, -.041, .157), .0015, CHROME)
    for o in PARTS[cover_start:]:
        o['assembly'] = 'removable printer hood'
    box('central cover handle', (0, -.069, .153), (.063, .008, .004), CHROME)
    box('1131 installation badge', (0,-.052,.156), (.065,.008,.0006), CHROME, .0003)
    text('1131 installation badge print','IBM   1131',(0,-.052,.1564),.005,BLACK,(0,0,0))


def keycap(name, label, x, y, width=.017, depth=.019, atlas=None, shell_material=KEY):
    # Tapered, slightly dished cap: a bevel around two stacked profiles.
    z = .035+(y+.20)*.12
    verts = [(x+dx*w/2, y+dy*d/2, z+h) for w,d,h in [(width,depth,0),(width*.86,depth*.86,.011)] for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    o = mesh(name, verts, [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)], shell_material, .0018)
    o['keycap']=True
    if label and atlas is not None:
        index,material=atlas
        points=[(v[0],v[1],v[2]+.00025) for v in verts[4:]]
        printing=decal(name+' legend',points,material)
        col,row=index%8,index//8
        uv=[(col/8,1-(row+1)/8),((col+1)/8,1-(row+1)/8),((col+1)/8,1-row/8),(col/8,1-row/8)]
        for loop in printing.data.loops:printing.data.uv_layers.active.data[loop.index].uv=uv[loop.vertex_index]
    elif label:
        text(name+' legend', label, (x, y, z+.0125), .0055, WHITE, (0, 0, 0))
    return o


def build_2741(width, depth):
    # Low, rounded desktop shell from the supplied 2741 reconstruction. The
    # loaded paper is an explicit configuration, not extra enclosure height.
    yz=[(-.205,.012),(.195,.012),(.195,.073),(.187,.096),(.172,.112),(.038,.112),(-.040,.073),(-.058,.047),(-.205,.029)]
    for side in (-1, 1):
        x0,x1=sorted((side*.27,side*.25))
        profile(f'2741 outer cheek {side}',x0,x1,yz,CREAM,.006)
    profile('2741 rear cover',-.25,.25,[(.155,.012),(.195,.012),(.195,.073),(.187,.096),(.172,.112),(.155,.112)],CREAM,.006)
    profile('2741 low keyboard deck',-.25,.25,[(-.205,.017),(-.055,.017),(-.055,.047),(-.205,.029)],CREAM,.008)
    box('2741 rounded palm edge',(0,-.194,.025),(.53,.028,.027),CREAM,.010)
    profile('2741 nameplate shoulder',-.25,.25,[(-.058,.047),(-.042,.077),(.038,.112),(.060,.112),(-.025,.075)],CREAM,.006)
    o=box('2741 keyboard well',(0,-.122,.043),(.354,.110,.008),BLACK,.004);o.rotation_euler.x=.12
    mechanism(width,.080,.100,CHROME,-.06,agile=True,carrier_y=.074)
    atlas=print_material('2741 printed APL keyboard legends','2741-apl-keyboard.png',True)
    keys=json.loads((ROOT/'models/2741-keyboard.json').read_text())['keys']
    key_material=mat('2741 graphite key plastic',(.025,.030,.033),.05,.4)
    for index,key in enumerate(keys):
        keycap(key['name'],key['legend'],key['x'],key['y'],key['width'],key['depth'],(index,atlas),key_material)
    printed_ruler(-.048,.071,-.17,height=.006)
    tilt=math.atan2(.035,.080)
    flat_badge('2741',(0,.004,.098),tilt)
    for side in (-1, 1):
        box(f'2741 top control slot {side}',(side*.225,.165,.113),(.009,.030,.001),BLACK,.001)
        box(f'2741 top control lever {side}',(side*.225,.166,.116),(.004,.014,.008),CHROME,.0006)
    paper=mat('loaded cream paper',(.82,.81,.74),0,.85)
    verts=[]
    for i in range(9):
        t=i/8;y=.093+.061*t+.004*math.sin(math.pi*t);z=.108+.108*t
        verts.extend([(-.193,y,z),(.193,y,z)])
    sheet=mesh('2741 loaded paper sheet',verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(8)],paper)
    solid=sheet.modifiers.new('paper thickness','SOLIDIFY');solid.thickness=.00018
    for x in (-.22,.22):
        for y in (-.16,.16):
            cyl(f'2741 rubber foot {x} {y}', (x,y,.004), .014,.008,RUBBER,(0,0,1))


def build_5471(width,depth):
    """System/3 case and keyboard, with shared Selectric construction helpers.

    Clean lower body follows the user's correction, not the reference's skirt.
    Control identities/layout follow GA21-9103-1 Figures 8-1 and 8-2.
    """
    paint=mat('5471 light gray enamel',(.59,.61,.57),.12,.40)
    cap=mat('5471 dark key plastic',(.024,.028,.03),0,.40)
    yz=[(-.23,.010),(.23,.010),(.23,.117),(.22,.140),(.20,.153),(.015,.153),(-.060,.095),(-.085,.055),(-.23,.034)]
    for side in (-1,1):
        x0,x1=sorted((side*.27,side*.25))
        profile(f'5471 outer cheek {side}',x0,x1,yz,paint,.008)
    profile('5471 rear enclosure',-.25,.25,[(.19,.01),(.23,.01),(.23,.117),(.22,.14),(.20,.153),(.19,.153)],paint,.008)
    profile('5471 keyboard deck',-.25,.25,[(-.23,.014),(-.075,.014),(-.075,.056),(-.23,.034)],paint,.009)
    box('5471 rounded front edge',(0,-.216,.027),(.530,.028,.032),paint,.012)
    profile('5471 front printer housing',-.25,.25,[(-.085,.055),(-.060,.095),(.015,.153),(.042,.153),(-.040,.091)],paint,.007)
    o=box('5471 keyboard well',(-.017,-.141,.041),(.356,.118,.007),BLACK,.004);o.rotation_euler.x=.12
    atlas=print_material('5471 keyboard printed legends','5471-keyboard.png',True)
    keys=json.loads((ROOT/'models/5471-keyboard.json').read_text())['keys']
    for index,key in enumerate(keys):
        keycap(key['name'],key['legend'],key['x'],key['y'],key['width'],key['depth'],(index,atlas),cap)
    # Separate status windows, not extra keyboard keys.
    from mathutils import Matrix
    rotation=Matrix.Rotation(.12,4,'X')
    center=Vector((.218,-.126,.052))
    box('5471 right indicator bezel',center,(.026,.103,.004),BLACK,.002).rotation_euler.x=.12
    verts=[center+rotation@Vector((x,y,.0025)) for x,y in [(-.012,-.05),(.012,-.05),(.012,.05),(-.012,.05)]]
    decal('5471 PROCEED and REQUEST PENDING',verts,print_material('5471 printed status legends','5471-indicators.png'))
    mechanism(width,.105,.145,CHROME,-.05,agile=True,carrier_y=.095,knob_sides=(1,))
    # Slanted dark carrier scale band, characteristic of this console.
    tilt=-math.atan2(.075,.058);rotation=Matrix.Rotation(tilt,4,'X')
    center=Vector((0,-.049,.106))
    o=box('5471 front carrier scale recess',center,(.435,.004,.039),BLACK,.002);o.rotation_euler.x=tilt
    verts=[center+rotation@Vector((x,-.0022,z)) for x,z in [(-.214,-.017),(.214,-.017),(.214,.017),(-.214,.017)]]
    decal('5471 carrier scale print',verts,print_material('5471 black scale legends','5471-front-scale.png'))
    # Thin transparent paper guide, supported by the IBM illustration. Avoid
    # copying the dense reconstruction's opaque/globby version of this surface.
    guide=mat('5471 clear paper deflector',(.78,.83,.82),0,.08,.26)
    guide.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.95
    surface=[(.055,.158),(.12,.177),(.175,.223),(.216,.227)]
    for j,((y0,z0),(y1,z1)) in enumerate(zip(surface,surface[1:])):
        o=mesh(f'5471 paper deflector panel {j}',[(-.222,y0,z0),(.222,y0,z0),(.222,y1,z1),(-.222,y1,z1)],[(0,1,2,3)],guide)
        o.modifiers.new('deflector thickness','SOLIDIFY').thickness=.0015
    for side in (-1,1):
        box(f'5471 paper guide end clip {side}',(side*.225,.128,.18),(.008,.018,.012),CHROME,.001)
        box(f'5471 upper control slot {side}',(side*.236,.195,.154),(.009,.024,.001),BLACK,.0008)
        box(f'5471 upper control lever {side}',(side*.236,.195,.158),(.004,.015,.008),BLACK,.0008)
    flat_badge('5471',(.180,.004,.146),math.atan2(.058,.075))
    for x in (-.22,.22):
        for y in (-.18,.18):cyl(f'5471 foot {x} {y}',(x,y,.004),.014,.008,RUBBER,(0,0,1))


def compact_1053(root):
    """Batch static geometry; preserve individual functional controls as nodes."""
    import re
    from collections import defaultdict
    groups=defaultdict(list)
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    deps=bpy.context.evaluated_depsgraph_get()
    for o in objects:
        # Evaluate bevels/normals before joining so one modifier does not change
        # another component's surface or dimensional frame.
        # Sub-millimeter bevels on type slugs and thin rods cost many triangles
        # without changing their visible outline. Keep shell/key edge radii.
        for modifier in list(o.modifiers):
            if modifier.type=='BEVEL':
                if sorted(o.dimensions)[1]<.015:
                    o.modifiers.remove(modifier)
                else:
                    modifier.segments=1 if o.get('keycap') else min(modifier.segments,2)
        bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get()
        evaluated=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
        o.modifiers.clear();o.data=evaluated
        match=re.match(r'data bit (\d\d)',o.name)
        if o.parent and o.parent.name=='selectric_spin':
            key='type element assembly'
        elif o.parent and o.parent.name=='selectric_carrier':
            key='moving carrier assembly'
        elif match:
            key='data bit '+match.group(1)+' actuator'
        elif o.get('assembly')=='removable printer hood':
            key='removable acrylic hood'
        elif o.name.startswith('platen knob '):
            key=' '.join(o.name.split()[:3])
        elif any(token in o.name for token in ('space key','tab key','return key')):
            key=next(token+' control' for token in ('space','tab','return') if token in o.name)
        elif o.name.startswith('TAB control') or o.name.startswith('blue tab set'):
            key='tab set clear control'
        else:
            key='static '+o.data.materials[0].name
        groups[(key,o.parent.name if o.parent else '')].append(o)
    for (key,_),parts in groups.items():
        parent=parts[0].parent
        names=[o.name for o in parts]
        bpy.ops.object.select_all(action='DESELECT')
        for o in parts:o.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]
        if len(parts)>1:bpy.ops.object.join()
        o=bpy.context.view_layer.objects.active;o.name=key;o.parent=parent
        o['semantic_parts']=json.dumps(names)
    return len(objects)


def finish(model):
    from datetime import datetime, timezone
    root = bpy.data.objects.get({'1053':'IBM 1053 console printer','2741':'IBM 2741 desktop APL terminal','5471':'IBM 5471 System 3 console','trs80':'TRS-80 Model I desktop system'}[model])
    for o in PARTS:
        if o.parent is None:o.parent = root
    carrier=bpy.data.objects.get('selectric_carrier')
    if carrier:carrier.parent=root
    bpy.context.view_layer.update()
    logical_count=len([o for o in bpy.context.scene.objects if o.type=='MESH'])
    if os.environ.get('COMPACT_'+model,'1')=='1':
        logical_count=compact_1053(root)
    hardware = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    points = [o.matrix_world @ v.co for o in hardware for v in o.data.vertices]
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene['dimension_status'] = 'Provisional photographic proportions. 2741 OEM desk envelope does not constrain desktop shell.'
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for o in root.children_recursive:o.select_set(True)
    for o in hardware:
        o['semantic_name'] = o.name
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    stem = 'trs80' if model=='trs80' else 'ibm'+model
    mechanism_config=None
    if carrier:
        travel_columns=125 if model=='5471' else 130
        mechanism_config={'version':1,'model':model,'nodes':{'carrier':'selectric_carrier','tilt':'selectric_tilt','spin':'selectric_spin'},'pitch_m':.00254,'max_column':travel_columns,'left_x_m':-travel_columns*.00254/2,'rest_x_m':float(carrier.location.x),'max_tilt_deg':20,'coordinate_system':'glTF Y-up; carrier +X, tilt local X, spin local Y','accuracy':'10 CPI travel; illustrative tilt range and timing, not verified Selectric character coding'}
        (OUTPUT/'mechanism.json').write_text(json.dumps(mechanism_config,indent=2)+'\n')
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/(stem+'.glb')), use_selection=True, export_extras=True)
    import struct
    glb_data=(OUTPUT/(stem+'.glb')).read_bytes()
    gltf=json.loads(glb_data[20:20+struct.unpack_from('<I',glb_data,12)[0]])
    triangle_count=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives'])
    draw_calls=sum(len(m['primitives']) for m in gltf['meshes'])
    bpy.ops.wm.obj_export(filepath=str(OUTPUT/(stem+'.obj')), export_selected_objects=True)
    # Check an independent round-trip scene while preserving the production scene.
    original = scene
    test_scene = bpy.data.scenes.new('GLB round-trip validation')
    bpy.context.window.scene = test_scene
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/(stem+'.glb')))
    imported = [o for o in test_scene.objects if o.type == 'MESH']
    if mechanism_config:assert set(mechanism_config['nodes'].values()) <= {o.name.removesuffix('.001') for o in test_scene.objects}, 'Motion pivots lost on export'
    assert {o.name for o in hardware} == {o.get('semantic_name') for o in imported}, 'GLB semantic identities changed'
    bpy.context.view_layer.update()
    # Import applies glTF's axis conversion back to Blender coordinates.
    ip = [o.matrix_world @ v.co for o in imported for v in o.data.vertices]
    imported_bounds = [[min(p[i] for p in ip), max(p[i] for p in ip)] for i in range(3)]
    assert max(abs(bounds[i][j]-imported_bounds[i][j]) for i in range(3) for j in range(2)) < .002, 'GLB bounds changed'
    bpy.context.window.scene = original
    for o in list(test_scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.scenes.remove(test_scene)
    scene.render.engine = 'CYCLES'
    scene.view_settings.exposure = -1.2
    scene.cycles.samples = int(os.environ.get('RENDER_SAMPLES', '32'))
    scene.cycles.use_denoising = True
    device = os.environ.get('BLENDER_DEVICE', 'CPU')
    if device != 'CPU':
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = device
        prefs.get_devices()
        assert any(d.type == device for d in prefs.devices), 'Requested GPU unavailable'
        for d in prefs.devices:
            d.use = d.type == device
        scene.cycles.device = 'GPU'
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new('neutral studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.25,.28,.32,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
    # Stage goes into the native scene only, never into the exported hardware.
    floor = box('render stage', (0,0,-.019), (200,200,.02), mat('stage',(.14,.17,.20),0,.8), 0)
    for name, loc, power, size in [('key',(.4,-.7,1.3),100,1),('fill',(-.8,-.2,.7),70,.8),('rim',(.2,.8,1),130,.7)]:
        data = bpy.data.lights.new(name,'AREA'); data.energy = power; data.shape = 'DISK'; data.size = size
        o = bpy.data.objects.new(name,data); scene.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector((0,0,.1))-o.location).to_track_quat('-Z','Y').to_euler()
    views = [('overview',(.70,-.9,.68),(0,0,.12),.86),('front',(0,-1,.38),(0,0,.12),.72),('left',(-.75,-.8,.52),(0,0,.12),.82),('right',(.75,-.8,.52),(0,0,.12),.82),('top',(0,-.05,1.2),(0,0,.10),.70),('detail',(.23,-.50,.48),(0,-.07,.14),.48)]
    if model == '2741':
        views[0] = ('overview',(.70,-.9,.74),(0,0,.10),.90)
    if model=='trs80':
        scene['dimension_status']='Keyboard 424 x 205 x 85 mm and monitor 400 x 310 x 280 mm constrained by Museums Victoria HT1839; photo-led expansion fascia and upright disk orientation, rear fittings inferred.'
        views=[('overview',(.85,-1.30,.91),(.035,-.015,.205),.92),('front',(.035,-1.4,.68),(.035,-.015,.205),.82),('left',(-.9,-1.2,.8),(.035,-.015,.205),.94),('right',(.9,-1.2,.8),(.035,-.015,.205),.94),('top',(.035,-.015,1.5),(.035,-.015,0),.92),('detail',(.40,-.72,.66),(.05,-.20,.065),.53)]
    if model=='trs80':views += [('perspective',(.85,-1.30,.80),(.035,-.015,.190),.92),('front-perspective',(.035,-1.30,.55),(.035,-.015,.190),.82)]
    for name, loc, aim, scale in views:
        data = bpy.data.cameras.new(name); data.type = 'ORTHO'; data.ortho_scale = scale
        if name in ('perspective','front-perspective'):data.type='PERSP';data.lens=58 if name=='perspective' else 60;data.sensor_width=36
        cam = bpy.data.objects.new('camera '+name,data); scene.collection.objects.link(cam); cam.location = loc
        cam.rotation_euler = (Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.camera = cam
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = str(OUTPUT/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    scene.camera = bpy.data.objects['camera overview']
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/(stem+'.blend')))
    report = {'model':model,'generated_utc':datetime.now(timezone.utc).isoformat(),'blender':bpy.app.version_string,'device':device,'mesh_count':len(hardware),'logical_component_count':logical_count,'triangle_count':triangle_count,'draw_calls':draw_calls,'glb_bytes':len(glb_data),'bounds_m':bounds,'dimensions_m':[b-a for a,b in bounds],'glb_round_trip':'mesh names and bounds passed','dimension_status':scene['dimension_status'],'objects':sorted(o.name for o in hardware),'remaining_mismatches':['Absolute shell dimensions inferred','Small legends and rear fittings provisional','2741 desk configuration not modeled; photographed desktop unit targeted']}
    if model=='trs80':
        report['dimension_status']=scene['dimension_status'];report['remaining_mismatches']=['Expansion-interface front height matched to supplied photo; museum lists a different overall height','Disk enclosure inferred from photo and museum unit rotated upright','Rear monitor controls and cable routes inferred','CRT coating and fine wear remain approximate'];report['reference']='https://vintagecomputer.com/tandy-trs-80-model-i.html'
    (OUTPUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CONSOLE_BUILD_COMPLETE',model)
