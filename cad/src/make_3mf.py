import trimesh, numpy as np, zipfile, json, sys
ID3="1 0 0 0 1 0 0 0 1 0 0 0"
MAT="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"
def mesh_xml(oid,m):
    vt="".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x,y,z in m.vertices)
    tr="".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in m.faces)
    return f'  <object id="{oid}" type="model"><mesh><vertices>{vt}</vertices><triangles>{tr}</triangles></mesh></object>'
def build(path, with_stand):
    parts=[('brown',1),('white',2),('orange',3)]
    objs=[]; comps=[]; cparts=[]; oid=1
    for name,extr in parts:
        objs.append(mesh_xml(oid,trimesh.load(f'final_{name}.stl')))
        comps.append(f'<component objectid="{oid}" transform="{ID3}"/>')
        cparts.append(f'  <part id="{oid}" subtype="normal_part"><metadata key="name" value="{name}"/><metadata key="matrix" value="{MAT}"/><metadata key="source_file" value="{name}.stl"/><metadata key="extruder" value="{extr}"/></part>')
        oid+=1
    ASM=oid; oid+=1
    cfg_objs=[f' <object id="{ASM}">\n  <metadata key="name" value="OrderAndPay"/>\n'+"\n".join(cparts)+'\n </object>']
    asm_objs=[f'  <object id="{ASM}" type="model"><components>{"".join(comps)}</components></object>']
    items=[f'<item objectid="{ASM}" transform="{ID3}" printable="1"/>']
    if with_stand:
        st=trimesh.load('order_pay_stand.stl'); st.apply_translation([120,0,0])
        sid=oid; oid+=1; objs.append(mesh_xml(sid,st))
        ASM2=oid; oid+=1
        asm_objs.append(f'  <object id="{ASM2}" type="model"><components><component objectid="{sid}" transform="{ID3}"/></components></object>')
        items.append(f'<item objectid="{ASM2}" transform="{ID3}" printable="1"/>')
        cfg_objs.append(f' <object id="{ASM2}">\n  <metadata key="name" value="Suporte"/>\n  <part id="{sid}" subtype="normal_part"><metadata key="name" value="stand"/><metadata key="matrix" value="{MAT}"/><metadata key="extruder" value="1"/></part>\n </object>')
    model=('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n <resources>\n'
           +"\n".join(objs+asm_objs)+'\n </resources>\n <build>'+"".join(items)+'</build>\n</model>')
    mcfg='<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'+"\n".join(cfg_objs)+'\n</config>'
    proj=json.dumps({"filament_colour":["#4E3426","#F5E8DB","#A05829"],"filament_type":["PLA","PLA","PLA"],"wall_loops":"3"})
    ct='<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels='<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',ct); z.writestr('_rels/.rels',rels)
        z.writestr('3D/3dmodel.model',model); z.writestr('Metadata/model_settings.config',mcfg)
        z.writestr('Metadata/project_settings.config',proj)
    print("wrote",path)
build('order_pay_plaque.3mf',False)
build('order_pay_set_100x150.3mf',True)
