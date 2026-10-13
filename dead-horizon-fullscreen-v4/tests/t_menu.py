import sys; sys.path.insert(0,'/home/claude')
from h import *
with sync_playwright() as p:
    b,ctx,pg=launch(p,1280,720)
    pg.goto("http://localhost:8802/game.html?debug=1",wait_until="load"); pg.wait_for_timeout(1200)
    pg.add_style_tag(content="#debug-hud{display:none!important}"); pg.screenshot(path="/home/claude/shots/final/00_title_menu.png")
    box=pg.locator("#c").bounding_box(); pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540); pg.wait_for_timeout(600)
    pg.evaluate("__DH.S.left=0;__DH.Z.length=0;__DH.P.hp=0;__DH.S.state='dead';__DH.PA.onDeath()"); pg.wait_for_timeout(1500)
    print("state:",pg.evaluate("__DH.S.state"),"anim:",pg.evaluate("__DH.PA.state"))
    pg.screenshot(path="/home/claude/shots/final/12_game_over.png"); print(pg.logs[:3]); b.close()
