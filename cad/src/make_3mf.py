import trimesh, numpy as np, zipfile, sys
# builds a single-object multi-volume 3MF (brown=ext1, white=ext2, orange=ext3) + optional stand object
def obj_xml(oid, V, F):
    vt="\n".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x,y,z in V)
    tr="\n".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in F)
    return f'  <object id="{oid}" type="model"><mesh><vertices>\n{vt}\n</vertices><triangles>\n{tr}\n</triangles></mesh></object>'
def build(path, with_stand):
    order=['brown','white','orange']; extr={'brown':1,'white':2,'orange':3}
    V=[];F=[];ranges={};voff=0;foff=0
    for n in order:
        m=trimesh.load(f'final_{n}.stl'); v=m.vertices; f=m.faces+voff
        ranges[n]=(foff,foff+len(f)-1); V.append(v); F.append(f); voff+=len(v); foff+=len(f)
    V=np.vstack(V); F=np.vstack(F)
    objects=[obj_xml(1,V,F)]
    items=['<item objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>']
    cfg_objs=['<object id="1">\n  <metadata type="object" key="name" value="Order&amp;Pay"/>\n'+
              "\n".join(f'  <volume firstid="{ranges[n][0]}" lastid="{ranges[n][1]}"><metadata type="volume" key="name" value="{n}"/><metadata type="volume" key="extruder" value="{extr[n]}"/></volume>' for n in order)+
              '\n </object>']
    if with_stand:
        st=trimesh.load('order_pay_stand.stl'); sv=st.vertices.copy(); sv[:,0]+=110  # beside plaque
        objects.append(obj_xml(2,sv,st.faces))
        items.append('<item objectid="2" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
        cfg_objs.append('<object id="2">\n  <metadata type="object" key="name" value="Suporte"/>\n  <volume firstid="0" lastid="%d"><metadata type="volume" key="name" value="stand"/><metadata type="volume" key="extruder" value="1"/></volume>\n </object>'%(len(st.faces)-1))
    model='<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06">\n <resources>\n'+"\n".join(objects)+'\n </resources>\n <build>'+"".join(items)+'</build>\n</model>'
    cfg='<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'+"\n".join(cfg_objs)+'\n</config>'
    ct='<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels='<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',ct); z.writestr('_rels/.rels',rels)
        z.writestr('3D/3dmodel.model',model); z.writestr('Metadata/Slic3r_PE_model.config',cfg)
    print("wrote",path)
build('order_pay_plaque.3mf',False)
build('order_pay_set_100x150.3mf',True)
