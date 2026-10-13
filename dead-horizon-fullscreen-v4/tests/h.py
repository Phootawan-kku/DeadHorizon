import json
from playwright.sync_api import sync_playwright
def launch(p, w=1280, h=720, args=None):
    b = p.chromium.launch(args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"] + (args or []))
    ctx = b.new_context(viewport={"width":w,"height":h})
    pg = ctx.new_page()
    pg.logs=[]; pg.fails=[]
    pg.on("console", lambda m: pg.logs.append((m.type, m.text[:300])) if m.type in ("error","warning") else None)
    pg.on("pageerror", lambda e: pg.logs.append(("pageerror", str(e)[:400])))
    pg.on("requestfailed", lambda r: pg.fails.append(r.url))
    return b, ctx, pg
def start(pg, url="http://localhost:8802/game.html?debug=1", settle=900):
    pg.goto(url, wait_until="load"); pg.wait_for_timeout(700)
    box = pg.locator("#c").bounding_box()
    pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540)
    pg.wait_for_timeout(settle)
    return box
def ev(pg, js): return pg.evaluate(js)
