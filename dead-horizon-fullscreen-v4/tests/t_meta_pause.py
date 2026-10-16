"""META menu must pause the run (V30). Needs a static server on :8802 (see with_srv.sh) and ?debug=1 for window.__DH."""
import sys
sys.path.insert(0, '.')
from h import *
from playwright.sync_api import sync_playwright

results = []
def check(name, ok, extra=''):
    results.append(ok)
    print(('PASS ' if ok else 'FAIL ') + name + (('  ' + str(extra)) if extra else ''))

def snap(pg):
    return pg.evaluate("""()=>({t:__DH.S.t,paused:__DH.GameState.isPaused,meta:__DH.GameState.metaOpen,
        z:__DH.Z.map(z=>Math.round(z.x*100)/100).join(','),inter:__DH.S.inter,left:__DH.S.left,hp:__DH.P.hp})""")

with sync_playwright() as p:
    b, ctx, pg = launch(p, 1280, 720)
    start(pg, settle=1500)

    # 1) clicking META pauses
    a = snap(pg)
    pg.click('#metaBtn'); pg.wait_for_timeout(250)
    s1 = snap(pg); pg.wait_for_timeout(1500); s2 = snap(pg)
    check('META click sets metaOpen', s1['meta'] is True)
    check('game clock frozen while META open', abs(s2['t'] - s1['t']) < 1e-6, (s1['t'], s2['t']))
    check('enemy positions frozen while META open', s1['z'] == s2['z'])
    check('wave spawner/intermission frozen', s1['inter'] == s2['inter'] and s1['left'] == s2['left'])
    check('"GAME PAUSED" chip visible', pg.is_visible('#meta-paused'))

    # 2) gameplay keys are ignored while paused
    pg.keyboard.press('Digit1'); pg.keyboard.press('KeyH'); pg.keyboard.press('KeyR'); pg.wait_for_timeout(200)
    s3 = snap(pg)
    check('keys do not advance the game while META open', abs(s3['t'] - s2['t']) < 1e-6)

    # 3) ESC resumes (and does NOT open the pause menu)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(900)
    s4 = snap(pg)
    check('ESC closes META', s4['meta'] is False and not pg.is_visible('#meta-menu'))
    check('ESC from META does not show PAUSED card', s4['paused'] is False and not pg.is_visible('#pause-menu'))
    check('game resumes after closing META', s4['t'] > s3['t'] + 0.2, (s3['t'], s4['t']))

    # 4) O toggles, backdrop closes, CLOSE button closes
    pg.keyboard.press('KeyO'); pg.wait_for_timeout(200)
    check('O opens META', snap(pg)['meta'] is True)
    pg.keyboard.press('KeyO'); pg.wait_for_timeout(200)
    check('O closes META', snap(pg)['meta'] is False)
    pg.click('#metaBtn'); pg.wait_for_timeout(200)
    pg.mouse.click(8, 8); pg.wait_for_timeout(200)
    check('backdrop click closes META', snap(pg)['meta'] is False)
    pg.click('#metaBtn'); pg.wait_for_timeout(200)
    pg.click('#meta-close'); pg.wait_for_timeout(300)
    check('RESUME button closes META', snap(pg)['meta'] is False)

    # 5) META opened from the Tab inventory panel pauses too
    pg.keyboard.press('Tab'); pg.wait_for_timeout(200)
    pg.click('#panel [data-meta]'); pg.wait_for_timeout(200)
    t0 = snap(pg)['t']; pg.wait_for_timeout(800)
    check('META via inventory panel pauses', snap(pg)['meta'] is True and abs(snap(pg)['t'] - t0) < 1e-6)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    # 6) pause menu + META interplay: closing META returns to the pause menu, still paused
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    check('ESC pauses (pause card)', snap(pg)['paused'] is True)
    pg.keyboard.press('KeyO'); pg.wait_for_timeout(200)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    s5 = snap(pg); pg.wait_for_timeout(600); s6 = snap(pg)
    check('closing META while paused stays paused', s5['paused'] is True and s5['meta'] is False and abs(s6['t'] - s5['t']) < 1e-6)
    pg.click('#resumeGame'); pg.wait_for_timeout(900)
    check('RESUME continues the game', snap(pg)['t'] > s6['t'] + 0.2)

    page_errors = [l for l in pg.logs if l[0] == 'pageerror']
    check('no page errors', not page_errors, page_errors[:2])
    b.close()

print('\n%d/%d passed' % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
