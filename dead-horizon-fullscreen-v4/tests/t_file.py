import sys; sys.path.insert(0,'/home/claude')
from h import *
with sync_playwright() as p:
    b,ctx,pg=launch(p,1280,720)
    pg.goto("file:///home/claude/work/dead-horizon-fullscreen-v4/game.html?debug=1",wait_until="load"); pg.wait_for_timeout(1200)
    box=pg.locator("#c").bounding_box(); pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540); pg.wait_for_timeout(800)
    ok=pg.evaluate("typeof __DH!=='undefined'")
    if ok:
        pg.evaluate("__DH.P.cd=0;__DH.equip('pistol');__DH.PA.shots=0"); pg.mouse.move(box["x"]+box["width"]*.8,box["y"]+box["height"]*.5); pg.wait_for_timeout(100); pg.mouse.down(); pg.wait_for_timeout(150); pg.mouse.up()
        print("state",pg.evaluate("__DH.S.state"),"shots",pg.evaluate("__DH.PA.shots"),"muzzle",pg.evaluate("JSON.stringify(__DH.muzzleWorld())"),"y",pg.evaluate("Math.round(__DH.P.y)"))
    print("hook:",ok,"| console:",pg.logs[:4]); b.close()
