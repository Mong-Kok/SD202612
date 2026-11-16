"""Independent fictional period passengers and approximate historical rolling stock."""
import math

def populate(api):
 box,beam,tri,quad,label,groups,COLORS=api
 def cylinder(mat,c,axis,r,length,segments=12):
  i,j=[k for k in range(3) if k!=axis]
  rings=[]
  for s in [-1,1]:
   ring=[]
   for k in range(segments):
    v=list(c);v[axis]+=s*length/2;v[i]+=r*math.cos(k*2*math.pi/segments);v[j]+=r*math.sin(k*2*math.pi/segments);ring.append(tuple(v))
   rings.append(ring)
  for k in range(segments):
   n=(k+1)%segments;quad(mat,rings[0][k],rings[0][n],rings[1][n],rings[1][k])
   for ring in rings:tri(mat,c,ring[k],ring[n])
 def ellipsoid(mat,c,r,seg=10,rows=6):
  for j in range(rows):
   for i in range(seg):
    def v(a,b):
     phi=-math.pi/2+a*math.pi/rows;t=b*2*math.pi/seg
     return (c[0]+r[0]*math.cos(phi)*math.cos(t),c[1]+r[1]*math.cos(phi)*math.sin(t),c[2]+r[2]*math.sin(phi))
    quad(mat,v(j,i),v(j,i+1),v(j+1,i+1),v(j+1,i))
 def train(kind,x,start,cars):
  upper='train_orange' if kind=='1900' else 'train_green_light';lower='train_red' if kind=='1900' else 'train_green_dark'
  length=18.4;pitch=18.9
  for car in range(cars):
   cy=start-car*pitch-length/2
   # End lower/upper body; side windows are independent glazed panels.
   passage=kind=='1900' and car==1
   if passage:
    box(lower,x,cy,-.08,2.7,length,.36)
    box('train_metal',x,cy,.08,2.57,length-.15,.04)
    for side in [-1,1]:
     for a,b in [(-length/2,5.95),(7.05,length/2)]:
      box(lower,x+side*1.3175,cy+(a+b)/2,.59,.065,b-a,.98)
      box(upper,x+side*1.3175,cy+(a+b)/2,1.85,.065,b-a,1.5)
     box(upper,x+side*1.3175,cy+6.5,2.40,.065,1.1,.40)
     box('train_red',x+side*.95,cy-1,.36,.57,10,.44)
     box('train_red',x+side*1.19,cy-1,.74,.14,10,.37)
    for end in [-1,1]:
     box(lower,x,cy+end*(length/2-.04),.42,2.7,.08,1.35)
     box(upper,x,cy+end*(length/2-.04),1.85,2.7,.08,1.5)
   else:
    box(lower,x,cy,.42,2.7,length,1.35);box(upper,x,cy,1.85,2.7,length,1.5)
   # Curved roof in longitudinal strips.
   for k in range(12):
    a=math.pi*k/12;b=math.pi*(k+1)/12
    quad('train_roof',(x+1.37*math.cos(a),cy-length/2,2.6+.54*math.sin(a)),(x+1.37*math.cos(b),cy-length/2,2.6+.54*math.sin(b)),(x+1.37*math.cos(b),cy+length/2,2.6+.54*math.sin(b)),(x+1.37*math.cos(a),cy+length/2,2.6+.54*math.sin(a)))
   box('train_under',x,cy,-.30,2.45,16,.3)
   for by in [cy-5.8,cy+5.8]:
    box('train_under',x,by,-.62,2.0,2.8,.45)
    for wy in [by-.88,by+.88]:
     cylinder('train_under',(x,wy,-.65),0,.4,1.85)
     for side in [-1,1]:cylinder('train_metal',(x+side*.94,wy,-.65),0,.31,.04)
   for side in [-1,1]:
    xx=x+side*1.36
    doors=[-6.5,6.5] if kind=='1900' else [-6.5,0,6.5]
    for d in doors:
     if passage and d==6.5:
      for dy in [-.84,.84]:
       box(upper,xx+side*.045,cy+d+dy,1.13,.045,.55,2.06)
       box('train_glass',xx+side*.072,cy+d+dy,1.8,.018,.43,.75)
      box('train_metal',xx,cy+d,.10,.07,1.10,.055)
      continue
     box(upper,xx,cy+d,1.12,.045,1.1,2.08)
     box('train_metal',xx+side*.028,cy+d,1.15,.025,.035,2.12)
     for dy in [-.27,.27]:box('train_glass',xx+side*.03,cy+d+dy,1.8,.02,.44,.75)
     box('train_metal',xx+side*.02,cy+d,.10,.035,1.10,.055)
    for dy in [-8,-4.9,-3.5,-2.1,-.7,.7,2.1,3.5,4.9,8]:
     if kind=='2200' and abs(dy)<1.0:continue
     box('train_metal',xx,cy+dy,1.79,.035,1.14,1.04)
     box('train_glass',xx+side*.025,cy+dy,1.8,.02,1.04,.94)
     if kind=='1900':box('train_metal',xx+side*.04,cy+dy,1.7,.02,1.04,.025)
   for end in [-1,1]:
    yy=cy+end*(length/2+.018)
    for dx in [-.88,.88]:
     box('train_metal',x+dx,yy,1.89,.73,.035,1.03);box('train_glass',x+dx,yy+end*.03,1.9,.65,.018,.93)
    box('train_metal',x,yy,1.39,.67,.04,2.05)
    box(upper,x,yy+end*.03,1.39,.59,.035,1.97)
    box('train_glass',x,yy+end*.055,1.88,.49,.025,.85)
    box(lower,x,yy+end*.055,.59,.59,.025,.39)
    if car in [0,cars-1]:
     lights=[0] if kind=='1900' else [-.94,.94]
     for dx in lights:
      cylinder('train_metal',(x+dx,yy+end*.06,2.52 if kind=='2200' else 2.9),1,.15,.15)
      cylinder('train_lamp',(x+dx,yy+end*.15,2.52 if kind=='2200' else 2.9),1,.10,.025)
     for dx in [-.94,.94]:cylinder('train_red',(x+dx,yy+end*.05,.71),1,.09,.06)
     if kind=='1900':
      # Approximate dove silhouette rather than a copied photograph.
      quad('train_white',(x-.58,yy+end*.10,.85),(x-.20,yy+end*.10,.40),(x+.20,yy+end*.10,.40),(x+.58,yy+end*.10,.85))
      cylinder('train_white',(x,yy+end*.10,.73),1,.14,.03)
     box('train_under',x,yy+end*.25,-.1,.28,.5,.2)
    else:box('train_under',x,yy+end*.07,1.4,.65,.18,2.1)
   for dy in [-5,-2.5,0,2.5,5]:box('train_roof',x,cy+dy,3.16,.55,.75,.22)
   if car%2==0:
    py=cy+4
    box('train_under',x,py,3.28,.75,1.3,.13)
    for side in [-1,1]:
     sx=x+side*.32
     beam('train_metal',(sx,py-.6,3.4),(sx,py,4.4),.025);beam('train_metal',(sx,py,4.4),(sx,py+.6,5.35),.025)
     beam('train_metal',(sx,py+.6,3.4),(sx,py,4.4),.025);beam('train_metal',(sx,py,4.4),(sx,py-.6,5.35),.025)
    box('train_metal',x,py,5.4,1.4,.13,.055)
  # Documentary model labels identify type, not an asserted exact consist/car number.
  label(kind+'系',x,start+.08,1.15,.20)
 train('1900',-26.7,-5,6)
 train('2200',-34.8,-5,6)
 return cylinder,ellipsoid

