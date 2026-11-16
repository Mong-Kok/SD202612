#!/usr/bin/env python3
"""Evidence-led, explicitly approximate 1967 Sanjo station reconstruction.
Coordinates: local east,north,up metres. Original photographs are references only.
"""
from pathlib import Path
import math,json,struct,hashlib,base64
from sanjo_materials import PALETTE,make_textures
from sanjo_figures import populate,people
from sanjo_detail import add_details
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'Resources/Sanjo1967';OUT.mkdir(parents=True,exist_ok=True)
COLORS={k:[c/255 for c in rgb] for k,rgb in PALETTE.items()}
groups={};labels=[];components=[];region='';vertex_maps={}
def set_region(value):
 global region
 region=value
def tri(mat,a,b,c):
 key=region+'__'+mat if region else mat
 g=groups.setdefault(key,{'name':key,'color':COLORS[mat],'vertices':[],'indices':[],'uv':[],'texture':mat})
 ab=[b[j]-a[j] for j in range(3)];ac=[c[j]-a[j] for j in range(3)]
 n=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
 norm=math.sqrt(sum(t*t for t in n))
 if norm<1e-10:return
 normal=tuple(round(t/norm,6) for t in n)
 drop=max(range(3),key=lambda j:abs(n[j]));axes=[j for j in range(3) if j!=drop]
 lookup=vertex_maps.setdefault(key,{})
 for v in (a,b,c):
  xyz=tuple(round(t,4) for t in v);uv=tuple(round(v[j]/2,4) for j in axes)
  corner=(xyz,uv,normal)
  if corner not in lookup:
   lookup[corner]=len(g['vertices'])//3;g['vertices']+=xyz;g['uv']+=uv
  g['indices'].append(lookup[corner])
def quad(mat,a,b,c,d):tri(mat,a,b,c);tri(mat,a,c,d)
def box(mat,x,y,z,w,d,h):
 a=(x-w/2,y-d/2,z-h/2);b=(x+w/2,y-d/2,z-h/2);c=(x+w/2,y+d/2,z-h/2);dd=(x-w/2,y+d/2,z-h/2)
 e=(a[0],a[1],z+h/2);f=(b[0],b[1],z+h/2);g=(c[0],c[1],z+h/2);hh=(dd[0],dd[1],z+h/2)
 for vs in [(a,dd,c,b),(e,f,g,hh),(a,b,f,e),(b,c,g,f),(c,dd,hh,g),(dd,a,e,hh)]:quad(mat,*vs)
