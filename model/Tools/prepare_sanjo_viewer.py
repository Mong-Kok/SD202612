#!/usr/bin/env python3
"""Offline viewer of the shared geolocated model. No CDN or device transfer."""
from pathlib import Path
import json,re,shutil,hashlib,base64
base=Path(__file__).resolve().parents[1]
out=base.parent/'三条駅3Dビューア'
model=json.loads((base/'Resources/Sanjo1967/model.json').read_text())
people=json.loads((base/'Resources/SanjoPeople1967/model.json').read_text())
lib=(out/'vendor/three.min.js').read_text()
controls=(out/'vendor/OrbitControls.js').read_text()
controls=re.sub(r"import\s*\{(.*?)\}\s*from\s*'three';",r'const {\1} = THREE;',controls,flags=re.S)
controls=re.sub(r'export\s*\{\s*OrbitControls\s*\};','',controls)
triangles=sum(len(m['indices'])//3 for m in model['meshes'])
head='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>京阪三条駅 1967年｜川側・疏水・鉄橋の詳細復元</title>
<style>*{box-sizing:border-box}body{margin:0;background:#171e1b;color:#ebeeec;font:14px/1.65 -apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;letter-spacing:0}header{padding:14px 20px;background:#222c27;display:flex;gap:14px 24px;align-items:center;flex-wrap:wrap}h1{font-size:20px;line-height:1.4;margin:0}small{color:#b8c6bc}.tools{display:flex;gap:4px;flex-wrap:wrap;flex:1}button{font:inherit;border:1px solid #6a7a70;background:#2d3b32;color:#fff;border-radius:4px;padding:7px 12px;min-height:38px;cursor:pointer;white-space:normal}button:hover{background:#435c4c}button[aria-pressed=true]{background:#dde8de;color:#183b29;border-color:#dde8de}main{display:grid;grid-template-columns:minmax(0,1fr) 286px;height:calc(100dvh - 148px);min-height:520px}#view{min-width:0;min-height:0;overflow:hidden;position:relative}canvas{display:block;width:100%;height:100%;touch-action:none}aside{padding:12px 18px;background:#eef1ef;color:#25332a;overflow:auto}h2{font-size:15px;margin:12px 0 6px}p{margin:7px 0}aside small{color:#59665d}a{color:#235b46;overflow-wrap:anywhere}#status{position:absolute;left:12px;bottom:12px;background:#171e1bc9;padding:4px 10px;font-size:12px;pointer-events:none}footer{padding:6px 20px;font-size:12px;color:#b8c6bc}input{accent-color:#376b4c}input[type=range]{width:100%}label{display:block;padding:3px 0}summary{cursor:pointer}aside details{margin-top:12px;border-top:1px solid #c5d0c9;padding-top:9px}.command{background:#753e43}.warn{border-left:3px solid #a65242;padding-left:9px;font-size:12px}@media(max-width:800px){header{padding:10px 12px;gap:10px}h1{font-size:18px}.tools{flex-basis:100%;gap:4px}button{font-size:12px;min-height:36px;padding:6px 10px}main{display:block;height:auto;min-height:0}#view{height:64dvh;min-height:380px}aside{display:grid;grid-template-columns:1fr 1fr;gap:0 18px;padding:12px 16px;overflow:visible}.evidence{grid-column:1/-1}footer{padding:8px 16px}}@media(max-width:380px){aside{grid-template-columns:1fr}.evidence{grid-column:auto}}</style></head><body>
<header><div><h1>京阪三条駅・地上時代</h1><small>1967年頃 · 資料に基づく推定復元</small></div><nav class="tools" aria-label="視点"><button data-preset="all" aria-pressed="true">全体</button><button data-preset="river4">４番線・川側</button><button data-preset="bridge1">１番線・鉄橋</button><button data-preset="gaps">床の隙間</button><button data-preset="crossing">構内踏切</button><button data-preset="front">駅舎正面</button><button data-preset="hall">改札・売店</button><button data-preset="south">南口</button><button data-preset="top">真上</button></nav></header>
<main><div id="view"><div id="status" role="status">モデルを読み込み中</div></div><aside>
<section><h2>駅と河川</h2><label><input id="stationVisible" type="checkbox" checked> 駅・河川を表示</label><label><input id="trainsVisible" type="checkbox" checked> 停車車両</label><label><input id="roofVisible" type="checkbox" checked> 屋根</label><label><input id="waterVisible" type="checkbox" checked> 水面</label><label><input id="flow" type="checkbox" checked> 水面の動き</label><label><input id="wire" type="checkbox"> 形状の線</label><label><input id="grid" type="checkbox"> 10m目盛</label><label for="alpha">駅の透明度 <output id="alphaValue">0%</output></label><input id="alpha" aria-label="駅の透明度" type="range" min="0" max="100" value="0"></section>
<section><h2>人物</h2><label><input id="peopleVisible" type="checkbox" checked> 当時の人々（推定）</label><label for="peopleAlpha">人物の透明度 <output id="peopleAlphaValue">15%</output></label><input id="peopleAlpha" aria-label="人物の透明度" type="range" min="0" max="100" value="15"><p><small>24人の架空の人物。特定の日の乗客ではありません。</small></p><p><button id="save" class="command" title="現在の画角の画像を保存">画像を保存</button></p><p><a href="sanjo1967.glb" download>汎用3D模型</a><br><a href="people1967.glb" download>人物模型</a></p></section>
<section class="evidence"><h2>川に張り出した４番線</h2><p>堤防の外へ出る床と、その下の柱・横梁・基礎を再現。形態は1979・1981年写真も参照しています。</p><h2>疏水上の１番線</h2><p>斜めの鉄橋と開いた床の隙間。疏水は構内を通り、床下で南へ流れます。</p><p class="warn">水位・橋桁断面・床の隙間寸法は推定。水面の動きは模式表現。実測の流れや当時の水音ではありません。京津線連絡線の正確な経路は未再現。</p><details><summary>年代・根拠・位置</summary><p><a href="https://kyotolove.kyoto/I0000301/" target="_blank" rel="noopener">島本由紀：地上時代の三条京阪</a><br><a href="https://ameblo.jp/tetsudotabi/entry-12518170672.html" target="_blank" rel="noopener">構内図と1987年の写真</a><br><a href="https://drfc-ob.com/wp/archives/101442" target="_blank" rel="noopener">1967年夏の駅舎・改札・南口</a><br><a href="https://www.asahi-net.or.jp/~uk9o-tkzw/hseki01.html" target="_blank" rel="noopener">1979年の川側ホーム</a><br><a href="https://www.keihan.co.jp/recommend/mizunomichi/michiannai/04/" target="_blank" rel="noopener">京阪公式：疏水と駅史</a><br><a href="https://research-opendata.gsi.go.jp/tech_data/2026-002-G/2026-002-G-lp.html" target="_blank" rel="noopener">国土地理院・1967年航空写真</a></p><p>後年写真は継続していた形態の参考。1980年代の仮駅舎は含めません。店舗数・内装・床板材・柱寸法は推定。1900系と更新前2200系の各6両は停車配置例で、特定日の編成ではありません。</p><p>北緯35.0087792669°、東経135.7725593261°。原点の楕円体高79.2225m。地盤標高41.78mと補正37.4425mを使用。当時の床高を測量した値ではありません。</p></details></section>
</aside></main><footer>__VERSION__ · 駅 __TRIANGLES__三角形 · three.js r160 / MIT License · 独自生成材質</footer>
'''.replace('__VERSION__',model['version']).replace('__TRIANGLES__',f'{triangles:,}')
head=head.replace('<button data-preset="gaps">','<button data-preset="underbridge">鉄橋の下</button><button data-preset="gaps">')
head=head.replace('<button data-preset="crossing">','<button data-preset="passage">車内通り抜け</button><button data-preset="crossing">')
head=head.replace('<button data-preset="gaps">','<button data-preset="overlook">疏水をのぞく</button><button data-preset="gaps">')
icon=base64.b64encode((out/'vendor/lucide-image-down.svg').read_bytes()).decode()
head=head.replace('>画像を保存</button>','><img alt="" width="16" height="16" style="vertical-align:middle;margin-right:6px;filter:invert(1)" src="data:image/svg+xml;base64,'+icon+'">画像を保存</button>')
head+='<script type="text/plain" id="lucideLicense">'+(out/'vendor/lucide-LICENSE.txt').read_text()+'</script>'
js='''
const station=__MODEL__,passengers=__PEOPLE__,stationSha='__SHA__';
try {
const host=document.getElementById('view'),scene=new THREE.Scene();scene.background=new THREE.Color(0x26322b);
const camera=new THREE.PerspectiveCamera(42,1,.035,2000);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
const canvas=renderer.domElement;canvas.setAttribute('aria-label','三条駅の3D模型');canvas.dataset.version=station.version;host.prepend(canvas);
const orbit=new OrbitControls(camera,canvas);orbit.enableDamping=true;orbit.minDistance=.2;orbit.maxDistance=600;
const root=new THREE.Group(),peopleRoot=new THREE.Group();scene.add(root,peopleRoot);
const materials=[],labelMaterials=[],peopleMaterials=[],parts=[],vehicleLabels=[],loader=new THREE.TextureLoader(),textureMaps={};
let pending=0,failed=0;
for(const [key,data] of Object.entries({...station.textures,...passengers.textures})){
 pending++;const t=loader.load('data:image/png;base64,'+data,()=>pending--,undefined,()=>{pending--;failed++;});t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());textureMaps[key]=t;
}
function addMeshes(model,parent,collection,opacity){
 for(const part of model.meshes){
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices,3));g.setIndex(part.indices);g.computeVertexNormals();g.setAttribute('uv',new THREE.Float32BufferAttribute(part.uv,2));
  const mat=new THREE.MeshLambertMaterial({color:0xffffff,map:textureMaps[part.texture],side:THREE.DoubleSide,transparent:opacity<1,opacity,depthWrite:opacity===1});collection.push(mat);
  const mesh=new THREE.Mesh(g,mat);parent.add(mesh);if(parent===root)parts.push({mesh,part});
 }
}
addMeshes(station,root,materials,1);addMeshes(passengers,peopleRoot,peopleMaterials,.85);
for(const l of station.labels){
 const c=document.createElement('canvas'),ctx=c.getContext('2d');c.height=160;ctx.font='100px sans-serif';c.width=Math.ceil(ctx.measureText(l.text).width)+20;
 ctx.font='100px sans-serif';ctx.fillStyle='#f3f4e8';ctx.textBaseline='middle';ctx.fillText(l.text,10,80);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;const mat=new THREE.MeshBasicMaterial({map:t,transparent:true,side:THREE.DoubleSide,depthWrite:false});labelMaterials.push(mat);
 const node=new THREE.Mesh(new THREE.PlaneGeometry(c.width/100*l.size,1.6*l.size),mat);node.position.set(...l.position);node.position.z+=l.size*.45;
 node.quaternion.setFromAxisAngle(new THREE.Vector3(1,0,0),Math.PI/2);if(l.facing==='north')node.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),Math.PI));root.add(node);if(['1900系','2200系'].includes(l.text))vehicleLabels.push(node);
}
scene.add(new THREE.AmbientLight(0xffffff,1.2));const sun=new THREE.DirectionalLight(0xfffaf0,1.25);sun.position.set(-40,60,100);scene.add(sun);
const grid=new THREE.GridHelper(400,40,0x96a69b,0x51665a);grid.rotation.x=Math.PI/2;grid.position.set(0,-65,-5.9);grid.visible=false;scene.add(grid);
const presets={all:[[-150,132,125],[-28,-65,-1]],river4:[[-75,-58,-.2],[-48.5,-62,-1.8]],bridge1:[[-32,-86,11],[-12,-76,-.5]],underbridge:[[-9,-89,-1.65],[-16,-82,-1.15]],gaps:[[-13.4,-81,1.65],[-14.25,-82.5,-2.0]],crossing:[[-22,-22,2.8],[-26.7,-31,-.6]],front:[[0,47,5],[0,-7,4]],hall:[[-2,-8,2.2],[6,-33,1.5]],south:[[19,-99,4],[19,-68,2]],top:[[-20,-65,285],[-20,-65,-1]]};
let currentPreset='all';
presets.passage=[[-24.2,-26.6,1.55],[-30.75,-26.6,1.3]];
presets.overlook=[[-14.43,-79.63,1.6],[-15.65,-79.33,-3.3]];
function preset(name){
 if(name==='crossing'){document.getElementById('trainsVisible').checked=false;document.getElementById('roofVisible').checked=false;visibility();}
 currentPreset=name;const [p,t]=presets[name];orbit.target.set(...t);camera.position.set(...p).sub(orbit.target).multiplyScalar(Math.max(1,.85/camera.aspect)).add(orbit.target);camera.up.set(0,0,1);orbit.update();canvas.dataset.preset=name;
 document.querySelectorAll('[data-preset]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.preset===name)));
}
document.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>preset(b.dataset.preset));
document.getElementById('stationVisible').onchange=e=>root.visible=e.target.checked;
document.getElementById('peopleVisible').onchange=e=>peopleRoot.visible=e.target.checked;
function visibility(){
 for(const {mesh,part} of parts){mesh.visible=(!part.name.startsWith('train_')||document.getElementById('trainsVisible').checked)&&(!['roof','roof_tile','train_roof'].includes(part.texture)||document.getElementById('roofVisible').checked)&&(!['water','foam'].includes(part.texture)||document.getElementById('waterVisible').checked);}
 vehicleLabels.forEach(n=>n.visible=document.getElementById('trainsVisible').checked);
}
for(const id of ['trainsVisible','roofVisible','waterVisible'])document.getElementById(id).onchange=visibility;
document.getElementById('alpha').oninput=e=>{const a=1-e.target.value/100;materials.forEach(m=>{m.opacity=a;m.transparent=a<1;m.depthWrite=a===1;});labelMaterials.forEach(m=>m.opacity=a);document.getElementById('alphaValue').textContent=e.target.value+'%';};
document.getElementById('peopleAlpha').oninput=e=>{const a=1-e.target.value/100;peopleMaterials.forEach(m=>{m.opacity=a;m.transparent=a<1;m.depthWrite=a===1;});document.getElementById('peopleAlphaValue').textContent=e.target.value+'%';};
document.getElementById('wire').onchange=e=>materials.forEach(m=>m.wireframe=e.target.checked);
document.getElementById('grid').onchange=e=>grid.visible=e.target.checked;
document.getElementById('save').onclick=async()=>{
 renderer.render(scene,camera);
 if(location.hostname==='localhost'&&new URLSearchParams(location.search).get('qa')==='1'){
  const controls=Object.fromEntries([...document.querySelectorAll('input')].map(e=>[e.id,e.type==='checkbox'?e.checked:e.value]));
  const response=await fetch('/__sanjo_capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({image:canvas.toDataURL('image/png'),preset:currentPreset,width:innerWidth,height:innerHeight,canvasWidth:canvas.width,canvasHeight:canvas.height,version:station.version,stationSha,controls,frames,phase,pending,failed,triangles:renderer.info.render.triangles})});
  document.getElementById('status').textContent=response.ok?'確認画像を保存済み':'確認画像の保存に失敗';canvas.dataset.capture=response.ok?'saved':'failed';return;
 }
 canvas.toBlob(blob=>{if(!blob)return;const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='sanjo1967-'+currentPreset+'.png';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);});
};
function resize(){camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();renderer.setSize(host.clientWidth,host.clientHeight);preset(currentPreset);}
new ResizeObserver(resize).observe(host);resize();preset('all');
let frames=0,phase=0,lastTime=0;
renderer.setAnimationLoop(time=>{
 const dt=Math.min(.1,Math.max(0,(time-lastTime)/1000));lastTime=time;
 if(document.getElementById('flow').checked){phase=(phase+dt*.22)%1;for(const k of ['water','foam'])if(textureMaps[k])textureMaps[k].offset.y=phase;}
 orbit.update();renderer.render(scene,camera);canvas.dataset.frames=String(++frames);canvas.dataset.waterPhase=phase.toFixed(4);canvas.dataset.texturePending=String(pending);canvas.dataset.textureErrors=String(failed);canvas.dataset.triangles=String(renderer.info.render.triangles);
 document.getElementById('status').textContent=failed?'材質の読み込み失敗':pending?'材質を読み込み中':'1967年頃 · 推定復元';
});
}catch(e){document.getElementById('status').textContent='表示できません：'+e.message;console.error(e);}
'''.replace('__MODEL__',json.dumps(model,ensure_ascii=False,separators=(',',':'))).replace('__PEOPLE__',json.dumps(people,ensure_ascii=False,separators=(',',':'))).replace('__SHA__',hashlib.sha256((base/'Resources/Sanjo1967/model.json').read_bytes()).hexdigest())
(out/'三条駅1967_3Dビューア.html').write_text(head+'<script>'+lib+'</script><script>'+controls+'</script><script>'+js+'</script></body></html>')
shutil.copy2(base/'Resources/Sanjo1967/sanjo1967.glb',out/'sanjo1967.glb')
shutil.copy2(base/'Resources/SanjoPeople1967/people1967.glb',out/'people1967.glb')
print(out/'三条駅1967_3Dビューア.html')
