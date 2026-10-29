import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/
import json, re, numpy as np, cv2
d=json.load(open(str(RAW/'osm_export_1.geojson')))
Q=json.load(open('osm_q.json')); mine=json.load(open('quadras_raw.json'))
init=np.load('init.npy'); Wi=np.load('Wi.npy'); S=1339/1110.0
def px(ll):
    ll=np.atleast_2d(np.array(ll,float)); P=np.c_[ll,np.ones(len(ll))]@init.T*S
    return (np.c_[P,np.ones(len(P))]@Wi.T)/S
def trim(P):
    m=np.median(P,axis=0); r=np.linalg.norm(P-m,axis=1); mad=np.median(r)+1e-6
    return P[r<max(3.2*mad,40)]
SC=2
def mask_of(poly):
    m=np.zeros((3000*SC//1,1300*SC//1),np.uint8); cv2.fillPoly(m,[(np.array(poly)*SC).astype(np.int32)],1); return m
moved=[];stay=0
for q in mine:
    p=q['n'].split(); key=p[0]+p[1] if p[0].isdigit() else None
    if key not in Q or len(Q[key])<8: continue
    P=trim(px(Q[key])); poly=np.array(q['poly']); m=mask_of(poly)
    def frac(dx,dy):
        ij=((P-[dx,dy])*SC).astype(int); ok=(ij[:,0]>=0)&(ij[:,1]>=0)&(ij[:,0]<m.shape[1])&(ij[:,1]<m.shape[0])
        return m[ij[ok,1],ij[ok,0]].sum()/len(P)
    base=frac(0,0); best=(base,0,0)
    for dx in range(-26,27,2):
        for dy in range(-26,27,2):
            sc=frac(dx,dy)-0.0012*np.hypot(dx,dy)
            if sc>best[0]-0.0012*np.hypot(best[1],best[2]): best=(frac(dx,dy),dx,dy)
    if best[0]>base+0.10:
        q['orig']=q['poly']; q['poly']=[[round(x+best[1],1),round(y+best[2],1)] for x,y in poly]; q['moved']=[best[1],best[2],round(base,2),round(best[0],2)]; moved.append(key)
print('quadras deslocadas:',len(moved),'de',sum(1 for q in mine if q['n'].split()[0].isdigit() and (q['n'].split()[0]+q['n'].split()[1]) in Q))
# polígonos oficiais do OSM para 102 S e 202 S
for f in d['features']:
    n=f['properties'].get('name','')
    m=re.match(r'(\d+) Sul \((ACSU-SE \d+)\)',n)
    if m and f['geometry']['type']=='Polygon':
        poly=px(f['geometry']['coordinates'][0]).round(1).tolist()
        hit=[q for q in mine if q['n']==f'{m.group(1)} S']
        if hit: hit[0]['poly']=poly; hit[0]['t']='osm'; hit[0]['o']=m.group(2)
        else: mine.append(dict(n=f'{m.group(1)} S',o=m.group(2),poly=poly,t='osm',cx=0,cy=0,k=-1))
# quadras que faltavam: envoltória das alamedas
OLD={'105N':'ARNO 12','107N':'ARNO 13','201N':None,'203N':'ARNO 21','207N':'ARNO 23','604N':'ARNE 71','105S':'ARSO 12','205S':'ARSO 22','207S':'ARSO 23','209S':'ARSO 24','303S':'ARSO 31','305S':'ARSO 32','308S':'ARSE 33','407S':'ARSO 43','304S':None,'310S':None,'111S':None,'1505S':None}
have={q['n'].replace(' ','') for q in mine}
added=[]
for key,old in OLD.items():
    if key in have or key not in Q: continue
    P=trim(px(Q[key]))
    if len(P)<6: continue
    m=np.zeros((3000,1300),np.uint8); hull=cv2.convexHull(P.astype(np.float32)); cv2.fillPoly(m,[hull.astype(np.int32)],1)
    m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); c=max(cs,key=cv2.contourArea)
    poly=cv2.approxPolyDP(c,1.5,True)[:,0,:].astype(float).round(1).tolist()
    n=key[:-1]+' '+key[-1]
    mine.append(dict(n=n,o=old,poly=poly,t='h',cx=0,cy=0,k=-2)); added.append((n,old,len(P),int(cv2.contourArea(c))))
print('adicionadas por envoltória:',added)

def mk(p):
    m=np.zeros((3000,1300),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
rev=[]
for q in mine:
    if not q.get('moved'): continue
    mq=mk(q['poly']); a=max(1,mq.sum())
    if any(o is not q and o['t']!='h' and (mq&mk(o['poly'])).sum()/a>0.22 for o in mine):
        q['poly']=q['orig']; q['moved']=None; rev.append(q['n'])
print('movimentos revertidos por sobreposição:',rev)
def ok_hull(q):
    P=np.array(q['poly'],np.float32); a=cv2.contourArea(P)
    (cx,cy),(w,h),_=cv2.minAreaRect(P); ar=max(w,h)/max(1,min(w,h))
    m=np.zeros((3000,1300),np.uint8); cv2.fillPoly(m,[P.astype(np.int32)],1)
    ov=0
    for o in mine:
        if o is q or o['t']=='h': continue
        mo=np.zeros_like(m); cv2.fillPoly(mo,[np.array(o['poly'],np.int32)],1); ov=max(ov,(m&mo).sum()/max(1,m.sum()))
    return 1500<=a<=7500 and ar<=2.6 and ov<0.2
bad=[q['n'] for q in mine if q['t']=='h' and (not ok_hull(q) or q['n'] in ('111 S','209 S'))]
mine=[q for q in mine if q['t']!='h' or q['n'] not in bad]
print('envoltórias rejeitadas:',bad,'| mantidas:',[q['n'] for q in mine if q['t']=='h'])
json.dump(mine,open('quadras_final.json','w'))
# lazer: polígonos 'leisure'
L=[]
for f in d['features']:
    pr=f['properties']
    if f['geometry']['type']=='Polygon' and pr.get('leisure'):
        L.append(dict(n=pr['name'],leisure=pr['leisure'],sport=pr.get('sport'),poly=px(f['geometry']['coordinates'][0]).round(1).tolist()))
json.dump(L,open('lazer.json','w')); print('lazer:',len(L),[l['n'] for l in L][:30])
# sobreposição de conferência
im=cv2.imread(str(TILES_DIR/'tile_1.png')); ov=im.copy()
for q in mine:
    p=(np.array(q['poly'])*S).astype(np.int32); col=(0,160,255) if q['t']=='h' else ((255,120,0) if q['t']=='osm' else (0,0,255) if q.get('moved') else (200,200,0))
    cv2.fillPoly(ov,[p],col)
im=cv2.addWeighted(ov,0.38,im,0.62,0)
for q in mine:
    p=(np.array(q['poly'])*S).astype(np.int32); cv2.polylines(im,[p],True,(0,0,0),1)
    cv2.putText(im,q['n'].replace(' ',''),(int(p[:,0].mean())-14,int(p[:,1].mean())+4),cv2.FONT_HERSHEY_SIMPLEX,0.36,(0,0,0),1,cv2.LINE_AA)
cv2.imwrite('fin_sul.png',im[int(1000*S):int(2150*S),int(120*S):int(950*S)]); cv2.imwrite('fin_norte.png',im[int(540*S):int(1100*S),int(150*S):int(950*S)])
