import sys, json
from playwright.sync_api import sync_playwright
url, tag = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv)>3 else 18
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width":int(__import__("os").environ.get("VW",1280)),"height":int(__import__("os").environ.get("VH",720))})
    errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.on("console", lambda m: errs.append(m.text[:200]) if m.type=="error" else None)
    pg.goto(url, wait_until="load"); pg.wait_for_timeout(800)
    box = pg.locator("#c").bounding_box()
    pg.mouse.click(box["x"]+box["width"]/2, box["y"]+box["height"]*342/540)
    pg.wait_for_timeout(1000)
    pg.keyboard.press("Digit2")
    # flat start: move away from the original spike so the comparison is fair, give lots of ammo, spawn enemies
    pg.evaluate("""(N)=>{const d=window.__DH; d.P.hp=d.P.max=100000; d.inv.ammo=99999; (d.spawn.length===2?d.spawn('normal',N):d.spawn(N))}""", N)
    # aim right, hold fire, strafe
    pg.mouse.move(box["x"]+box["width"]*0.8, box["y"]+box["height"]*0.55)
    pg.mouse.down()
    pg.wait_for_timeout(500)
    pg.evaluate("window.__DH_ms=[]")
    pg.evaluate("""()=>{window.__fr=[];let l=performance.now();const f=t=>{window.__fr.push(t-l);l=t;window.__run&&requestAnimationFrame(f)};window.__run=true;requestAnimationFrame(f)}""")
    for i in range(8):
        pg.keyboard.down("KeyD")
        for _ in range(4): pg.mouse.up(); pg.mouse.down(); pg.wait_for_timeout(130)
        pg.keyboard.up("KeyD")
        pg.keyboard.press("Space"); pg.keyboard.down("KeyA")
        for _ in range(4): pg.mouse.up(); pg.mouse.down(); pg.wait_for_timeout(130)
        pg.keyboard.up("KeyA")
    pg.evaluate("window.__run=false")
    r = pg.evaluate("""()=>{const a=window.__fr.slice(5),m=window.__DH_ms.slice(5);const s=x=>x.slice().sort((p,q)=>p-q);
      const av=x=>x.reduce((p,q)=>p+q,0)/x.length;const pc=(x,q)=>s(x)[Math.floor(x.length*q)];
      return {frames:a.length,intervalAvg:av(a),intervalP95:pc(a,.95),fps:1000/av(a),jsAvg:av(m),jsP95:pc(m,.95),jsMax:Math.max(...m),
      Z:window.__DH.Z.length,B:window.__DH.B.length,PT:window.__DH.PT.length}}""")
    pg.mouse.up()
    print(tag, json.dumps({k:(round(v,2) if isinstance(v,float) else v) for k,v in r.items()}))
    print("ERRORS", errs[:5])
    pg.screenshot(path=f"/home/claude/shots/{tag}_perf.png")
    b.close()
