import sys, cv2, numpy as np, trimesh, qrcode, math
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import simplify

URL = sys.argv[1]
Wmm = float(sys.argv[2]); Hmm = float(sys.argv[3])
OUT = sys.argv[4] if len(sys.argv)>4 else 'v2'
ppm = 24.0                                    # higher res for small part

# ---- classify original poster art ----
img=cv2.imread('poster.png'); H0,W0=img.shape[:2]
rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB).astype(np.float32)
centers=np.array([[31,17,10],[245,232,219],[160,88,41],[166,150,136],[90,70,56]],np.float32)
cmap=np.array([0,1,2,1,0])
d=np.linalg.norm(rgb[:,:,None,:]-centers[None,None,:,:],axis=3)
lab=cmap[d.argmin(2)].astype(np.uint8)

# ---- target canvas ----
CW,CH=int(round(Wmm*ppm)),int(round(Hmm*ppm))
k=CW/W0; artH=int(round(H0*k)); yoff=(CH-artH)//2
lab_r=cv2.resize(lab,(CW,artH),interpolation=cv2.INTER_NEAREST)
canvas=np.zeros((CH,CW),np.uint8); canvas[yoff:yoff+artH,:]=lab_r

# ---- generate fresh QR from URL ----
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=0)
qr.add_data(URL); qr.make(fit=True)
mat=(np.array(qr.get_matrix(),dtype=np.uint8))   # 1=dark
n=mat.shape[0]
print("QR version modules:",n,"for url len",len(URL))

# QR module-area corners from original poster -> canvas coords
qc=np.array([[277,588],[855,589],[855,1161],[276,1161]],np.float32)
def mapc(p): return np.array([p[0]*k, p[1]*k+yoff])
tl,tr,br,bl=mapc(qc[0]),mapc(qc[1]),mapc(qc[2]),mapc(qc[3])
# fill module-area bg white first (erase old qr)
cv2.fillConvexPoly(canvas,np.array([tl,tr,br,bl],np.int32),1)
ex=(tr-tl)/n; ey=(bl-tl)/n
for r in range(n):
    for c in range(n):
        if mat[r,c]==1:
            p0=tl+ex*c+ey*r; p1=tl+ex*(c+1)+ey*r; p2=tl+ex*(c+1)+ey*(r+1); p3=tl+ex*c+ey*(r+1)
            cv2.fillConvexPoly(canvas,np.array([p0,p1,p2,p3],np.int32),0)

# ---- thicken the tiny subtitle so it prints on a 0.2mm nozzle ----
white=(canvas==1).astype(np.uint8)
frac=white.mean(1); rp=np.where(frac>0.4)[0]
if len(rp):
    ptop=rp.min()
    y0=max(0,int(ptop-14*ppm)); y1=int(ptop-1.0*ppm)   # subtitle band above QR panel
    band=(canvas[y0:y1]==1).astype(np.uint8)
    band=cv2.dilate(band,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=1)
    seg=canvas[y0:y1]; seg[band>0]=1; canvas[y0:y1]=seg
    print(f"thickened subtitle band rows {y0}..{y1}")

# verify decode
pal=np.array([[31,17,10],[245,232,219],[160,88,41]],np.uint8)
prev=pal[canvas]
dec,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(prev,cv2.COLOR_RGB2BGR))
print("DECODE:",repr(dec),"OK" if dec==URL else "**MISMATCH**")
cv2.imwrite(f'{OUT}_design.png',cv2.cvtColor(prev,cv2.COLOR_RGB2BGR))

# ---- extrude 3 colors ----
R=4.0; BASE_Z=2.0; SKIN_Z=0.6
plate=box(R,R,Wmm-R,Hmm-R).buffer(R,join_style=1,resolution=24)
def px2mm(c):
    p=c.reshape(-1,2).astype(float); p[:,0]/=ppm; p[:,1]=(CH-p[:,1])/ppm; return p
def mask_geom(mask):
    cnts,hier=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hier is None: return None
    hier=hier[0]; polys=[]
    for i,c in enumerate(cnts):
        if hier[i][3]!=-1 or cv2.contourArea(c)<1: continue
        ext=px2mm(cv2.approxPolyDP(c,0.5,True))
        if len(ext)<3: continue
        holes=[]; ch=hier[i][2]
        while ch!=-1:
            hc=cnts[ch]
            if cv2.contourArea(hc)>=1:
                h=px2mm(cv2.approxPolyDP(hc,0.5,True))
                if len(h)>=3: holes.append(h)
            ch=hier[ch][0]
        try:
            pg=Polygon(ext,holes)
            if not pg.is_valid: pg=pg.buffer(0)
            if not pg.is_empty: polys.append(pg)
        except: pass
    if not polys: return None
    return simplify(unary_union(polys).intersection(plate),0.03).buffer(0)
def to_meshes(g,z0,h):
    if g is None or g.is_empty: return []
    gs=g.geoms if isinstance(g,MultiPolygon) else [g]; out=[]
    for x in gs:
        if x.is_empty or x.area<0.005: continue
        try:
            m=trimesh.creation.extrude_polygon(x,height=h); m.apply_translation([0,0,z0]); out.append(m)
        except: pass
    return out
colors={'brown':[78,52,38,255],'white':[245,232,219,255],'orange':[160,88,41,255]}
brown=[trimesh.creation.extrude_polygon(plate,height=BASE_Z)]
parts={'white':[],'orange':[]}
for val,name in {0:'brown',1:'white',2:'orange'}.items():
    ms=to_meshes(mask_geom((canvas==val).astype(np.uint8)*255),BASE_Z,SKIN_Z)
    (brown if name=='brown' else parts[name]).extend(ms)
parts['brown']=brown
scene=trimesh.Scene()
for name,ms in parts.items():
    mesh=trimesh.util.concatenate(ms); mesh.visual.face_colors=colors[name]
    mesh.export(f'{OUT}_{name}.stl')
    print(f"{name:6s} solids={len(ms):3d} faces={len(mesh.faces):5d} z={[round(b,1) for b in mesh.bounds[:,2]]}")
    scene.add_geometry(mesh,geom_name=name)
scene.export(f'{OUT}_plaque.3mf')
print("plaque bounds:",[round(v,1) for v in scene.extents])
