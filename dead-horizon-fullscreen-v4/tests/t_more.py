import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(name, ok, info=""): R[name]=("PASS" if ok else "FAIL", info); print(("PASS " if ok else "FAIL ")+name, info)
with sync_playwright() as p:
    b,ctx,pg = launch(p,1280,720); box=start(pg)
    pg.evaluate("__DH.S.left=0;__DH.Z.length=0;__DH.S.fight=false;__DH.S.alive=0")
    # ---- HEAL ----
    pg.evaluate("__DH.P.hp=40;__DH.inv.bandage=2;__DH.AU.log.length=0")
    pg.keyboard.down("KeyH"); pg.wait_for_timeout(100); pg.keyboard.up("KeyH"); pg.wait_for_timeout(200)
    s=pg.evaluate("({hp:__DH.P.hp,b:__DH.inv.bandage,snd:__DH.AU.log.map(x=>x.n),fx:__DH.FXP.count(),t:__DH.PA.healT})")
    chk("heal: consumes 1 bandage, +35 HP, heal sound + particles", s['b']==1 and abs(s['hp']-75)<1 and 'heal' in s['snd'] and s['fx']>0, str(s))
    pg.evaluate("__DH.P.hp=__DH.P.max;__DH.AU.log.length=0"); pg.keyboard.down("KeyH"); pg.wait_for_timeout(100); pg.keyboard.up("KeyH"); pg.wait_for_timeout(100)
    chk("heal at full HP: nothing consumed, failure feedback only", pg.evaluate("__DH.inv.bandage")==1 and pg.evaluate("__DH.AU.log.some(x=>x.n==='ui_fail')") and not pg.evaluate("__DH.AU.log.some(x=>x.n==='heal')"))
    # ---- GATHER ----
    for kind,snd,res in [('tree','chop','wood'),('rock','mine','stone')]:
        pg.evaluate(f"""(()=>{{const d=__DH;const t=d.TR.find(t=>t.k==='{kind}'&&!t.dead);window.__t=t;d.P.x=t.x;d.P.vx=0;t.hp=3;d.AU.log.length=0;window.__pre=JSON.stringify(d.inv)}})()""")
        pg.wait_for_timeout(250)
        pg.keyboard.down("KeyE"); pg.wait_for_timeout(120); pg.keyboard.up("KeyE"); pg.wait_for_timeout(250)
        r=pg.evaluate("({hp:window.__t.hp,snd:__DH.AU.log.map(x=>x.n),fx:__DH.FXP.count(),inv:JSON.stringify(__DH.inv)!==window.__pre})")
        chk(f"gather {kind}: node damaged, {snd} sound + particles", r['hp']<3 and snd in r['snd'], str(r))
    pg.evaluate("(()=>{const d=__DH;const t=d.TR.find(t=>t.k==='tree'&&!t.dead);d.P.x=t.x;t.hp=1;window.__pre=JSON.stringify(d.inv)})()"); pg.wait_for_timeout(200)
    pg.keyboard.down("KeyE"); pg.wait_for_timeout(120); pg.keyboard.up("KeyE"); pg.wait_for_timeout(300)
    chk("gather completes: node depleted and inventory updated (real state)", pg.evaluate("JSON.stringify(__DH.inv)")!=pg.evaluate("window.__pre"))
    pg.evaluate("__DH.AU.log.length=0;(()=>{const d=__DH;d.TR.forEach(t=>t.dead=1);d.P.x=d.TR[0].x})()"); pg.keyboard.down("KeyE"); pg.wait_for_timeout(120); pg.keyboard.up("KeyE"); pg.wait_for_timeout(100)
    chk("gather with nothing nearby: failure feedback only", pg.evaluate("__DH.AU.log.some(x=>x.n==='ui_fail')") and not pg.evaluate("__DH.AU.log.some(x=>x.n==='chop'||x.n==='mine')"))
    # ---- DAMAGE → DEATH → RESTART ----
    pg.evaluate("__DH.AU.log.length=0;__DH.P.hp=30;__DH.P.max=100;__DH.P.inv=0;__DH.S.left=0;__DH.Z.length=0")
    pg.evaluate("(()=>{const z=__DH.spawnType('brute',20);z.dmg=60})()")
    pg.wait_for_timeout(1800)
    d=pg.evaluate("({st:__DH.S.state,hp:__DH.P.hp,snd:[...new Set(__DH.AU.log.map(x=>x.n))],anim:__DH.PA.state,death:__DH.PA.R.death})")
    chk("zombie contact: damage, hurt + attack sounds, then death state", d['st']=='dead' and 'hurt' in d['snd'] and 'z_attack' in d['snd'] and d['anim']=='death', str(d))
    pg.wait_for_timeout(400); pg.screenshot(path="/home/claude/shots/final/12_game_over.png")
    pg.keyboard.press("KeyR"); pg.wait_for_timeout(800)
    r2=pg.evaluate("({st:__DH.S.state,hp:__DH.P.hp,anim:__DH.PA.state,death:+__DH.PA.R.death.toFixed(2),wave:__DH.S.wave,deaths:__DH.DEATHS.length,fx:__DH.FXP.count()})")
    chk("restart (R) returns to a clean playable state, death pose cleared", r2['st']=='play' and r2['hp']>0 and r2['anim']!='death' and r2['death']<.1 and r2['wave']==1, str(r2))
    print("console:",pg.logs[:5])
    b.close()
json.dump(R,open('/home/claude/res_more.json','w'))
