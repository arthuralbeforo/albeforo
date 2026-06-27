import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.affinity import translate

def _eo(polys):
    geom=None
    for p in polys:
        if len(p)<3: continue
        r=Polygon(p)
        if not r.is_valid: r=r.buffer(0)
        if r.is_empty: continue
        geom=r if geom is None else geom.symmetric_difference(r)
    return geom if geom is not None else Polygon()

def text_geom(text, font, size, tracking=0.0):
    fp=FontProperties(fname=font)
    if tracking==0.0:
        return _eo(TextPath((0,0),text,size=size,prop=fp).to_polygons())
    x=0.0; parts=[]
    for ch in text:
        if ch==' ':
            x+=size*0.34+tracking*size; continue
        tp=TextPath((0,0),ch,size=size,prop=fp)
        g=_eo(tp.to_polygons())
        ink=tp.get_extents().width
        if not g.is_empty:
            parts.append(translate(g,xoff=x-tp.get_extents().x0))
        x+=ink+size*0.16+tracking*size
    return unary_union(parts) if parts else Polygon()

def place_center(geom, cx, cy):
    minx,miny,maxx,maxy=geom.bounds
    return translate(geom, xoff=cx-(minx+maxx)/2, yoff=cy-(miny+maxy)/2)

def width_of(geom):
    minx,_,maxx,_=geom.bounds; return maxx-minx