def beam(mat,a,b,r=.08):
 v=[b[i]-a[i] for i in range(3)];ln=math.sqrt(sum(t*t for t in v));v=[t/ln for t in v]
 q=[-v[1],v[0],0] if abs(v[2])<.9 else [1,0,0];n=math.sqrt(sum(t*t for t in q));q=[t/n*r for t in q]
 w=[v[1]*q[2]-v[2]*q[1],v[2]*q[0]-v[0]*q[2],v[0]*q[1]-v[1]*q[0]]
 pa=[tuple(a[j]+q[j]*c+w[j]*s for j in range(3)) for c,s in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 pb=[tuple(p[j]+b[j]-a[j] for j in range(3)) for p in pa]
 for i in range(4):quad(mat,pa[i],pa[(i+1)%4],pb[(i+1)%4],pb[i])
 quad(mat,*reversed(pa));quad(mat,*pb)
def label(text,x,y,z,size=1.0,face='north'):
 labels.append(dict(text=text,position=[x,y,z],size=size,facing=face))
def hiproof(x,y,w,d,eave,ridge):
 a=(x-w/2,y-d/2,eave);b=(x+w/2,y-d/2,eave);c=(x+w/2,y+d/2,eave);dd=(x-w/2,y+d/2,eave)
 r1=(x-w/2+min(w,d)*.35,y,ridge);r2=(x+w/2-min(w,d)*.35,y,ridge)
 tri('roof_tile',dd,a,r1);tri('roof_tile',b,c,r2);quad('roof_tile',a,b,r2,r1);quad('roof_tile',c,dd,r1,r2)
 for i in range(1,int(w)):
  xx=x-w/2+i
  if r1[0]<=xx<=r2[0]:
   beam('steel',(xx,y-d/2,eave+.02),(xx,y,ridge+.02),.022);beam('steel',(xx,y,ridge+.02),(xx,y+d/2,eave+.02),.022)
def canopy(name,x,yn,ys,width=3.6,raised=False,split=False):
 spans=[(ys,-33),(-29,yn)] if split else [(ys,yn)]
 for a,b in spans:
  box('platform',x,(a+b)/2,-.12 if raised else -.42,width,b-a,.24 if raised else .84)
  for side in [-1,1]:box('edge',x+side*(width/2-.15),(a+b)/2,.02,.28,b-a,.08)
 for yy in range(int(ys+4),int(yn),8):
  box('steel',x,yy,1.76,.18,.18,3.5)
  box('column',x,yy,.8,.185,.185,1.6)
  for sign in [-1,1]:beam('steel',(x,yy,2.26),(x+sign*width/2,yy,3.31),.055)
  beam('steel',(x-width/2,yy,3.31),(x+width/2,yy,3.31),.06)
  for dz in [1.9,2.45,3.0]:beam('steel',(x-.13,yy,dz),(x+.13,yy,dz+.43),.023)
  box('white',x+.5,yy,3.18,.09,1.6,.07)
  if not split or not -34<yy+2<-28:
   box('wood',x+width*.25,yy+2,.48,.55,1.6,.08)
   for yy2 in [yy+1.4,yy+2.6]:box('steel',x+width*.25,yy2,.23,.40,.10,.46)
 for s in [-1,1]:
  quad('roof',(x,ys,3.64),(x+s*(width/2+.3),ys,3.32),(x+s*(width/2+.3),yn,3.32),(x,yn,3.64))
 box('frame',x-width/2-.3,(yn+ys)/2,3.28,.12,yn-ys,.22)
 box('frame',x+width/2+.3,(yn+ys)/2,3.28,.12,yn-ys,.22)
 label(name,x,yn-.5,2.26,.8)
 components.append({'name':name+'番ホーム','evidence':'aerial footprint + 1967 platform photograph','confidence':'approximate','boundsEN':[x-width/2,ys,x+width/2,yn]})
def track(points):
 for a,b in zip(points[:-1],points[1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);nx=-dy/ln;ny=dx/ln
  for i in range(int(ln/1.0)+1):
   t=i/max(1,int(ln));cx=a[0]+dx*t;cy=a[1]+dy*t
   beam('sleeper',(cx-nx*1.15,cy-ny*1.15,-1.17),(cx+nx*1.15,cy+ny*1.15,-1.17),.085)
  for side in [-1,1]:
   beam('rail',(a[0]+nx*.7175*side,a[1]+ny*.7175*side,-1.05),(b[0]+nx*.7175*side,b[1]+ny*.7175*side,-1.05),.045)
# North facade anchor: traced aerial pixel (480,420), main hall runs south.
box('platform',0,-11.5,-.15,28,23,.30)
# Open facade, central columns and upper wall, rather than a solid entrance block.
box('plaster',0,-22,5.4,27,.45,3.6)
for x in [-13,-6.5,6.5,13]:box('plaster',x,-22,1.8,.60,.45,3.6)
for x in [-13.3,13.3]:box('plaster',x,-11.5,3.6,.5,23,7.2)
for x in [-13,-7.6,-2.7,2.7,7.6,13]:box('plaster',x,-.4,1.65,.55,.8,3.3)
box('plaster',0,-.4,3.5,27,.8,.75)
box('plaster',0,-.4,6.65,27,.8,1.1)
# Upper facade windows, mullions and signboard.
for x in [-8.8,8.8]:
 box('window',x,.06,5.13,6.7,.10,2.2)
 for dx in [-3.3,-2.2,-1.1,0,1.1,2.2,3.3]:box('frame',x+dx,.15,5.13,.06,.12,2.25)
 for z in [4.05,4.6,5.15,5.7,6.25]:box('frame',x,.15,z,6.7,.12,.06)
box('sign',0,.24,5.25,8.0,.18,2.1);label('京阪電車',0,.35,5.76,.40);label('三 条 駅',0,.36,4.55,1.0)
# Full-width entrance canopy and neutral fascia (advert artwork not copied).
box('roof',0,1.2,3.28,29,3.8,.20);box('plaster',0,3.1,3.62,29,.2,.78)
label('大阪・淀屋橋  ／  宇治  ／  びわ湖方面',0,3.23,3.43,.42)
# Clock and decorative grilles visible in north photo.
box('frame',0,.23,6.86,1.42,.18,1.42);box('white',0,.34,6.86,1.22,.03,1.22)
for i in range(12):
 a=i*math.pi/6;beam('sign',(.45*math.sin(a),.37,6.86+.45*math.cos(a)),(.53*math.sin(a),.37,6.86+.53*math.cos(a)),.018)
beam('sign',(0,.40,6.86),(.38,.40,6.86),.025);beam('sign',(0,.40,6.86),(-.26,.40,6.99),.03)
# Raised hipped roof and lower surrounding eaves.
hiproof(0,-11.3,29.0,24.5,7.12,8.2)
box('plaster',0,-11.3,7.80,20,14,.9);hiproof(0,-11.3,21.3,15.3,8.26,9.40)
# Window grille ends reconstructed from front photograph.
for x in [-12.1,12.1]:
 for dx in [-.25,0,.25]:box('frame',x+dx,.22,5.1,.035,.05,1.1)
 for z in [4.85,5.1,5.35]:box('frame',x,.22,z,.9,.05,.035)
# Ticket booths and gates; placements schematic, no copied ad textures.
for x in [-10,10]:
 box('plaster',x,-7,1.35,4.8,3,2.7);box('window',x,-5.45,1.85,4.2,.04,1.05)
for x in [-5,-2,1,4]:box('steel',x,-15,.6,.7,1.8,1.2)
# Covered circulation from north hall toward riverside platforms and Keishin area.
for x,y,w,d in [(-31,1,34,3),(4,-38,8,31),(13,-48,4,37)]:
 box('platform',x,y,-.15,w,d,.3);box('roof',x,y,4.45,w,d,.22)
 for xx,yy in [(x-w/2+.3,y-d/2+.3),(x+w/2-.3,y+d/2-.3)]:box('steel',xx,yy,2.25,.18,.18,4.5)
# Entrance forecourt and the road deck across the canal, inferred from aerial/photo.
box('platform',0,6,-.18,30,12,.36)
box('platform',-13,7,-.30,16,10,.60)
components.append(dict(name='北口前の歩道・疏水上の道路床',evidence='FH000011; 1967 orthophoto',confidence='外形・厚さ・通りとの接続は概略。疏水を北口直前で露出させない推定床。'))
# Track 4 is a raised river-side deck; track 2 platforms have a real crossing gap.
for name,x,yn,ys,w in [('4',-47.4,15,-138,4.4),('3',-39.25,8,-119,5.9),('2・3',-30.75,0,-119,5.05),('2',-22.8,0,-86,4.85)]:
 set_region('riverdeck' if name=='4' else '')
 canopy(name,x,yn,ys,w,raised=name=='4',split=x in [-30.75,-22.8])
set_region('')
for x in [-43.7,-34.8,-26.7]:
 track([(x,-3),(x,-133),(-38+(x+43.7)*.35,-180)])
 box('steel',x,-3.5,-.55,2,.25,.85)
# Diagonal track 1 over the former canal; connections are an approximate plan.
set_region('bridge1')
track([(-7,-37),(-24,-113),(-36,-155),(-37,-180)])
set_region('')
# Keishin platforms run from south terminal towards the bend into Sanjo-dori.
canopy('5',23,-15,-65,3.2);canopy('6',30,-13,-65,3.2)
for x in [26.5,33.5]:track([(x,-67),(x,-12),(x+2,13),(x+9,30),(x+27,36)])
# South entrance, broad fascia and shallow canopy from the 1967 photograph.
box('platform',19,-68,-.1,17,7,.2);box('roof',19,-68,3.6,18,8,.25)
for x in [11,16,23,27]:box('plaster',x,-71,1.8,.32,.4,3.6)
box('plaster',19,-72.1,3.8,18,.18,.65)
label('三 条 駅 南 口',19,-72.25,3.55,.7,'south')
# Posts, open truss gantries and contact wires (spacing estimated).
for yy in [10,-20,-50,-80,-110,-140]:
 for xx in [-50,-20]:
  box('steel',xx,yy,3.4,.22,.22,6.8)
  for z in range(1,6):beam('steel',(xx-.22,yy,z),(xx+.22,yy,z+.8),.035)
 beam('steel',(-50,yy,6.6),(-20,yy,6.6),.055)
 beam('steel',(-50,yy,7.2),(-20,yy,7.2),.045)
 for xx in range(-50,-20,3):beam('steel',(xx,yy,6.6),(xx+1.5,yy,7.2),.035);beam('steel',(xx+1.5,yy,7.2),(xx+3,yy,6.6),.035)
for x in [-43.7,-34.8,-26.7]:beam('steel',(x,10,5.5),(x,-138,5.5),.025)
add_details((box,beam,quad,label,set_region,components,track))
set_region('')
figure_api=(box,beam,tri,quad,label,groups,COLORS)
cylinder,ellipsoid=populate(figure_api)
components += [dict(name='北駅舎',evidence='FH000011 / 1967 orthophoto',confidence='outline traced; height, depth details estimated',boundsEN=[-14,-24,14,1]),dict(name='南口・京津線・架線',evidence='FH000016 / orthophoto / official history',confidence='approximate; no as-built drawing')]
model={'schema':'geofield-historic-model/1','id':'historic:keihan-sanjo-1967','title':'京阪三条駅・地上時代（1967年）','epoch':'1967年頃（昭和42年）','version':'2026-10-11.3','anchor':{'latitude':35.00877926694519,'longitude':135.77255932611365,'orthometricHeight':41.78,'geoidCorrection':37.4425,'ellipsoidHeight':79.2225},'activationRadiusMetres':500,'localAxes':'east,north,up; metres; origin at north facade centre','heightBasis':'Floor approximated by 2025 DEM1A JGD2024 height 41.78m; official geoid2024+Hrefconv 37.4425m; historical floor not surveyed','horizontalBasis':'1967 GSI orthophoto EPSG6674, reprojected to geographic coordinates; JGD2011/WGS84 epoch difference not corrected','uncertainty':'輪郭は航空写真から概略採寸。高さ・細部・配線は推定を含む。測量精度の復元ではありません。','appearance':'車両は1900系の旧1810系タイプと更新前2200系を参考にした各6両の配置例。正確な編成順・車番は未再現。1969年と地上末期のカラー写真を参考に屋根・柱・床・枕木の色と質感を推定。駅舎正面の1967年の色は未確認。テクスチャは独自生成で写真転載ではない。退色と撮影年代差があるため厳密な色再現ではない。','sources':[{'title':'京阪公式：2200系（1964年登場）','url':'https://www.keihan.co.jp/traffic/railfan/vehicle/2200.html'},{'title':'三条駅地上時代：カラー構内・仮改札口（ぎんがてつどう別館）','url':'https://jijiganko.web.fc2.com/keihansyowa02.html'},{'title':'1969年8月16日の三条ホーム：色退色の注意あり（さっしい）','url':'https://sassy.la.coocan.jp/archives/archives_s44-08a.html'},{'title':'1979年4月9日の川側ホーム（ありし日の駅舎たち）','url':'https://www.asahi-net.or.jp/~uk9o-tkzw/hseki01.html'},{'title':'1967年の駅舎・改札・ホーム・南口写真（無印不良品／DRFC-OB）','url':'https://drfc-ob.com/wp/archives/101442'},{'title':'京阪公式：三条駅の変遷と過去写真','url':'https://www.keihan.co.jp/recommend/mizunomichi/michiannai/04/'},{'title':'国土地理院：1967年京都のオルソ画像・地表モデル','url':'https://research-opendata.gsi.go.jp/tech_data/2026-002-G/2026-002-G-lp.html'},{'title':'国土地理院：最新1m標高原本','url':'https://service.gsi.go.jp/kiban/app/'}],'vehicles':{'types':['1900系・旧1810系タイプ','2200系・更新前'],'carsEach':6,'note':'1969年カラー写真を参考にした外形。各6両の配置例で、特定日の編成・車番・運用は未再現。停車展示。'},'components':components,'meshes':list(groups.values()),'labels':labels}
texture_bytes=make_textures()
model['version']='2026-10-12.1'
model['sources'][:0]=[
 {'title':'島本由紀：三条京阪・地上時代（回想、掲載写真1956・1973・1981・1987年など）','url':'https://kyotolove.kyoto/I0000301/'},
 {'title':'鉄道で行く旅：京阪三条駅付近の今昔・前編（1960年図、1971年頃回想図、1987年写真）','url':'https://ameblo.jp/tetsudotabi/entry-12518170672.html'}]
model['uncertainty']='1967年頃を対象とした資料ベースの推定復元。川側支持構造は1979・1981年写真も参照。疏水幅・水位・鉄橋断面・床の隙間寸法・店舗の配置は未実測。1980年代の仮駅舎は含めない。測量・施工図の精度を保証しない。'
model['waterways']={'canal':{'boundsEN':[-20,-175,-6,8],'waterHeightNorth':-3.3,'waterHeightSouth':-3.85,'weirNorth':-126,'assumed':True},'kamo':{'boundsEN':[-112,-175,-59,18],'waterHeight':-5.6,'assumed':True},'note':'流路の位置は航空写真との概略照合。水位、幅、落差、流量、季節は未確認。水面の動きはMac閲覧用の模式表現で物理シミュレーションではない。'}
model['xrInspection']={'platform4':'堤防から張り出した床・川側の柱・横梁・基礎・手すりを同一地理原点で保持。','platform1':'疏水に斜めに架かる鉄橋、支持桁と床板の間の実開口。全体を覆う不透明な地面は置かない。','historicalAccuracy':'橋桁形式・細部寸法と水位は推定。現地精度と実物遮蔽は未検証。'}
model['vehicles']['openPassage']={'type':'1900系・旧1810系タイプ','carIndex':1,'doorCentreNorth':-26.6,'floorZ':.1,'note':'左右の扉が開いた構造例。正確な1967年の運用・停車位置・車内設備は未確認。車両通り抜けの仕組みを示す模式表現。'}
model['platformClearances']={'track2East':.125,'track2West':.175,'track3East':.175,'track3West':.15,'track4West':.15,'note':'模型内の乗降隙間。実測値ではない。従来の0.8m前後の隙間を修正した推定寸法。'}
used_textures={g['texture'] for g in groups.values()}
model['textures']={k:base64.b64encode(v).decode() for k,v in texture_bytes.items() if k in used_textures}
model['textureBasis']='Original procedural sRGB PNG textures; 2 metre repeat; geometry 1967, material inference from 1969 and later color photos'
for k,v in texture_bytes.items():
 if k in used_textures:(OUT/(k+'.png')).write_bytes(v)
(OUT/'model.json').write_text(json.dumps(model,ensure_ascii=False,separators=(',',':')))
station_model=model
station_groups=groups
groups={};labels=[];vertex_maps={}
person_count=people((box,beam,tri,quad,label,groups,COLORS),ellipsoid)
person_model={**station_model,'id':'historic:keihan-sanjo-people-1967','title':'三条駅・当時の人々（推定）','appearance':'1967年の駅写真に見える服装を参考に独自生成した24人。特定の実在者・日時・混雑状況の再現ではありません。','uncertainty':'当時の服装を参考にした架空の人物模型。顔・服装・配置は推定。','components':[],'vehicles':None,'personCount':person_count,'meshes':list(groups.values()),'labels':labels,'textures':{k:base64.b64encode(texture_bytes[k]).decode() for k in groups}}
people_out=OUT.parent/'SanjoPeople1967';people_out.mkdir(exist_ok=True)
(people_out/'model.json').write_text(json.dumps(person_model,ensure_ascii=False,separators=(',',':')))
for k in groups:(people_out/(k+'.png')).write_bytes(texture_bytes[k])
model=station_model;groups=station_groups;labels=model['labels']
# Portable GLB geometry, local Y-up convention. Native app adds vector station labels.
def export_glb(model,destination):
 binary=bytearray();views=[];access=[];meshes=[];materials=[];images=[];textures=[]
 def acc(data,typ,comp,count,mins=None,maxs=None,target=34962):
  while len(binary)%4:binary.append(0)
  o=len(binary);binary.extend(data);views.append({'buffer':0,'byteOffset':o,'byteLength':len(data),'target':target});a={'bufferView':len(views)-1,'componentType':comp,'count':count,'type':typ}
  if mins is not None:a.update(min=mins,max=maxs)
  access.append(a);return len(access)-1
 for group in model['meshes']:
  v=group['vertices'];v2=[c for i in range(0,len(v),3) for c in (v[i],v[i+2],-v[i+1])];idx=group['indices']
  pi=acc(struct.pack('<'+'f'*len(v2),*v2),'VEC3',5126,len(v2)//3,[min(v2[k::3]) for k in range(3)],[max(v2[k::3]) for k in range(3)])
  ii=acc(struct.pack('<'+'I'*len(idx),*idx),'SCALAR',5125,len(idx),target=34963)
  uv=group['uv'];ti=acc(struct.pack('<'+'f'*len(uv),*uv),'VEC2',5126,len(uv)//2)
  while len(binary)%4:binary.append(0)
  image_data=texture_bytes[group['texture']];o=len(binary);binary.extend(image_data)
  views.append({'buffer':0,'byteOffset':o,'byteLength':len(image_data)})
  images.append({'bufferView':len(views)-1,'mimeType':'image/png'})
  textures.append({'source':len(images)-1,'sampler':0})
  materials.append({'name':group['name'],'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':len(textures)-1},'metallicFactor':0,'roughnessFactor':.85}})
  meshes.append({'name':group['name'],'primitives':[{'attributes':{'POSITION':pi,'TEXCOORD_0':ti},'indices':ii,'material':len(materials)-1}]})
 gltf={'asset':{'version':'2.0','generator':'GeoFieldAR evidence-led Sanjo1967 generator'},'scene':0,'scenes':[{'nodes':list(range(len(meshes)))}],'nodes':[{'mesh':i} for i in range(len(meshes))],'meshes':meshes,'materials':materials,'images':images,'textures':textures,'samplers':[{'wrapS':10497,'wrapT':10497,'magFilter':9729,'minFilter':9987}],'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':access,'extras':{'anchor':model['anchor'],'warning':model['uncertainty'],'nativeTextLabels':model['labels']}}
 j=json.dumps(gltf,separators=(',',':')).encode();j+=b' '*((-len(j))%4);binary+=b'\0'*((-len(binary))%4)
 destination.write_bytes(struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(binary))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(binary),b'BIN\0')+binary)
export_glb(station_model,OUT/'sanjo1967.glb')
export_glb(person_model,people_out/'people1967.glb')
print('station triangles',sum(len(g['indices'])//3 for g in station_model['meshes']),'people',person_count,'people triangles',sum(len(g['indices'])//3 for g in person_model['meshes']))
