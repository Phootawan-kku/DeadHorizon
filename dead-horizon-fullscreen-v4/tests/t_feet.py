import sys, json; sys.path.insert(0,'/home/claude')
from h import *
from PIL import Image
import io, numpy as np
with sync_playwright() as p:
    b,ctx,pg = launch(p,1280,720); box=start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.S.left=0;__DH.Z.length=0;__DH.S.fight=false")
    pg.mouse.move(box["x"]+box["width"]*.8, box["y"]+box["height"]*.5)
    # ---------- foot-slide measurement ----------
    pg.evaluate("""window.__f=[];(()=>{const d=__DH;const f=()=>{const R=d.PA.R;window.__f.push([performance.now(),d.P.x,R.lL,R.lR,R.liL,R.liR,d.PA.state==='run'?1:0]);if(window.__fr)requestAnimationFrame(f)};window.__fr=true;requestAnimationFrame(f)})()""")
    pg.keyboard.down("KeyD"); pg.wait_for_timeout(2500); pg.keyboard.up("KeyD"); pg.evaluate("window.__fr=false")
    fr=pg.evaluate("window.__f"); import math
    L=20.0; segs=[]; 
    for foot,(piv,ia,il) in {'L':(-6.25,2,4),'R':(4.5,3,5)}.items():
        cur=[]
        for t,x,lL,lR,liL,liR,run in fr:
            th=[lL,lR][ia-2]; lift=[liL,liR][il-4]
            fx=x+piv-L*math.sin(th)
            if run and lift<.05: cur.append((t,fx))
            else:
                if len(cur)>=4: segs.append(cur)
                cur=[]
    dev=[]; 
    for sgm in segs:
        x0=sgm[0][1]; xs=[v for _,v in sgm]
        # deviation from a perfectly planted foot (fx constant) = max |fx - mean|; slide speed = slope
        m=sum(xs)/len(xs); dev.append(max(abs(v-m) for v in xs))
    print(f"foot-slide: {len(segs)} stance segments, max drift from planted position = {max(dev):.2f}px, mean = {sum(dev)/len(dev):.2f}px (sprite px; 1 sprite px = 1.25 canvas px)")
    # ---------- idle is not frozen ----------
    pg.wait_for_timeout(600)
    frames=[]
    for i in range(14):
        sx=pg.evaluate("Math.round(__DH.P.x-__DH.cx)"); y=pg.evaluate("Math.round(__DH.P.y)"); sc=box["width"]/960
        png=pg.screenshot(clip={"x":box["x"]+(sx-24)*sc,"y":box["y"]+(y-62)*sc,"width":48*sc,"height":70*sc})
        frames.append(np.asarray(Image.open(io.BytesIO(png)).convert("L"),dtype=np.int16)); pg.wait_for_timeout(180)
    st=pg.evaluate("__DH.PA.state"); base=frames[0]
    diffs=[int((np.abs(f-base)>25).sum()) for f in frames[1:]]
    print("idle state:",st,"| pixels changed vs first frame over 2.5s (threshold>25):",diffs)
    print("console:",pg.logs[:3]); b.close()
