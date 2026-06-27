import sys, numpy as np, cv2, qrcode
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely.affinity import translate, scale
from vlib import text_geom, place_center, width_of

URL=sys.argv[1] if len(sys.argv)>1 else "https://app.tremdeminas.uk/menu/a9ca755a-b451-4786-91cb-a4630bbb17b2"
Wmm=float(sys.argv[2]) if len(sys.argv)>2 else 100.0
Hmm=float(sys.argv[3]) if len(sys.argv)>3 else 150.0
CX=Wmm/2
F=lambda n:f"fonts/{n}.ttf"
# scale all reference (measured at 100x150) layout by board factor
sx=Wmm/100.0; sy=Hmm/150.0
def Y(v): return v*sy
def X(v): return v*sx

plate=box(4*sx,4*sy,Wmm-4*sx,Hmm-4*sy).buffer(4*min(sx,sy),join_style=1,resolution=24)

white=[]; orange=[]
# 1) COUNTER | BALCAO  (orange, sans tracked)
g=text_geom("COUNTER | BALCÃO",F("Outfit-Regular"),X(4.6),tracking=0.12)
orange.append(place_center(g,CX,Y(131.5)))
# 2) Order & Pay  (Gloock; Order/Pay white, & orange)
go=text_geom("Order",F("Gloock-Regular"),X(8.6)); ga=text_geom("&",F("Gloock-Regular"),X(8.6)); gp=text_geom("Pay",F("Gloock-Regular"),X(8.6))
wo=width_of(go); wa=width_of(ga); wp=width_of(gp); sp=X(0.6)
tot=wo+sp+wa+sp+wp; x0=CX-tot/2
go=translate(go,xoff=x0-go.bounds[0]); 
ga=translate(ga,xoff=x0+wo+sp-ga.bounds[0])
gp=translate(gp,xoff=x0+wo+sp+wa+sp-gp.bounds[0])
# vertical align baselines: center group
grp=unary_union([go,ga,gp]); dy=Y(121.5)-(grp.bounds[1]+grp.bounds[3])/2
white.append(translate(go,yoff=dy)); white.append(translate(gp,yoff=dy)); orange.append(translate(ga,yoff=dy))
# 3) Faça seu pedido. (orange italic)
g=text_geom("Faça seu pedido.",F("Lora-Italic"),X(6.2))
orange.append(place_center(g,CX,Y(108.0)))
# 4) subtitle (white, Lora BoldItalic) two lines
g1=text_geom("Scan, order, relax.",F("Lora-BoldItalic"),X(3.7))
g2=text_geom("We bring it to your table.",F("Lora-BoldItalic"),X(3.7))
white.append(place_center(g1,CX,Y(100.6)))
white.append(place_center(g2,CX,Y(95.4)))
# 5) QR panel + modules
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=0); qr.add_data(URL); qr.make(fit=True)
mat=np.array(qr.get_matrix(),np.uint8); n=mat.shape[0]
qx0=X(24.43); qtopY=Y(84.30); mod=X(50.97)/n
panel=box(X(21.0),Y(29.7),X(78.9),Y(88.3)).buffer(X(2.2),join_style=1,resolution=16)
darks=[]
for r in range(n):
    for c in range(n):
        if mat[r,c]==1:
            x=qx0+c*mod; ytop=qtopY-r*mod
            darks.append(box(x,ytop-mod,x+mod,ytop))
darkU=unary_union(darks)
white.append(panel.difference(darkU))   # panel white, dark modules cut out -> brown shows
# 6) Instagram pill + icon + handle
pill=box(X(27.95),Y(18.4),X(71.5),Y(26.2)); pill=pill.buffer((Y(26.2)-Y(18.4))/2,join_style=1,resolution=24).intersection(box(X(20),Y(18.4),X(80),Y(26.2)).buffer(10))
pill=box(X(27.95)+ (Y(26.2)-Y(18.4))/2, Y(18.4), X(71.5)-(Y(26.2)-Y(18.4))/2, Y(26.2)).buffer((Y(26.2)-Y(18.4))/2,join_style=1,resolution=24)
pcy=(Y(18.4)+Y(26.2))/2
# IG icon (white): rounded square frame + ring + dot, ~5mm
isz=X(4.9); icx=X(33.5); icy=pcy
rad=isz*0.27
fr_out=box(icx-isz/2+rad,icy-isz/2+rad,icx+isz/2-rad,icy+isz/2-rad).buffer(rad,join_style=1,resolution=16)  # rounded square
fr_in=fr_out.buffer(-isz*0.135)
frame=fr_out.difference(fr_in)
ring=Point(icx,icy).buffer(isz*0.265).difference(Point(icx,icy).buffer(isz*0.265-isz*0.125))
dot=Point(icx+isz*0.255,icy+isz*0.255).buffer(isz*0.072)
ig=unary_union([frame,ring,dot])
# handle text
ht=text_geom("@tremdeminas_uk",F("Outfit-Regular"),X(3.5))
ht=place_center(ht,X(33.5)+isz/2+X(2.0)+width_of(ht)/2 - 0 , pcy)
# recenter group (icon+text) within pill horizontally
grp2=unary_union([ig,ht]); gx=(grp2.bounds[0]+grp2.bounds[2])/2; shift=CX-gx
ig=translate(ig,xoff=shift); ht=translate(ht,xoff=shift)
orange.append(pill)
white.append(ig); white.append(ht)

W=unary_union(white).buffer(0)
O=unary_union(orange).buffer(0).difference(W)          # white wins overlaps
W=W.intersection(plate); O=O.intersection(plate)
brownTop=plate.difference(W).difference(O)

# ---------- raster preview + QR decode ----------
PP=22
def raster(geom,img,color,bg):
    if geom.is_empty: return
    geoms=geom.geoms if geom.geom_type.startswith('Multi') else [geom]
    for g in geoms:
        if g.geom_type!='Polygon': continue
        ext=np.array(g.exterior.coords); ext[:,0]*=PP; ext[:,1]=(Hmm-ext[:,1])*PP
        cv2.fillPoly(img,[ext.astype(np.int32)],color)
        for ir in g.interiors:
            h=np.array(ir.coords); h[:,0]*=PP; h[:,1]=(Hmm-h[:,1])*PP
            cv2.fillPoly(img,[h.astype(np.int32)],bg)
brown=(31,17,10); cream=(245,232,219); orng=(160,88,41)
img=np.zeros((int(Hmm*PP),int(Wmm*PP),3),np.uint8); img[:]=brown
raster(plate,img,brown,brown)
raster(O,img,orng,brown)
raster(W,img,cream,brown)
cv2.imwrite('vec_design.png',cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
d,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
print("QR decode:",repr(d),"OK" if d==URL else "MISMATCH")

import pickle
pickle.dump({'plate':plate,'W':W,'O':O,'brownTop':brownTop},open('vec_geom.pkl','wb'))
print("saved vec_geom.pkl ; module mm",round(mod,2))
