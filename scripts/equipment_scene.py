"""Additional photo-led procedural equipment. Geometry in meters, Z up, front -Y.
Uses low-level helpers from console_scene and pcdual_scene; no source mesh parts.
"""
from mathutils import Matrix
EQ_ROOT=None

def eq_group(name):
    g=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(g);g.parent=EQ_ROOT;return g

def eq_own(g,start):pc_own(g,start)

def eq_key(name,loc,w,d,material,angle=0,height=None):
    rot=Matrix.Rotation(angle,4,'X');center=Vector(loc);height=(.009 if w>.006 else .0008) if height is None else height
    verts=[]
    for ww,dd,z in [(w,d,0),(w*.94,d*.92,height*.78),(w*.83,d*.80,height)]:
        verts += [center+rot@Vector((u*ww/2,v*dd/2,z)) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    verts.append(center+rot@Vector((0,0,height*.88)))
    faces=[(3,2,1,0)]+[(r*4+i,r*4+(i+1)%4,(r+1)*4+(i+1)%4,(r+1)*4+i) for r in range(2) for i in range(4)]+[(8+i,8+(i+1)%4,12) for i in range(4)]
    o=mesh(name,verts,faces,material);o['keycap']=True;return o

def build_3279():
    global EQ_ROOT
    EQ_ROOT=bpy.data.objects['IBM 3279 graphics workstation']
    beige=mat('3279 textured warm beige',(.48,.46,.38),.04,.58);dark=mat('3279 charcoal bezel',(.010,.012,.014),.03,.5)
    keywhite=mat('3279 ivory keys',(.74,.72,.64),0,.43);keyblack=mat('3279 dark keys',(.014,.017,.019),.02,.4)
    chart=print_material('3279 graphics screen','3279-area-chart.png');p=chart.node_tree.nodes.get('Principled BSDF');tex=next(n for n in chart.node_tree.nodes if n.type=='TEX_IMAGE');chart.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.35;p.inputs['Roughness'].default_value=.28;p.inputs['Coat Weight'].default_value=.30
    badge=print_material('3279 IBM badge','3279-badge.png')
    g=eq_group('3279 display cabinet');start=len(PARTS)
    sections=[(-.040,.460,.420,.330,.022),(-.012,.462,.422,.330,.025),(.255,.450,.405,.327,.042),(.420,.415,.355,.315,.046)];n=24
    verts=[v for y,w,h,z,r in sections for v in pc_round_ring(w,h,y,z,r)]
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]+[tuple(range(72,96))]
    o=mesh('3279 deep rounded beige cabinet',verts,faces,beige)
    for f in o.data.polygons:f.use_smooth=True
    outer=pc_round_ring(.458,.416,-.046,.330,.022);inner=pc_round_ring(.328,.306,-.047,.330,.014)
    mesh('3279 dark front surround',outer+inner,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],dark)
    back=pc_round_ring(.296,.267,-.023,.330,.018)
    o=mesh('3279 sculpted inner bezel',inner+back,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],dark)
    for f in o.data.polygons:f.use_smooth=True
    verts=[];uv=[];nx=28;nz=24
    for j in range(nz+1):
        v=j/nz
        for i in range(nx+1):
            u=i/nx;x=(u-.5)*.295;z=(v-.5)*.266
            verts.append((x,-.024-.007*(1-(2*u-1)**2)*(1-(2*v-1)**2),.330+z));uv.append((u,v))
    o=mesh('3279 convex color CRT',verts,[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)],chart);layer=o.data.uv_layers.new()
    for loop in o.data.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
    for f in o.data.polygons:f.use_smooth=True
    pc_plate('3279 IBM bezel badge',(0,-.048,.518),.027,.018,badge)
    box('3279 red power rocker bezel',(-.201,-.049,.202),(.022,.005,.054),keyblack,.003)
    box('3279 red power rocker',(-.201,-.053,.202),(.014,.006,.039),RED,.002)
    text('3279 power I','I',(-.201,-.057,.214),.010,WHITE);text('3279 power O','O',(-.201,-.057,.191),.009,WHITE)
    box('3279 upper right control recess',(.196,-.049,.416),(.026,.004,.118),keyblack,.003)
    for i in range(3):
        box('3279 blue control button',(.196,-.052,.456-i*.038),(.015,.005,.013),BLUE,.001)
        cyl('3279 control indicator',(.196,-.055,.441-i*.038),.0017,.001,WHITE,(0,-1,0),12)
    box('3279 brightness control recess',(.196,-.050,.220),(.028,.004,.091),keyblack,.003)
    for z in (.190,.248):cyl('3279 brightness dial',(.196,-.054,z),.007,.005,keyblack,(0,-1,0),24)
    for side in (-1,1):
        for i in range(25):
            y=.16+i*.0075;x=side*(.228-max(0,y-.255)*.10)
            box('3279 side cooling slit',(x,y,.493-max(0,y-.255)*.12),(.0015,.0023,.043),dark,.0005)
        pc_cable('3279 side panel seam',[(side*.231,.005,.245),(side*.227,.255,.285),(side*.210,.402,.30),(side*.210,.402,.44)],.00065,dark)
    eq_own(g,start)
    g=eq_group('3279 pedestal');start=len(PARTS)
    box('3279 stand plinth',(0,.06,.035),(.324,.245,.050),beige,.008)
    box('3279 tilt neck',(0,.09,.093),(.180,.135,.095),beige,.012)
    box('3279 pedestal front vent',(0,-.064,.055),(.075,.002,.030),dark,.009)
    for i in range(5):box('3279 pedestal vent rib',(0,-.066,.045+i*.004),(.058,.002,.0015),keyblack,.0003)
    cyl('3279 tilt pivot',(.171,.04,.074),.009,.006,CHROME,(1,0,0),24);eq_own(g,start)
    g=eq_group('3279 sculpted keyboard');start=len(PARTS);cy=-.330
    profile('3279 keyboard body',-.290,.290,[(cy-.13,.012),(cy+.13,.012),(cy+.13,.090),(cy+.08,.084),(cy-.13,.032)],beige,.008)
    angle=math.radians(14)
    def kz(y):return .035+(y-(cy-.13))*math.tan(angle)
    o=box('3279 inset key bed',(0,cy+.018,kz(cy+.018)+.001),(.510,.150,.005),keyblack,.003);o.rotation_euler.x=angle
    for row in range(4):
        y=cy+.069-row*.025
        for col in range(13):
            x=-.177+col*.023
            eq_key('3279 alphanumeric key',(x,y,kz(y)+.003),.021,.022,keywhite if 0<col<12 else keyblack,angle)
    for row in range(5):
        for col in range(2):
            x=-.249+col*.021;y=cy+.069-row*.025
            eq_key('3279 left command key',(x,y,kz(y)+.003),.019,.022,keyblack,angle)
    accents=[RED,BLUE,mat('3279 green command key',(.08,.32,.15)),mat('3279 yellow command key',(.64,.49,.04)),BLUE]
    for row in range(5):
        for col in range(3):
            x=.183+col*.023;y=cy+.069-row*.025
            eq_key('3279 right command key',(x,y,kz(y)+.003),.020,.022,accents[row] if col==2 else keyblack,angle)
    y=cy-.043;eq_key('3279 black space bar',(-.035,y,kz(y)+.003),.235,.021,keyblack,angle)
    pc_cable('3279 keyboard right wrist seam',[(.158,cy-.13,.033),(.158,cy-.058,kz(cy-.058)+.002)],.00055,keyblack)
    eq_own(g,start)
    g=eq_group('3279 keyboard lead');start=len(PARTS);pc_cable('3279 black keyboard lead',[(0,cy+.13,.045),(0,-.15,.024),(-.04,-.10,.024),(-.04,.02,.04)],.0035,keyblack);eq_own(g,start)

