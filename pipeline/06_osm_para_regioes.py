import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/
import json, re, math, numpy as np, cv2, unicodedata
from calib import g_units, TILES
d=json.load(open(str(RAW/'osm_export_2.geojson'))); F=d['features']
RECTS=[(x,y,x+w,y+h) for (x,y,w,h) in TILES.values()]
def inside(p): return any(a<=p[0]<=c and b<=p[1]<=e for a,b,c,e in RECTS)
slug=lambda s:re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode()).strip('-')
def U(c): return g_units(np.array(c,float))
def dp(P,tol,closed=False):
    P=np.asarray(P,np.float32).reshape(-1,1,2); return cv2.approxPolyDP(P,tol,closed)[:,0,:]
def rnd(P): return [[int(round(x)),int(round(y))] for x,y in P]
def runs(P):
    out=[];cur=[]
    for p in P:
        if inside(p): cur.append(p)
        else:
            if len(cur)>1: out.append(cur)
            cur=[]
    if len(cur)>1: out.append(cur)
    return out
def clip_rect(P,x0,y0,x1,y1):
    def cl(pts,inn,inter):
        out=[]
        for i in range(len(pts)):
            a,b=pts[i-1],pts[i]
            if inn(b):
                if not inn(a): out.append(inter(a,b))
                out.append(b)
            elif inn(a): out.append(inter(a,b))
        return out
    P=[tuple(p) for p in P]
    P=cl(P,lambda p:p[0]>=x0,lambda a,b:(x0,a[1]+(b[1]-a[1])*(x0-a[0])/(b[0]-a[0]))) if P else P
    P=cl(P,lambda p:p[0]<=x1,lambda a,b:(x1,a[1]+(b[1]-a[1])*(x1-a[0])/(b[0]-a[0]))) if P else P
    P=cl(P,lambda p:p[1]>=y0,lambda a,b:(a[0]+(b[0]-a[0])*(y0-a[1])/(b[1]-a[1]),y0)) if P else P
    P=cl(P,lambda p:p[1]<=y1,lambda a,b:(a[0]+(b[0]-a[0])*(y1-a[1])/(b[1]-a[1]),y1)) if P else P
    return P
def circle(c,r,n=14): return [[c[0]+r*math.cos(2*math.pi*i/n),c[1]+r*math.sin(2*math.pi*i/n)] for i in range(n)]
def strip(a,b,hw):
    a=np.array(a);b=np.array(b);v=b-a;n=np.array([-v[1],v[0]])/ (np.linalg.norm(v)+1e-9)*hw
    return [a+n,b+n,b-n,a-n]
def poly_of(f): 
    g=f['geometry']; return g['coordinates'][0] if g['type']=='Polygon' else None
def find(pred): return [f for f in F if pred(f['properties'],f['geometry'])]
out=[]
def reg(id,n,c,d_,parts,s=None,f=None,replace=False,ln=False):
    out.append(dict(id=id,n=n,c=c,d=d_,parts=parts,s=s,f=f,replace=replace,ln=ln))
