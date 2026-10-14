"""Weapon-skin regression test (Pistol Redline / CT Tactical, Pump Shotgun Heirloom / Blue Arc).
Run from the project root:  python3 -m http.server 8802 &  then  python3 tests/t_weapon_skins.py
Checks: assets load (no HTTP>=400, no console errors), buy/equip through the real shop UI, per-weapon slot targeting,
coin accounting, persistence across reload, unequip fallback, normalizeMeta stripping unknown / un-owned skin ids."""
import json, sys
from playwright.sync_api import sync_playwright
URL = "http://localhost:8802/game.html?debug=1"
SK = {'pistol_redline': ('pistol', 1500), 'pistol_ct': ('pistol', 2500), 'shotgun_heirloom': ('shotgun', 1200), 'shotgun_bluearc': ('shotgun', 3000)}
bad = []
def check(name, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + name, info)
    if not ok: bad.append(name)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-gpu", "--use-gl=swiftshader", "--autoplay-policy=no-user-gesture-required"])
    pg = b.new_context(viewport={"width": 1280, "height": 720}).new_page()
    logs, http = [], []
    pg.on("console", lambda m: logs.append(m.text[:200]) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: logs.append(str(e)[:200]))
    pg.on("response", lambda r: http.append((r.status, r.url)) if r.status >= 400 else None)
    def start():
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(800)
        box = pg.locator("#c").bounding_box(); pg.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] * 342 / 540); pg.wait_for_timeout(800)
    start(); ev = pg.evaluate
    ev("__DH.Meta.coins=50000"); coins0 = 50000
    ev("__DH.openMeta('shop')"); pg.wait_for_timeout(300)
    for sid, (wp, price) in SK.items():
        pg.click(f'[data-selectcos="{sid}"]'); pg.wait_for_timeout(120)
        label = ev("document.getElementById('cosmetic-target-label').textContent")
        check(f'{sid} shop target label names the right weapon', ('Pump Shotgun' if wp == 'shotgun' else 'Pistol') in label, label)
        pg.click(f'[data-buy="{sid}"]'); pg.wait_for_timeout(120); pg.click(f'[data-equip="{sid}"]'); pg.wait_for_timeout(120)
        check(f'{sid} owned+equipped on {wp}', ev(f"__DH.Meta.ownedCos.includes('{sid}')&&__DH.Meta.equipped.weapons.{wp}==='{sid}'"))
    spent = sum(v[1] for v in SK.values())
    check('coins charged exactly once each', ev("__DH.Meta.coins") == coins0 - spent, ev("__DH.Meta.coins"))
    # the later skin of each weapon replaces the earlier one in that weapon's slot (one skin per weapon)
    check('one skin per weapon slot', ev("__DH.Meta.equipped.weapons.pistol==='pistol_ct'&&__DH.Meta.equipped.weapons.shotgun==='shotgun_bluearc'"))
    start()
    check('equipped skins persist after reload', ev("__DH.Meta.equipped.weapons.pistol==='pistol_ct'&&__DH.Meta.equipped.weapons.shotgun==='shotgun_bluearc'"))
    ev("__DH.openMeta('shop')"); pg.wait_for_timeout(300)
    pg.click('[data-selectcos="pistol_ct"]'); pg.click('[data-unequip="pistol_ct"]'); pg.wait_for_timeout(150)
    check('unequip returns to stock pistol', ev("!__DH.Meta.equipped.weapons.pistol"))
    ev("localStorage.setItem('deadHorizonMetaV5',JSON.stringify({ownedCos:['char_survivor','knife_m9_default'],equipped:{weapons:{pistol:'pistol_redline',shotgun:'nope'}}}))")
    start()
    check('un-owned / unknown skin ids stripped on load', ev("Object.keys(__DH.Meta.equipped.weapons).join()")=='knife')
    check('no HTTP errors', not http, http); check('no console errors', not logs, logs)
    b.close()
sys.exit(1 if bad else 0)
