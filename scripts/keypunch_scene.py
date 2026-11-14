"""029 correction against Columbia / IBM manual photos. No source GLB geometry.

Preserve the desk/leg reference frame for locked-camera baseline comparisons.
Card transport is an open assembly, not a ramp with rectangles on its surface.
"""
from mathutils import Matrix

def kp_box(name,loc,size,material,bevel=.001):return box('029 '+name,loc,size,material,bevel)

def kp_keycap(k,index,center,scale,angle,atlas,gray,blue):
    x0,y0,x1,y1=k['rect'];origin=Vector(center);rot=Matrix.Rotation(angle,4,'X')
    # Source Fig. 8 has y increasing downward; local key-plane Y increases rearward.
    def local(p,z):return Vector(((p[0]-1115)*scale,(440-p[1])*scale,z))
    outline=k['shape'] or [[x0,y1],[x1,y1],[x1,y0],[x0,y0]]
    points=[local(p,0) for p in outline];cx=sum(p.x for p in points)/len(points);cy=sum(p.y for p in points)/len(points)
    n=len(points);verts=[]
    for shrink,z in [(1,0),(.91,.008),(.80,.0105)]:
        verts += [origin+rot@Vector((cx+(p.x-cx)*shrink,cy+(p.y-cy)*shrink,z)) for p in points]
    faces=[tuple(reversed(range(n)))]+[(r*n+i,r*n+(i+1)%n,(r+1)*n+(i+1)%n,(r+1)*n+i) for r in range(2) for i in range(n)]+[tuple(range(2*n,3*n))]
    o=mesh('029 key '+k['legend'].replace('\n',' '),verts,faces,blue if k['blue'] else gray);o['keycap']=True
    # Legend placed on the broad portion of asymmetric caps, clear of the notch.
    px=(x0+x1)/2;py=(y0+y1)/2
    if k['legend']=='ERROR\nRESET':py=y1-60
    if k['legend']=='LEFT\nZERO':py=y0+55
    w=min((x1-x0)*scale*.75,.029);h=min((y1-y0)*scale*.70,.019)
    c=local([px,py],.0108)
    o=decal('029 legend '+str(index),[origin+rot@(c+Vector((u*w/2,v*h/2,0))) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]],atlas)
    layer=o.data.uv_layers.active
    for loop in o.data.loops:
        u,v=layer.data[loop.index].uv;layer.data[loop.index].uv=((index%8+u)/8,1-(index//8+1-v)/8)

def build_029():
    global EQ_ROOT
    EQ_ROOT=bpy.data.objects['IBM 029 keypunch']
    body=mat('029 olive gray enamel',(.19,.215,.195),.12,.46)
    tabletop=mat('029 warm pale laminate',(.65,.66,.60),0,.57)
    lower=mat('029 lower cabinet charcoal',(.064,.075,.069),.13,.5)
    keygray=mat('029 gray alphanumeric keys',(.43,.46,.43),0,.43)
    blue=mat('029 blue function keys',(.012,.24,.46),.04,.35)
    black=mat('029 black mechanical interior',(.006,.009,.008),.05,.56)
    metal=mat('029 brushed steel parts',(.40,.43,.40),.73,.29)
    legs=mat('029 leg brushed steel',(.23,.26,.25),.72,.33)
    paper=mat('029 cream card stock',(.69,.64,.47),0,.8)
    labelmat=print_material('029 IBM 29 nameplate print','029-nameplate.png')
    cardmat=print_material('029 punched card print','029-card.png')
    # Fixed tabletop/cabinet/feet coordinates are shared with the rejected baseline.
    g=eq_group('029 desk and legs');start=len(PARTS)
    kp_box('desktop',(0,0,.765),(1.30,.76,.035),tabletop,.004)
    # The photo shows a desk, not a box: the rear machinery cabinet occupies
    # one quarter of the 760 mm desktop depth; the front 570 mm remains open.
    # Cabinet Y .19.. .38 m, operator clearance Y -.38.. .19 m.
    kp_box('shallow rear machinery cabinet',(-.045,.285,.487),(1.17,.190,.520),lower,.002)
    kp_box('rear cabinet service door',(.05,.187,.48),(.400,.004,.340),lower,.002)
    for x in (-.151,.251):kp_box('door vertical seam',(x,.184,.48),(.0015,.001,.34),black,0)
    for z in (.31,.65):kp_box('door horizontal seam',(.05,.184,z),(.40,.001,.0015),black,0)
    kp_box('service latch',(.235,.181,.61),(.014,.003,.026),metal,.001)
    for x in (-.59,.59):
        for y in (-.30,.30):
            kp_box('slender steel leg',(x,y,.38),(.029,.029,.75),legs,.001)
            kp_box('leg foot pad',(x,y,.005),(.027,.027,.005),RUBBER,.001)
        kp_box('lower side rail',(x,0,.18),(.025,.60,.025),legs,.001)
    eq_own(g,start)

    # Sparse structural shell: open transport bay below independently shaped covers.
    g=eq_group('029 structural head enclosure');start=len(PARTS)
    cheek=[(-.12,.805),(.315,.805),(.315,1.235),(.050,1.235),(-.055,1.030)]
    profile('029 left end cheek',-.585,-.540,cheek,body,.003)
    profile('029 right end cheek',.515,.560,cheek,body,.003)
    kp_box('rear head panel',(-.012,.303,1.02),(1.10,.025,.430),body,.002)
    kp_box('lower front crossbeam',(-.012,-.105,.846),(1.10,.048,.076),body,.002)
    kp_box('card deck support',(-.012,.095,.889),(1.055,.355,.018),body,.002)
    for x in (-.552,.530):
        for z in (.825,1.18):cyl('029 cheek fastening screw',(x,-.131,z),.0025,.0015,metal,(0,-1,0),16)
    eq_own(g,start)

    g=eq_group('029 left stacker and curved guides');start=len(PARTS)
    # Sloping punched-card stacker at upper left; metallic apron below it.
    traycenter=Vector((-.400,.075,1.102));angle=math.radians(53)
    def tray_box(name,offset,size,material,bevel=.001):
        p=traycenter+Matrix.Rotation(angle,4,'X')@Vector(offset)
        o=kp_box(name,p,size,material,bevel);o.rotation_euler.x=angle;return o
    tray_box('left stacker backing',(0,0,0),(.270,.275,.008),metal)
    for sx in (-1,1):tray_box('stacker raised side rail',(sx*.134,0,.012),(.009,.286,.026),metal,.001)
    # Repeated slots/ruler on the metal backing remain visible above a modest stack.
    for x in (-.092,-.062,.062,.092):tray_box('stacker guide slot',(x,.015,.0046),(.003,.220,.001),black,0)
    tray_box('stacker punched cards',(0,-.028,.012),(.187,.145,.010),paper,.0004)
    pc_plate('029 stacker card face',traycenter+Matrix.Rotation(angle,4,'X')@Vector((0,-.028,.0174)),.186,.144,cardmat,angle)
    tray_box('stacker lower card stop',(0,-.132,.024),(.278,.014,.035),metal,.002)
    kp_box('left front metallic apron',(-.400,-.045,.948),(.267,.128,.096),metal,.003)
    # A curved take-up shield gives the left station its distinctive rolled edge.
    cyl('029 left horizontal guide roller',(-.405,-.075,1.008),.024,.220,metal,(1,0,0),32)
    kp_box('left guide projecting tab',(-.309,-.116,.968),(.112,.009,.018),metal,.001)
    kp_box('left station black slot',(-.43,-.111,.922),(.052,.002,.035),black,.001)
    eq_own(g,start)

    g=eq_group('029 central punch and read stations');start=len(PARTS)
    # Continuous horizontal route, visible through the open face of the unit.
    kp_box('transport dark backplate',(-.16,.012,.970),(.290,.014,.145),black,.002)
    kp_box('transport metal bed',(-.02,-.033,.909),(.780,.154,.012),metal,.001)
    for z in (.928,1.035):cyl('029 transverse card rail',(-.015,-.064,z),.0045,.790,metal,(1,0,0),24)
    for x in (-.25,-.13,.03,.26,.44):
        cyl('029 card feed pressure roller',(x,-.077,.925),.012,.027,RUBBER,(1,0,0),24)
        kp_box('roller mounting arm',(x,-.043,.947),(.014,.055,.040),metal,.001)
    # One card in the station is consistent with the manual photograph's loaded state.
    kp_box('card in punch station',(-.145,-.084,.975),(.187,.0014,.083),paper,.0003)
    pc_plate('029 printed card at station',(-.145,-.0850,.975),.187,.083,cardmat)
    kp_box('left punch head shield',(-.277,-.075,.986),(.038,.060,.126),metal,.002)
    eq_own(g,start)

    g=eq_group('029 program drum cover');start=len(PARTS)
    # Cover is split around the narrow vertical inspection window, not an opaque cube.
    # Inspection face leans back 12 degrees so its opening looks slightly up.
    def program_face(name,x,z,w,h):
        y=-.004+(z-1.066)*math.tan(math.radians(12))
        o=kp_box(name,(x,y,z),(w,.030,h),body,.0015);o.rotation_euler.x=math.radians(-12)
    program_face('program cover wide front',-.127,1.151,.205,.168)
    program_face('program cover right jamb',.054,1.151,.023,.168)
    program_face('program cover window top',.010,1.221,.066,.029)
    program_face('program cover window sill',.010,1.080,.066,.026)
    kp_box('program cover roof',(-.080,.158,1.230),(.295,.260,.015),body,.002)
    kp_box('program window dark recess',(.011,.061,1.151),(.050,.010,.128),black,.001)
    cyl('029 vertical program drum',(.010,.050,1.150),.023,.115,paper,(0,0,1),32)
    for z in [1.105+i*.008 for i in range(12)]:
        cyl('029 program card row mark',(.010,.050,z),.02315,.0007,black,(0,0,1),32)
    for z in (1.092,1.209):cyl('029 program drum rim',(.010,.050,z),.025,.004,metal,(0,0,1),32)
    eq_own(g,start)

    g=eq_group('029 right card hopper and throat');start=len(PARTS)
    # Open top input hopper, with two separator fingers, above an open lower throat.
    kp_box('hopper front wall',(.343,.005,1.151),(.345,.022,.166),body,.002)
    kp_box('hopper back wall',(.343,.285,1.151),(.345,.020,.166),body,.002)
    for x in (.162,.516):kp_box('hopper side wall',(x,.145,1.151),(.017,.280,.166),body,.002)
    kp_box('hopper dark interior floor',(.34,.145,1.082),(.335,.258,.010),black,.001)
    kp_box('hopper loaded cards',(.34,.145,1.096),(.187,.125,.018),paper,.0005)
    for x in (.247,.430):
        o=kp_box('hopper sloped separator finger',(x,.125,1.171),(.040,.028,.104),body,.001);o.rotation_euler.x=math.radians(-12)
    # Upper deck bridge and downstand match the visible rectangular center post.
    kp_box('upper bridge roof',(.112,.145,1.227),(.098,.30,.021),body,.001)
    kp_box('center post face',(.112,-.002,1.003),(.083,.044,.246),body,.002)
    kp_box('center post foot',(.112,-.029,.906),(.107,.090,.018),metal,.001)
    kp_box('hopper lower metal back',(.34,.061,.973),(.300,.010,.127),metal,.001)
    cyl('029 right vertical feed roller',(.482,-.014,.975),.022,.119,metal,(0,0,1),32)
    kp_box('right card throat small ledge',(.383,-.076,.930),(.165,.095,.008),metal,.001)
    pc_cable('029 hopper wire card guide',[(.248,-.031,1.063),(.265,-.082,1.060),(.28,-.097,1.018),(.297,-.095,.999),(.310,-.073,1.055)],.0015,metal)
    pc_plate('029 IBM 29 head nameplate',(.395,-.007,1.179),.109,.017,labelmat)
    eq_own(g,start)

    g=eq_group('029 combination keyboard and operator switches');start=len(PARTS)
    deckangle=math.radians(9.5);panelangle=math.atan2(.085,.045);cx=.355
    # A low keyboard deck and a steep switch panel, with an actual break in slope.
    profile('029 keyboard pod lower body',.111,.600,[(-.358,.787),(-.060,.787),(-.060,.947),(-.100,.935),(-.145,.850),(-.358,.814)],body,.002)
    # Place the complete key bed in its own shallow frame, above the shell surface.
    bedcenter=(cx,-.254,.834)
    o=kp_box('black keyboard deck',bedcenter,(.470,.197,.007),black,.002);o.rotation_euler.x=deckangle
    atlas=print_material('029 keycap legend atlas','029-keyboard-legends.png',True)
    for i,k in enumerate(json.loads((ROOT/'models/029-keyboard.json').read_text())['keys']):
        kp_keycap(k,i,(cx,-.244,.841),.000212,deckangle,atlas,keygray,blue)
    panelcenter=Vector((cx,-.1225,.8925));rot=Matrix.Rotation(panelangle,4,'X')
    o=kp_box('brushed operator switch panel',panelcenter,(.478,.095,.005),metal,.001);o.rotation_euler.x=panelangle
    # Vertical seams divide the operator panel into the photographed three fields.
    for x in (cx-.115,cx+.130):
        p=panelcenter+rot@Vector((x-cx,0,.003));o=kp_box('operator panel division',p,(.0008,.091,.0006),black,0);o.rotation_euler.x=panelangle
    for i,dx in enumerate((-.204,-.140,-.048,-.010,.028,.068,.191)):
        p=panelcenter+rot@Vector((dx,.013,.005))
        o=kp_box('switch black mounting slot',p,(.010,.028,.0015),black,.001);o.rotation_euler.x=panelangle
        direction=rot@Vector((0,0,1));cyl('029 operator toggle lever',p+direction*.005,.002,.015,metal,direction,16)
    o=kp_box('operator lamp',panelcenter+rot@Vector((-.225,.013,.005)),(.018,.018,.003),black,.001);o.rotation_euler.x=panelangle
    # The keyboard is a separate desktop pod, supported on short feet.
    for x in (.17,.54):
        for y in (-.316,-.090):
            kp_box('keyboard rubber support foot',(x,y,.78475),(.038,.024,.0045),RUBBER,.0008)
    eq_own(g,start)

    # Reference-led depth correction: fix the rear edge, bring the head's open
    # front behind the independent keyboard. The former head/pod footprints
    # overlapped; there is now ~42 mm of clear tabletop between their bodies.
    head_groups=['029 structural head enclosure','029 left stacker and curved guides',
                 '029 central punch and read stations','029 program drum cover',
                 '029 right card hopper and throat']
    for name in head_groups:
        assembly=bpy.data.objects[name];assembly.scale.y=.75
        assembly.location.y=.315*(1-.75)
