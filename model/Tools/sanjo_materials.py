"""Original repeatable material textures inferred from reference photos, not photo crops.
RGB values are sRGB; 2m tile coordinates. Deterministic, stdlib-only PNG authoring.
"""
import math,random,zlib,struct,base64
PALETTE={'plaster':(178,168,145),'roof':(75,80,77),'roof_tile':(67,68,65),'steel':(65,71,63),'column':(188,187,171),'window':(43,66,69),'frame':(137,142,129),'platform':(88,85,78),'edge':(178,175,157),'rail':(119,83,57),'sleeper':(75,54,39),'sign':(38,67,67),'white':(230,224,204)}
PALETTE.update({'train_orange':(226,169,76),'train_red':(137,30,43),'train_green_light':(119,162,136),'train_green_dark':(31,74,65),'train_roof':(76,82,82),'train_under':(36,37,35),'train_metal':(141,149,148),'train_glass':(27,49,57),'train_lamp':(245,233,181),'train_white':(233,229,210),'person_skin':(190,148,115),'person_hair':(37,32,27),'person_suit':(51,62,70),'person_shirt':(216,211,190),'person_dress':(129,88,83),'person_brown':(110,86,60),'person_shoe':(39,34,29),'person_bag':(91,55,33)})
PALETTE.update({'water':(49,103,107),'foam':(183,209,200),'stone':(120,124,117),'gravel':(126,125,116),'wood':(111,83,55),'foliage':(69,102,62)})
def png(rgb,n=256):
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 rows=b''.join(b'\0'+rgb[y*n*3:(y+1)*n*3] for y in range(n))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')
def make_textures():
 textures={}
 for name,base in PALETTE.items():
  rng=random.Random('sanjo1967-'+name);raw=bytearray()
  for y in range(256):
   for x in range(256):
    grain=rng.gauss(0,2.2);pat=0
    if name=='roof':pat=8*math.cos(x*2*math.pi/8)+( -10 if y%128<2 else 0)+2*math.sin(y/15)
    elif name=='roof_tile':
     row=y//32;xx=(x+(row%2)*16)%32;yy=y%32
     pat=7*math.sin(xx*math.pi/32)-16*(xx<2)-18*(yy<3)+6*(yy>27)+3*math.sin(row*2.3+x//32*1.7)
    elif name=='plaster':pat=3*math.sin(x/29)*math.sin(y/47)+2*math.sin(y/6);grain*=.6
    elif name in ['steel','frame','column']:pat=2*math.sin(x/7)+2*math.sin(y/23);grain*=.6
    elif name=='platform':pat=3*math.sin(x/27)*math.sin(y/35);grain*=1.8
    elif name=='edge':pat=-19*(x%64<2)-3*(y%128<2);grain*=.8
    elif name=='sleeper':pat=8*math.sin(x/2.8+1.5*math.sin(y/35))+4*math.sin(x/1.1);grain*=1.2
    elif name=='rail':pat=5*math.sin(y/13)+7*math.sin(x/10);grain*=1.6
    elif name=='window':pat=7*math.sin((x+y*.2)/85);grain*=.2
    elif name=='water':pat=12*math.sin(y/5+2*math.sin(x/25))+6*math.sin(y/2+x/31);grain*=.4
    elif name=='foam':pat=12*math.sin(y/3+x/8);grain*=1.5
    elif name=='stone':pat=-22*(y%32<3 or (x+(y//32%2)*32)%64<3);grain*=2
    elif name=='gravel':pat=8*math.sin(x*1.4)*math.cos(y*1.1);grain*=2.5
    elif name=='wood':pat=7*math.sin(x/2+2*math.sin(y/36));grain*=1.2
    elif name=='foliage':pat=8*math.sin(x/5)*math.cos(y/7);grain*=1.2
    elif name in ['sign','white']:grain*=.25
    for c in base:raw.append(max(0,min(255,round(c+pat+grain))))
  textures[name]=png(bytes(raw))
 return textures
