import sys, json; sys.path.insert(0,'/home/claude')
from h import *
with sync_playwright() as p:
    b,ctx,pg = launch(p)
    pg.goto("http://localhost:8802/game.html?debug=1", wait_until="load"); pg.wait_for_timeout(500)
    box=pg.locator("#c").bounding_box(); pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540); pg.wait_for_timeout(500)
    res=pg.evaluate("async()=>{const o=[];for(const n of __DH.AU.names())o.push(await __DH.AU.renderOffline(n));return o}")
    json.dump(res,open('/home/claude/res_audio_levels.json','w')); b.close()
