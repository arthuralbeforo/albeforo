import sys, numpy as np, cv2, qrcode
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely.affinity import translate
from vlib import text_geom, place_center, width_of

URL=sys.argv[1] if len(sys.argv)>1 else "https://app.tremdeminas.uk/menu/a9ca755a-b451-4786-91cb-a4630bbb17b2"
Wmm=float(sys.argv[2]) if len(sys.argv)>2 else 100.0
Hmm=float(sys.argv[3]) if len(sys.argv)>3 else 150.0
CX=Wmm/2
F=lambda n:f"fonts/{n}.ttf"
sx=Wmm/100.0; sy=Hmm/150.0
def X(v): return v*sx
def Y(v): return v*sy

plate=box(4*sx,4*sy,Wmm-4*sx,Hmm-4*sy).buffer(4*min(sx,sy),join_style=1,resolution=24)
white=[]; orange=[]

# 1) COUNTER | BALCAO (orange, sans tracked)
g=text_geom("COUNTER | BALCÃO",F("Outfit-Regular"),X(5.3),tracking=0.12)
orange.append(place_center(g,CX,Y(140.0)))
# 2) Order & Pay (Gloock)
sz=X(10.6)
go=text_geom("Order",F("Gloock-Regular"),sz); ga=text_geom("&",F("Gloock-Regular"),sz); gp=text_geom("Pay",F("Gloock-Regular"),sz)
wo=width_of(go); wa=width_of(ga); wp=width_of(gp); sp=X(0.7)
tot=wo+sp+wa+sp+wp; x0=CX-tot/2
go=translate(go,xoff=x0-go.bounds[0])
ga=translate(ga,xoff=x0+wo+sp-ga.bounds[0])
gp=translate(gp,xoff=x0+wo+sp+wa+sp-gp.bounds[0])
grp=unary_union([go,ga,gp]); dy=Y(128.5)-(grp.bounds[1]+grp.bounds[3])/2
white.append(translate(go,yoff=dy)); white.append(translate(gp,yoff=dy)); orange.append(translate(ga,yoff=dy))
# 3) Faça seu pedido. (orange italic)
g=text_geom("Faça seu pedido.",F("Lora-Italic"),X(7.2))
orange.append(place_center(g,CX,Y(112.5)))
# 4) subtitle (white Lora BoldItalic)
g1=text_geom("Scan, order, relax.",F("Lora-BoldItalic"),X(4.4))
g2=text_geom("We bring it to your table.",F("Lora-BoldItalic"),X(4.4))
white.append(place_center(g1,CX,Y(104.0)))
white.append(place_center(g2,CX,Y(98.2)))
# 5) QR panel + modules (bigger, centered)
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=0); qr.add_data(URL); qr.make(fit=True)
mat=np.array(qr.get_matrix(),np.uint8); n=mat.shape[0]
qr_w=X(60.0); mod=qr_w/n
qr_top=Y(90.5); qx0=CX-qr_w/2
panel=box(qx0-X(3.2),qr_top-qr_w-X(3.2),qx0+qr_w+X(3.2),qr_top+X(3.2)).buffer(X(3.0),join_style=1,resolution=20)
darks=[]
for r in range(n):
    for c in range(n):
        if mat[r,c]==1:
            x=qx0+c*mod; ytop=qr_top-r*mod
            darks.append(box(x,ytop-mod,x+mod,ytop))
white.append(panel.difference(unary_union(darks)))
# 6) Instagram pill fitted to content (icon + handle), bigger
isz=X(6.2); pcy=Y(14.0)
def ig_icon(icx):
    rad=isz*0.27
    out=box(icx-isz/2+rad,pcy-isz/2+rad,icx+isz/2-rad,pcy+isz/2-rad).buffer(rad,join_style=1,resolution=16)
    frame=out.difference(out.buffer(-isz*0.135))
    ring=Point(icx,pcy).buffer(isz*0.265).difference(Point(icx,pcy).buffer(isz*0.265-isz*0.125))
    dot=Point(icx+isz*0.255,pcy+isz*0.255).buffer(isz*0.072)
    return unary_union([frame,ring,dot])
ht=text_geom("@tremdeminas_uk",F("Outfit-Regular"),X(4.6))
htw=width_of(ht); gap=X(2.6); padx=X(5.0)
content_w=isz+gap+htw
gx0=CX-content_w/2
ig=ig_icon(gx0+isz/2)
ht=place_center(ht,gx0+isz+gap+htw/2,pcy)
pill_h=isz+X(3.4)
pill=box(gx0-padx+pill_h/2, pcy-pill_h/2, gx0+content_w+padx-pill_h/2, pcy+pill_h/2).buffer(pill_h/2,join_style=1,resolution=24)
orange.append(pill); white.append(ig); white.append(ht)

W=unary_union(white).buffer(0)
O=unary_union(orange).buffer(0).difference(W)
W=W.intersection(plate); O=O.intersection(plate)
brownTop=plate.difference(W).difference(O)

PP=22
def raster(geom,img,color,bg):
    if geom.is_empty: return
    gs=geom.geoms if geom.geom_type.startswith('Multi') else [geom]
    for g in gs:
        if g.geom_type!='Polygon': continue
        e=np.array(g.exterior.coords); e[:,0]*=PP; e[:,1]=(Hmm-e[:,1])*PP
        cv2.fillPoly(img,[e.astype(np.int32)],color)
        for ir in g.interiors:
            h=np.array(ir.coords); h[:,0]*=PP; h[:,1]=(Hmm-h[:,1])*PP
            cv2.fillPoly(img,[h.astype(np.int32)],bg)
brown=(31,17,10); cream=(245,232,219); orng=(160,88,41)
img=np.zeros((int(Hmm*PP),int(Wmm*PP),3),np.uint8); img[:]=brown
raster(plate,img,brown,brown); raster(O,img,orng,brown); raster(W,img,cream,brown)
cv2.imwrite('vec_design.png',cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
d,_,_=cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
print("QR decode:",repr(d),"OK" if d==URL else "MISMATCH","| module mm",round(mod,2))
import pickle; pickle.dump({'plate':plate,'W':W,'O':O,'brownTop':brownTop},open('vec_geom.pkl','wb'))
