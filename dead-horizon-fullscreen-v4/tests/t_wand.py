"""Magic Wand: fireballs that ignite enemies (burn = damage over time, stacks, ignores armor), free mana ammo, crafting.
Run: bash tests/with_srv.sh <project dir> 8802 python3 tests/t_wand.py"""
import sys; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(n,ok,i=""): R[n]=bool(ok); print(("PASS " if ok else "FAIL ")+n,i)
URL="http://localhost:8802/game.html?debug=1"
def frames(pg,n=8): pg.evaluate("n=>new Promise(r=>{(function f(){--n>0?requestAnimationFrame(f):r()})()})",n)
def secs(pg,s):   # wait for game time (not wall-clock), robust to slow headless frame rates
    t0=pg.evaluate("__DH.S.t"); pg.wait_for_function("(a)=>__DH.S.t>=a[0]+a[1]",arg=[t0,s],timeout=int(s*6000)+4000)
def spawn(pg,t='tank',off=110,hp=None):
    pg.evaluate("""([t,off,hp])=>{__DH.Z.length=0;const z=__DH.spawnType(t,off);z.sp=0;z.cd=999;if(hp){z.hp=z.max=hp}window.__z=z;__DH.P.cd=0;__DH.P.rl=0;__DH.P.mag.wand=12}""",[t,off,hp])
    frames(pg,6); pg.evaluate("()=>{const z=window.__z;__DH.mouse.x=480+(z.x-__DH.P.x);__DH.mouse.y=z.y-19}")
def fire(pg):
    pg.evaluate("window.__m0=__DH.P.mag.wand;__DH.mouse.down=true")
    try: pg.wait_for_function("__DH.P.mag.wand<window.__m0",timeout=4000)
    except Exception: pass
    pg.evaluate("__DH.mouse.down=false"); frames(pg,5)
