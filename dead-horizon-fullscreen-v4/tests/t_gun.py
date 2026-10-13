import sys, json; sys.path.insert(0,'/home/claude')
from h import *
from PIL import Image
import io
RANGED=["pistol","revolver","burst","heavy","smg","tactical","machine","shotgun","double","autoShot","rifle","tacticalRifle","sniper","launcher","flamethrower","crossbow"]
JS_WAIT = """()=>new Promise(res=>{const d=__DH;const sh0=window.__sh0;let f=0;
 const t=()=>{f++;if((d.PA.shots||0)>sh0){const m=d.PA.lastMuz,out=[];
   for(const b of d.B){if(b._o)continue;const sp=Math.hypot(b.vx,b.vy),ux=b.vx/sp,uy=b.vy/sp,rx=b.x-m.x,ry=b.y-m.y;
     out.push({dist:Math.hypot(rx,ry),cross:Math.abs(rx*uy-ry*ux),dot:rx*ux+ry*uy,sp,a:Math.atan2(b.vy,b.vx)})}
   res({muz:m,aim:d.P.aim,dir:d.P.dir,kick:d.PA.kick,kickR:d.PA.kickR,flK:d.PA.flK,flash:d.P.flash,bul:out.slice(0,3),n:d.B.length,snd:d.AU.log.slice(-3).map(x=>x.n),mag:d.P.mag[d.P.wp]});return}
   if(f>40){res({timeout:1,rl:d.P.rl,mag:d.P.mag[d.P.wp],cd:d.P.cd,wp:d.P.wp,down:d.mouse.down});return}requestAnimationFrame(t)};requestAnimationFrame(t)})"""
with sync_playwright() as p:
    b,ctx,pg = launch(p, 1280, 720)
    box = start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.S.left=0;__DH.Z.length=0")
    for w in RANGED: pg.evaluate(f"__DH.own('{w}')")
    pg.evaluate("for(const k of Object.keys(__DH.inv))if(typeof __DH.inv[k]==='number')__DH.inv[k]=999")
    results={}; frames=[]
    angles=[(0.78,0.45),(0.9,0.62),(0.22,0.55)]  # right-up, right-flat, left-down(ish)
    for w in RANGED:
        pg.evaluate(f"__DH.equip('{w}');__DH.P.cd=0;__DH.P.rl=0;__DH.P.mag['{w}']=__DH.P.mag['{w}']||5;__DH.P.mag['{w}']=Math.max(__DH.P.mag['{w}'],3)")
        wres=[]
        for (ax,ay) in angles:
            pg.mouse.move(box["x"]+box["width"]*ax, box["y"]+box["height"]*ay); pg.wait_for_timeout(120)
            pg.evaluate("__DH.P.cd=0;__DH.P.rl=0;__DH.PA.kick=0;__DH.PA.kickR=0")
            pg.evaluate("window.__sh0=__DH.PA.shots||0;for(const b of __DH.B)b._o=1")
            pg.mouse.down()
            r = pg.evaluate(JS_WAIT)
            pg.mouse.up()
            wres.append(r); pg.wait_for_timeout(60)
        results[w]=wres
    # summarise
    bad=[]
    for w,rs in results.items():
        for r in rs:
            if r.get('timeout'): bad.append((w,'no shot',r)); continue
            for bl in r['bul']:
                # origin check: bullet must lie on the line through muzzle along its velocity and within ~2 substeps of travel
                if bl['cross']>2 or bl['dot']<-1 or bl['dist']>bl['sp']*0.12: bad.append((w,'origin',round(bl['cross'],2),round(bl['dist'],1),round(bl['sp'])))
            if r['kick']<=0 or r['flK']<0: bad.append((w,'kick'))
    print("weapons tested:",len(results),"| shots:",sum(len(v) for v in results.values()))
    print("origin/recoil failures:",bad if bad else "none")
    print("sample pistol:",json.dumps(results['pistol'][1])[:420])
    print("sample shotgun:",json.dumps(results['shotgun'][1])[:420])
    print("sounds seen:",sorted({s for rs in results.values() for r in rs for s in r.get('snd',[])}))
    print("LOGS",pg.logs[:6])
    b.close()
