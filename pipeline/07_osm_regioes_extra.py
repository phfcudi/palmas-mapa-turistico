import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/
import json, re, math, numpy as np, cv2, unicodedata
from calib import g_units, TILES, REF
d=json.load(open(str(RAW/'osm_export_3.geojson'))); F=d['features']
RECTS=[(x,y,x+w,y+h) for (x,y,w,h) in TILES.values()]
inside=lambda p:any(a<=p[0]<=c and b<=p[1]<=e for a,b,c,e in RECTS)
slug=lambda s:re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode()).strip('-')
U=lambda c:g_units(np.array(c,float))
dp=lambda P,t,cl=False:cv2.approxPolyDP(np.asarray(P,np.float32).reshape(-1,1,2),t,cl)[:,0,:]
rnd=lambda P:[[int(round(x)),int(round(y))] for x,y in P]
def runs(P):
    out=[];cur=[]
    for p in P:
        if inside(p): cur.append(p)
        else:
            if len(cur)>1: out.append(cur)
            cur=[]
    if len(cur)>1: out.append(cur)
    return out
circle=lambda c,r,n=14:[[c[0]+r*math.cos(2*math.pi*i/n),c[1]+r*math.sin(2*math.pi*i/n)] for i in range(n)]
out=[]
def reg(id,n,c,d_,parts,s=None,f=None,replace=False,ln=False): out.append(dict(id=id,n=n,c=c,d=d_,parts=parts,s=s,f=f,replace=replace,ln=ln))
ap=lambda ll,t=6:{'k':'a','q':rnd(dp(U(ll),t,True))}
# ---- ferrovia ----
rail=[x for x in F if x['properties'].get('railway')=='rail' and x['geometry']['type']=='LineString']
parts=[{'k':'l','q':rnd(dp(r,22))} for x in rail for r in runs(U(x['geometry']['coordinates'])) if len(r)>1]
reg('ferrovia','Ferrovia Norte-Sul','v','Corredor ferroviário que passa a oeste de Luzimangues e abastece o Terminal Multimodal. Traçado do OpenStreetMap.',parts,replace=True,ln=True); print('ferrovia trechos',len(parts))
# ---- terminal multimodal ----
vli=[x for x in F if x['properties'].get('name')=='Terminal VLI Porto Nacional'][0]
st=[x for x in F if x['properties'].get('railway')=='station'][0]
reg('terminal','Terminal Multimodal Palmas / Porto Nacional','i','Terminal Multimodal de Palmas / Porto Nacional e Terminal VLI, na Ferrovia Norte-Sul: integra ferrovia e rodovias no escoamento da produção regional. Contornos e posição do OpenStreetMap.',
    [ap(vli['geometry']['coordinates'][0],8),{'k':'a','q':rnd(circle(U(st['geometry']['coordinates'])[0],320))}],s='Terminal Multimodal',replace=True)
acc=[x for x in F if x['properties'].get('name')=='Acesso Terminal de Porto Nacional']
pp=[{'k':'l','q':rnd(dp(r,15))} for x in acc for r in runs(U(x['geometry']['coordinates']))]
if pp: reg('acesso-terminal','Acesso ao Terminal de Porto Nacional','v','Vias de acesso ao terminal multimodal. Traçado do OpenStreetMap.',pp,s='Acesso ao Terminal',ln=True)
rc=[x for x in F if x['properties'].get('name')=='Rota das Capivaras']
pp=[{'k':'l','q':rnd(dp(r,15))} for x in rc for r in runs(U(x['geometry']['coordinates']))]
if pp: reg('rota-capivaras','Rota das Capivaras','v','Via nomeada Rota das Capivaras, perto da Agrotins. Traçado do OpenStreetMap.',pp,s='Rota das Capivaras',ln=True)
# ---- equipamentos ----
def poi(name,cat,desc,s=None):
    for x in F:
        if x['properties'].get('name')==name:
            g=x['geometry']
            if g['type']=='Polygon': reg('eq-'+slug(name),name,cat,desc,[ap(g['coordinates'][0])],s=s or name)
            elif g['type']=='Point':
                c=U(g['coordinates'])[0]
                if inside(c): reg('eq-'+slug(name),name,cat,desc,[{'k':'a','q':rnd(circle(c,230))}],s=s or name)
            return
