import sys, json; sys.path.insert(0,'/home/claude')
from h import *
VP=[(1280,720),(1366,768),(1920,1080),(2560,1440),(1024,768),(844,390)]
JS="""()=>{const c=document.getElementById('c').getBoundingClientRect(),sc=c.width/960,H=540,W=960;
 const L=(n,x,y,w,h)=>({n,x:c.left+x*sc,y:c.top+y*sc,w:w*sc,h:h*sc});
 const hud=[L('health',12,12,232,42),L('coins',12,58,124,20),L('wave',W/2-112,10,224,46),L('kills',W-112,64,100,20),L('consumables',12,H-100,150,46),L('weaponbar',201,H-105,558,51),L('ammo',W-196,H-100,184,46)];
 const sel=['.game-control','#game-help','#statusFS','#boss-hud','#panel'];const html=[];
 for(const s of sel)document.querySelectorAll(s).forEach(e=>{const r=e.getBoundingClientRect(),cs=getComputedStyle(e);if(r.width>0&&r.height>0&&cs.display!=='none'&&cs.visibility!=='hidden')html.push({n:s+(e.id?'#'+e.id:'')+':'+(e.textContent||'').trim().slice(0,12),x:r.left,y:r.top,w:r.width,h:r.height})});
 const ov=(a,b)=>a.x<b.x+b.w&&b.x<a.x+a.w&&a.y<b.y+b.h&&b.y<a.y+a.h;const hits=[];
 for(const a of html)for(const b of hud)if(ov(a,b))hits.push(a.n+' ✕ '+b.n);
 for(let i=0;i<hud.length;i++)for(let j=i+1;j<hud.length;j++)if(ov(hud[i],hud[j]))hits.push(hud[i].n+' ✕ '+hud[j].n);
 for(let i=0;i<html.length;i++)for(let j=i+1;j<html.length;j++)if(ov(html[i],html[j]))hits.push(html[i].n+' ✕ '+html[j].n);
 const out=html.filter(a=>a.x<-1||a.y<-1||a.x+a.w>innerWidth+1||a.y+a.h>innerHeight+1).map(a=>a.n);
 const cr=hud.filter(a=>a.x<c.left-1||a.y<c.top-1||a.x+a.w>c.right+1||a.y+a.h>c.bottom+1).map(a=>a.n);
 return{canvas:[Math.round(c.width),Math.round(c.height)],scale:+sc.toFixed(3),overlaps:hits,htmlOutside:out,hudOutside:cr,htmlCount:html.length}}"""
with sync_playwright() as p:
    for (w,h) in VP:
        b,ctx,pg = launch(p,w,h); box=start(pg)
        pg.evaluate("__DH.S.left=0;__DH.Z.length=0")
        r=pg.evaluate(JS); pg.wait_for_timeout(300)
        pg.screenshot(path=f"/home/claude/shots/layout_{w}x{h}.png")
        print(f"{w}x{h}", json.dumps(r, ensure_ascii=False), "| console:",pg.logs[:2])
        b.close()