def passenger_positions():
 positions=[(-48,-10),(-48,-28),(-48,-52),(-48,-88),(-39.2,-16),(-39.2,-22),(-39.2,-43),(-39.2,-68),(-39.2,-97),(-30.6,-12),(-30.6,-25),(-30.6,-37),(-30.6,-59),(-30.6,-82),(-22.8,-16),(-22.8,-30),(-22.8,-46),(-22.8,-69),(23,-22),(23,-40),(30,-27),(30,-48),(-5,-2),(4,-2)]
 # Keep fictional passengers away from canopy posts, benches and the crossing stairs.
 return [({-39.2:-38.55,-30.6:-30.05,-22.8:-23.4}.get(x,x),-26 if (x,y)==(-22.8,-30) else y) for x,y in positions]

def people(api,ellipsoid):
 box,beam,tri,quad,label,groups,COLORS=api
 positions=passenger_positions()
 for idx,(x,y) in enumerate(positions):
  skin='person_skin';cloth=['person_suit','person_shirt','person_dress','person_brown'][idx%4]
  height=[1.64,1.73,1.58,1.69][idx%4];sc=height/1.7
  z=.005*sc  # Shoe bottoms touch the platform surface at local z=0.
  def p(a,b,c):return (x+a*sc,y+b*sc,z+c*sc)
  def limb(mat,a,b,r):beam(mat,p(*a),p(*b),r*sc)
  # Rounded torso/head and articulated arms/legs, no photograph of a real person.
  ellipsoid(cloth,p(0,0,1.12),(.21*sc,.13*sc,.34*sc))
  ellipsoid(skin,p(0,0,1.55),(.115*sc,.105*sc,.145*sc))
  ellipsoid('person_hair',p(0,.025,1.65),(.12*sc,.10*sc,.055*sc))
  box('person_shoe',*p(-.105,-.045,.04),.13*sc,.26*sc,.09*sc);box('person_shoe',*p(.105,.035,.04),.13*sc,.26*sc,.09*sc)
  for side in [-1,1]:
   knee=(side*.10,side*.055,.43)
   limb('person_suit',(side*.10,0,.89),knee,.068);limb('person_suit',knee,(side*.105,side*.04,.10),.055)
   elbow=(side*.27,(-.05 if idx%3 else .05),1.04)
   limb(cloth,(side*.19,0,1.32),elbow,.059);limb(cloth,elbow,(side*.23,-.07,.83),.045)
   ellipsoid(skin,p(side*.23,-.07,.80),(.05*sc,.045*sc,.068*sc))
  if idx%4==2:
   # Knee-length skirt silhouette.
   for i in range(12):
    a=i*math.pi/6;b=(i+1)*math.pi/6
    quad(cloth,p(.18*math.cos(a),.13*math.sin(a),.99),p(.18*math.cos(b),.13*math.sin(b),.99),p(.27*math.cos(b),.20*math.sin(b),.53),p(.27*math.cos(a),.20*math.sin(a),.53))
  elif idx%4==0:
   box('person_shirt',*p(0,-.126,1.32),.10*sc,.016*sc,.18*sc)
   box('person_brown',*p(0,-.14,1.2),.035*sc,.02*sc,.30*sc)
   if idx%8==0:
    ellipsoid('person_brown',p(0,0,1.67),(.18*sc,.16*sc,.025*sc));ellipsoid('person_brown',p(0,0,1.72),(.115*sc,.10*sc,.065*sc))
  if idx%3==0:box('person_bag',*p(.26,-.04,.56),.18*sc,.14*sc,.25*sc)
 return len(positions)
