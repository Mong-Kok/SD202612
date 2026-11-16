"""Water, open bridge decks and period fittings; unmeasured dimensions stay explicit."""
import math

def add_details(api):
 box,beam,quad,label,region,components,track=api
 def evidence(name,source,assumption,**extra):
  components.append(dict(name=name,evidence=source,confidence=assumption,**extra))
 def fence(a,b,z=.72,height=1.2):
  length=math.dist(a,b);steps=max(1,math.ceil(length/.35))
  for i in range(steps+1):
   x=a[0]+(b[0]-a[0])*i/steps;y=a[1]+(b[1]-a[1])*i/steps
   beam('frame',(x,y,z-height/2),(x,y,z+height/2),.019)
  for zz in [z-height/2,z+height/2]:beam('frame',(*a,zz),(*b,zz),.038)
 def lattice(x,y,h=3.7):
  for dx in [-.15,.15]:box('steel',x+dx,y,h/2,.055,.13,h)
  for i in range(int(h/.45)):
   beam('steel',(x-.15,y,i*.45),(x+.15,y,(i+1)*.45),.025)
   beam('steel',(x+.15,y,i*.45),(x-.15,y,(i+1)*.45),.025)

 # The river-side slab has no ground box beneath it. The bank slopes away westward.
 region('river')
 quad('stone',(-45,18,-.5),(-45,-175,-.5),(-47,-175,-4.5),(-47,18,-4.5))
 quad('gravel',(-47,18,-4.5),(-47,-175,-4.5),(-59,-175,-5.6),(-59,18,-5.6))
 quad('water',(-112,18,-5.6),(-112,-175,-5.6),(-59,-175,-5.6),(-59,18,-5.6))
 for yy in range(-173,18,8):
  quad('foam',(-91,yy,-5.585),(-86,yy-.1,-5.585),(-86,yy-.23,-5.585),(-91,yy-.12,-5.585))
 evidence('鴨川・東岸の傾斜護岸','1967 orthophoto; Sanjo1979; KyotoLove1981 river photograph',
          '流路・護岸形態は照合。河床・水位・幅・勾配は推定。',boundsEN=[-112,-175,-45,18],waterZ=-5.6)
 region('riverdeck')
 box('column',-49.58,-61.5,-.45,.12,153,.9)
 for yy in range(-135,15,6):
  box('column',-49.35,yy,-2.46,.28,.36,4.44)
  box('column',-49.35,yy,-4.80,.70,.85,.24)
  box('column',-47.65,yy,-.46,3.75,.32,.44)
  beam('column',(-49.35,yy,-1.16),(-48.53,yy,-.65),.14)
  box('column',-49.35,yy,-.88,.66,.44,.28)
  # Landward buttresses follow the retaining wall rather than floating over water.
  beam('stone',(-46.0,yy,-.65),(-49.0,yy,-3.9),.16)
 fence((-49.57,-138),(-49.57,15),.66,1.22)
 box('column',-49.57,-61.5,.18,.13,153,.36)
 evidence('４番線：堤防から張り出す床と支持柱','Sanjo1979; KyotoLove1981 river photograph; 1967 orthophoto',
          '後年写真の連続した柱・梁・基礎・手すりを1967年へ推定適用。断面・6m間隔・張出量は未実測。',
          boundsEN=[-49.7,-138,-45.1,15],floorZ=0,foundationZ=-4.92)
 for yy in [10,-20,-50,-80,-110,-140]:box('steel',-49.8,yy,-.16,.75,.55,.16)

 region('canal')
 for x in [-20.3,-5.7]:box('stone',x,-83.5,-2.07,.60,183,3.86)
 quad('water',(-20,8,-3.3),(-20,-126,-3.3),(-6,-126,-3.3),(-6,8,-3.3))
 quad('water',(-20,-126,-3.85),(-20,-175,-3.85),(-6,-175,-3.85),(-6,-126,-3.85))
 box('stone',-13,-126.15,-3.8,14,.45,.7)
 quad('foam',(-20,-126,-3.28),(-20,-126.4,-3.83),(-6,-126.4,-3.83),(-6,-126,-3.28))
 for yy in range(-170,8,6):
  zz=-3.285 if yy>-126 else -3.835
  for xx in [-17.6,-12.8,-8.1]:
   quad('foam',(xx,yy,zz),(xx+.18,yy,zz),(xx+.3,yy-1.8,zz),(xx+.12,yy-1.8,zz))
 # The official photograph confirms canal control structures, not these dimensions.
 for x in [-19.4,-13,-6.6]:
  box('stone',x,-127,-2.3,.8,3.2,2.9)
 for x in [-16.2,-9.8]:box('wood',x,-126.6,-2.3,5.5,.2,2.8)
 beam('steel',(-20,-127,-.75),(-6,-127,-.75),.10)
 evidence('駅構内の疏水・堰','京阪公式・keihan-image07b; KyotoLove回想; 1967 orthophoto',
          '疏水が構内を南北に流れ、制水構造があることは資料で確認。流路幅14m・床下3.3m・堰位置と落差は推定。',
          boundsEN=[-20,-175,-6,8],waterZ=-3.3)

 # Diagonal platform 1 uses separate slab panels; there is no solid slab behind gaps.
 region('bridge1')
 start=(-7,-37);end=(-24,-113);length=math.dist(start,end)
 vx=(end[0]-start[0])/length;vy=(end[1]-start[1])/length;ux=-vy;uy=vx
 def p(u,s,z):return (start[0]+ux*u+vx*s,start[1]+uy*u+vy*s,z)
 def panel(mat,u0,u1,s0,s1,z0,z1):
  vs=[p(u0,s0,z0),p(u1,s0,z0),p(u1,s1,z0),p(u0,s1,z0)]
  top=[p(u0,s0,z1),p(u1,s0,z1),p(u1,s1,z1),p(u0,s1,z1)]
  quad(mat,*reversed(vs));quad(mat,*top)
  for i in range(4):quad(mat,vs[i],vs[(i+1)%4],top[(i+1)%4],top[i])
 pitch=.5;gap=.04;panel_count=int(length/pitch)
 for i in range(panel_count):panel('platform',1.8,5.0,i*pitch,i*pitch+pitch-gap,-.18,0)
 for u in [2.05,4.75]:
  panel('steel',u-.075,u+.075,0,length,-.82,-.18)
  panel('steel',u-.19,u+.19,0,length,-.82,-.74)
 for u in [-1.12,1.12]:
  panel('steel',u-.075,u+.075,0,length,-2.045,-1.255)
  panel('steel',u-.23,u+.23,0,length,-2.045,-1.945)
  panel('steel',u-.20,u+.20,0,length,-1.335,-1.255)
 for ss in range(0,int(length),3):
  beam('steel',p(-1.4,ss,-1.98),p(5.25,ss,-1.98),.095)
  beam('steel',p(-1.1,ss,-2.05),p(4.8,ss+2.9,-2.05),.028)
  for uu in [-1.12,1.12,2.05,4.75]:
   for zz in [-1.85,-1.60,-1.39]:
    box('train_metal',*p(uu,ss,zz),.055,.055,.055)
 for ss in [0,length]:
  beam('stone',p(-1.6,ss,-2.15),p(5.4,ss,-2.15),.45)
  for uu in [-1.12,4.75]:beam('stone',p(uu,ss,-3.8),p(uu,ss,-2.1),.3)
 # Thin railings and narrow canopy do not close the floor openings.
 for i in range(int(length/.7)+1):beam('frame',p(5,i*.7,0),p(5,i*.7,1.2),.019)
 for zz in [.14,1.2]:beam('frame',p(5,0,zz),p(5,length,zz),.036)
 for ss in range(3,int(length),8):
  beam('steel',p(3.4,ss,0),p(3.4,ss,3.5),.065)
  beam('steel',p(1.4,ss,3.2),p(5.35,ss,3.2),.055)
  for side in [1.4,5.35]:beam('steel',p(3.4,ss,2.35),p(side,ss,3.2),.045)
  beam('white',p(3.5,ss-.65,3.08),p(3.5,ss+.65,3.08),.035)
 quad('roof',p(1.4,0,3.2),p(3.4,0,3.6),p(3.4,length,3.6),p(1.4,length,3.2))
 quad('roof',p(3.4,0,3.6),p(5.35,0,3.2),p(5.35,length,3.2),p(3.4,length,3.6))
 label('１　宇治方面',*p(3.4,3,2.1),.48)
 # A short concourse link touches the north end without covering the canal at midspan.
 panel('platform',1.8,12,0,2,-.25,0)
 # The 1969 connection-removal date is established, but its exact route is not.
 evidence('１番線：疏水に斜めに架かる鉄橋と床の実開口','KyotoLove回想; 1960社史図掲載記事; 1967 orthophoto; 京阪公式連絡線撤去1969年',
          '鉄橋・斜め配置・床の隙間の存在を参照。桁断面、床板材、40mm隙間・500mm間隔、屋根は推定。京津線連絡線の正確な経路は未再現。',
          floorZ=0,panelGapMetres=gap,panelPitchMetres=pitch,panelCount=panel_count,
          trackEndpoints=[start,end],platformOffsets=[1.8,5],openDeck=True)

 region('crossing')
 # Two rail flangeways remain open in the timber crossing deck.
 x0=-26.7
 intervals=[(-33.275,x0-.78),(x0-.66,x0+.66),(x0+.78,-20.375)]
 for a,b in intervals:box('wood',(a+b)/2,-31,-1.08,b-a,3.2,.20)
 for x in [-30.75,-22.8]:
  for sign in [-1,1]:
   for i in range(6):
    yy=-31+sign*(.45+i*.23);height=(i+1)/6
    box('platform',x,yy,-1+height/2,2.4,.23,height)
   box('steel',x,-31+sign*2.08,1.45,2.8,.08,.07)
  # Sliding fence is parked aside; no fictitious modern lifting boom.
  fence((x-.95,-28.15),(x+.95,-28.15),.62,1.1)
  for yy in [-29,-33]:box('steel',x+1.5,yy,1.4,.09,.09,2.8)
 box('roof',-26.7,-31,3.50,12.2,4.5,.14)
 box('sign',-26.7,-28.68,2.53,5.6,.14,.8);label('構内踏切',-26.7,-28.57,2.24,.42)
 evidence('２・３番線への屋根付き構内踏切','KyotoLove1987写真と回想; tetsudotabi1987踏切写真と1971回想図',
          '歩行者踏切と横から出る柵の存在を参照。1967年の正確な位置・階段・柵機構は未確認。',
          gapNorthSouth=[-33,-29],deckZ=-.98,operatingSimulation=False)

 region('')
 # Facade fluting, angular decorative grilles, drains and gutters from the 1967 photo.
 for x in [i*.28 for i in range(-14,15)]:box('frame',x,.35,5.29,.034,.09,2.10)
 for x in [-12.15,12.15]:
  for dx in [-.43,0,.43]:
   beam('frame',(x+dx,.29,4.45),(x+dx+.22,.29,5.15),.025)
   beam('frame',(x+dx+.22,.29,5.15),(x+dx,.29,5.87),.025)
 for x in [-13.9,13.9]:beam('frame',(x,.6,6.9),(x,.6,.12),.06)
 beam('frame',(-14.6,.7,7.02),(14.6,.7,7.02),.055)
 for xx in [-9.7,9.7]:
  box('sign',xx,1.5,2.66,5.8,.10,.66)
  label('大阪 淀屋橋方面' if xx>0 else 'びわ湖・宇治方面',xx,1.57,2.4,.30)
 # Open ticket windows, counters, non-electronic manual gates and a timetable board.
 for x in [-10,10]:
  box('wood',x,-5.30,1.0,4.5,.45,.10)
  for dx in [-1.6,0,1.6]:box('frame',x+dx,-5.38,1.8,.04,.12,.95)
  box('sign',x,-5.31,2.60,4.3,.06,.45)
  label('定期券うりば' if x<0 else 'きっぷうりば',x,-5.25,2.41,.32)
 for x in [-5,-2,1,4]:
  box('frame',x,-13.96,.60,.6,.08,1.15)
  box('wood',x,-14.5,1.16,.7,1.25,.06)
  beam('steel',(x+.5,-14.0,.2),(x+.5,-14.0,1.1),.04)
 for text,x in [('改札口',-4),('出口',5)]:
  box('sign',x,-13.9,2.5,3,.08,.65);label(text,x,-13.8,2.25,.42)
 box('white',0,-21.65,3.4,11,.04,1.65)
 for x in range(-5,6):box('sign',x,-21.60,3.4,.028,.03,1.60)
 for zz in [2.7,3.1,3.5,3.9]:box('sign',0,-21.60,zz,11,.03,.024)
 label('発車時刻表',0,-21.56,3.94,.36)
 for x in [-8,0,8]:box('white',x,-8,3.15,.10,3.0,.075)
 evidence('出札・有人改札・案内板・正面の装飾','DRFC1967 FH000011/FH000012/FH000013',
          '装飾・窓口・手動改札の形式を参照。内部配置・時刻表の細字・広告図案は未復元。')
 # Concourse stalls are period-inspired, not a measured merchant-by-merchant plan.
 for yy,text in [(-30,'売店'),(-37,'のれん街'),(-44,'味のれん')]:
  box('plaster',9.5,yy,1.3,5.2,4.8,2.6)
  box('window',9.5,yy+2.44,1.7,4.5,.06,1.25)
  box('wood',9.5,yy+2.6,.94,4.7,.70,.12)
  box('sign',9.5,yy+2.5,2.8,5.4,.09,.55);label(text,9.5,yy+2.58,2.57,.36)
  for xx in [7.5,8.3,9.1,9.9,10.7,11.5]:box('sign',xx,yy+2.60,2.2,.62,.04,.56)
  for xx in [7.7,8.5,9.3,10.1,10.9]:box('white',xx,yy+2.6,1.10,.46,.38,.23)
 for yy in [-24,-34,-44]:
  lattice(4,yy,4.4);beam('steel',(4,yy,3.2),(8,yy,4.4),.05)
  box('white',5,yy,4.24,.08,2.2,.08)
 box('sign',2,-24,3.5,8,.13,1.1)
 label('１ 宇治　２ 特急　３ 急行　４ 普通',2,-23.91,3.20,.30)
 evidence('改札内の売店・食堂街・行先案内','KyotoLove構内写真（年代不明）; tetsudotabiのれん街・味のれん記述',
          '構内店舗・名称・案内板の形式を参照。1967年の店数・位置・店別意匠・営業状況は未確定。')
 for x,y in [(-22.8,-55),(-39.2,-58)]:
  box('stone',x,y,.17,1.1,1.3,.34);box('gravel',x,y,.36,.95,1.15,.045)
  beam('wood',(x,y,.38),(x,y,1.28),.055)
  for angle in range(0,360,45):
   a=math.radians(angle)
   quad('foliage',(x,y,1.4),(x+.11,y+.06,1.1),(x+.66*math.cos(a),y+.66*math.sin(a),1.75),(x-.06,y-.10,1.25))
 # South entrance: lattice support and the small shop visible on its left.
 lattice(27,-71,3.55)
 box('plaster',9,-69.5,1.1,3.8,4,2.2)
 quad('roof',(7,-72,2.3),(11,-72,2.3),(11,-70,2.85),(7,-70,2.85))
 box('wood',9,-72.2,.9,3.7,.65,.1)
 for xx in [7.6,8.3,9,9.7,10.4]:box('white',xx,-72.2,1.13,.5,.4,.38)
 box('sign',19,-72.12,4.42,10,.10,.58);label('京阪電車　三条駅南口',19,-72.22,4.18,.39,'south')
 evidence('南口の格子柱・売店の庇・商品台','DRFC1967 FH000016',
          '写真に見える形式を参照。商品・小寸法・奥行は推定。')
 region('')
