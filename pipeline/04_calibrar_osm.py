import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/
import json, numpy as np, cv2
d=json.load(open(str(RAW/'osm_export_1.geojson')))
Q=json.load(open('osm_q.json')); mine=json.load(open('quadras_raw.json'))
S=1339/1110.0
# afim inicial lon/lat -> px de referência, a partir dos centróides (ajuste robusto)
A=[];B=[]
for q in mine:
    p=q['n'].split()
    if p[0].isdigit() and (p[0]+p[1]) in Q and len(Q[p[0]+p[1]])>=12:
        A.append(np.median(np.array(Q[p[0]+p[1]]),axis=0)); B.append(np.array(q['poly']).mean(axis=0))
A=np.c_[np.array(A),np.ones(len(A))];B=np.array(B)
keep=np.ones(len(A),bool)
for _ in range(4):
    c,_,_,_=np.linalg.lstsq(A[keep],B[keep],rcond=None); r=np.linalg.norm(A@c-B,axis=1); keep=r<np.percentile(r,85)
init=c.T  # 2x3: [lon,lat,1] -> px ref
im=cv2.imread(str(TILES_DIR/'tile_1.png'))
H,W=im.shape[:2]
def render(M,w=3):
    out=np.zeros((H,W),np.uint8)
    for f in d['features']:
        g=f['geometry']
        if g['type']!='LineString': continue
        P=np.c_[np.array(g['coordinates']),np.ones(len(g['coordinates']))]@M.T*S
        cv2.polylines(out,[P.astype(np.int32)],False,255,w)
    return out
r0=render(init)
road=((im.min(axis=2)>=245)|((im[:,:,2]<215)&(im[:,:,0]>235)&(im[:,:,1]>225))).astype(np.float32)
road=cv2.GaussianBlur(road,(0,0),2.5); osm=cv2.GaussianBlur(r0.astype(np.float32)/255,(0,0),2.5)
mask=(cv2.dilate(r0,np.ones((9,9),np.uint8))>0).astype(np.uint8)
warp=np.eye(2,3,dtype=np.float32)
try:
    cc,warp=cv2.findTransformECC(road,osm,warp,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,300,1e-6),mask,7)
    print('ECC cc',round(cc,3))
except Exception as e: print('ECC falhou',e)
Wm=np.vstack([warp,[0,0,1]]); Wi=np.linalg.inv(Wm)[:2]
# px (escala real) = Wi @ [px_init*S,1]
def to_px(lonlat,ref=True):
    P=np.c_[np.atleast_2d(lonlat),np.ones(len(np.atleast_2d(lonlat)))]@init.T*S
    P=np.c_[P,np.ones(len(P))]@Wi.T
    return P/S if ref else P
np.save('init.npy',init); np.save('Wi.npy',Wi)
# sobreposição para conferir
ov=im.copy()
for f in d['features']:
    g=f['geometry']
    if g['type']=='LineString':
        cv2.polylines(ov,[to_px(np.array(g['coordinates']),ref=False).astype(np.int32)],False,(0,0,255),2)
cv2.imwrite('osm_ov.png',ov[int(1000*S):int(1500*S),int(250*S):int(900*S)])
print('deslocamento médio (px) antes/depois:',round(float(np.linalg.norm(warp[:,2])),1))
