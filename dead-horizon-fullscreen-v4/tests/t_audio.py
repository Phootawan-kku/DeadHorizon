import sys, json; sys.path.insert(0,'/home/claude')
from h import *
R={}
def chk(name, ok, info=""): R[name]=("PASS" if ok else "FAIL", info); print(("PASS " if ok else "FAIL ")+name, info)
with sync_playwright() as p:
    b,ctx,pg = launch(p, 1280, 720)
    pg.goto("http://localhost:8802/game.html?debug=1", wait_until="load"); pg.wait_for_timeout(600)
    chk("no AudioContext before user gesture (autoplay-safe)", pg.evaluate("__DH.AU.ctxState()")=="none")
    box=pg.locator("#c").bounding_box(); pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540); pg.wait_for_timeout(700)
    chk("AudioContext running after first click", pg.evaluate("__DH.AU.ctxState()")=="running")
    # ---- offline level analysis of every sound ----
    res=pg.evaluate("""async()=>{const out=[];for(const n of __DH.AU.names())out.push(await __DH.AU.renderOffline(n));return out}""")
    clip=[r for r in res if r['peak']>0.99]; silent=[r for r in res if r['peak']<0.02 or r['activeSeconds']<0.01]
    loud=sorted(res,key=lambda r:-r['peak'])[:3]; quiet=sorted(res,key=lambda r:r['peak'])[:3]
    chk("all %d sounds render non-silent"%len(res), not silent, str([s['name'] for s in silent]))
    chk("no sound clips (peak<0.99 after compressor)", not clip, str([(c['name'],round(c['peak'],2)) for c in clip]))
    print("  loudest:",[(r['name'],round(r['peak'],2)) for r in loud]," quietest:",[(r['name'],round(r['peak'],3)) for r in quiet])
    json.dump(res,open('/home/claude/res_audio_levels.json','w'))
    # ---- settings UI: pause menu sliders ----
    pg.evaluate("__DH.setPaused(true)"); pg.wait_for_timeout(200)
    has=pg.evaluate("!!document.querySelector('#pause-audio [data-aud=master]')")
    chk("pause menu shows audio sliders", has)
    pg.evaluate("""(()=>{const el=document.querySelector('#pause-audio [data-aud=master]');el.value=30;el.dispatchEvent(new Event('input',{bubbles:true}))})()""")
    pg.evaluate("""(()=>{const el=document.querySelector('#pause-audio [data-aud=sfx]');el.value=55;el.dispatchEvent(new Event('input',{bubbles:true}))})()""")
    pg.wait_for_timeout(300); g=pg.evaluate("__DH.AU.gains()")
    chk("slider changes master/sfx bus gain", abs(g['master']-.3)<.02 and abs(g['sfx']-.55)<.02, str(g))
    pg.click("#pause-audio [data-aud-mute]"); pg.wait_for_timeout(300)
    g=pg.evaluate("__DH.AU.gains()"); chk("mute button silences master bus", g['master']<.01 and pg.evaluate("__DH.AU.settings.mute"), str(g))
    n0=pg.evaluate("__DH.AU.stats.played"); pg.evaluate("__DH.AU.play('shot_pistol')"); chk("no audio nodes are created while muted", pg.evaluate("__DH.AU.stats.played")==n0)
    pg.click("#pause-audio [data-aud-mute]"); pg.wait_for_timeout(300); g=pg.evaluate("__DH.AU.gains()")
    chk("unmute restores volume", abs(g['master']-.3)<.02, str(g))
    # persistence across reload
    pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    st=pg.evaluate("JSON.stringify(__DH?__DH.AU.settings:null)"); chk("audio settings persist after reload", '"master":0.3' in st and '"sfx":0.55' in st, st)
    # META settings tab
    pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540); pg.wait_for_timeout(500)
    pg.evaluate("__DH.openMeta('settings')"); pg.wait_for_timeout(300)
    chk("META → SETTINGS tab renders audio controls", pg.evaluate("!!document.querySelector('#meta-content [data-aud=amb]')") if pg.evaluate("!!document.getElementById('meta-content')") else pg.evaluate("!!document.querySelector('.meta-content [data-aud=amb], #metaContent [data-aud=amb]')"))
    pg.screenshot(path="/home/claude/shots/ui_meta_settings.png")
    pg.evaluate("document.querySelector('[data-aud-mute]')&&0"); 
    # M key toggles
    pg.evaluate("__DH.AU.set('mute',false)"); pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    print("LOGS",pg.logs[:5]); print("FAILED REQ",pg.fails)
    b.close()
json.dump(R,open('/home/claude/res_audio.json','w'))