# IBM 029 builder lives in keypunch_scene.py, composed by make-ibm029.xtl.

def build_cor24():
    global EQ_ROOT
    EQ_ROOT=bpy.data.objects['COR24 TB development board']
    mask=mat('COR24 green solder mask',(.045,.18,.12),.15,.47);edgegreen=mat('COR24 laminate edge',(.15,.22,.11),0,.7);black=mat('COR24 black packages',(.010,.014,.017),.05,.48);tin=mat('COR24 solder and tin',(.49,.51,.48),.80,.27);gold=mat('COR24 gold header pins',(.50,.36,.09),.75,.29);ceramic=mat('COR24 tan capacitors',(.32,.24,.13),0,.5)
    g=eq_group('COR24 board laminate and artwork');start=len(PARTS)
    box('COR24 90 x 50 mm laminate',(0,0,.0008),(.090,.050,.0016),edgegreen,.0018)
    o=pc_plate('COR24 solder mask and routing',(0,0,.00162),.089,.049,print_material('COR24 reconstructed trace artwork','cor24-top-artwork.png'),0)
    eq_own(g,start)
    g=eq_group('COR24 FPGA and SRAM');start=len(PARTS)
    box('Lattice FPGA LQFP body',(-.020,-.001,.0029),(.020,.020,.0024),black,.00025)
    pc_plate('Lattice FPGA markings',(-.020,-.001,.00415),.019,.019,print_material('COR24 FPGA marking','cor24-fpga-label.png'),0)
    cyl('FPGA pin one index',(-.028,-.009,.0042),.00065,.00008,black,(0,0,1),12)
    for side in (-1,1):
        for i in range(36):
            p=-.00875+i*.0005
            for x,y,sx,sy in [(-.020+side*.0107,-.001+p,.0015,.00022),(-.020+p,-.001+side*.0107,.00022,.0015)]:
                box('FPGA gull wing lead',(x,y,.00215),(sx,sy,.00032),tin,0)
    box('ISSI SRAM TSOP body',(.016,-.004,.0028),(.0185,.011,.002),black,.00020)
    pc_plate('ISSI SRAM markings',(.016,-.004,.00385),.0178,.0103,print_material('COR24 SRAM marking','cor24-sram-label.png'),0)
    for side in (-1,1):
        for i in range(24):box('SRAM gull wing lead',(.0085+i*.00065,-.004+side*.006,.00205),(.00025,.0011,.00030),tin,0)
    eq_own(g,start)
    g=eq_group('COR24 USB power and switches');start=len(PARTS)
    # Mini USB shell, with an actual hollow front mouth.
    x=-.038;y=.020
    box('mini USB top shell',(x,y,.0060),(.0078,.009,.00045),CHROME,.00025)
    for side in (-1,1):box('mini USB side shell',(x+side*.0038,y,.0040),(.00045,.009,.0040),CHROME,.00012)
    box('mini USB black tongue',(x,y+.002,.0038),(.0053,.004,.0010),black,.0001)
    for i in range(5):box('mini USB contact',(x-.0016+i*.0008,y+.0025,.0044),(.0004,.003,.00018),gold,0)
    box('voltage regulator U3',(-.023,.020,.0025),(.0065,.0035,.0016),black,.0002)
    for i in range(3):box('regulator terminal',(-.025+i*.002,.0175,.0019),(.0007,.0016,.0003),tin,0)
    for x in (-.006,.011):
        box('pushbutton metal cage',(x,.021,.0028),(.0056,.0036,.002),CHROME,.0003)
        box('pushbutton dark red plunger',(x,.021,.0041),(.0035,.0019,.0009),RED,.0003)
    eq_own(g,start)
    g=eq_group('COR24 passive components');start=len(PARTS)
    for i,(x,y) in enumerate([(-.013,.014),(-.017,.014),(-.024,.014),(-.032,.009),(-.034,-.004),(-.034,-.008),(-.024,-.015),(-.020,-.016),(-.015,-.016),(-.005,-.020),(.001,-.018),(.014,-.013),(.029,.007),(-.004,.004),(-.004,-.002),(-.004,-.011),(-.010,.019),(.020,.017),(.025,.017)]):
        for side in (-1,1):box('passive solder pad',(x+side*.0008,y,.00182),(.00065,.0010,.00025),tin,0)
        box('SMD capacitor resistor',(x,y,.00208),(.0010,.0009,.0006),ceramic if i%3 else black,.00005)
    box('oscillator package',(-.015,-.021,.0025),(.005,.003,.0015),black,.0001)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=(-.006,-.022,.0031));o=bpy.context.object;o.name='blue resonator X1';o.scale=(.0022,.0014,.0018);register(o,BLUE)
    eq_own(g,start)
    g=eq_group('COR24 angled pin headers');start=len(PARTS)
    for name,x,y,n,axis in [('left upper',-.044,.008,4,'y'),('left lower',-.044,-.010,6,'y'),('bottom left',-.033,-.023,6,'x'),('bottom right',.029,-.023,6,'x')]:
        for i in range(n):
            xx=x+(i*.00254 if axis=='x' else 0);yy=y+(i*.00254 if axis=='y' else 0)
            box(name+' plastic header',(xx,yy,.0029),(.0025,.0025,.0026),black,.00015)
            box(name+' gold vertical pin',(xx,yy,.0038),(.00064,.00064,.0044),gold,0)
            if axis=='x':box(name+' outward pin',(xx,yy-.003,.0057),(.00064,.006,.00064),gold,0)
            else:box(name+' outward pin',(xx-.003,yy,.0057),(.006,.00064,.00064),gold,0)
    eq_own(g,start)

