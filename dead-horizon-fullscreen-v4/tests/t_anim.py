import sys, json; sys.path.insert(0,'/home/claude')
from h import *
from PIL import Image
import io
def crop(pg, box, n, tag, dt=45):
    out=[]
    for i in range(n):
        st = pg.evaluate("({a:__DH.PA.state,vy:Math.round(__DH.P.vy),y:Math.round(__DH.P.y),ph:+__DH.PA.phase.toFixed(2),sx:Math.round(__DH.P.x-__DH.cx)})")
        sc = box["width"]/960
        cx_ = box["x"]+st["sx"]*sc; cy_ = box["y"]+(st["y"]-62)*sc
        png = pg.screenshot(clip={"x":cx_-45*sc,"y":cy_-30*sc,"width":90*sc,"height":110*sc})
        out.append((st, Image.open(io.BytesIO(png)).convert("RGB")))
        pg.wait_for_timeout(dt)
    return out
def sheet(frames, path, cols=8, scale=2):
    w,h = frames[0][1].size; rows=(len(frames)+cols-1)//cols
    S = Image.new("RGB",(cols*w*scale//1, rows*h*scale),(20,20,20))
    for i,(st,im) in enumerate(frames):
        S.paste(im.resize((w*scale,h*scale),Image.NEAREST),((i%cols)*w*scale,(i//cols)*h*scale))
    S.save(path)
with sync_playwright() as p:
    b,ctx,pg = launch(p, 1280, 720)
    box = start(pg)
    pg.evaluate("__DH.P.hp=__DH.P.max=99999; __DH.S.left=0; __DH.Z.length=0")
    pg.mouse.move(box["x"]+box["width"]*.75, box["y"]+box["height"]*.62)
    res={}
    # idle
    idle = crop(pg, box, 8, 'idle', 120); res['idle']=[f[0]['a'] for f in idle]
    sheet(idle,'/home/claude/shots/anim_idle.png')
    # run
    pg.keyboard.down("KeyD"); pg.wait_for_timeout(250)
    run = crop(pg, box, 16, 'run', 20); res['run']=[f[0]['a'] for f in run]
    sheet(run,'/home/claude/shots/anim_run.png')
    # jump while running
    pg.keyboard.down("Space"); pg.wait_for_timeout(90); pg.keyboard.up("Space")
    jump = crop(pg, box, 24, 'jump', 12); res['jump']=[(f[0]['a']) for f in jump]
    sheet(jump,'/home/claude/shots/anim_jump.png')
    pg.keyboard.up("KeyD"); pg.wait_for_timeout(300)
    print(json.dumps(res))
    print("LOGS",pg.logs[:5])
    b.close()
