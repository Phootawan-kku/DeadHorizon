import sys; sys.path.insert(0,'/home/claude')
from h import *
with sync_playwright() as p:
    b,ctx,pg = launch(p)
    box = start(pg)
    print("state", ev(pg,"({st:__DH.S.state,y:Math.round(__DH.P.y),gy:Math.round(__DH.gy(__DH.P.x)),anim:__DH.PA.state,wp:__DH.P.wp,audio:__DH.AU.ctxState()})"))
    pg.wait_for_timeout(1500)
    pg.screenshot(path="/home/claude/shots/new_play1.png")
    print("LOGS", pg.logs[:10]); print("FAILED", pg.fails)
    b.close()
