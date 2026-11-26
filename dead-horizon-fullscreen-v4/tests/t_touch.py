"""Touch-controls test: emulated phone (844x390, real multi-touch via CDP). Run with the server on :8802 (tests/with_srv.sh).
Checks that every control changes game state: move/jump sticks, weapon-slot taps, aim+fire (and release), two fingers at once,
heal/reload/bag/jump/skill/pause buttons, inert-at-title, portrait hint, no JS errors."""
import sys, json, os
from playwright.sync_api import sync_playwright
URL="http://localhost:8802/game.html?debug=1"
def run():
  with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox","--autoplay-policy=no-user-gesture-required"])
    ctx=b.new_context(viewport={'width':844,'height':390},device_scale_factor=2,is_mobile=True,has_touch=True,user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36")
    pg=ctx.new_page(); logs=[]
    pg.on("pageerror",lambda e:logs.append(str(e)[:300])); pg.on("console",lambda m:logs.append(m.text[:200]) if m.type=="error" else None)
    cdp=ctx.new_cdp_session(pg)
    def T(kind,pts): cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':pts})
    res={}
    def slot_xy(i):
        return pg.evaluate("""(i)=>{const G=DH_API,L=G.UX.LB,r=document.getElementById('c').getBoundingClientRect(),W=G.W,H=G.H,sc=L.sc,k=L.k,OX=Math.round((W-L.sheetW*sc)/2),LY=H-10-Math.round(L.slotH*sc);const tx=v=>W/2+(v-W/2)*k,ty=v=>(H-10)+(v-(H-10))*k;return [r.left+tx(OX+L.slotX[i]*sc+46*sc)/W*r.width,r.top+ty(LY+66*sc)/H*r.height]}""",i)
    pg.goto(URL); pg.wait_for_timeout(900)
    res['touch_on_at_title']=pg.evaluate("DH_TOUCH.on")
    res['ui_live_at_title']=pg.evaluate("document.getElementById('touch-ui').classList.contains('live')")
    box=pg.locator('#c').bounding_box()
    pg.touchscreen.tap(box['x']+box['width']/2, box['y']+box['height']*441/540); pg.wait_for_timeout(1200)
    res['ui_live_in_play']=pg.evaluate("document.getElementById('touch-ui').classList.contains('live')")
    pg.screenshot(path='/tmp/dh_touch_touch_idle.png')
    # give a varied loadout
    pg.evaluate("(a)=>{__DH.Meta.weaponsOwned=a.slice();__DH.Meta.hotbar=a.slice()}",['knife','pistol','shotgun','rifle','wand','launcher'])
    pg.wait_for_timeout(300)
    # --- MOVE: drag left stick right
    x0=pg.evaluate("__DH.P.x")
    T('touchStart',[{'x':120,'y':300,'id':1}]); T('touchMove',[{'x':190,'y':300,'id':1}]); pg.wait_for_timeout(600)
    pg.screenshot(path='/tmp/dh_touch_touch_move.png')
    x1=pg.evaluate("__DH.P.x"); T('touchEnd',[]); pg.wait_for_timeout(200)
    x2=pg.evaluate("__DH.P.x"); pg.wait_for_timeout(300); x3=pg.evaluate("__DH.P.x")
    res['move_right_dx']=round(x1-x0,1); res['stops_after_release']=abs(x3-x2)<1
    # move left
    T('touchStart',[{'x':190,'y':300,'id':1}]); T('touchMove',[{'x':120,'y':300,'id':1}]); pg.wait_for_timeout(500); x4=pg.evaluate("__DH.P.x"); T('touchEnd',[])
    res['move_left_dx']=round(x4-x3,1)
    # --- JUMP via stick up
    pg.wait_for_timeout(400); y0=pg.evaluate("__DH.P.y")
    T('touchStart',[{'x':150,'y':300,'id':1}]); T('touchMove',[{'x':150,'y':240,'id':1}]); pg.wait_for_timeout(180); y1=pg.evaluate("__DH.P.y"); T('touchEnd',[])
    res['jump_stick_dy']=round(y1-y0,1)
    # --- slot tap: select weapon 2 (pistol)
    pg.evaluate("document.querySelector('canvas#c')")
    sl=pg.evaluate("""(()=>{const G=DH_API,L=G.UX.LB,r=document.getElementById('c').getBoundingClientRect(),W=G.W,H=G.H,sc=L.sc,k=L.k,OX=Math.round((W-L.sheetW*sc)/2),LY=H-10-Math.round(L.slotH*sc);
      const tx=v=>W/2+(v-W/2)*k,ty=v=>(H-10)+(v-(H-10))*k;return [1,3].map(i=>{const x=tx(OX+L.slotX[i]*sc+46*sc),y=ty(LY+66*sc);return [r.left+x/W*r.width,r.top+y/H*r.height]})})()""")
    pg.touchscreen.tap(sl[0][0],sl[0][1]); pg.wait_for_timeout(300); res['slot2_equipped']=pg.evaluate("__DH.P.wp")
    pg.touchscreen.tap(sl[1][0],sl[1][1]); pg.wait_for_timeout(300); res['slot4_equipped']=pg.evaluate("__DH.P.wp")
    pg.touchscreen.tap(sl[0][0],sl[0][1]); pg.wait_for_timeout(300)
    # --- AIM/FIRE: hold right stick
    m0=pg.evaluate("__DH.P.mag.pistol"); 
    T('touchStart',[{'x':560,'y':300,'id':2}]); T('touchMove',[{'x':630,'y':290,'id':2}]); pg.wait_for_timeout(900)
    pg.screenshot(path='/tmp/dh_touch_touch_fire.png')
    m1=pg.evaluate("__DH.P.mag.pistol"); T('touchEnd',[]); pg.wait_for_timeout(250); m2=pg.evaluate("__DH.P.mag.pistol"); pg.wait_for_timeout(500); m3=pg.evaluate("__DH.P.mag.pistol")
    res['fire_shots_while_held']=m0-m1; res['stops_firing_after_release']=(m2==m3)
    # --- TWO FINGERS: move + aim at once
    xa=pg.evaluate("__DH.P.x"); mm0=pg.evaluate("__DH.P.mag.pistol")
    T('touchStart',[{'x':120,'y':300,'id':1},{'x':560,'y':300,'id':2}]); T('touchMove',[{'x':190,'y':300,'id':1},{'x':630,'y':300,'id':2}]); pg.wait_for_timeout(700)
    res['two_finger_moved']=round(pg.evaluate("__DH.P.x")-xa,1); res['two_finger_fired']=mm0-pg.evaluate("__DH.P.mag.pistol"); T('touchEnd',[]); pg.wait_for_timeout(200)
    # --- BUTTONS
    def tap_btn(a):
        bb=pg.locator(f'.tb[data-a="{a}"]').bounding_box(); pg.touchscreen.tap(bb['x']+bb['width']/2,bb['y']+bb['height']/2); pg.wait_for_timeout(250)
    pg.evaluate("(()=>{__DH.P.hp=40})()"); h0=pg.evaluate("__DH.P.hp"); tap_btn('heal'); res['heal_hp_gain']=round(pg.evaluate("__DH.P.hp")-h0,1)
    pg.evaluate("__DH.P.mag.pistol=2"); tap_btn('reload'); pg.wait_for_timeout(1500); res['reload_mag']=pg.evaluate("__DH.P.mag.pistol")
    tap_btn('bag'); res['bag_panel_open']=pg.evaluate("document.getElementById('panel').style.display")=='block'; tap_btn('bag')
    # jump button held
    bb=pg.locator('.tb[data-a="jump"]').bounding_box(); yy0=pg.evaluate("__DH.P.y")
    T('touchStart',[{'x':bb['x']+20,'y':bb['y']+20,'id':3}]); pg.wait_for_timeout(180); res['jump_button_dy']=round(pg.evaluate("__DH.P.y")-yy0,1); T('touchEnd',[])
    pg.wait_for_timeout(300)
    # wand shows SKILL button
    w=slot_xy(4); pg.touchscreen.tap(w[0],w[1])
    pg.wait_for_timeout(700); res['skill_button_visible_with_wand']=pg.evaluate("!document.getElementById('t-skill').hidden")
    pg.screenshot(path='/tmp/dh_touch_touch_wand.png')
    # --- PAUSE
    tap_btn('pause'); res['paused']=pg.evaluate("__DH.GameState.isPaused"); pg.wait_for_timeout(250); res['ui_inert_when_paused']=not pg.evaluate("document.getElementById('touch-ui').classList.contains('live')")
    pg.screenshot(path='/tmp/dh_touch_touch_pause.png')
    res['errors']=logs
    print(json.dumps(res,indent=1)); b.close()
def portrait():
  with sync_playwright() as p:
    b=p.chromium.launch(args=["--no-sandbox"])
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
    pg=ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(900)
    print('rotate_hint_portrait',pg.evaluate("document.getElementById('t-rotate').classList.contains('show')"))
    pg.screenshot(path='/tmp/dh_touch_touch_portrait.png'); b.close()
run(); portrait()
