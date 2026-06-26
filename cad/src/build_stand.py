import sys, numpy as np, trimesh, math
from shapely.geometry import Polygon
# args: plaque_w plaque_h plaque_t  (mm)
PW=float(sys.argv[1]) if len(sys.argv)>1 else 100.0
PH=float(sys.argv[2]) if len(sys.argv)>2 else 150.0
PT=float(sys.argv[3]) if len(sys.argv)>3 else 2.6
clear=0.5; s=PT+clear
theta=math.radians(13)
# scale base depth with plaque height so a taller plaque won't tip
D=max(42.0, round(PH*0.34,1))
stand_W=round(PW*0.88,1)
backH=max(28.0, round(PH*0.24,1))
floor=2.5; frontShelf=4.0
# outer solid side-profile (y=depth, z=height)
solid=Polygon([(0,0),(D,0),(D,backH),(D*0.42,frontShelf),(0,frontShelf)])
u=np.array([math.sin(theta),math.cos(theta)])
n=np.array([math.cos(theta),-math.sin(theta)])
P0=np.array([D*0.34,floor]); L=backH+8; P1=P0+u*L
h=(s/2)*n
slot=Polygon([P0-h,P0+h,P1+h,P1-h])
prof=solid.difference(slot)
mesh=trimesh.creation.extrude_polygon(prof,height=stand_W)
mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90),[1,0,0]))
mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90),[0,0,1]))
mesh.apply_translation(-mesh.bounds[0])
mesh.visual.face_colors=[120,80,55,255]
mesh.export('order_pay_stand.stl')
print(f"stand for plaque {PW}x{PH}: size {[round(v,1) for v in mesh.extents]}mm watertight={mesh.is_watertight}")

# side profile diagram with plaque
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(5,5)); xs,ys=prof.exterior.xy; ax.fill(xs,ys,color='#8a6a4b',alpha=.9,label='suporte')
botC=P0; top=botC+u*PH; pn=n
b1=botC+pn*(PT/2); b2=botC-pn*(PT/2); t1=top+pn*(PT/2); t2=top-pn*(PT/2)
ax.fill([b1[0],b2[0],t2[0],t1[0]],[b1[1],b2[1],t2[1],t1[1]],color='#3a2418',alpha=.85,label=f'placa {int(PH)}mm')
ax.set_aspect('equal'); ax.set_xlabel('profundidade (mm)'); ax.set_ylabel('altura (mm)')
ax.set_title('Perfil do suporte + placa'); ax.legend(loc='upper right',fontsize=8); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig('stand_profile.png',dpi=110)
print("saved stand_profile.png")