def area_part(ll,tol=10): return {'k':'a','q':rnd(dp(U(ll),tol,True))}
def named(n): return [f for f in F if f['properties'].get('name')==n]
# ---------- áreas que substituem contornos desenhados à mão ----------
f=named('Aeroporto de Palmas – Brigadeiro Lysias Rodrigues')[0]
reg('aeroporto','Aeroporto de Palmas — Brigadeiro Lysias Rodrigues','i','Principal aeroporto do Tocantins (código IATA PMW, ICAO SBPJ), ao sul do Plano Diretor, na margem do lago. Contorno do OpenStreetMap.',[area_part(poly_of(f),12)],s='Aeroporto',replace=True)
f=named('Associação Tocantinense de Aviação - ATA')[0]
reg('ata','Aeródromo da Associação Tocantinense de Aviação (ATA)','i','Aeródromo (ICAO SWEJ) a oeste de Luzimangues, com pista de asfalto de cerca de 1.000 m. Contorno do OpenStreetMap.',[area_part(poly_of(f),6)],s='ATA',replace=True)
f=named('Agrotins')
f=[x for x in f if x['geometry']['type']=='Polygon'][0]
reg('agrotins','Agrotins — Centro Agrotecnológico','p','Centro Agrotecnológico de Palmas, às margens do lago, onde ocorre a Agrotins, feira agrotecnológica do Tocantins. Segundo o OpenStreetMap, ocupa cerca de 350 hectares (Km 23 da TO-050). Contorno do OpenStreetMap.',[area_part(poly_of(f),6)],s='Agrotins',replace=True)
f=named('Aterro Sanitário de Palmas')[0]
reg('aterro','Aterro Sanitário de Palmas','i','Destino final dos resíduos da capital, afastado da área urbana, a sudeste de Taquaralto. Contorno do OpenStreetMap.',[area_part(poly_of(f),8)],s='Aterro',replace=True)
fl=[x for x in F if x['properties'].get('aeroway')=='runway' and x['geometry']['type']=='LineString' and 'ref' not in x['properties'] and x['properties'].get('name') is None]
for x in fl:
    c=x['geometry']['coordinates']
    if len(c)==2 and abs(c[0][1]+10.1085)<0.01:
        a,b=U(c); reg('flyer','Aeródromo Sítio Flyer','i','Pequeno aeródromo ao norte do Plano Diretor, com pista curta mapeada no OpenStreetMap.',[{'k':'a','q':rnd(strip(a,b,110))}],s='Sítio Flyer',replace=True)
f=named('Aeródromo Fazenda Terra Prometida')[0]; a,b=U(f['geometry']['coordinates'])
reg('terra-prometida','Aeródromo Fazenda Terra Prometida','i','Aeródromo agrícola com pista de asfalto de 1.210 m, a sudeste de Taquaralto (dado do OpenStreetMap).',[{'k':'a','q':rnd(strip(a,b,130))}],s='Terra Prometida')
# lago: reservatório UHE Lajeado recortado
f=named('Reservatório UHE Luís Eduardo Magalhães (Lajeado)')[0]
P=U(f['geometry']['coordinates'][0]); P=clip_rect(P,20000,3600,66200,69960)
reg('lago-palmas','Lago de Palmas (Rio Tocantins)','n','Reservatório formado no Rio Tocantins pela usina hidrelétrica Luís Eduardo Magalhães (Lajeado). Banha toda a orla oeste de Palmas, separa a capital de Luzimangues e Porto Nacional e é atravessado pela TO-080. Contorno do OpenStreetMap.',[{'k':'a','q':rnd(dp(P,40,True))}],s='Lago de Palmas',f=7,replace=True)
f=named('Lagoa do Parque Cesamar')[0]
reg('lagoa-cesamar','Lagoa do Parque Cesamar','n','Lagoa do Parque Cesamar, no Plano Diretor Sul. Contorno do OpenStreetMap.',[area_part(poly_of(f),5)],s='Lagoa Cesamar',f=30)
f=named('SANEATINS')[0]
reg('saneatins','Reservatório da Saneatins','i','Reservatório de água ao sul do Plano Diretor, identificado como SANEATINS no OpenStreetMap.',[area_part(poly_of(f),5)],s='Saneatins',f=30)
# ---------- pontos de interesse ----------
def poi(name,id,cat,desc,s=None,tol=5,f=None):
    f_=named(name)
    f_=[x for x in f_ if x['geometry']['type']=='Polygon']
    if not f_: print('sem polígono:',name); return
    reg(id,name,cat,desc,[area_part(poly_of(f_[0]),tol)],s=s,f=f)
