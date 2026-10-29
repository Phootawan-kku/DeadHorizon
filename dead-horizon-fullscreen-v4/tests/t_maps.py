"""Per-map backdrops: each map draws its own image, loaded on demand; Maps tab shows thumbnails.
Run: bash tests/with_srv.sh <project dir> 8802 python3 tests/t_maps.py"""
import sys; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(n,ok,i=""): R[n]=ok; print(("PASS " if ok else "FAIL ")+n,i)
def frames(pg,n=8): pg.evaluate("n=>new Promise(r=>{(function f(){--n>0?requestAnimationFrame(f):r()})()})",n)
MAPS={'forest':'forest','industrial':'industrial','hospital':'hospital','military':'military'}
with sync_playwright() as p:
    b,ctx,pg=launch(p); start(pg,"http://localhost:8802/game.html?debug=1")
    pg.evaluate("document.getElementById('debug-hud').style.display='none'")
    ART="window.DEAD_HORIZON_ART"
    chk("A1 map backdrops are NOT preloaded at startup (lazy)", pg.evaluate(f"!{ART}.get('assets/environment/maps/military.png')"))
    sky={}
    for m in ['town',*MAPS]:
        pg.evaluate("(m)=>{__DH.S.map=m;__DH.Z.length=0}",m)
        if m!='town': pg.wait_for_function(f"{ART}.ready('assets/environment/maps/{m}.png')",timeout=8000)
        frames(pg)
        # sample the sky area of the real canvas (top-centre, away from HUD panels)
        sky[m]=pg.evaluate("()=>{const c=document.querySelector('canvas'),x=c.getContext('2d').getImageData(Math.floor(c.width*0.62),Math.floor(c.height*0.30),1,1).data;return [x[0],x[1],x[2]]}")
    print(sky)
    chk("B1 every map draws a different backdrop", len({tuple(v) for v in sky.values()})==5, str(sky))
    chk("B2 backdrop images are 1280x720", all(pg.evaluate(f"{ART}.get('assets/environment/maps/{m}.png').naturalWidth")==1280 for m in MAPS))
    chk("B3 town still uses the original backdrop", pg.evaluate(f"{ART}.ready('assets/environment/dead_horizon_bg.png')"))
    pg.evaluate("__DH.Meta.stats.bestWave=30"); pg.keyboard.press("KeyO"); frames(pg); pg.click("[data-tab=maps]"); pg.wait_for_timeout(500)
    chk("C1 Maps tab shows a thumbnail for each of the 5 maps", pg.locator(".map-thumb").count()==5)
    chk("C2 locked map (military, wave 50) is dimmed and its SELECT is disabled", pg.locator(".map-locked").count()==1 and pg.locator("[data-map=military]").is_disabled())
    pg.click("[data-map=hospital]"); frames(pg,4)
    chk("C3 selecting a map sets it and marks it SELECTED", pg.evaluate("__DH.Meta.map")=='hospital' and "SELECTED" in pg.locator(".map-sel").inner_text())
    pg.keyboard.press("KeyO"); frames(pg)
    chk("D1 no console errors / failed requests", not [l for l in pg.logs if not (isinstance(l,tuple) and l[0]=='warning')] and not pg.fails, str((pg.logs,pg.fails[:3]))); b.close()
bad=[k for k,v in R.items() if not v]; print("\n%d checks, %d failed"%(len(R),len(bad))); sys.exit(1 if bad else 0)
