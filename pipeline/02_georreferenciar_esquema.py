import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from paths import *          # RAW, TILES_DIR, PROC, EXTERNAL ...
os.chdir(PROC)               # nomes relativos (cells.json, init.npy...) resolvem em data/processed/
import json, re, math, numpy as np, cv2
from PIL import Image
cells={c['k']:c for c in json.load(open('cells.json'))}
MANC=json.load(open('manc.json'))
AX=438
SB=[357,388,437,491,546,598,651,702,752,804,855,905,955,1003,1050,1100]
RB=[1033,1075,1148,1226,1310,1394,1469,1547,1618,1688,1780,1856,1930,2011,2073,2110]
NY=([45,113,157,193,242,276,293,328,357],[562,668,724,779,843,887,932,983,1033])
W=([104,170,217,263,314,374,421,438],[150,205,265,330,387,452,502,520])
EU=([438,456,500,561,609,672,725,780],[520,542,596,660,726,797,870,925])
EL=([438,456,500,561,629,700,780],[520,542,596,669,750,790,830])
EN=([438,456,486,538,594,650,714,760],[520,542,596,660,726,797,870,905])
def band(cy):
    for b in range(15):
        if SB[b]<=cy<SB[b+1]: return b+1
def col(cx,b):
    if cx<AX:
        for lim,c in [(400,1),(345,3),(285,5),(240,7),(195,9),(140,11)]:
            if cx>lim: return c
        return 13
    for lim,c in [(480,2),(530,4),(600,6)]:
        if cx<lim: return c
    return 12 if (b>=5 or cx>690) else (8 if cx<640 else 10)
def mapxy(pts,north,b):
    out=[]
    for x,y in pts:
        xs,xr=W if x<AX else (EN if north else (EU if b<=5 else EL))
        rx=np.interp(x,xs,xr) if x<AX else np.interp(x,xs,xr)
        if x<AX: rx=np.interp(x,W[0],W[1],left=None) if x>=W[0][0] else 150+(x-104)*0.62*1.0
        ry=np.interp(y,NY[0],NY[1]) if y<357 else (np.interp(y,SB,RB) if y<=1100 else RB[-1]+(y-1100))
        out.append([round(float(rx),1),round(float(ry),1)])
    return out

import collections
def ocr_num(t):
    t=t.replace('$','S').replace('O','0').replace('o','0')
    return [int(m) for m in re.findall(r'(?<!\d)(\d{3,4})(?!\d)',t)]
centers=collections.defaultdict(list)
for c in cells.values():
    if c['dark'] or c['cy']<398 or c['cy']>1095 or c['cx']>790 or c['cx']<90 or c['a']<500 or c['a']>9000: continue
    b=band(c['cy'])
    for v in ocr_num(c['t']):
        if v//100==b and (v%100)%2==(1 if c['cx']<AX else 0) and 1<=v%100<=13:
            centers[(b,v%100)].append(c['cx']); break
cen={(5,9):194,(5,11):145,(6,7):248,(6,11):178,(7,9):218,(7,11):170,(7,13):123}
gcen={1:421,3:374,5:314,7:263,9:217,11:170,13:104,2:456,4:500,6:561,8:609,10:672,12:700}
def col2(cx,b):
    side=[cc for cc in gcen if (cc%2==1)==(cx<AX)]
    if cx>=AX: side=[cc for cc in side if cc in ((2,4,6,12) if b>=5 else (2,4,6,8,10,12))]
    cand=[(abs(cx-cen.get((b,cc),gcen[cc])),cc) for cc in side]
    if cx>=AX and cx>=600 and b>=5: return 12
    return min(cand)[1]
res=[];taken=set()
MK={}
for (x,y,n,o) in MANC:
    k=min(cells,key=lambda k:(cells[k]['cx']-x)**2+(cells[k]['cy']-y)**2)
    if (cells[k]['cx']-x)**2+(cells[k]['cy']-y)**2<150 and k not in MK: MK[k]=(n,o)
    else: print('manual sem célula',n,o)