poi('Estádio Nilton Santos','estadio-nilton-santos','p','Estádio de futebol de Palmas, ao sul do Plano Diretor.',s='Estádio')
poi('Rodoviária de Palmas','rodoviaria-palmas','i','Terminal Rodoviário de Palmas, junto à Av. LO-27 (Quadra 1212 Sul).',s='Rodoviária')
poi('Praia do Prata','praia-do-prata','p','Praia na orla do Lago de Palmas, ao sul do Plano Diretor.',s='Praia do Prata')
poi('22º Batalhão de Infantaria','22-bi','i','Área militar do 22º Batalhão de Infantaria, a leste do Plano Diretor Sul.',s='22º BI')
poi('Marinha do Brasil','marinha','i','Área militar da Marinha do Brasil, na orla do lago ao sul do Plano Diretor.',s='Marinha')
poi('Escola Superior de Polícia','esp','i','Escola Superior de Polícia (área de treinamento), a leste do Parque Cesamar.',s='Esc. Sup. Polícia')
poi('Entrada Taquaruçu','entrada-taquarucu','p','Portal de entrada do distrito de Taquaruçu, referência turística.',s='Entrada')
def point_poi(name,id,cat,desc,r=260,s=None,f_=None):
    p=[x for x in named(name) if x['geometry']['type']=='Point']
    if p:
        c=U(p[0]['geometry']['coordinates'])[0]
        if inside(c): reg(id,name,cat,desc,[{'k':'a','q':rnd(circle(c,r))}],s=s or name,f=f_)
point_poi('Kartódromo de Palmas','kartodromo','p','Kartódromo de Palmas, junto ao Estádio Nilton Santos.',s='Kartódromo')
point_poi('Cachoeira de Taquaruçu','cachoeira-taquarucu','p','Uma das cachoeiras do distrito de Taquaruçu, na Serra do Lajeado.',r=320,s='Cachoeira')
# ---------- localidades (pontos do OSM dentro do mosaico) ----------
skip={'Palmas','Luzimangues','Capivara','Poção','Prata','Taquarussu do Porto','Barcelona Residencial','Águas Lindas','Jardim Madri','Jardim Bela Vista','Jardim Europa','Laguna I','Laguna II','Laguna III','Park dos Buritis','Jardim do Porto','103 Norte'}
for x in F:
    p=x['properties']
    if x['geometry']['type']!='Point' or p.get('place') not in ('hamlet','village','suburb','neighbourhood'): continue
    n=p.get('name','')
    if not n or n in skip or re.search(r'\(',n): continue
    c=U(x['geometry']['coordinates'])[0]
    if not inside(c): continue
    reg('loc-'+slug(n),n,'b',f'Localidade mapeada no OpenStreetMap ({p["place"]}). Posição aproximada do ponto, sem limites definidos.',[{'k':'a','q':rnd(circle(c,480))}],s=n,f=14)
# ---------- localidades com contorno a partir das vias ----------
allroads=[U(x['geometry']['coordinates']) for x in F if x['geometry']['type']=='LineString' and 'highway' in x['properties']]
V=np.vstack(allroads)
HAND=json.load(open('hand_polys.json'))
def hullfix(id,expand=1.3,minpts=14):
    h=np.array(HAND[id],np.float32); c=h.mean(axis=0); big=(c+(h-c)*expand).astype(np.float32).reshape(-1,1,2)
    sel=np.array([v for v in V if cv2.pointPolygonTest(big,(float(v[0]),float(v[1])),False)>=0])
    if len(sel)<minpts: return None
    hull=cv2.convexHull(sel.astype(np.float32))[:,0,:]; hc=hull.mean(axis=0); hull=hc+(hull-hc)*1.05
    ratio=cv2.contourArea(hull.astype(np.float32))/max(1,cv2.contourArea(h))
    print(id,'vértices',len(sel),'razão de área',round(ratio,2))
    return hull if 0.5<=ratio<=2.4 else None
for id_ in ('taquaralto','taquarussu','capivara'):
    hh=hullfix(id_)
    if hh is not None: out.append(dict(id=id_,keep=True,parts=[{'k':'a','q':rnd(hh)}],replace=True,patch=True))
# ---------- rodovias e avenidas ----------
def lines_of(pred):
    parts=[]
    for x in F:
        p=x['properties']
        if x['geometry']['type']=='LineString' and 'highway' in p and pred(p):
            for r in runs(U(x['geometry']['coordinates'])):
                if len(r)>=2: parts.append({'k':'l','q':rnd(dp(r,22))})
    return parts
def road(id,n,d_,pred,s=None,replace=False):
    P=lines_of(pred)
    if P: reg(id,n,'v',d_,P,s=s or n,replace=replace,ln=True); print(id,len(P),'trechos')
