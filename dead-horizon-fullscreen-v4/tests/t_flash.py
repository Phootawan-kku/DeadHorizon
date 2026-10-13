import sys, json; sys.path.insert(0,'/home/claude')
from h import *
from PIL import Image, ImageDraw
import io
W=["pistol","smg","shotgun","rifle","sniper","launcher"]
with sync_playwright() as p:
    b,ctx,pg = launch(p, 1280, 720)
    box = start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999;__DH.S.left=0;__DH.Z.length=0;__DH.S.fight=false")
    for w in W: pg.evaluate(f"__DH.own('{w}')")
    pg.evaluate("for(const k of Object.keys(__DH.inv))if(typeof __DH.inv[k]==='number')__DH.inv[k]=999")
    tiles=[]
    for lab,(ax,ay) in [("R-up",(.80,.42)),("L-down",(.18,.62))]:
        for w in W:
            pg.evaluate(f"__DH.equip('{w}');__DH.P.cd=0;__DH.P.rl=0;__DH.P.mag['{w}']=10")
            pg.mouse.move(box["x"]+box["width"]*ax, box["y"]+box["height"]*ay); pg.wait_for_timeout(150)
            # fire once and freeze the world on a frame where the flash is active
            pg.evaluate("__DH.P.cd=0")
            pg.mouse.down()
            for _ in range(30):
                if pg.evaluate("__DH.P.flash>0.035"):
                    pg.evaluate("__DH.GameState.isPaused=true"); break
                pg.wait_for_timeout(2)
            pg.mouse.up()
            pg.wait_for_timeout(40)
            sx=pg.evaluate("Math.round(__DH.P.x-__DH.cx)"); y=pg.evaluate("Math.round(__DH.P.y)")
            sc=box["width"]/960
            png=pg.screenshot(clip={"x":box["x"]+(sx-70)*sc,"y":box["y"]+(y-95)*sc,"width":140*sc,"height":120*sc})
            im=Image.open(io.BytesIO(png)).convert("RGB").resize((280,240),Image.NEAREST)
            d=ImageDraw.Draw(im); d.text((4,2),f"{w} {lab} fl={pg.evaluate('__DH.P.flash>0')}",fill=(255,255,255))
            tiles.append(im)
            pg.evaluate("__DH.GameState.isPaused=false"); pg.wait_for_timeout(250)
    sheet=Image.new("RGB",(280*6,240*2))
    for i,t in enumerate(tiles): sheet.paste(t,((i%6)*280,(i//6)*240))
    sheet.save("/home/claude/shots/gun_flash.png"); print("saved", pg.logs[:3])
    b.close()