with sync_playwright() as p:
    b,ctx,pg=launch(p); start(pg,URL)
    pg.evaluate("document.getElementById('debug-hud').style.display='none'")
    d=pg.evaluate("({w:window.DEAD_HORIZON_DATA.weapons.wand,r:window.DEAD_HORIZON_DATA.recipes.find(r=>r.out==='wand'),errs:document.getElementById('debug-hud').textContent.includes('Data errors: 0')})")
    chk("A1 wand exists with ignite data and a craft recipe; data validates", d['w'] and d['w']['ignite']['dps']>0 and d['r'] and d['errs'], str(d['r']))
    chk("A2 sprite and icon are loaded", pg.evaluate("(()=>{const a=window.DEAD_HORIZON_ART;return a.ready('assets/weapons/hires/wand.png')&&a.ready('assets/weapons/hires/wand_icon.png')})()"))
    pg.evaluate("__DH.S.left=0;__DH.unlockWeapon('wand');__DH.Meta.hotbar=['knife','pistol','wand']"); pg.evaluate("__DH.equip('wand')")
    chk("A3 wand is owned, on the hotbar and in hand", pg.evaluate("__DH.P.wp")=='wand' and 'wand' in pg.evaluate("__DH.getHotbarWeapons()"))
    # ---- direct hit + ignite
    spawn(pg,'tank',110); hp0=pg.evaluate("window.__z.hp"); fire(pg); secs(pg,0.25)
    z=pg.evaluate("({hp:window.__z.hp,n:window.__z.burn&&window.__z.burn.n,t:window.__z.burn&&window.__z.burn.t})")
    chk("B1 fireball hits for ~26 and ignites the target (burn stack 1)", z['n']==1 and 15<hp0-z['hp']<75, str((hp0,z)))
    pg.screenshot(path='/home/claude/shots/90_burning.png',clip={"x":440,"y":380,"width":520,"height":200})
    hpA=pg.evaluate("window.__z.hp"); secs(pg,1.0); hpB=pg.evaluate("window.__z.hp")
    chk("B2 the target keeps taking burn damage with no further shots (~7/s)", 4<hpA-hpB<12, f"{hpA}->{hpB}")
    secs(pg,3.6); z2=pg.evaluate("({hp:window.__z.hp,burn:window.__z.burn})"); hpC=z2['hp']; secs(pg,1.0); hpD=pg.evaluate("window.__z.hp")
    chk("B3 burn expires after ~4s and damage stops", z2['burn'] is None and abs(hpC-hpD)<0.01, f"{z2['burn']} {hpC}->{hpD}")
    # ---- stacking
    spawn(pg,'tank',110)
    for i in range(5):
        fire(pg); secs(pg,0.55)
    n=pg.evaluate("window.__z.burn&&window.__z.burn.n")
    chk("B4 burn stacks with repeated hits and caps at 3", n==3, str(n))
    # ---- armor is ignored by burn
    spawn(pg,'armored',110); pg.evaluate("window.__z.armor=400;window.__z.hp=window.__z.max=95"); fire(pg); secs(pg,0.3)
    arm=pg.evaluate("window.__z.armor"); h1=pg.evaluate("window.__z.hp"); secs(pg,1.2); h2=pg.evaluate("window.__z.hp")
    chk("B5 burn damages an armored enemy whose armor is still up", arm>300 and h2<h1-4 and pg.evaluate("!!window.__z.burn"), f"armor {arm} hp {h1}->{h2}")
    # ---- burn kills and gives normal kill credit
    spawn(pg,'normal',110,hp=9); k0=pg.evaluate("({k:__DH.Meta.stats.kills,xp:__DH.Meta.prog.xp})")
    pg.evaluate("window.__z.hp=9"); pg.evaluate("__DH.P.cd=0")
    # damage 26 would one-shot it, so ignite directly with a stray sub-lethal hit: use an unarmed ignite
    pg.evaluate("(()=>{const z=window.__z;z.hp=60;z.max=60})()"); fire(pg); pg.evaluate("window.__z.hp=Math.min(window.__z.hp,12)")
    pg.wait_for_function("window.__z.dead",timeout=9000); k1=pg.evaluate("({k:__DH.Meta.stats.kills,xp:__DH.Meta.prog.xp,melee:__DH.Meta.stats.meleeKills})")
    chk("B6 an enemy that burns to death counts as a kill and pays XP", k1['k']==k0['k']+1 and k1['xp']>k0['xp'], str((k0,k1)))
    # ---- free mana
    inv0=pg.evaluate("JSON.stringify(__DH.inv)")
    pg.evaluate("__DH.Z.length=0;__DH.P.mag.wand=3;__DH.P.rl=0;__DH.P.cd=0"); pg.keyboard.press("KeyR"); frames(pg,4)
    reloading=pg.evaluate("__DH.P.rl")>0; secs(pg,1.8)
    chk("C1 reloading recharges to full without using any ammo items", reloading and pg.evaluate("__DH.P.mag.wand")==12 and pg.evaluate("JSON.stringify(__DH.inv)")==inv0)
    pg.evaluate("__DH.inv.ammo=0;__DH.P.mag.wand=0;__DH.P.rl=0"); pg.keyboard.press("KeyR"); frames(pg,4); secs(pg,1.8)
    chk("C2 works with zero ammo in the inventory (unlimited mana)", pg.evaluate("__DH.P.mag.wand")==12)
    # ---- point blank
    spawn(pg,'tank',18); fire(pg); secs(pg,0.3)
    chk("D1 a point-blank shot also ignites", pg.evaluate("!!window.__z.burn"))
    # ---- crafting through the real UI
    pg.evaluate("__DH.Meta.weaponsOwned=['knife','pistol'];__DH.Meta.hotbar=['knife','pistol'];Object.assign(__DH.inv,{wood:20,fuel:6,part:9,electronics:5})")
    pg.keyboard.press("Tab"); frames(pg,8)
    btn=pg.locator("#panel button.r, #panel button").filter(has_text="CRAFT & UNLOCK")
    cnt=btn.count(); idx=pg.evaluate("window.DEAD_HORIZON_DATA.recipes.filter(r=>r.kind==='weapon').findIndex(r=>r.out==='wand')")
    pg.evaluate("""()=>{const i=window.DEAD_HORIZON_DATA.recipes.findIndex(r=>r.out==='wand');const bs=[...document.querySelectorAll('#panel button')];window.__wb=bs.filter(b=>b.dataset.i==i||b.dataset.r==i||b.dataset.recipe==i)[0]||null}""")
    clicked=pg.evaluate("(()=>{const w=window.__wb;if(w){w.click();return 'by-dataset'}const rows=[...document.querySelectorAll('#panel *')].filter(e=>e.children.length<6&&/Magic Wand/i.test(e.textContent));const el=rows.map(e=>e.closest('div')).find(d=>d&&d.querySelector('button'));if(el){el.querySelector('button').click();return 'by-text'}return 'none'})()")
    frames(pg,6)
    chk("E1 crafting the wand through the panel unlocks it and adds it to the hotbar", 'wand' in pg.evaluate("__DH.Meta.weaponsOwned") and 'wand' in pg.evaluate("__DH.getHotbarWeapons()") and pg.evaluate("__DH.inv.fuel")==2, f"clicked {clicked}")
    pg.keyboard.press("Tab"); frames(pg,4)
    chk("F1 no console errors or failed requests", not [l for l in pg.logs if not (isinstance(l,tuple) and l[0]=='warning')] and not pg.fails, str((pg.logs,pg.fails[:3]))); b.close()
bad=[k for k,v in R.items() if not v]; print("\n%d checks, %d failed"%(len(R),len(bad))); [print("  FAIL:",k) for k in bad]; sys.exit(1 if bad else 0)
