import sys; sys.path.insert(0,'/home/claude')
from h import *
with sync_playwright() as p:
    b,ctx,pg = launch(p,1280,720); start(pg)
    pg.evaluate("window.__fsl=[];document.addEventListener('fullscreenchange',()=>__fsl.push(['change',!!document.fullscreenElement,Math.round(performance.now())]));document.addEventListener('fullscreenerror',()=>__fsl.push(['ERROR',Math.round(performance.now())]))")
    for i in range(3):
        pg.click("#fullscreen-toggle"); 
        for t in range(6):
            pg.wait_for_timeout(250); print(i,t,pg.evaluate("[!!document.fullscreenElement,innerWidth,innerHeight,document.body.className||'']"))
        print("events:",pg.evaluate("__fsl"))
    b.close()