def build_macbook():
    global EQ_ROOT
    EQ_ROOT=bpy.data.objects['MacBook Pro M1 Max']
    alloy=mat('MacBook satin aluminum',(.42,.45,.47),.80,.30);black=mat('MacBook black keys bezel',(.006,.008,.010),.05,.40);seam=mat('MacBook seams',(.06,.07,.08),.2,.45)
    g=eq_group('MacBook base');start=len(PARTS)
    box('MacBook rounded lower unibody',(0,0,.009),(.356,.248,.0168),alloy,.006)
    box('MacBook keyboard inset',(0,.031,.0175),(.281,.115,.0012),black,.003)
    for row in range(6):
        y=.079-row*.0172
        for col in range(14 if row<5 else 5):
            if row==5:
                x=[-.119,-.097,0,.097,.119][col];w=.155 if col==2 else .019
            else:x=-.127+col*.0195;w=.0182
            eq_key('MacBook key',(x,y,.0178),w,.0143,black,height=.0009)
    for side in (-1,1):
        pc_plate('MacBook speaker perforations',(side*.158,.034,.0177),.018,.123,print_material('MacBook perforated speaker grille','macbook-speakers.png'),0)
        for y in (-.02,.028,.067):box('MacBook USB C port',(side*.1782,y,.009),(.0006,.009,.003),black,.001)
    # A trackpad seam is a shallow outline rather than a raised block.
    for x in (-.0775,.0775):box('MacBook trackpad side seam',(x,-.062,.01755),(.00025,.088,.00012),seam,0)
    for y in (-.106,-.018):box('MacBook trackpad end seam',(0,y,.01755),(.155,.00025,.00012),seam,0)
    box('MacBook front opening relief',(0,-.124,.012),(.060,.0014,.004),seam,.001)
    for x in (-.14,.14):
        for y in (-.09,.09):cyl('MacBook rubber foot',(x,y,.001),.007,.002,RUBBER,(0,0,1),24)
    cyl('MacBook hinge barrel',(0,.118,.019),.004,.285,black,(1,0,0),32);eq_own(g,start)
    g=eq_group('MacBook open display');start=len(PARTS)
    box('MacBook thin rounded display shell',(0,0,.115),(.354,.005,.230),alloy,.003)
    pc_plate('MacBook black screen surround',(0,-.0028,.115),.348,.224,black)
    pc_plate('MacBook APL display',(0,-.0030,.119),.331,.205,print_material('MacBook APL wallpaper','macbook-apl-screen.png'))
    box('MacBook camera notch',(0,-.0033,.217),(.025,.0004,.008),black,.001)
    cyl('MacBook camera lens',(0,-.0037,.218),.0013,.0002,seam,(0,-1,0),16)
    eq_own(g,start);g.location=(0,.119,.019);g.rotation_euler.x=math.radians(-12)
