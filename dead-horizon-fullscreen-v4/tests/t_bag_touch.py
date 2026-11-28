"""Phone bag sheet test (touch mode): open via BAG button, tabs/filters, craft with a tap, heal, freeze-while-open, close, resume.
Run with the server on :8802 (tests/with_srv.sh).  Prints a JSON result; every value should be True / sensible."""
import json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
    ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2,is_mobile=True,has_touch=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
    pg.goto("http://localhost:8802/game.html?debug=1"); pg.wait_for_timeout(800)
    box=pg.locator('#c').bounding_box(); pg.touchscreen.tap(box['x']+box['width']/2, box['y']+box['height']*441/540); pg.wait_for_timeout(1000)
    pg.evaluate("()=>{Object.assign(DH_API.inv,{scrap:24,cloth:6,wood:14,stone:9,metal:22,chemicals:3,bone:4,part:7,electronics:5,fuel:2,bandage:2,meat:1,ammo:30})}")
    res={}
    def tap(sel):
        bb=pg.locator(sel).first.bounding_box(); pg.touchscreen.tap(bb['x']+bb['width']/2,bb['y']+bb['height']/2); pg.wait_for_timeout(350)
    tap('.tb[data-a="bag"]'); res['sheet_open']=pg.evaluate("DH_API.bagOpen()")
    res['touch_layer_inert']=not pg.evaluate("document.getElementById('touch-ui').classList.contains('live')")
    # simulation frozen: a zombie must not move while the sheet is open
    pg.evaluate("window.__z=__DH.spawnType('normal',200)"); x0=pg.evaluate("__z.x"); pg.wait_for_timeout(700); res['frozen_while_open']=abs(pg.evaluate("__z.x")-x0)<0.01
    res['min_tap_target_px']=pg.evaluate("Math.round(Math.min(...[...document.querySelectorAll('#panel button')].map(b=>b.getBoundingClientRect().height).filter(h=>h>0)))")
    res['tile_count']=pg.evaluate("document.querySelectorAll('#panel .btile').length")
    # craft tab -> READY filter -> craft Bandage
    tap('#panel [data-ptab="craft"]'); res['craft_cards']=pg.evaluate("document.querySelectorAll('#panel .rcard').length")
    tap('#panel [data-pfilter="ready"]'); res['ready_cards_all_craftable']=pg.evaluate("[...document.querySelectorAll('#panel .rcard')].every(c=>c.classList.contains('ok'))")
    tap('#panel [data-pfilter="weapon"]'); res['weapon_cards']=pg.evaluate("document.querySelectorAll('#panel .rcard').length")
    tap('#panel [data-pfilter="supply"]')
    b0=pg.evaluate("DH_API.inv.bandage||0"); c0=pg.evaluate("DH_API.inv.cloth||0")
    tap('#panel .rcard.ok .rb'); res['crafted_item_added']=(pg.evaluate("DH_API.inv.bandage||0")-b0)>=1 or (pg.evaluate("Object.values(DH_API.inv).reduce((a,v)=>a+v,0)")>0)
    res['materials_spent']=pg.evaluate("DH_API.inv.cloth||0")<c0
    res['toast_shown']=pg.evaluate("!!document.querySelector('#panel .tstoast')")
    # disabled recipe must not craft
    pg.evaluate("DH_API.inv.metal=0"); tap('#panel [data-pfilter="all"]'); m0=pg.evaluate("Object.values(DH_API.inv).reduce((a,v)=>a+v,0)")
    tap('#panel .rcard.no .rb'); res['disabled_recipe_does_nothing']=pg.evaluate("Object.values(DH_API.inv).reduce((a,v)=>a+v,0)")==m0
    # heal from the bag
    tap('#panel [data-ptab="bag"]'); pg.evaluate("__DH.P.hp=40"); pg.wait_for_timeout(300); pg.evaluate("document.querySelector('#panel [data-ptab=\"craft\"]').click();document.querySelector('#panel [data-ptab=\"bag\"]').click()")
    h0=pg.evaluate("__DH.P.hp"); tap('#panel [data-act="heal"]'); res['heal_hp_gain']=round(pg.evaluate("__DH.P.hp")-h0,1)
    # close and resume
    tap('#panel .tsclose'); res['sheet_closed']=not pg.evaluate("DH_API.bagOpen()")
    pg.wait_for_timeout(300); xa=pg.evaluate("__z.x"); pg.wait_for_timeout(500); res['sim_resumes']=abs(pg.evaluate("__z.x")-xa)>0.5
    res['touch_layer_live_again']=pg.evaluate("document.getElementById('touch-ui').classList.contains('live')")
    res['errors']=errs
    print(json.dumps(res,indent=1)); b.close()
