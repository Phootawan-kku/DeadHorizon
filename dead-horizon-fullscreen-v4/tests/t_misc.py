import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(name, ok, info=""): R[name]=("PASS" if ok else "FAIL", info); print(("PASS " if ok else "FAIL ")+name, info)
with sync_playwright() as p:
    b,ctx,pg = launch(p, 1280, 720)
    box = start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.S.left=0;__DH.Z.length=0;__DH.S.fight=false;__DH.own('smg');__DH.own('shotgun')")
    pg.evaluate("__DH.inv.ammo=100")
    pg.mouse.move(box["x"]+box["width"]*.8, box["y"]+box["height"]*.55)
    # ---------- RELOAD ----------
    pg.evaluate("__DH.equip('pistol');__DH.P.mag.pistol=3;__DH.AU.log.length=0")
    pg.evaluate("""window.__rl=[];(()=>{const d=__DH;const f=()=>{window.__rl.push({t:performance.now(),rl:d.P.rl,mag:d.P.mag.pistol,rlF:d.PA.rlF,ammo:d.inv.ammo,snd:d.AU.log.length});if(window.__rlrun)requestAnimationFrame(f)};window.__rlrun=true;requestAnimationFrame(f)})()""")
    pg.keyboard.down("KeyR"); pg.wait_for_timeout(120); pg.keyboard.up("KeyR")
    pg.wait_for_timeout(2200)
    pg.evaluate("window.__rlrun=false")
    tr=pg.evaluate("window.__rl"); snd=pg.evaluate("__DH.AU.log.map(x=>[x.n,x.t])")
    midmag=[r['mag'] for r in tr if r['rl']>0]
    chk("reload: mag unchanged while reloading", len(set(midmag))==1 and midmag[0]==3, f"mags during reload={set(midmag)}")
    chk("reload: ammo not refilled until timer ends", all(r['ammo']==100 for r in tr if r['rl']>0))
    fin=tr[-1]; chk("reload: completes and refills", fin['mag']==12 and fin['ammo']==91, f"final mag={fin['mag']} reserve={fin['ammo']}")
    names=[n for n,_ in snd if n in('mag_out','mag_in','rack')]
    chk("reload: sound sequence mag_out→mag_in→rack, once each", names==['mag_out','mag_in','rack'], str(names))
    # ---------- SWITCH CANCELS RELOAD ----------
    pg.evaluate("__DH.P.mag.pistol=2;__DH.AU.log.length=0")
    pg.keyboard.down("KeyR"); pg.wait_for_timeout(100); pg.keyboard.up("KeyR"); pg.wait_for_timeout(200)
    pg.keyboard.press("Digit1"); pg.wait_for_timeout(50)
    pg.evaluate("__DH.AU.log.length=0"); pg.wait_for_timeout(1500)
    s=pg.evaluate("({rl:__DH.P.rl,mag:__DH.P.mag.pistol,wp:__DH.P.wp,late:__DH.AU.log.filter(x=>['mag_out','mag_in','rack'].includes(x.n)).length})")
    chk("switch during reload cancels it (no refill, no late reload sounds)", s['rl']==0 and s['mag']==2 and s['late']==0, str(s))
    # ---------- EMPTY / NO AMMO ----------
    pg.evaluate("__DH.equip('smg');__DH.inv.ammo=0;__DH.P.mag.smg=0;__DH.P.rl=0;__DH.P.cd=0;__DH.AU.log.length=0;__DH.B.length=0")
    pg.mouse.down(); pg.wait_for_timeout(2000); pg.mouse.up()
    e=pg.evaluate("({empty:__DH.AU.log.filter(x=>x.n==='empty').length,shots:__DH.AU.log.filter(x=>x.n.startsWith('shot_')).length,rl:__DH.P.rl,B:__DH.B.length})")
    chk("empty magazine: no shots, click is rate-limited (not per frame)", e['shots']==0 and 1<=e['empty']<=7 and e['rl']==0 and e['B']==0, str(e)+" (2s held ≈120 frames)")
    # ---------- SHOOT WHILE JUMPING / MOVING ----------
    pg.evaluate("__DH.inv.ammo=200;__DH.P.mag.smg=30;__DH.P.rl=0;__DH.P.cd=0;__DH.AU.log.length=0;__DH.B.length=0")
    pg.keyboard.down("KeyD"); pg.keyboard.down("Space"); pg.wait_for_timeout(60); pg.mouse.down()
    st=[]
    for i in range(14):
        st.append(pg.evaluate("[__DH.PA.state,__DH.P.mag.smg,Math.round(__DH.P.x)]")); pg.wait_for_timeout(45)
    pg.mouse.up(); pg.keyboard.up("Space"); pg.keyboard.up("KeyD")
    air=[x for x in st if x[0] in('jump_up','jump_apex','fall','jump_start')]
    fired_air = air[0][1]-air[-1][1] if air else 0
    chk("shooting while jumping+moving works", len(air)>=4 and fired_air>0 and st[-1][2]>st[0][2], f"air frames={len(air)}, rounds fired during air={fired_air}, x {st[0][2]}→{st[-1][2]}")
    pg.wait_for_timeout(800)
    # ---------- MELEE + HIT REACTION + DEATH ANIM ----------
    pg.evaluate("__DH.equip('knife');__DH.P.cd=0;__DH.P.aim=0;__DH.P.dir=1;__DH.AU.log.length=0")
    z=pg.evaluate("(()=>{const z=__DH.spawnType('normal',34);window.__tz=z;return {hp:z.hp,x:z.x-__DH.P.x}})()")
    hp0=z['hp']; pg.mouse.move(box["x"]+box["width"]*.8, box["y"]+box["height"]*.7)
    pg.mouse.down(); pg.wait_for_timeout(120); pg.mouse.up()
    m=pg.evaluate("(()=>{const z=window.__tz;return {hp:z&&z.hp,hr:z&&z.hr,swing:__DH.PA.swingT,log:__DH.AU.log.map(x=>x.n)}})()")
    chk("melee: swing arc + swing sound + damage + hit sound", ('melee_swing' in m['log']) and m['hp']<hp0 and 'melee_hit' in m['log'], str(m))
    pg.evaluate("__DH.Z.forEach(z=>{if(z.hp>0)z.hp=1})")
    for _ in range(6):
        pg.mouse.down(); pg.wait_for_timeout(120); pg.mouse.up(); pg.wait_for_timeout(350)
        if pg.evaluate("__DH.DEATHS.length")>0: break
    dn=pg.evaluate("__DH.DEATHS.length"); snd2=pg.evaluate("__DH.AU.log.some(x=>x.n==='z_death')")
    chk("kill spawns a death animation + death sound", dn>=1 and snd2, f"deaths={dn}")
    pg.wait_for_timeout(2300)
    chk("death animations clean themselves up", pg.evaluate("__DH.DEATHS.length")==0)
    print("LOGS",pg.logs[:5])
    b.close()
json.dump(R,open('/home/claude/res_misc.json','w'))
