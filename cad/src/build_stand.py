import numpy as np, trimesh, math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

# ---- parameters (mm) ----
PLAQUE_W=70.0; PLAQUE_T=3.0
clear=0.5; s=PLAQUE_T+clear           # slot width 3.5
theta=math.radians(13)                # lean from vertical
D=42.0                                # base depth
stand_W=78.0                          # width (plaque 70 + play)
floor=2.5                             # solid floor under slot (plaque rests here)

# outer solid side-profile (y=depth, z=height), CCW
solid=Polygon([(0,0),(D,0),(D,27),(18,4),(0,4)])

# slot rectangle leaning back
u=np.array([math.sin(theta),math.cos(theta)])     # bottom->top dir
n=np.array([math.cos(theta),-math.sin(theta)])    # in-plane normal
P0=np.array([15.0,floor]); L=32.0; P1=P0+u*L
h=(s/2)*n
slot=Polygon([P0-h,P0+h,P1+h,P1-h])

prof=solid.difference(slot)
print("profile area",round(prof.area,1),"valid",prof.is_valid)

# extrude along X (width)
mesh=trimesh.creation.extrude_polygon(prof,height=stand_W)
# extrude_polygon extrudes in +Z of the polygon's plane (x=y,y=z) -> need orient:
# Our polygon is in (Y,Z); extrude_polygon treats poly coords as (X,Y) and extrudes Z.
# So result has X=depth, Y=height, Z=width. Rotate to put depth->Y, height->Z, width->X.
T=trimesh.transformations.rotation_matrix(math.radians(90),[1,0,0])
mesh.apply_transform(T)
# now align: rotate about z to make width along X
T2=trimesh.transformations.rotation_matrix(math.radians(90),[0,0,1])
mesh.apply_transform(T2)
mesh.apply_translation(-mesh.bounds[0])
print("stand bounds(mm) X,Y,Z:",[round(v,1) for v in mesh.extents])
mesh.visual.face_colors=[120,80,55,255]
mesh.export('order_pay_stand.stl')
print("watertight",mesh.is_watertight,"vol",round(mesh.volume,0))

# ---- side-profile diagram with plaque drawn ----
fig,ax=plt.subplots(figsize=(5,5))
xs,ys=prof.exterior.xy; ax.fill(xs,ys,color='#8a6a4b',alpha=.9,label='suporte')
# plaque: leaning, bottom at slot floor center
pc=P0+u*0.0
pdir=u; pn=n
base_c=P0+u*(0)  # bottom center of plaque in slot
botC=P0
plate_len=105
top=botC+u*plate_len
for off in (-PLAQUE_T/2,PLAQUE_T/2):
    pass
b1=botC+pn*(PLAQUE_T/2); b2=botC-pn*(PLAQUE_T/2)
t1=top+pn*(PLAQUE_T/2);  t2=top-pn*(PLAQUE_T/2)
ax.fill([b1[0],b2[0],t2[0],t1[0]],[b1[1],b2[1],t2[1],t1[1]],color='#3a2418',alpha=.85,label='placa 105mm')
ax.set_aspect('equal'); ax.set_xlabel('profundidade (mm)'); ax.set_ylabel('altura (mm)')
ax.set_title('Perfil lateral do suporte + placa'); ax.legend(loc='upper right',fontsize=8)
ax.grid(alpha=.3); plt.tight_layout(); plt.savefig('stand_profile.png',dpi=110)
print("saved stand_profile.png")
