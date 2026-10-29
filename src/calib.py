import json, numpy as np, cv2
from paths import PROC, RAW, TILES_DIR
TILES={1:(62921.26,1751.24,28314.36,66181.52),2:(60145.16,67406.01,28446.66,66155.06),3:(82466.11,67534.97,28526.06,66207.98),
4:(106155.16,57161.66,28499.6,66049.2),5:(37300.07,3600.09,28473.14,66366.76),6:(20603.62,2965.35,28552.52,66234.44),7:(-911.76,0.06,28473.14,66234.44)}
REF=1110.0
init=np.load(PROC / 'init.npy'); Wi=np.load(PROC / 'Wi.npy'); S1=1339/1110.0
def g_units(ll):
    """lon/lat -> unidades do SVG (global, via calibração do Plano Diretor)"""
    ll=np.atleast_2d(np.array(ll,float)); P=np.c_[ll,np.ones(len(ll))]@init.T*S1
    P=(np.c_[P,np.ones(len(P))]@Wi.T)/S1          # px de referência do tile 1
    x,y,w,h=TILES[1]; k=w/REF
    return np.c_[x+P[:,0]*k,y+P[:,1]*k]
if __name__=='__main__':
    d=json.load(open(RAW / 'osm_export_2.geojson', encoding='utf-8'))
    HW=[np.array(f['geometry']['coordinates']) for f in d['features'] if f['geometry']['type']=='LineString' and 'highway' in f['properties'] and f['properties']['highway'] in ('trunk','primary','secondary','tertiary','trunk_link','primary_link','secondary_link')]
    HWu=[g_units(l) for l in HW]
    out={}
    for t,(ox,oy,w,h) in TILES.items():
        im=cv2.imread(str(TILES_DIR / f'tile_{t}.png')); H,Wd=im.shape[:2]; kx=Wd/w; ky=H/h
        r=np.zeros((H,Wd),np.uint8)
        for L in HWu:
            P=np.c_[(L[:,0]-ox)*kx,(L[:,1]-oy)*ky]
            if P[:,0].max()<0 or P[:,0].min()>Wd or P[:,1].max()<0 or P[:,1].min()>H: continue
            cv2.polylines(r,[P.astype(np.int32)],False,255,3)
        n=int((r>0).sum())
        road=((im.min(axis=2)>=245)|((im[:,:,0]>240)&(im[:,:,1]>150)&(im[:,:,2]<215))).astype(np.float32)
        road=cv2.GaussianBlur(road,(0,0),2.5); osm=cv2.GaussianBlur(r.astype(np.float32)/255,(0,0),2.5)
        mask=(cv2.dilate(r,np.ones((9,9),np.uint8))>0).astype(np.uint8)
        warp=np.eye(2,3,dtype=np.float32); cc=None
        f=0.3; sm=lambda a:cv2.resize(a,None,fx=f,fy=f,interpolation=cv2.INTER_AREA)
        if n>3000:
            try:
                cc,warp=cv2.findTransformECC(sm(road),sm(osm),warp,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,120,1e-5),sm(mask),5)
                warp[:,2]/=f
            except Exception as e: warp=np.eye(2,3,dtype=np.float32)
        print('tile',t,'pixels OSM',n,'cc',None if cc is None else round(cc,3),'deslocamento px',np.round(warp[:,2],1),'matriz',np.round(warp[:,:2].ravel(),4))
        out[t]=warp.tolist(); json.dump(out,open(PROC / 'tile_warp.json','w'))
    json.dump(out,open(PROC / 'tile_warp.json','w'))
