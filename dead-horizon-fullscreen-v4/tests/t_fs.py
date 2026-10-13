import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(name, ok, info=""): R[name]=("PASS" if ok else "FAIL", info); print(("PASS " if ok else "FAIL ")+name, info)
def ptr(pg): return pg.evaluate("({x:__DH.mouse.x,y:__DH.mouse.y,fs:!!document.fullscreenElement,t:__DH.S.t,st:__DH.S.state})")
def map_ok(pg):
    bx=pg.locator("#c").bounding_box(); pg.mouse.move(bx["x"]+bx["width"]*.75, bx["y"]+bx["height"]*.25); pg.wait_for_timeout(150); a=ptr(pg)
    return abs(a['x']-720)<2 and abs(a['y']-135)<2, f"pointer→{a['x']:.1f},{a['y']:.1f} canvas {bx['width']:.0f}x{bx['height']:.0f}"
with sync_playwright() as p:
    b,ctx,pg = launch(p,1280,720); start(pg); pg.wait_for_timeout(500)
    chk("Start auto-enters fullscreen (original behaviour preserved)", ptr(pg)['fs'])
    ok,i=map_ok(pg); chk("fullscreen: pointer→logical mapping correct", ok, i)
    pg.evaluate("__DH.P.cd=0;__DH.equip('pistol');__DH.PA.shots=0"); bx=pg.locator("#c").bounding_box(); pg.mouse.move(bx["x"]+bx["width"]*.9, bx["y"]+bx["height"]*.5); pg.wait_for_timeout(120)
    aim=pg.evaluate("__DH.P.aim"); pg.mouse.down(); pg.wait_for_timeout(120); pg.mouse.up()
    chk("fullscreen: aiming + shooting work", abs(aim)<.6 and pg.evaluate("__DH.PA.shots")>=1, f"aim={aim:.2f} shots={pg.evaluate('__DH.PA.shots')}")
    pg.screenshot(path="/home/claude/shots/fullscreen_on.png")
    pg.click("#fullscreen-toggle"); pg.wait_for_timeout(900)
    chk("leave fullscreen via toggle button", not ptr(pg)['fs'])
    ok,i=map_ok(pg); chk("windowed after leaving: mapping correct, game still in play", ok and ptr(pg)['st']=='play', i)
    t0=ptr(pg)['t']; pg.wait_for_timeout(500); chk("game loop advancing after leaving fullscreen", ptr(pg)['t']>t0+.3)
    pg.click("#fullscreen-toggle"); pg.wait_for_timeout(900)
    chk("re-enter fullscreen via toggle button", ptr(pg)['fs'])
    ok,i=map_ok(pg); chk("re-entered: mapping correct", ok, i)
    pg.evaluate("__DH.P.cd=0;__DH.PA.shots=0"); pg.mouse.down(); pg.wait_for_timeout(120); pg.mouse.up()
    chk("re-entered: shooting works", pg.evaluate("__DH.PA.shots")>=1)
    print("console/page errors:",pg.logs[:5]); b.close()
json.dump(R,open('/home/claude/res_fs.json','w'))
