import cv2, numpy as np, trimesh
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import simplify

ppm=12.0
canvas=np.load('label_canvas.npy'); CH,CW=canvas.shape
Wmm,Hmm=CW/ppm,CH/ppm
R=6.0; BASE_Z=2.4; SKIN_Z=0.6
plate=box(R,R,Wmm-R,Hmm-R).buffer(R,join_style=1,resolution=24)

def px2mm(c):
    p=c.reshape(-1,2).astype(float); p[:,0]/=ppm; p[:,1]=(CH-p[:,1])/ppm; return p
def mask_to_geom(mask):
    cnts,hier=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hier is None: return None
    hier=hier[0]; polys=[]
    for i,c in enumerate(cnts):
        if hier[i][3]!=-1 or cv2.contourArea(c)<2: continue
        ext=px2mm(cv2.approxPolyDP(c,0.6,True))
        if len(ext)<3: continue
        holes=[]; ch=hier[i][2]
        while ch!=-1:
            hc=cnts[ch]
            if cv2.contourArea(hc)>=2:
                h=px2mm(cv2.approxPolyDP(hc,0.6,True))
                if len(h)>=3: holes.append(h)
            ch=hier[ch][0]
        try:
            pg=Polygon(ext,holes)
            if not pg.is_valid: pg=pg.buffer(0)
            if not pg.is_empty: polys.append(pg)
        except: pass
    if not polys: return None
    g=simplify(unary_union(polys).intersection(plate),0.04)
    return g.buffer(0)
def to_meshes(g,z0,h):
    if g is None or g.is_empty: return []
    gs=g.geoms if isinstance(g,MultiPolygon) else [g]; out=[]
    for x in gs:
        if x.is_empty or x.area<0.01: continue
        try:
            m=trimesh.creation.extrude_polygon(x,height=h); m.apply_translation([0,0,z0]); out.append(m)
        except Exception as e: print("  warn",e)
    return out

colors={'brown':[78,52,38,255],'white':[245,232,219,255],'orange':[160,88,41,255]}
brown=[trimesh.creation.extrude_polygon(plate,height=BASE_Z)]
parts={'white':[], 'orange':[]}
for val,name in {0:'brown',1:'white',2:'orange'}.items():
    ms=to_meshes(mask_to_geom((canvas==val).astype(np.uint8)*255),BASE_Z,SKIN_Z)
    (brown if name=='brown' else parts[name]).extend(ms)
parts['brown']=brown

scene=trimesh.Scene()
for name,ms in parts.items():
    wt=sum(m.is_watertight for m in ms)
    mesh=trimesh.util.concatenate(ms)
    mesh.visual.face_colors=colors[name]
    mesh.export(f'order_pay_{name}.stl')
    print(f"{name:6s}: solids={len(ms):3d} watertight={wt:3d}/{len(ms)} faces={len(mesh.faces):5d} z=[{mesh.bounds[0,2]:.1f},{mesh.bounds[1,2]:.1f}] vol={mesh.volume:.0f}mm3")
    scene.add_geometry(mesh,geom_name=name)
scene.export('order_pay_qr_3mf.3mf')
print("scene bounds:",[[round(v,1) for v in r] for r in scene.bounds.tolist()])
