"""Armory hotbar loadout: equip / unequip / swap, visible state, persistence, old saves.
Run: bash tests/with_srv.sh <project dir> 8802 python3 tests/t_hotbar.py"""
import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(n,ok,i=""): R[n]=ok; print(("PASS " if ok else "FAIL ")+n, i)
URL="http://localhost:8802/game.html?debug=1"
def frames(pg,n=4): pg.evaluate("n=>new Promise(r=>{(function f(){--n>0?requestAnimationFrame(f):r()})()})",n)
def armory(pg):
    pg.keyboard.press("KeyO"); frames(pg,8); pg.click("[data-tab=armory]"); frames(pg,4)
def hb(pg): return pg.evaluate("__DH.getHotbarWeapons()")
def card_text(pg,wid): return pg.evaluate("(w)=>{const b=document.querySelector('[data-mod=\"'+w+'\"]');return b?b.closest('.meta-item').innerText:''}",wid)
with sync_playwright() as p:
    b,ctx,pg=launch(p); start(pg,URL)
    ids=pg.evaluate("Object.keys(window.DEAD_HORIZON_DATA.weapons).filter(k=>!window.DEAD_HORIZON_DATA.weapons[k].locked).slice(0,12)")
    seven=ids[:7]
    pg.evaluate("(a)=>{__DH.Meta.weaponsOwned=a.slice();__DH.Meta.hotbar=a.slice(0,6)}",seven)
    armory(pg)
    chk("A1 hotbar header shows 6/6 and the 7th weapon is NOT EQUIPPED with a SWAP IN button",
        "6/6" in pg.inner_text(".hb-head") and "NOT EQUIPPED" in card_text(pg,seven[6]) and pg.locator(f"[data-hb=swapin][data-id={seven[6]}]").count()==1)
    chk("A2 equipped cards say EQUIPPED · SLOT n", "EQUIPPED · SLOT 2" in card_text(pg,seven[1]))
    pg.screenshot(path="/home/claude/shots/40_armory_full.png")
    # unequip the pistol (slot 2)
    pg.click(f"[data-hb=unequip][data-id={seven[1]}]"); frames(pg,4)
    h=hb(pg)
    chk("B1 UNEQUIP removes it from the hotbar and the rest close up", seven[1] not in h and len(h)==5 and h[:1]==[seven[0]], str(h))
    chk("B2 UI now says NOT EQUIPPED for it and shows a confirmation note", "NOT EQUIPPED" in card_text(pg,seven[1]) and "Unequipped" in pg.inner_text(".hb-note"), pg.inner_text(".hb-note"))
    chk("B3 the 7th weapon now offers EQUIP (room available)", pg.locator(f"[data-hb=equip][data-id={seven[6]}]").count()==1)
    pg.screenshot(path="/home/claude/shots/41_armory_unequipped.png")
    pg.click(f"[data-hb=equip][data-id={seven[6]}]"); frames(pg,4)
    chk("B4 EQUIP adds it to the free slot", hb(pg)[-1]==seven[6] and len(hb(pg))==6, str(hb(pg)))
    # swap flow while full
    pg.click(f"[data-hb=swapin][data-id={seven[1]}]"); frames(pg,4)
    chk("C1 SWAP IN shows swap banner and REPLACE buttons", "SWAP" in pg.inner_text(".hb-note") and pg.locator("[data-hb=replace]").count()==6)
    pg.screenshot(path="/home/claude/shots/42_armory_swap.png")
    old_slot=hb(pg).index(seven[2])
    pg.click(f"[data-hb=replace][data-id={seven[2]}]"); frames(pg,4)
    h=hb(pg)
    chk("C2 REPLACE puts the new weapon in the same slot", h[old_slot]==seven[1] and seven[2] not in h and len(h)==6, str(h))
    # cancel
    pg.click(f"[data-hb=swapin][data-id={seven[2]}]"); frames(pg,3); pg.click("[data-hb=cancel]"); frames(pg,3)
    chk("C3 CANCEL leaves the hotbar untouched", pg.locator("[data-hb=replace]").count()==0 and seven[2] not in hb(pg))
    # the digit keys follow the loadout
    pg.keyboard.press("KeyO"); frames(pg,8)
    pg.keyboard.press("Digit6"); frames(pg,4)
    chk("D1 key 6 selects the 6th hotbar weapon", pg.evaluate("__DH.P.wp")==hb(pg)[5], pg.evaluate("__DH.P.wp"))
    # unequipping the weapon in hand switches to another one
    held=pg.evaluate("__DH.P.wp"); armory(pg)
    chk("D2 the weapon in hand is badged IN HAND", "IN HAND" in card_text(pg,held))
    pg.click(f"[data-hb=unequip][data-id={held}]"); frames(pg,4)
    chk("D3 unequipping the held weapon hands you another hotbar weapon", pg.evaluate("__DH.P.wp")!=held and pg.evaluate("__DH.P.wp") in hb(pg), pg.evaluate("__DH.P.wp"))
    # cannot empty the hotbar
    for _ in range(8):
        h=hb(pg)
        if len(h)<=1: break
        pg.click(f"[data-hb=unequip][data-id={h[-1]}]"); frames(pg,3)
    last=hb(pg)
    chk("E1 the last weapon cannot be unequipped (button disabled)", len(last)==1 and pg.locator(f"[data-hb=unequip][data-id={last[0]}]").is_disabled(), str(last))
    # persistence
    pg.evaluate("(a)=>{__DH.Meta.hotbar=a;localStorage.setItem('deadHorizonMetaV5',JSON.stringify(__DH.Meta))}",[seven[3],seven[0],seven[5]])
    pg.goto(URL,wait_until="load"); pg.wait_for_timeout(500)
    chk("F1 the chosen order survives a reload", hb(pg)==[seven[3],seven[0],seven[5]], str(hb(pg)))
    # unlockWeapon: auto-add only if room
    pg.evaluate("(a)=>{__DH.Meta.weaponsOwned=a.slice(0,4);__DH.Meta.hotbar=a.slice(0,5).slice(0,4)}",seven)
    pg.evaluate("(w)=>__DH.unlockWeapon(w)",seven[4]); added=seven[4] in hb(pg)
    pg.evaluate("(a)=>{__DH.Meta.weaponsOwned=a.slice(0,6);__DH.Meta.hotbar=a.slice(0,6)}",seven)
    pg.evaluate("(w)=>__DH.unlockWeapon(w)",seven[6]); full_added=seven[6] in hb(pg)
    chk("G1 a newly unlocked weapon takes a free slot but not when the hotbar is full", added and not full_added, f"{added} {full_added}")
    chk("H1 no console errors", not pg.logs, str(pg.logs)); b.close()
    # old save without a hotbar field and 7 owned weapons -> first six (same as before)
    old={"saveVersion":2,"coins":9,"ownedCos":["char_survivor","knife_m9_default"],"equipped":{"character":"char_survivor","weapon":None,"effect":"fx_blood","weapons":{"knife":"knife_m9_default"}},"weaponsOwned":seven,"stats":{"kills":3}}
    b=p.chromium.launch(args=["--no-sandbox"]); cx=b.new_context(viewport={"width":1280,"height":720})
    cx.add_init_script("if(!localStorage.getItem('__s')){localStorage.setItem('deadHorizonMetaV5',%s);localStorage.setItem('__s','1')}"%json.dumps(json.dumps(old)))
    pg=cx.new_page(); pg.logs=[]; pg.on("pageerror",lambda e:pg.logs.append(str(e)[:200]))
    start(pg,URL)
    chk("I1 an old save with no hotbar field starts with its first six weapons", len(hb(pg))>=2 and len(hb(pg))<=6, str(hb(pg)))
    chk("I2 old save loads without errors", not pg.logs, str(pg.logs)); b.close()
bad=[k for k,v in R.items() if not v]; print("\n%d checks, %d failed"%(len(R),len(bad))); [print("  FAIL:",k) for k in bad]
sys.exit(1 if bad else 0)
