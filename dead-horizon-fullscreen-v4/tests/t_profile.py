import sys, json; sys.path.insert(0,'/home/claude')
from h import *
with sync_playwright() as p:
    b,ctx,pg = launch(p)
    box=start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.inv.ammo=99999;__DH.equip('pistol');__DH.spawn(18)")
    pg.evaluate("""(()=>{const d=__DH;window.__pf={};const wrap=(o,k,name)=>{const f=o[k];o[k]=function(...a){const t=performance.now();const r=f.apply(this,a);const e=performance.now()-t;const q=window.__pf[name]=window.__pf[name]||{n:0,t:0,m:0};q.n++;q.t+=e;q.m=Math.max(q.m,e);return r}};
      for(const k of ['drawLighting','drawShadows','drawDeaths','drawMotes','drawScreenFx','fxUpdate','step'])wrap(d.PA,k,'PA.'+k);wrap(d.FXP,'draw','FXP.draw');wrap(d.FXP,'update','FXP.update')})()""")
    pg.mouse.move(box["x"]+box["width"]*.8, box["y"]+box["height"]*.55)
    for i in range(10):
        pg.keyboard.down("KeyD")
        for _ in range(4): pg.mouse.up(); pg.mouse.down(); pg.wait_for_timeout(130)
        pg.keyboard.up("KeyD"); pg.keyboard.down("KeyA")
        for _ in range(4): pg.mouse.up(); pg.mouse.down(); pg.wait_for_timeout(130)
        pg.keyboard.up("KeyA")
    r=pg.evaluate("window.__pf"); tot=pg.evaluate("(()=>{const m=window.__DH_ms.slice(-400);return m.reduce((a,b)=>a+b,0)/m.length})()")
    for k,v in sorted(r.items(),key=lambda x:-x[1]['t']): print(f"{k:16s} avg {v['t']/v['n']:.3f} ms  max {v['m']:.2f} ms  calls {v['n']}")
    print("whole-frame JS avg:",round(tot,2),"ms")
    b.close()
