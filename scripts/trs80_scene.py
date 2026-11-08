"""TRS-80 Model I: separate component frames, reference-led exterior surfaces.

Meters, Blender Z up, front -Y. See docs/trs80.md for evidence and uncertainties.
Appended after console_scene.py by make-trs80.xtl, not an independent bpy entry.
"""
from mathutils import Matrix


def trs_group(name):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o)
    o.parent=bpy.data.objects['TRS-80 Model I desktop system']
    return o


def trs_own(group,start):
    for o in PARTS[start:]:
        world=o.matrix_world.copy();o.parent=group;o.matrix_world=world


def trs_plate(name,center,width,height,material,rotation=(math.pi/2,0,0)):
    rot=Matrix.Rotation(rotation[0],4,'X')
    return decal(name,[Vector(center)+rot@Vector((x,y,0)) for x,y in [(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2)]],material)


def trs_cable(name,points,radius,material):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=12
    data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);register(o,material)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')


def trs_key(name,x,y,z,width,legend,atlas,ivory=False):
    # Sloping sides and a shallow dished top, rather than printed cubes.
    depth=.016;h=.010;verts=[]
    for w,d,zz in [(width,depth,0),(width-.002,depth-.002,h*.8),(width-.004,depth-.004,h)]:
        verts.extend([(u*w/2,v*d/2,zz) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]])
    verts.append((0,0,h-.0012));faces=[(3,2,1,0)]
    for ring in range(2):
        faces.extend([(ring*4+i,ring*4+(i+1)%4,(ring+1)*4+(i+1)%4,(ring+1)*4+i) for i in range(4)])
    faces.extend([(8+i,8+(i+1)%4,12) for i in range(4)])
    angle=math.radians(10);rot=Matrix.Rotation(angle,4,'X');center=Vector((x,y,z))
    o=mesh(name,[center+rot@Vector(v) for v in verts],faces,WHITE if ivory else bpy.data.materials['TRS-80 black keycaps'],.0005);o['keycap']=True
    w=width-.004;d=depth-.004
    o=decal(name+' legend',[center+rot@Vector(v) for v in [(-w/2,-d/2,h+.00015),(w/2,-d/2,h+.00015),(w/2,d/2,h+.00015),(-w/2,d/2,h+.00015)]],atlas)
    layer=o.data.uv_layers.active;col=legend%8;row=legend//8
    for loop in o.data.loops:
        u,v=layer.data[loop.index].uv;layer.data[loop.index].uv=((col+u)/8,1-(row+1-v)/8)


