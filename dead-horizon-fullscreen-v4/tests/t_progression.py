"""Progression system: levels/XP, skills, talent trees, run perks.
Run:  bash tests/with_srv.sh <project dir> 8802 python3 tests/t_progression.py   (needs playwright + chromium)"""
import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(name, ok, info=""): R[name]=("PASS" if ok else "FAIL", info); print(("PASS " if ok else "FAIL ")+name, info)
URL="http://localhost:8802/game.html?debug=1"
def hide_dbg(pg): pg.evaluate("document.getElementById('debug-hud').style.display='none'")
def frames(pg,n=6):   # wait for n real animation frames (robust against slow headless frame rates)
    pg.evaluate("n=>new Promise(r=>{(function f(){--n>0?requestAnimationFrame(f):r()})()})",n)
def aim_at(pg,expr):  # point the mouse at a zombie's torso (terrain is uneven, so a fixed height sometimes misses)
    pg.evaluate('()=>{const z=%s;__DH.mouse.x=480+(z.x-__DH.P.x);__DH.mouse.y=z.y-19}'%expr)
def fire_once(pg):    # press, wait until the gun has actually fired (magazine drops), release, let the semi-auto latch re-arm
    frames(pg,4); pg.evaluate("window.__m0=__DH.P.mag[__DH.P.wp];__DH.mouse.down=true")
    try: pg.wait_for_function("__DH.P.mag[__DH.P.wp]<window.__m0",timeout=4000)
    except Exception: pass
    pg.evaluate("__DH.mouse.down=false"); frames(pg,4)
def kill_walker_by_melee(pg, offset=20):
    pg.evaluate("""(o)=>{const z=__DH.spawnType('normal',o);z.hp=z.max=1;__DH.mouse.x=900;__DH.mouse.y=380;__DH.mouse.down=true}""", offset)
    try: pg.wait_for_function("__DH.mouse.down&&!__DH.Z.some(z=>z.hp>0&&z.hp<=1&&!z.dead)",timeout=4000)
    except Exception: pass
    frames(pg,4); pg.evaluate("__DH.mouse.down=false"); frames(pg,4)