ref=lambda p:p.get('ref','')
road('br010','BR-010','Rodovia federal que margeia Palmas a leste e segue para o sul passando por Taquaralto. Traçado do OpenStreetMap (inclui trechos sinalizados como TO-010).',lambda p:'BR-010' in ref(p) or ref(p)=='TO-010',replace=True)
road('to080','TO-080','Rodovia estadual que cruza Palmas pela Praça dos Girassóis, atravessa o lago pela ponte e chega a Luzimangues e Porto Nacional. Traçado do OpenStreetMap.',lambda p:ref(p)=='TO-080',replace=True)
road('to030','TO-030','Rodovia estadual que liga a região de Taquaralto a Taquarussu do Porto. Traçado do OpenStreetMap.',lambda p:ref(p)=='TO-030',replace=True)
road('to348','TO-348','Rodovia estadual que sai da TO-080, em Luzimangues, rumo ao norte. Traçado do OpenStreetMap.',lambda p:ref(p)=='TO-348',replace=True)
road('to455','TO-455','Rodovia estadual que parte da TO-080 rumo ao sul, passando pelo Terminal Multimodal. Traçado do OpenStreetMap.',lambda p:ref(p)=='TO-455',replace=True)
road('to050','TO-050','Rodovia estadual que segue ao sul de Palmas, acompanhando a BR-010 e levando à Agrotins (Km 23). Traçado do OpenStreetMap.',lambda p:ref(p)=='TO-050' or p.get('name')=='Rodovia To 050')
road('teotonio','Avenida Teotônio Segurado','Eixo central de Palmas, corre de norte a sul e divide o Plano Diretor em lados leste e oeste. Traçado do OpenStreetMap.',lambda p:p.get('name')=='Avenida Teotônio Segurado',replace=True)
road('av-jk','Avenida Juscelino Kubitschek','Eixo leste-oeste que passa pela Praça dos Girassóis e separa o Plano Diretor Norte do Sul. Traçado do OpenStreetMap.',lambda p:p.get('name') in ('Avenida Juscelino Kubitschek','Avenida Jucelino Kubitschek'),s='Av. JK')
road('av-ns15','Avenida Parque NS-15','Via que contorna o Plano Diretor pela orla do lago. Traçado do OpenStreetMap.',lambda p:p.get('name') in ('Avenida Parque NS-15','Avenida NS-15'),s='Av. NS-15')
road('av-tocantins','Avenida Tocantins','Principal avenida da região sul de Palmas (Taquaralto), paralela à BR-010. Traçado do OpenStreetMap.',lambda p:p.get('name')=='Avenida Tocantins',s='Av. Tocantins')
road('av-joaquim','Avenida Joaquim Teotônio Segurado','Continuação do eixo central ao norte, em diagonal, no Plano Diretor Norte. Traçado do OpenStreetMap.',lambda p:p.get('name')=='Avenida Joaquim Teotônio Segurado',s='Av. J. Teotônio Segurado')
# ---------- cursos d'água nomeados ----------
byname={}
for x in F:
    p=x['properties']
    if x['geometry']['type']=='LineString' and p.get('waterway') in ('river','stream') and p.get('name') and p.get('tunnel') is None:
        for r in runs(U(x['geometry']['coordinates'])):
            if len(r)>=2: byname.setdefault(p['name'],[]).append(r)
def length(r): r=np.array(r); return float(np.sum(np.hypot(*np.diff(r,axis=0).T)))
cand=sorted(((sum(length(r) for r in rs),n,rs) for n,rs in byname.items()),reverse=True)
kept=0
for L,n,rs in cand:
    if L<3500 or kept>=40: continue
    kept+=1
    reg('agua-'+slug(n),n,'n',f'Curso d’água mapeado no OpenStreetMap{" (rio)" if n.startswith("Rio") else ""}.',[{'k':'l','q':rnd(dp(r,25))} for r in rs],s=n,ln=True)
print('cursos d’água:',kept)
json.dump(out,open('osm_regs.json','w'))
print(len(out),'itens;',sum(len(o['parts']) for o in out),'partes;',round(len(json.dumps(out))/1e3),'KB')