def build_trs80():
    silver=mat('TRS-80 silver painted ABS',(.39,.415,.43),.52,.34)
    edge_silver=mat('TRS-80 bright trim',(.57,.59,.60),.7,.25)
    charcoal=mat('TRS-80 textured charcoal',(.018,.021,.022),.07,.52)
    mat('TRS-80 black keycaps',(.012,.014,.016),.03,.36)
    dark=mat('TRS-80 recess interiors',(.004,.006,.007),0,.8)
    screen=mat('unpowered gray CRT phosphor',(.20,.23,.235),.08,.26)
    # Broad glass reflection is part of the photographed blank, powered-off CRT.
    p=screen.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.35;p.inputs['Coat Roughness'].default_value=.2
    badges={key:print_material('TRS-80 '+key+' printed badge','trs80-'+key+'-badge.png') for key in ('cpu','expansion','monitor','disk')}
    atlas=print_material('TRS-80 key legend atlas','trs80-key-legends.png',True)

    # Keyboard/CPU, museum width 424 mm, depth 205 mm, rear height 85 mm.
    group=trs_group('keyboard CPU assembly');start=len(PARTS);cy=-.235
    profile('CPU silver wedge',-.212,.212,[(cy-.1025,.012),(cy+.1025,.012),(cy+.1025,.070),(cy+.085,.070),(cy-.1025,.028)],silver,.005)
    box('CPU lower dark seam',(0,cy,.013),(.420,.200,.008),charcoal,.003)
    angle=math.radians(10)
    def deck(y):return .032+(y-(cy-.1025))*math.tan(angle)
    o=box('CPU inset black keyboard surround',(0,cy+.006,deck(cy+.006)+.001),(.385,.151,.008),charcoal,.005);o.rotation_euler.x=angle
    o=box('keyboard recessed key bed',(-.047,cy+.009,deck(cy+.009)+.006),(.282,.131,.003),dark,.002);o.rotation_euler.x=angle
    rows=[list('1234567890')+[': *','- =','BREAK'],list('QWERTYUIOP')+['@','↑','↓'],list('ASDFGHJKL')+['; +','ENTER'],['SHIFT']+list('ZXCVBNM')+[', <','. >','/ ?','SHIFT'],['←','SPACE','→']]
    index=0
    for row,labels in enumerate(rows):
        y=cy+.059-row*.024
        if row==4:
            layout=[(-.162,.024),(-.065,.145),(.043,.024)]
        else:layout=[(-.173+j*.019+(0 if row<2 else .004 if row==2 else 0),.017 if label not in ('SHIFT','ENTER') else .020) for j,label in enumerate(labels)]
        for (x,w),label in zip(layout,labels):
            trs_key('CPU '+label+' key '+str(index),x+(.009 if label=='ENTER' else 0),y,deck(y)+.008,.033 if label=='ENTER' else w,index,atlas,label=='ENTER');index+=1
    # The separate CLEAR key is above the contrasting ENTER key.
    trs_key('CPU CLEAR key',.076,cy+.017,deck(cy+.017)+.008,.017,52,atlas)
    trs_plate('CPU model badge',(.153,cy+.006,deck(cy+.006)+.008),.059,.074,badges['cpu'],(angle,0,0))
    cyl('CPU power LED',(.122,cy-.050,deck(cy-.050)+.006),.0034,.002,RED,(0,-math.sin(angle),math.cos(angle)),24)
    for i in range(38):box('CPU rear vent '+str(i),(-.142+i*.0078,cy+.091,.071),(.0021,.013,.0007),dark,.0002)
    for x in (-.18,.18):
        for y in (cy-.07,cy+.07):cyl('CPU rubber foot',(x,y,.006),.010,.010,RUBBER,(0,0,1),20)
    # DIN sockets on the back, observed in the museum object description.
    for x in (.11,.145,.18):
        cyl('CPU rear DIN socket',(x,cy+.103,.043),.006,.002,dark,(0,1,0),24)
        for i in range(5):
            a=i*math.tau/5;cyl('CPU DIN pin',(x+.003*math.cos(a),cy+.1045,.043+.003*math.sin(a)),.00055,.001,CHROME,(0,1,0),8)
    trs_own(group,start)

    # Expansion interface: shallow front section with a raised rear monitor shelf.
    group=trs_group('expansion interface assembly');start=len(PARTS)
    profile('EI enclosure',-.212,.212,[(.005,.009),(.212,.009),(.212,.110),(.105,.110),(.105,.066),(.005,.066)],silver,.004)
    box('EI bottom seam',(0,.108,.012),(.420,.200,.005),charcoal,.001)
    box('EI front fascia',(0,.003,.037),(.408,.004,.047),silver,.002)
    for x,w in [(-.154,.085),(-.021,.108)]:
        box('EI removable connector cover',(x,-.0005,.038),(w,.003,.032),silver,.0008)
        for side in (-1,1):box('EI cover seam',(x+side*w/2,-.002,.038),(.0007,.001,.030),charcoal,0)
    for i in range(32):box('EI top ventilation slot '+str(i),(-.145+i*.008,.068,.0666),(.0023,.044,.001),dark,.0003)
    trs_plate('EI front badge',(.151,-.0005,.037),.043,.047,badges['expansion'])
    cyl('EI connector cover screw',(-.072,-.0025,.031),.0024,.0015,CHROME,(0,-1,0),16)
    for side in (-1,1):
        box('EI side port surround',(side*.213,.137,.055),(.002,.045,.020),charcoal,.001)
        box('EI card edge connector',(side*.214,.137,.055),(.001,.035,.005),dark,0)
    trs_own(group,start);group.location.y=-.040

    # Silver RCA-derived monitor: open front ring, tapered rear shell, convex CRT.
    group=trs_group('video monitor assembly');start=len(PARTS);z0=.114
    # Reference GLB depth slices: front width ~0.505 source units, rear
    # ~0.475; roof falls 0.074 source units (~58 mm at the 0.79 alignment).
    # Preserve the 400 mm front, with a curved shoulder and a 66 mm rear drop.
    sections=[(.013,.400,0,.280,.008),(.033,.400,0,.280,.010),(.180,.398,.010,.260,.012),(.270,.392,.018,.232,.016),(.310,.376,.022,.214,.019)]
    def cabinet_ring(y,w,bottom,top,r):
        pts=[]
        # Counter-clockwise around the X/Z section, rounded corners.
        for cx,cz,start_angle in [(w/2-r,top-r,0),(-w/2+r,top-r,90),(-w/2+r,bottom+r,180),(w/2-r,bottom+r,270)]:
            for j in range(7):
                angle=math.radians(start_angle+j*90/6)
                pts.append((cx+r*math.cos(angle),y,z0+cz+r*math.sin(angle)))
        return pts
    verts=[point for section in sections for point in cabinet_ring(*section)];n=28
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(sections)-1) for i in range(n)]
    faces.append(tuple(range((len(sections)-1)*n,len(sections)*n)))
    shell=mesh('monitor rounded sloping cabinet',verts,faces,silver)
    for face in shell.data.polygons:face.use_smooth=True
    # A separate thin, dark inset follows the roof, bounded by silver shoulders.
    roof=mat('monitor dark brown roof insert',(.012,.008,.006),.08,.32)
    verts=[]
    for y,w,bottom,top,r in sections[1:]:verts.extend([(-w/2+.018,y,z0+top+.0005),(w/2-.018,y,z0+top+.0005)])
    mesh('monitor recessed sloping roof insert',verts,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(len(sections)-2)],roof)
    box('monitor bottom silver rail',(0,.025,z0+.013),(.388,.031,.026),silver,.004)
    box('monitor thin upper lip',(0,.015,z0+.274),(.378,.008,.008),charcoal,.0018)
    # Lower front speaker/vent grille. Individual recesses produce real shadows.
    box('monitor lower fascia',(0,.008,z0+.032),(.386,.012,.046),silver,.002)
    for i in range(37):
        x=-.147+i*.0056
        for zz in (.024,.036):box('monitor lower grille slot',(x,.0012,z0+zz),(.0022,.001,.009),dark,.0007)
    # Black fascia with separate CRT opening and right badge/control column.
    box('monitor right control fascia',(.153,.011,z0+.162),(.061,.010,.214),charcoal,.002)
    for name,x,z,w,h in [('CRT left border',-.181,.163,.013,.218),('CRT right border',.112,.163,.018,.218),('CRT top border',-.039,.264,.282,.016),('CRT bottom border',-.039,.061,.282,.017)]:
        box(name,(x,.009,z0+z),(w,.016,h),charcoal,.003)
    # Rounded-rectangle rings form the actual deep, sloping CRT bezel.
    def ring(w,h,y,z,r=5,n=64):
        points=[]
        for i in range(n):
            a=math.tau*i/n;c=math.cos(a);s=math.sin(a)
            points.append((-.039+w/2*math.copysign(abs(c)**(2/r),c),y,z+h/2*math.copysign(abs(s)**(2/r),s)))
        return points
    n=64;outer=[]
    for i in range(n):
        a=math.tau*i/n;c=math.cos(a);ss=math.sin(a);r=max(abs(c),abs(ss))
        outer.append((-.039+.146*c/r,.003,z0+.163+.109*ss/r))
    inner=ring(.252,.179,.026,z0+.163,r=3.8)
    o=mesh('deep rounded CRT bezel',outer+inner,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],charcoal)
    for face in o.data.polygons:face.use_smooth=True
    # Glass rings bow forward smoothly. No emissive image: source screen is off.
    verts=[(-.039,.009,z0+.163)];rings=12
    for j in range(1,rings+1):
        t=j/rings;verts.extend(ring(.251*t,.178*t,.009+.017*t*t,z0+.163,r=3.8))
    faces=[(0,1+i,1+(i+1)%n) for i in range(n)]
    for j in range(rings-1):
        a=1+j*n;b=a+n;faces.extend([(a+i,b+i,b+(i+1)%n,a+(i+1)%n) for i in range(n)])
    glass=mesh('convex smoked CRT glass',verts,faces,screen)
    for face in glass.data.polygons:face.use_smooth=True
    trs_plate('monitor model badge',(.153,.004,z0+.187),.045,.067,badges['monitor'])
    cyl('monitor power button bezel',(.153,.003,z0+.253),.007,.005,edge_silver,(0,-1,0),32)
    cyl('monitor red power button',(.153,-.0002,z0+.253),.0048,.004,RED,(0,-1,0),32)
    for x in (.118,.142):
        cyl('monitor control bezel',(x,-.0005,z0+.030),.0062,.003,CHROME,(0,-1,0),24)
        cyl('monitor black control knob',(x,-.003,z0+.030),.0042,.007,charcoal,(0,-1,0),24)
        box('monitor knob index',(x,-.007,z0+.032),(.0007,.0005,.003),WHITE,0)
    cyl('monitor front video socket',(.168,-.0005,z0+.030),.0043,.004,CHROME,(0,-1,0),24)
    for side in (-1,1):
        for i in range(12):box('monitor side cooling slot',(side*(.1995-max(0,.15+i*.009-.180)*.033),.15+i*.009,z0+.205),(.0007,.003,.016),dark,.0003)
    for i in range(25):box('monitor rear ventilation',( -.15+i*.012,.3105,z0+.160),(.004,.0008,.032),dark,.0003)
    for x in (-.14,.14):box('monitor foot',(x,.09,z0-.004),(.045,.05,.010),RUBBER,.003)
    trs_own(group,start);group.location.y=-.040

    # One vertically mounted 5.25-inch mini-disk beside the interface.
    # Museum enclosure 325 x 155 x 90 mm, rotated onto its narrow side.
    group=trs_group('mini disk drive assembly');start=len(PARTS);dx=.300;dy=.098
    box('disk silver enclosure',(dx,dy,.084),(.090,.325,.155),silver,.002)
    box('disk black front bezel',(dx,dy-.165,.084),(.085,.009,.150),charcoal,.002)
    box('disk inset drive mechanism',(dx+.010,dy-.170,.105),(.053,.002,.103),dark,.001)
    box('disk vertical media opening',(dx+.014,dy-.172,.102),(.003,.003,.096),dark,.0006)
    for side in (-1,1):box('disk insertion guide',(dx+.014+side*.003,dy-.174,.102),(.001,.003,.094),charcoal,.0003)
    box('disk door latch hub',(dx+.015,dy-.175,.102),(.011,.008,.013),charcoal,.001)
    box('disk closed latch handle',(dx+.025,dy-.180,.102),(.027,.006,.007),charcoal,.001)
    cyl('disk activity LED',(dx-.025,dy-.173,.132),.0023,.002,RED,(0,-1,0),16)
    trs_plate('disk model badge',(dx-.020,dy-.173,.039),.033,.041,badges['disk'])
    for i in range(9):box('disk top ventilation slot',(dx-.030+i*.0075,dy+.125,.162),(.0025,.044,.001),dark,.0004)
    box('disk rear face',(dx,dy+.164,.084),(.085,.004,.148),charcoal,.001)
    box('disk ribbon port',(dx,dy+.167,.085),(.050,.002,.007),dark,0)
    for x in (dx-.030,dx+.030):
        for y in (dy-.13,dy+.13):box('disk rubber foot',(x,y,.004),(.012,.018,.007),RUBBER,.001)
    trs_own(group,start);group.location.y=-.040

    # Visible ribbon and two loose cable runs, following the photo, not its glare.
    group=trs_group('interconnect cables');start=len(PARTS)
    verts=[]
    for x,y,z in [(-.160,-.128,.068),(-.162,-.090,.035),(-.163,-.042,.024),(-.164,-.030,.042)]:verts.extend([(x-.022,y,z),(x+.022,y,z)])
    mesh('CPU to expansion flat ribbon',verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(3)],mat('ribbon gray PVC',(.38,.40,.39),0,.7))
    trs_cable('monitor signal cable',[(.168,-.044,z0+.029),(.167,-.065,.085),(.148,-.075,.02),(.13,-.13,.014),(.17,-.16,.045),(.18,-.132,.043)],.0026,charcoal)
    trs_cable('expansion to disk cable',[(.214,.097,.055),(.239,.091,.035),(.250,.18,.019),(.270,.245,.026),(.300,.227,.085)],.0035,charcoal)
    trs_own(group,start)