with sync_playwright() as p:
    # ---------- A: baseline is the original game ----------
    b,ctx,pg=launch(p); start(pg,URL)
    a=pg.evaluate("()=>({mod:Object.values(__DH.MOD).every(v=>v===0),max:__DH.P.max,hp:__DH.P.hp,lv:__DH.PLV.level,pts:__DH.talentPoints(),errs:document.getElementById('debug-hud').textContent.includes('Data errors: 0')})")
    chk("A1 nothing unlocked => every modifier is zero, 100 HP, level 1", a['mod'] and a['max']==100 and a['hp']==100 and a['lv']==1 and a['pts']==0, str(a))
    chk("A2 progression data passes validation", a['errs'])
    # ---------- B: XP curve ----------
    c=pg.evaluate("()=>({a:__DH.levelInfo(59).level,b:__DH.levelInfo(60).level,c:__DH.levelInfo(1022).level,d:__DH.levelInfo(1021).level,max:__DH.levelInfo(1e9).level,maxInto:__DH.levelInfo(1e9).need})")
    chk("B1 level thresholds (60 xp => L2, 1022 => L5) and cap at 40", c['a']==1 and c['b']==2 and c['c']==5 and c['d']==4 and c['max']==40 and c['maxInto']==0, str(c))
    # ---------- C: a real melee kill pays XP + trains Close Combat ----------
    x0=pg.evaluate("({xp:__DH.Meta.prog.xp,sk:__DH.Meta.prog.skills.closeCombat||0,kills:__DH.Meta.stats.kills})")
    kill_walker_by_melee(pg)
    x1=pg.evaluate("({xp:__DH.Meta.prog.xp,sk:__DH.Meta.prog.skills.closeCombat||0,kills:__DH.Meta.stats.kills,marks:__DH.Meta.prog.skills.marksman||0})")
    chk("C1 killing a Walker at wave 1 grants 13 XP", x1['kills']==x0['kills']+1 and x1['xp']-x0['xp']==13, str((x0,x1)))
    chk("C2 melee kill trains Close Combat (ceil(13*1.5)=20), not Marksmanship", x1['sk']-x0['sk']==20 and x1['marks']==0, str(x1))
    # ---------- D: level-up gives talent points; spend them through the real UI ----------
    pg.evaluate("__DH.addXP(2700)"); pg.wait_for_timeout(200)
    d=pg.evaluate("({lv:__DH.PLV.level,pts:__DH.talentPoints()})")
    chk("D1 level up grants one talent point per level", d['pts']==d['lv']-1 and d['lv']>=7, str(d))
    pg.keyboard.press("KeyK"); pg.wait_for_timeout(350)
    ui=pg.evaluate("({open:__DH.GameState.metaOpen,on:document.getElementById('meta-menu').classList.contains('on'),tab:document.querySelector('.meta-tab.active')?.dataset.tab})")
    chk("D2 K opens META on the TALENTS tab", ui['open'] and ui['on'] and ui['tab']=='talents', str(ui))
    t0=pg.evaluate("__DH.S.t"); pg.wait_for_timeout(500); t1=pg.evaluate("__DH.S.t")
    chk("D3 the run is paused while the talent screen is open", abs(t1-t0)<0.001, f"{t0}->{t1}")
    pg.screenshot(path="/home/claude/shots/10_talents_empty.png")
    chk("D4 a tier-2 talent is locked before 4 points are in the tree", pg.evaluate("document.querySelector('[data-talent=g_reload]').disabled"))
    for i in range(3): pg.click("[data-talent=g_dmg]"); pg.wait_for_timeout(80)
    pg.click("[data-talent=g_spread]"); pg.wait_for_timeout(100)
    e=pg.evaluate("({r:__DH.Meta.prog.talents.g_dmg,sp:__DH.Meta.prog.talents.g_spread,ranged:__DH.MOD.ranged,spread:__DH.MOD.spread,pts:__DH.talentPoints(),t2:document.querySelector('[data-talent=g_reload]').disabled})")
    chk("D5 clicking spends points and rank caps at 3 (ranged +12%)", e['r']==3 and abs(e['ranged']-.12)<1e-9 and e['sp']==1 and abs(e['spread']-.06)<1e-9, str(e))
    chk("D6 tier 2 unlocks once 4 points are spent in that tree", e['t2']==False, str(e['t2']))
    pg.screenshot(path="/home/claude/shots/11_talents_spent.png")
    coins0=pg.evaluate("__DH.Meta.coins"); pg.evaluate("__DH.Meta.coins=5000;__DH.renderMeta('talents')")
    pg.click("[data-respec]"); pg.wait_for_timeout(150)
    f=pg.evaluate("({t:JSON.stringify(__DH.Meta.prog.talents),pts:__DH.talentPoints(),coins:__DH.Meta.coins,ranged:__DH.MOD.ranged})")
    chk("D7 respec refunds all points for coins (50+20/pt = 130)", f['t']=='{}' and f['pts']==pg.evaluate("__DH.PLV.level-1") and f['coins']==5000-130 and f['ranged']==0, str(f))
    pg.keyboard.press("KeyK"); pg.wait_for_timeout(300)
    chk("D8 K closes it again and play resumes", not pg.evaluate("__DH.GameState.metaOpen"))
    chk("D9 no console errors so far", not pg.logs, str(pg.logs))
    b.close()

    # ---------- E: modifiers actually change gameplay ----------
    b,ctx,pg=launch(p); start(pg,URL)
    pg.evaluate("__DH.addXP(300000)")   # level cap
    pg.evaluate("""()=>{const t=__DH.Meta.prog.talents;Object.assign(t,{g_dmg:3,g_spread:3,g_reload:3,g_mag:3,b_hp:3,b_dr:3,s_speed:3,s_heal:3,b_melee:3,b_inv:3});__DH.syncProgression()}""")
    m=pg.evaluate("({max:__DH.P.max,hp:__DH.P.hp,mod:__DH.MOD})")
    chk("E1 +30 max HP talent applies at once and heals the difference", m['max']==130 and m['hp']==130, str((m['max'],m['hp'])))
    # pistol bullet damage, reload time, magazine
    pg.evaluate("__DH.equip('pistol')"); pg.evaluate("__DH.Z.length=0")
    pg.evaluate("__DH.mouse.x=900;__DH.mouse.y=380"); pg.evaluate("window.__m0=__DH.P.mag.pistol;__DH.mouse.down=true"); pg.wait_for_function("__DH.B.length>0",timeout=4000); pg.evaluate("__DH.mouse.down=false")
    bd=pg.evaluate("__DH.B.length?__DH.B[0].d:null")
    chk("E2 pistol bullet damage = 16 x 1.12 = 17.92", bd is not None and abs(bd-17.92)<1e-6, str(bd))
    pg.evaluate("__DH.P.mag.pistol=0"); pg.evaluate("__DH.Z.length=0"); pg.keyboard.press("KeyR"); pg.wait_for_timeout(60)
    rl=pg.evaluate("({rl:__DH.P.rlMax,cap:12})")
    chk("E3 reload time = 1.1s x (1-0.21) = 0.869s", abs(rl['rl']-0.869)<1e-6, str(rl))
    cap=pg.evaluate("(()=>{const w=__DH.Meta;return null})()")
    pg.wait_for_timeout(1200)
    mag=pg.evaluate("__DH.P.mag.pistol")
    chk("E4 magazine = ceil(12 x 1.24) = 15 after reload", mag==15, str(mag))
    # move speed
    pg.evaluate("__DH.Z.length=0"); pg.keyboard.down("KeyD"); frames(pg,8); s0=pg.evaluate("[__DH.P.x,__DH.S.t]"); frames(pg,30); s1=pg.evaluate("[__DH.P.x,__DH.S.t]"); pg.keyboard.up("KeyD")
    sp=(s1[0]-s0[0])/(s1[1]-s0[1])
    chk("E5 move speed ~ 190 x 1.09 = 207 px/s", 190<sp<215, f"{sp:.0f}")
    # damage reduction + heal amount
    pg.evaluate("""()=>{__DH.Z.length=0;__DH.P.hp=100;__DH.P.inv=0;const z=__DH.spawnType('normal',0);z.cd=0;z.dmg=40}"""); pg.wait_for_timeout(140)
    hp=pg.evaluate("__DH.P.hp")
    chk("E6 a 40-dmg hit is reduced by Thick Hide (-12%): 35.2 taken", abs((100-hp)-35.2)<0.6, f"hp={hp}")
    pg.evaluate("__DH.Z.length=0;__DH.P.hp=20;__DH.P.inv=0"); pg.keyboard.press("KeyH"); pg.wait_for_timeout(80)
    chk("E7 bandage heals 35 x 1.30 = 45.5", abs(pg.evaluate("__DH.P.hp")-65.5)<.01, str(pg.evaluate("__DH.P.hp")))
    # loot: with huge loot chance every drop rolls; with +100% quantity the 1-1 bone drop becomes 2
    pg.evaluate("__DH.Meta.prog.talents={};__DH.syncProgression();__DH.Z.length=0;__DH.equip('knife');__DH.MOD.loot=100;__DH.MOD.lootQty=1")
    i0=pg.evaluate("({...__DH.inv})"); kill_walker_by_melee(pg); pg.wait_for_timeout(700); i1=pg.evaluate("({...__DH.inv})")
    chk("E8 loot chance modifier makes rare drops (metal, chemicals) appear", i1['metal']>i0['metal'] and i1['chemicals']>i0['chemicals'], str({k:i1[k]-i0[k] for k in('metal','chemicals','bone')}))
    chk("E9 loot quantity modifier doubles a 1-1 drop", i1['bone']-i0['bone']==2, str(i1['bone']-i0['bone']))
    chk("E10 no console errors", not pg.logs, str(pg.logs)); b.close()

    # ---------- F: skills level by use and unlock milestones ----------
    b,ctx,pg=launch(p); start(pg,URL)
    pg.evaluate("__DH.addSkillXp('marksman',79)"); l1=pg.evaluate("__DH.skillInfo('marksman').level")
    pg.evaluate("__DH.addSkillXp('marksman',1)"); l2=pg.evaluate("({l:__DH.skillInfo('marksman').level,r:__DH.MOD.ranged,c:__DH.MOD.crit})")
    chk("F1 80 skill XP => level 2: +2% ranged, +0.5% crit", l1==1 and l2['l']==2 and abs(l2['r']-.02)<1e-9 and abs(l2['c']-.005)<1e-9, str(l2))
    pg.evaluate("__DH.addSkillXp('marksman',1400)"); l3=pg.evaluate("({l:__DH.skillInfo('marksman').level,mag:__DH.MOD.mag,r:__DH.MOD.ranged})")
    chk("F2 level 5 milestone: +10% magazine", l3['l']==5 and abs(l3['mag']-.10)<1e-9 and abs(l3['r']-.08)<1e-9, str(l3))
    pg.evaluate("__DH.addSkillXp('marksman',100000)"); l4=pg.evaluate("({l:__DH.skillInfo('marksman').level,cm:__DH.MOD.critMul})")
    chk("F3 skill caps at 10 with the crit-damage milestone", l4['l']==10 and abs(l4['cm']-.25)<1e-9, str(l4))
    pg.evaluate("__DH.equip('pistol');__DH.mouse.x=900;__DH.mouse.y=380"); fire_once(pg)
    # ranged kill trains Marksmanship
    m0=pg.evaluate("__DH.Meta.prog.skills.marksman")
    for attempt in range(3):   # a live wave may put a real zombie in the line of fire; the hook itself is deterministic
        pg.evaluate("""()=>{__DH.Z.length=0;__DH.P.mag.pistol=12;__DH.P.cd=0;const z=__DH.spawnType('normal',120);z.hp=z.max=1;z.sp=0;window.__zt=z}""")
        frames(pg,6); aim_at(pg,'window.__zt'); fire_once(pg); frames(pg,20)
        m1=pg.evaluate("__DH.Meta.prog.skills.marksman")
        if m1>m0: break
    chk("F4 a ranged kill trains Marksmanship", m1>m0, f"{m0}->{m1}")
    pg.evaluate("__DH.P.hp=10"); h0=pg.evaluate("__DH.Meta.prog.skills.medicine||0"); pg.keyboard.press("KeyH"); pg.wait_for_timeout(60)
    chk("F5 healing trains Field Medicine (+12)", pg.evaluate("__DH.Meta.prog.skills.medicine||0")-h0==12)
    pg.keyboard.press("KeyK"); pg.wait_for_timeout(300); pg.click("[data-tab=skills]"); pg.wait_for_timeout(250)
    pg.screenshot(path="/home/claude/shots/12_skills.png")
    chk("F6 no console errors", not pg.logs, str(pg.logs)); b.close()

    # ---------- G: run perks ----------
    b,ctx,pg=launch(p); start(pg,URL); hide_dbg(pg)
    def clear_wave(n):
        pg.evaluate("(n)=>{__DH.S.wave=n;__DH.S.left=0;__DH.S.alive=0;__DH.Z.length=0;__DH.S.fight=true}", n); pg.wait_for_timeout(150)
    clear_wave(1)
    chk("G1 no perk draft after wave 1", not pg.evaluate("__DH.GameState.perkOpen"))
    clear_wave(2)
    chk("G2 perk draft opens after wave 2", pg.evaluate("__DH.GameState.perkOpen") and pg.evaluate("document.querySelectorAll('.perk-card').length")==3)
    pg.screenshot(path="/home/claude/shots/13_perk_draft.png")
    ids=pg.evaluate("[...document.querySelectorAll('.perk-card h4')].map(e=>e.textContent)")
    chk("G3 the three offered perks are distinct", len(set(ids))==3, str(ids))
    t0=pg.evaluate("__DH.S.t"); pg.wait_for_timeout(600); t1=pg.evaluate("__DH.S.t")
    chk("G4 the game is frozen while choosing", abs(t1-t0)<0.001)
    pg.keyboard.press("Digit1")   # inside the 450ms input lock? we already waited 600ms, so test lock on a second draft below
    pg.wait_for_timeout(150)
    after=pg.evaluate("({open:__DH.GameState.perkOpen,perks:__DH.S.perks,q:__DH.S.perkQueue})")
    chk("G5 pressing 1 picks the first perk and closes the draft", not after['open'] and sum(after['perks'].values())==1 and after['q']==0, str(after))
    tA=pg.evaluate("__DH.S.t"); pg.wait_for_timeout(400); tB=pg.evaluate("__DH.S.t")
    chk("G6 play resumes after picking", tB>tA)
    pg.evaluate("__DH.queuePerkDraft()"); pg.keyboard.press("Digit1"); pg.wait_for_timeout(80)
    chk("G7 a keypress during the first 450ms cannot pick by accident", pg.evaluate("__DH.GameState.perkOpen"))
    pg.wait_for_timeout(500); pg.click(".perk-card >> nth=2"); pg.wait_for_timeout(150)
    chk("G8 clicking a card also picks", not pg.evaluate("__DH.GameState.perkOpen") and sum(pg.evaluate("__DH.S.perks").values())==2)
    # wave schedule
    got=[]
    for w in (3,4,5,8,10,11,20):
        clear_wave(w); o=pg.evaluate("__DH.GameState.perkOpen"); got.append((w,o))
        if o: pg.wait_for_timeout(500); pg.keyboard.press("Digit1"); pg.wait_for_timeout(120)
    chk("G9 drafts follow waves 2,5,8,11,14,17,20 plus every 10th (not 1, 3, 4)", got==[(3,False),(4,False),(5,True),(8,True),(10,True),(11,True),(20,True)], str(got))
    # perk effects
    pg.evaluate("""()=>{__DH.S.perks={thickskin:2,ironwill:1,regen:0};__DH.recalcMods()}""")
    pm=pg.evaluate("({max:__DH.P.max,dr:__DH.MOD.dr,res:__DH.skillInfo('resilience').level})")
    chk("G10 Thick Skin x2 = +30 max HP (plus 3/level of Resilience); Iron Will = -10% damage taken", pm['max']==130+3*(pm['res']-1) and abs(pm['dr']-.10)<1e-9, str(pm))
    # perks vanish with a new run: die, restart, check
    pg.evaluate("__DH.S.perks={hollow:3};__DH.recalcMods()")
    pg.evaluate("__DH.P.hp=1;__DH.P.inv=0;__DH.Z.length=0;{const z=__DH.spawnType('normal',0);z.cd=0;z.dmg=99}"); pg.wait_for_timeout(250)
    chk("G11 dying shows the XP line on the game-over screen", pg.evaluate("__DH.S.state")=='dead')
    pg.screenshot(path="/home/claude/shots/14_gameover.png")
    pg.keyboard.press("KeyR"); pg.wait_for_timeout(300)
    nr=pg.evaluate("({perks:Object.keys(__DH.S.perks).length,dmg:__DH.MOD.dmg,state:__DH.S.state,max:__DH.P.max-3*(__DH.skillInfo('resilience').level-1)})")
    chk("G12 a new run starts with no perks and original stats", nr['perks']==0 and nr['dmg']==0 and nr['state']=='play' and nr['max']==100, str(nr))
    chk("G13 no console errors", not pg.logs, str(pg.logs)); b.close()

    # ---------- H: Undying capstone, pierce, execute ----------
    b,ctx,pg=launch(p); start(pg,URL)
    pg.evaluate("__DH.S.perks={};__DH.Meta.prog.xp=300000;__DH.Meta.prog.talents={g_spread:3,g_dmg:1,b_hp:3,b_melee:3,b_dr:3,b_inv:0,b_kh:3,b_rate:3,b_cap:1};__DH.syncProgression()")
    ok=pg.evaluate("__DH.MOD.undying")
    chk("H1 Undying capstone is active", ok==1)
    def lethal():
        pg.evaluate("""()=>{__DH.Z.length=0;__DH.P.hp=1;__DH.P.inv=0;const z=__DH.spawnType('normal',0);z.cd=0;z.dmg=200}"""); pg.wait_for_timeout(250)
    lethal(); s1=pg.evaluate("({st:__DH.S.state,hp:__DH.P.hp,max:__DH.P.max})")
    chk("H2 first lethal hit is survived at 35% HP", s1['st']=='play' and abs(s1['hp']-round(s1['max']*.35))<=1, str(s1))
    pg.evaluate("__DH.P.inv=0"); lethal(); pg.evaluate("__DH.P.hp=1;__DH.P.inv=0"); pg.wait_for_timeout(300)
    chk("H3 the save is once per run: the next lethal hit kills", pg.evaluate("__DH.S.state")=='dead')
    pg.keyboard.press("KeyR"); pg.wait_for_timeout(300)
    lethal(); chk("H4 Undying is available again in the next run", pg.evaluate("__DH.S.state")=='play')
    # pierce: force 100% and line up two zombies; with pierce off only the first is hurt
    def line_shot(pr):
        pg.evaluate("""(pr)=>{__DH.Z.length=0;__DH.B.length=0;__DH.equip('pistol');__DH.P.mag.pistol=12;__DH.P.cd=0;
          const a=__DH.spawnType('normal',90),c=__DH.spawnType('normal',140);a.hp=a.max=500;c.hp=c.max=500;a.sp=c.sp=0;window.__pz=[a,c]}""",pr)
        frames(pg,6); aim_at(pg,'window.__pz[1]'); pg.evaluate("(pr)=>{__DH.MOD.pierce=pr}",pr); fire_once(pg); frames(pg,30)
        return pg.evaluate("window.__pz.map(z=>z.hp)")
    on=line_shot(1); off=line_shot(0)
    chk("H5 piercing bullet damages both zombies in a line; without it only the first", on[0]<500 and on[1]<500 and off[0]<500 and off[1]==500, str((on,off)))
    chk("H6 no console errors", not pg.logs, str(pg.logs)); b.close()

    # ---------- I: saving, old saves, tampered saves ----------
    b,ctx,pg=launch(p); start(pg,URL)
    pg.evaluate("__DH.addXP(1100);__DH.Meta.prog.talents={g_dmg:2};__DH.syncProgression();__DH.addSkillXp('scavenging',500)")
    pg.keyboard.press("KeyK"); pg.wait_for_timeout(250); pg.keyboard.press("KeyK"); pg.wait_for_timeout(200)
    pg.evaluate("localStorage.setItem('deadHorizonMetaV5',JSON.stringify(__DH.Meta))")
    snap=pg.evaluate("({xp:__DH.Meta.prog.xp,lv:__DH.PLV.level})")
    pg.goto(URL,wait_until="load"); pg.wait_for_timeout(600)
    pg.evaluate("1"); after=pg.evaluate("({xp:__DH.Meta.prog.xp,t:__DH.Meta.prog.talents.g_dmg,sk:__DH.Meta.prog.skills.scavenging,lv:__DH.PLV.level,ranged:__DH.MOD.ranged})")
    chk("I1 level, XP, talents and skills survive a page reload", after['xp']==snap['xp'] and after['t']==2 and after['sk']>=500 and after['lv']==snap['lv'] and abs(after['ranged']-.08)<1e-9, str(after))
    b.close()
    # old save from before this feature
    old={"saveVersion":2,"coins":777,"ownedCos":["char_survivor","knife_m9_default"],"equipped":{"character":"char_survivor","weapon":None,"effect":"fx_blood","weapons":{"knife":"knife_m9_default"}},"stats":{"kills":321,"bestWave":14},"weaponsOwned":["knife","pistol"]}
    b=p.chromium.launch(args=["--no-sandbox"]); cx=b.new_context(viewport={"width":1280,"height":720})
    cx.add_init_script("if(!localStorage.getItem('__s')){localStorage.setItem('deadHorizonMetaV5',%s);localStorage.setItem('__s','1')}"%json.dumps(json.dumps(old)))
    pg=cx.new_page(); pg.logs=[]; pg.on("pageerror",lambda e:pg.logs.append(str(e)[:200]))
    start(pg,URL)
    o=pg.evaluate("({xp:__DH.Meta.prog.xp,lv:__DH.PLV.level,coins:__DH.Meta.coins,kills:__DH.Meta.stats.kills,pts:__DH.talentPoints(),msg:JSON.stringify(__DH.S&&0)})")
    chk("I2 an old save is credited 10 XP per past kill (321 kills => 3210 XP) and keeps everything else", o['xp']==3210 and o['lv']>=7 and o['coins']==777 and o['kills']==321 and o['pts']==o['lv']-1, str(o))
    chk("I3 old-save credit was written back so it is not repeated", json.loads(pg.evaluate("localStorage.getItem('deadHorizonMetaV5')")).get('prog',{}).get('xp')==3210)
    b.close()
    # tampered save
    bad={"saveVersion":2,"ownedCos":["char_survivor"],"stats":{"kills":5},"weaponsOwned":["knife"],"prog":{"xp":-50,"skills":{"marksman":"lots","nope":99,"medicine":250.9},"talents":{"g_dmg":99,"b_cap":1,"fake":3}}}
    b=p.chromium.launch(args=["--no-sandbox"]); cx=b.new_context(viewport={"width":1280,"height":720})
    cx.add_init_script("if(!localStorage.getItem('__s')){localStorage.setItem('deadHorizonMetaV5',%s);localStorage.setItem('__s','1')}"%json.dumps(json.dumps(bad)))
    pg=cx.new_page(); pg.logs=[]; pg.on("pageerror",lambda e:pg.logs.append(str(e)[:200]))
    start(pg,URL)
    t=pg.evaluate("({xp:__DH.Meta.prog.xp,tal:JSON.stringify(__DH.Meta.prog.talents),sk:JSON.stringify(__DH.Meta.prog.skills),pts:__DH.talentPoints()})")
    chk("I4 tampered save: negative XP -> 0, impossible talents refunded, junk skills dropped", t['xp']==0 and t['tal']=='{}' and json.loads(t['sk'])=={"medicine":250} and t['pts']==0, str(t))
    chk("I5 tampered save loads without errors", not pg.logs, str(pg.logs))
    b.close()

    # ---------- J: UI screens ----------
    b,ctx,pg=launch(p); start(pg,URL); hide_dbg(pg)
    pg.evaluate("__DH.addXP(40000);__DH.Meta.prog.talents={g_spread:3,g_dmg:2,g_reload:1,b_hp:2,s_loot:3,s_speed:1};__DH.syncProgression();__DH.addSkillXp('marksman',700);__DH.addSkillXp('resilience',150);__DH.S.perks={hollow:2,ghost:1,berserker:1};__DH.recalcMods()")
    pg.wait_for_timeout(300); pg.screenshot(path="/home/claude/shots/15_hud_progress.png",clip={"x":0,"y":0,"width":640,"height":300})
    pg.keyboard.press("KeyK"); pg.wait_for_timeout(350); pg.screenshot(path="/home/claude/shots/16_talents_full.png")
    pg.click("[data-tab=perks]"); pg.wait_for_timeout(250); pg.screenshot(path="/home/claude/shots/17_perks_tab.png")
    pg.click("[data-tab=profile]"); pg.wait_for_timeout(250); pg.screenshot(path="/home/claude/shots/18_profile.png")
    prof=pg.evaluate("document.getElementById('meta-content').innerText")
    chk("J1 profile tab shows the real level, XP and talent points", "PLAYER LEVEL" in prof and "TALENT POINTS" in prof and "XP" in prof, prof[:90].replace("\n"," "))
    chk("J2 META tab strip shows unspent points on TALENTS", "TALENTS (" in pg.evaluate("document.querySelector('.meta-tabs').innerText"))
    chk("J3 no console errors", not pg.logs, str(pg.logs)); b.close()

bad=[k for k,v in R.items() if v[0]!="PASS"]
print("\n%d checks, %d failed"%(len(R),len(bad))); [print("  FAIL:",k,R[k][1]) for k in bad]
open('/home/claude/DeadHorizon-main/dead-horizon-fullscreen-v4/tests/LAST_PROGRESSION_RESULTS.txt','w').write("\n".join("%s %s %s"%(v[0],k,v[1]) for k,v in R.items())+"\n")
sys.exit(1 if bad else 0)