for k,(n,o) in MK.items():
    c=cells[k]; north=n.endswith('N'); b=int(re.match(r'\D*(\d)',n).group(1)) if False else 1
    res.append(dict(k=k,n=n,o=o,poly=mapxy(c['poly'],north or c['cy']<357,1),cx=c['cx'],cy=c['cy'],t='m')); taken.add(k)
for c in cells.values():
    if c['k'] in taken or c['dark'] or c['cy']<398 or c['cy']>1095 or c['cx']>790 or c['cx']<90 or c['a']<500 or c['a']>9000 or re.match(r'\W*A[VE]',c['t']): continue
    b=band(c['cy']); cc=col2(c['cx'],b)
    if (b==3 and cc in (4,6)) or (b==4 and cc in (6,8,10)): continue
    n=f"{b}{cc:02d} S"
    if cc in (1,2): o=f"ACSU-{'SO' if cc==1 else 'SE'} {b}0"
    elif cc%2==1: o=f"ARSO {b}{(cc-1)//2}"
    elif cc==12: o=f"ASR-SE {b}5"
    else: o=f"ARSE {b}{cc//2-1}"
    if n=='312 S': o=None
    res.append(dict(k=c['k'],n=n,o=o,poly=mapxy(c['poly'],False,b),cx=c['cx'],cy=c['cy'],t='r'))

seen={}
for q in list(res):
    if q['t']!='r': continue
    b,cc=int(re.match(r'(\d+?)(\d\d) S',q['n']).group(1)),int(q['n'].split()[0][-2:])
    exp=cen.get((b,cc),gcen[cc]); d=abs(q['cx']-exp)
    if q['n'] in seen:
        o=seen[q['n']]
        if d<o[0]: res.remove(o[1]); seen[q['n']]=(d,q)
        else: res.remove(q)
    else: seen[q['n']]=(d,q)

DROP={'211 S','308 S','312 S','207 N'}
res=[q for q in res if q['n'] not in DROP]
# remove sobreposições fortes (mantém a maior)
H,W_=2600,1200
masks=[]
for q in res:
    m=np.zeros((H,W_),np.uint8); cv2.fillPoly(m,[np.array(q['poly'],np.int32)],1); masks.append(m)
drop=set()
for i in range(len(res)):
    for j in range(i+1,len(res)):
        if i in drop or j in drop: continue
        ov=(masks[i]&masks[j]).sum()
        if ov>0.35*min(masks[i].sum(),masks[j].sum()):
            drop.add(i if masks[i].sum()<masks[j].sum() else j)
print('sobrepostas removidas:',[res[i]['n'] for i in drop])
res=[q for i,q in enumerate(res) if i not in drop]
# encolhe 5% em direção ao centróide para não encostar nas avenidas
for q in res:
    p=np.array(q['poly']); c=p.mean(axis=0); q['poly']=[[round(float(x),1),round(float(y),1)] for x,y in (c+(p-c)*0.95)]
json.dump(res,open('quadras_raw.json','w'))
# sobreposição de conferência
S=1339/1110.0
im=cv2.imread(str(TILES_DIR/'tile_1.png'))
ov=im.copy()
for q in res:
    p=(np.array(q['poly'])*S).astype(np.int32)
    col_=(0,0,255) if q['t']=='r' else (255,0,0)
    cv2.fillPoly(ov,[p],col_); 
im=cv2.addWeighted(ov,0.35,im,0.65,0)
for q in res:
    p=(np.array(q['poly'])*S).astype(np.int32); cv2.polylines(im,[p],True,(0,0,0),1)
    cv2.putText(im,q['n'].replace(' ',''),(int(np.mean(p[:,0]))-14,int(np.mean(p[:,1]))+4),cv2.FONT_HERSHEY_SIMPLEX,0.38,(0,0,0),1,cv2.LINE_AA)
cv2.imwrite('ov_sul.png',im[int(1000*S):int(2150*S),int(120*S):int(950*S)])
cv2.imwrite('ov_norte.png',im[int(540*S):int(1060*S),int(150*S):int(950*S)])
print(len(res))
