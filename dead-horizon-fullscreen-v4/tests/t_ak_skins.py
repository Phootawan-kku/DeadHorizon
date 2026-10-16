"""AK-47 skin regression (Assault Rifle: Arctic Ghost / Neon Circuit / Royal Bengal). Needs a static server on :8802.
Checks: default AK + skin assets load (no HTTP>=400, no console errors), buy/equip through the real shop UI, targets the rifle slot,
coin accounting, persistence across reload, unequip fallback, normalizeMeta stripping un-owned ids; saves close-up screenshots."""
import sys
sys.path.insert(0, '.')
from h import *
from playwright.sync_api import sync_playwright
SK = {'rifle_arctic_ghost': 1500, 'rifle_neon_circuit': 3000, 'rifle_royal_bengal': 4800}
bad = []
def check(name, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + name, info)
    if not ok: bad.append(name)
with sync_playwright() as p:
    b, ctx, pg = launch(p, 1280, 720)
    http = []
    pg.on("response", lambda r: http.append((r.status, r.url)) if r.status >= 400 else None)
    start(pg, settle=800); ev1 = pg.evaluate
    pg.add_style_tag(content="#debug-hud{display:none!important}")
    ev1("__DH.Meta.coins=50000"); ev1("__DH.own('rifle');__DH.equip('rifle')")
    box = pg.locator("#c").bounding_box()
    def shot_gun(name):
        pg.mouse.move(box['x'] + box['width'] * .8, box['y'] + box['height'] * .55); pg.wait_for_timeout(500)
        pos = ev1("(()=>{const P=__DH.P;return {x:P.x-__DH.cx,y:P.y}})()")
        k = box['width'] / 960
        pg.screenshot(path=f"/home/claude/shots/{name}.png", clip={'x': box['x'] + (pos['x'] - 60) * k, 'y': box['y'] + (pos['y'] - 90) * k, 'width': 160 * k, 'height': 110 * k})
    shot_gun('ak_in_hand_default')
    ev1("__DH.openMeta('shop')"); pg.wait_for_timeout(300)
    pg.click('[data-selectcos="rifle_neon_circuit"]'); pg.wait_for_timeout(200)
    pg.screenshot(path="/home/claude/shots/ak_shop.png")
    for sid, price in SK.items():
        pg.click(f'[data-selectcos="{sid}"]'); pg.wait_for_timeout(120)
        label = ev1("document.getElementById('cosmetic-target-label').textContent")
        check(f'{sid} shop target names Assault Rifle', 'Assault Rifle' in label, label)
        pg.click(f'[data-buy="{sid}"]'); pg.wait_for_timeout(120); pg.click(f'[data-equip="{sid}"]'); pg.wait_for_timeout(120)
        check(f'{sid} owned + equipped on rifle', ev1(f"__DH.Meta.ownedCos.includes('{sid}')&&__DH.Meta.equipped.weapons.rifle==='{sid}'"))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(700)
        shot_gun('ak_in_hand_' + sid)
        ev1("__DH.openMeta('shop')"); pg.wait_for_timeout(250)
    check('coins charged exactly once each', ev1("__DH.Meta.coins") == 50000 - sum(SK.values()), ev1("__DH.Meta.coins"))
    check('pistol / shotgun slots untouched', ev1("!__DH.Meta.equipped.weapons.pistol&&!__DH.Meta.equipped.weapons.shotgun"))
    check('one skin per weapon slot', ev1("__DH.Meta.equipped.weapons.rifle==='rifle_royal_bengal'"))
    start(pg, settle=800)
    check('equipped AK skin persists after reload', ev1("__DH.Meta.equipped.weapons.rifle==='rifle_royal_bengal'"))
    ev1("__DH.openMeta('shop')"); pg.wait_for_timeout(300)
    pg.click('[data-selectcos="rifle_royal_bengal"]'); pg.click('[data-unequip="rifle_royal_bengal"]'); pg.wait_for_timeout(150)
    check('unequip returns to the stock AK', ev1("!__DH.Meta.equipped.weapons.rifle"))
    ev1("localStorage.setItem('deadHorizonMetaV5',JSON.stringify({ownedCos:['char_survivor','knife_m9_default'],equipped:{weapons:{rifle:'rifle_neon_circuit'}}}))")
    start(pg, settle=800)
    check('un-owned AK skin id is stripped on load', ev1("!__DH.Meta.equipped.weapons.rifle"))
    check('no HTTP errors for assets', not http, http[:3])
    errs = [l for l in pg.logs if l[0] in ('pageerror', 'error')]
    check('no console / page errors', not errs, errs[:2])
    b.close()
print('\nFAILED: %s' % bad if bad else '\nALL PASSED'); sys.exit(1 if bad else 0)