poi('Terminal de Passageiros','i','Terminal de passageiros do Aeroporto de Palmas. Contorno do OpenStreetMap.','Terminal aeroporto')
poi('Centro de Ensino Médio de Taquaralto','p','Escola de ensino médio em Taquaralto. Contorno do OpenStreetMap.','CEM Taquaralto')
poi('Colégio Dom Bosco Taquaralto','p','Colégio em Taquaralto. Contorno do OpenStreetMap.','Dom Bosco')
poi('Centro de Formação Profissional de Taquaralto','p','Centro de formação profissional em Taquaralto. Contorno do OpenStreetMap.','Formação Prof.')
poi('Subestação Taquaralto 2','i','Subestação de energia em Taquaralto. Contorno do OpenStreetMap.','Subestação')
poi('Biblioteca de Taquaralto','p','Biblioteca em Taquaralto (posição do OpenStreetMap).','Biblioteca')
poi('Serviço Nacional de Aprendizagem Comercial - Unidade Operativa Taquaralto','p','Unidade do SENAC em Taquaralto (posição do OpenStreetMap).','SENAC')
# ---- sub-blocos residenciais ----
S1=TILES[1][2]/REF; O1=np.array(TILES[1][:2])
subs=[]
for x in F:
    p=x['properties']
    if p.get('landuse')=='residential' and x['geometry']['type']=='Polygon':
        P=U(x['geometry']['coordinates'][0]); subs.append(dict(n=p.get('name'),U=P,c=P.mean(axis=0),a=cv2.contourArea(P.astype(np.float32))))
print('sub-blocos',len(subs))
CODE=re.compile(r'^(QI|QR|QD|QS|APM|HM|L-|Quadra|ARS|ARN|AV|Q\.|Q )',re.I)
seen=set()
for s_ in subs:
    n=s_['n']
    if not n or CODE.match(n) or n in seen: continue
    seen.add(n)
    reg('res-'+slug(n),n,'b','Condomínio ou residencial mapeado no OpenStreetMap. Contorno do OpenStreetMap.',[{'k':'a','q':rnd(dp(s_['U'],6,True))}],s=n,f=22)
print('residenciais nomeados:',sorted(seen))
# áreas desenhadas à mão que ganham contorno a partir dos sub-blocos
HAND=json.load(open('hand_polys.json'))
for id_,exp in (('taquaralto',1.7),):
    h=np.array(HAND[id_],np.float32); c=h.mean(axis=0); big=(c+(h-c)*exp).astype(np.float32).reshape(-1,1,2)
    sel=[s_ for s_ in subs if cv2.pointPolygonTest(big,(float(s_['c'][0]),float(s_['c'][1])),False)>=0]
    tot=sum(s_['a'] for s_ in sel); ratio=tot/max(1,cv2.contourArea(h)); print(id_,'sub-blocos',len(sel),'razão de área',round(ratio,2))
    if len(sel)>=8 and 0.3<=ratio<=3: out.append(dict(id=id_,patch=True,replace=True,parts=[{'k':'a','q':rnd(dp(s_['U'],8,True))} for s_ in sel]))
# ---- correções de quadras do Plano Diretor ----
Q=json.load(open('quadras_final.json')); fix={}
tor=lambda P:(P-O1)/S1
SUBR=[dict(c=tor(s_['c']),a=cv2.contourArea(tor(s_['U']).astype(np.float32)),P=tor(s_['U'])) for s_ in subs]
asg={}
for q in Q:
    poly=np.array(q['poly'],np.float32); c=poly.mean(axis=0); big=(c+(poly-c)*1.12).reshape(-1,1,2).astype(np.float32)
    for i,s_ in enumerate(SUBR):
        if cv2.pointPolygonTest(big,(float(s_['c'][0]),float(s_['c'][1])),False)>=0:
            dd=np.hypot(*(s_['c']-c))
            if i not in asg or dd<asg[i][0]: asg[i]=(dd,q['n']+'|'+str(q['o']))
by={}
for i,(dd,k) in asg.items(): by.setdefault(k,[]).append(i)
nfix=0
for q in Q:
    k=q['n']+'|'+str(q['o']); ids=by.get(k,[])
    if len(ids)<2: continue
    A=cv2.contourArea(np.array(q['poly'],np.float32)); tot=sum(SUBR[i]['a'] for i in ids)
    hull=cv2.convexHull(np.vstack([SUBR[i]['P'] for i in ids]).astype(np.float32))[:,0,:]; hc=hull.mean(axis=0); hull=hc+(hull-hc)*1.03
    hr=cv2.contourArea(hull.astype(np.float32))/max(1,A)
    if 0.5<=tot/A<=1.3 and 0.75<=hr<=1.45:
        fix[k]=[[round(float(x),1),round(float(y),1)] for x,y in hull]; nfix+=1
print('quadras com contorno corrigido por sub-blocos:',nfix,'de',len(Q))
json.dump(fix,open('quadra_fix.json','w')); json.dump(out,open('osm_regs2.json','w'))
print(len(out),'itens')
