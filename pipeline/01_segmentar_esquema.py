import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/
import numpy as np, cv2, re, json, pytesseract
from PIL import Image
raw=Image.open(str(EXTERNAL/'mapa_de-palmas-plano-diretor-com-quadras.gif')).convert('RGB')
im=np.array(raw); gray=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY).astype(float)
nonwhite=(im.min(axis=2)<235).astype(np.uint8)
K=np.ones((3,3),np.uint8)
def comps(mask):
    n,lab,st,cen=cv2.connectedComponentsWithStats(mask,connectivity=4); return n,lab,st
n,lab,st=comps(cv2.erode(nonwhite,K))
cells=[]  # máscaras finais (dilatadas de volta)
for i in range(1,n):
    a=st[i,4]
    if a<450 or a>26000: continue
    m=(lab==i).astype(np.uint8)
    if a>3200:   # possível fusão: erodir mais até separar
        best=None
        for it in (1,2,3,4):
            e=cv2.erode(m,K,iterations=it); n2,l2,s2=comps(e)
            parts=[j for j in range(1,n2) if s2[j,4]>=250]
            if len(parts)>=2: best=(it,[(l2==j).astype(np.uint8) for j in parts]); break
        if best:
            it,ps=best
            # redistribuir pixels da máscara original ao fragmento mais próximo
            dist=[cv2.distanceTransform(1-p,cv2.DIST_L2,3) for p in ps]
            owner=np.argmin(np.stack(dist),axis=0)
            for k in range(len(ps)):
                cells.append(((owner==k)&(m>0)).astype(np.uint8))
            continue
    cells.append(cv2.dilate(m,K))
print('células',len(cells))
out=[]
for k,m in enumerate(cells):
    ys,xs=np.where(m>0)
    if len(xs)<300: continue
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max(); mm=m[y0:y1+1,x0:x1+1]>0
    g=gray[y0:y1+1,x0:x1+1]; fill=np.median(g[mm])
    inner=cv2.erode(mm.astype(np.uint8),K)>0
    txt=(((g<fill-55) if fill>105 else (g>fill+60))&inner)
    img=cv2.resize(np.where(txt,0,255).astype(np.uint8),None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC)
    img=cv2.copyMakeBorder(img,20,20,20,20,cv2.BORDER_CONSTANT,value=255)
    t=pytesseract.image_to_string(img,config='--psm 6').strip().replace('\n',' | ')
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    c=max(cs,key=cv2.contourArea); ap=cv2.approxPolyDP(c,1.6,True)[:,0,:].tolist()
    out.append(dict(k=k,cx=float(xs.mean()),cy=float(ys.mean()),a=int(mm.sum()),bb=[int(x0),int(y0),int(x1),int(y1)],dark=bool(fill<=105),t=t,poly=ap))
json.dump(out,open('cells.json','w'))
print(len(out),'quadras; escuras(AV):',sum(d['dark'] for d in out))
