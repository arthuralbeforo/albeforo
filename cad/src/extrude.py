import pickle, numpy as np, trimesh
from shapely.geometry import MultiPolygon, GeometryCollection
d=pickle.load(open('vec_geom.pkl','rb'))
plate=d['plate']; W=d['W']; O=d['O']; BT=d['brownTop']
BASE_Z=2.4; SKIN=0.6   # solid brown 0..2.4 ; flush colored top 2.4..3.0 ; total 3.0
def polys(g):
    if g.is_empty: return []
    if isinstance(g,(MultiPolygon,GeometryCollection)): return [x for x in g.geoms if x.geom_type=='Polygon' and x.area>1e-4]
    return [g] if g.geom_type=='Polygon' else []
def extrude(g,z0,h):
    out=[]
    for p in polys(g):
        try:
            m=trimesh.creation.extrude_polygon(p,height=h); m.apply_translation([0,0,z0]); out.append(m)
        except Exception as e: print("warn",e)
    return out
colors={'brown':[78,52,38,255],'white':[245,232,219,255],'orange':[160,88,41,255]}
# brown = full solid slab 0..2.4  +  background ring 2.4..3.0 (tiles the top with W,O)
brown=[trimesh.creation.extrude_polygon(plate,height=BASE_Z)]+extrude(BT,BASE_Z,SKIN)
parts={'brown':brown,'white':extrude(W,BASE_Z,SKIN),'orange':extrude(O,BASE_Z,SKIN)}
scene=trimesh.Scene()
for name,ms in parts.items():
    mesh=trimesh.util.concatenate(ms); mesh.visual.face_colors=colors[name]
    mesh.export(f'final_{name}.stl')
    print(f"{name:6s} solids={len(ms):3d} faces={len(mesh.faces):5d} z={[round(b,1) for b in mesh.bounds[:,2]]}")
    scene.add_geometry(mesh,geom_name=name)
scene.export('final_plaque.3mf'); print("extents",[round(v,1) for v in scene.extents])
