import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(name, ok, info=""): R[name]=("PASS" if ok else "FAIL", info); print(("PASS " if ok else "FAIL ")+name, info)
with sync_playwright() as p:
    b,ctx,pg = launch(p)
    box=start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.S.left=0;__DH.Z.length=0;__DH.S.fight=false")
    pg.mouse.move(box["x"]+box["width"]*.8, box["y"]+box["height"]*.5)
    # ---- footsteps ----
    pg.evaluate("__DH.AU.log.length=0;window.__st=[];window.__x0=__DH.P.x;(()=>{const d=__DH;let last=d.AU.log.length;const f=()=>{for(let i=last;i<d.AU.log.length;i++){const n=d.AU.log[i].n;if(n.startsWith('step_'))window.__st.push({n,state:d.PA.state,mv:Math.abs(d.PA.spd)})}last=d.AU.log.length;if(window.__stR)requestAnimationFrame(f)};window.__stR=true;requestAnimationFrame(f)})()")
    pg.keyboard.down("KeyD"); pg.wait_for_timeout(1600); pg.keyboard.up("KeyD")
    dist=pg.evaluate("__DH.P.x-window.__x0"); n1=pg.evaluate("window.__st.length")
    pg.wait_for_timeout(800); n2=pg.evaluate("window.__st.length")
    sts=pg.evaluate("window.__st")
    exp=dist/26
    chk("footsteps match distance run (≈1 per 26px)", n1>0 and abs(n1-exp)<=3, f"dist={dist:.0f}px steps={n1} expected≈{exp:.1f}")
    chk("footsteps stop when the character stops", n2==n1, f"steps at stop={n1}, 0.8s later={n2}")
    chk("every step happened while in the run state, never idle/air", all(s['state']=='run' for s in sts), str({s['state'] for s in sts}))
    land_run=pg.evaluate("__DH.AU.log.filter(x=>x.n==='land'||x.n==='jump').length")
    chk("running over terrain slopes triggers no false jump/land", land_run==0, f"jump/land events during plain running={land_run}")
    # run across several hills in both directions
    pg.evaluate("__DH.AU.log.length=0;__DH.PA.landings=0")
    pg.keyboard.down("KeyA"); pg.wait_for_timeout(2500); pg.keyboard.up("KeyA"); pg.keyboard.down("KeyD"); pg.wait_for_timeout(3500); pg.keyboard.up("KeyD")
    chk("no false landings across long slope traversal", pg.evaluate("__DH.PA.landings")==0 and pg.evaluate("__DH.AU.log.filter(x=>x.n==='land').length")==0, f"landings={pg.evaluate('__DH.PA.landings')}")
    # ---- single jump: exactly one takeoff, one landing ----
    pg.wait_for_timeout(500); pg.evaluate("__DH.AU.log.length=0;__DH.PA.landings=0;__DH.PA.takeoffs=0")
    pg.keyboard.down("Space"); pg.wait_for_timeout(90); pg.keyboard.up("Space"); pg.wait_for_timeout(1800)
    c=pg.evaluate("({j:__DH.AU.log.filter(x=>x.n==='jump').length,l:__DH.AU.log.filter(x=>x.n==='land').length,L:__DH.PA.landings,T:__DH.PA.takeoffs,st:__DH.PA.state})")
    chk("one jump = one takeoff + one landing (sound & effect), none repeated while grounded", c['j']==1 and c['l']==1 and c['L']==1 and c['T']==1 and c['st']=='idle', str(c))
    # ---- combat: voices, particles, cleanup ----
    pg.evaluate("__DH.own('machine');__DH.equip('machine');__DH.inv.ammo=99999;__DH.P.mag.machine=42;__DH.S.left=0")
    pg.evaluate("__DH.spawn(24);__DH.Z.forEach(z=>{z.hp=z.max=99999})")
    pg.evaluate("window.__mx={v:0,fx:0,pt:0};(()=>{const d=__DH;const f=()=>{window.__mx.v=Math.max(window.__mx.v,d.AU.voices());window.__mx.fx=Math.max(window.__mx.fx,d.FXP.count());window.__mx.pt=Math.max(window.__mx.pt,d.PT.length);if(window.__mxR)requestAnimationFrame(f)};window.__mxR=true;requestAnimationFrame(f)})();__DH.AU.log.length=0;__DH.AU.stats.dropped=0")
    pg.mouse.down()
    for i in range(6):
        pg.keyboard.down("KeyD" if i%2==0 else "KeyA"); pg.wait_for_timeout(700); pg.keyboard.up("KeyD" if i%2==0 else "KeyA")
    pg.mouse.up()
    mx=pg.evaluate("window.__mx"); lg=pg.evaluate("(()=>{const o={};__DH.AU.log.forEach(x=>o[x.n]=(o[x.n]||0)+1);return o})()")
    shots=lg.get('shot_smg',0)
    chk("voice cap respected during sustained automatic fire", mx['v']<=34, f"max simultaneous voices={mx['v']} (cap 34), dropped by limiter={pg.evaluate('__DH.AU.stats.dropped')}")
    chk("zombie ambient audio plays with distance (dx) attached", (lg.get('z_groan',0)+lg.get('z_rasp',0))>=1 and any(('dx' in x and x['dx'] is not None) for x in pg.evaluate("__DH.AU.log.filter(x=>x.n.startsWith('z_'))")), str({k:v for k,v in lg.items() if k.startswith('z_') or k.startswith('shot')}))
    # clear threats, wait, check nothing lingers
    pg.evaluate("__DH.Z.length=0;__DH.S.alive=0;__DH.S.left=0;__DH.B.length=0"); pg.wait_for_timeout(3500)
    pg.evaluate("window.__mxR=false")
    after=pg.evaluate("({fx:__DH.FXP.count(),deaths:__DH.DEATHS.length,lts:__DH.LTS.length,voices:__DH.AU.voices(),B:__DH.B.length,PT:__DH.PT.length,CS:__DH.CS.length})")
    chk("no lingering particles/lights/voices after combat ends", after['fx']==0 and after['deaths']==0 and after['lts']==0 and after['voices']<=1 and not pg.evaluate("__DH.AU.log.filter(x=>performance.now()-x.t>0&&!x.n.startsWith('amb_')&&performance.now()-x.t<2500).length"), f"(voices<=1 allows one ambient one-shot by design) peak FXP during combat={mx['fx']}/360, peak PT={mx['pt']}, after={after}")
    print("LOGS",pg.logs[:5])
    b.close()
json.dump(R,open('/home/claude/res_sync.json','w'))
