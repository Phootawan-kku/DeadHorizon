import sys, json; sys.path.insert(0,'/home/claude')
from h import *
from PIL import Image
import io
OUT="/home/claude/shots/final"; import os; os.makedirs(OUT,exist_ok=True)
with sync_playwright() as p:
    b,ctx,pg = launch(p,1920,1080); box=start(pg,settle=1200)
    pg.add_style_tag(content="#debug-hud{display:none!important}")
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.S.left=0;__DH.Z.length=0;__DH.own('smg');__DH.own('shotgun');__DH.own('rifle');__DH.own('sniper');__DH.inv.ammo=500;__DH.S.inter=99;__DH.MS=0")
    pg.evaluate("__DH.P.mag.smg=30;__DH.P.mag.shotgun=6;__DH.P.mag.rifle=30")
    def snap(name): pg.screenshot(path=f"{OUT}/{name}.png")
    # 1 run
    pg.mouse.move(box["x"]+box["width"]*.8, box["y"]+box["height"]*.55); pg.keyboard.down("KeyD"); pg.wait_for_timeout(900); snap("01_running"); 
    # 2 jump (apex)
    pg.keyboard.down("Space")
    for _ in range(40):
        if pg.evaluate("__DH.PA.state")=='jump_apex': break
        pg.wait_for_timeout(15)
    snap("02_jumping"); pg.keyboard.up("Space"); pg.keyboard.up("KeyD"); pg.wait_for_timeout(700)
    # 3 shooting with zombies (rifle) frozen on a flash frame
    pg.evaluate("__DH.equip('rifle');__DH.P.hp=__DH.P.max=99999")
    for t,off in [('normal',300),('fast',420),('tank',520),('armored',640),('spitter',-330),('exploder',-210)]: pg.evaluate(f"__DH.spawnType('{t}',{off})")
    pg.evaluate("__DH.Z.forEach(z=>{z.sp=0})"); pg.mouse.move(box["x"]+box["width"]*.78, box["y"]+box["height"]*.62); pg.wait_for_timeout(200)
    pg.evaluate("__DH.P.cd=0"); pg.mouse.down()
    for _ in range(40):
        if pg.evaluate("__DH.P.flash>0.04"): pg.evaluate("__DH.GameState.isPaused=true"); break
        pg.wait_for_timeout(3)
    pg.mouse.up(); snap("03_shooting_lighting"); pg.evaluate("__DH.GameState.isPaused=false")
    # 4 blood moon / 5 power outage (zombie readability)
    pg.evaluate("__DH.Z.forEach(z=>{z.sp=0});__DH.S.event='BLOOD MOON';__DH.S.eventT=40"); pg.wait_for_timeout(300); pg.evaluate("__DH.GameState.isPaused=true"); snap("04_blood_moon"); pg.evaluate("__DH.GameState.isPaused=false")
    pg.evaluate("__DH.S.event='POWER OUTAGE';__DH.S.eventT=40"); pg.wait_for_timeout(300); pg.evaluate("__DH.GameState.isPaused=true"); snap("05_power_outage"); pg.evaluate("__DH.GameState.isPaused=false")
    pg.evaluate("__DH.S.event=null")
    # 6 reload pose
    pg.evaluate("__DH.Z.length=0;__DH.S.alive=0;__DH.equip('smg');__DH.P.mag.smg=4"); pg.keyboard.press("KeyR"); pg.wait_for_timeout(5); pg.keyboard.down("KeyR"); pg.wait_for_timeout(80); pg.keyboard.up("KeyR")
    pg.wait_for_timeout(420); snap("06_reloading")
    # 7 low health + damage flash
    pg.wait_for_timeout(1500); pg.evaluate("__DH.P.hp=22;__DH.FX&&0")
    snap("07_low_health")
    # menus
    pg.keyboard.press("Tab"); pg.evaluate("Object.assign(__DH.inv,{scrap:20,cloth:20,wood:20,metal:20,part:20,electronics:20})"); pg.keyboard.press("Tab"); pg.wait_for_timeout(150); pg.keyboard.press("Tab"); pg.wait_for_timeout(300); snap("08_inventory_crafting"); pg.keyboard.press("Tab")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300); snap("09_pause_audio_settings"); pg.evaluate("__DH.setPaused(false)")
    pg.keyboard.press("KeyO"); pg.wait_for_timeout(300); pg.click("[data-tab=shop]"); pg.wait_for_timeout(300); snap("10_cosmetics"); pg.click("[data-tab=settings]"); pg.wait_for_timeout(300); snap("11_meta_settings"); pg.keyboard.press("Escape")
    print(pg.logs[:5]); b.close()
