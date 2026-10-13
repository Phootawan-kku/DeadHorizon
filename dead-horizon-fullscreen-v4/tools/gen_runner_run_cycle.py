from PIL import Image, ImageDraw, ImageOps
import math, json
N=8; S=4
OUT=(0,0,2,255); PANT=(47,44,63,255); PANT_HI=(64,63,80,255)
SHIN=(54,66,69,255); SHIN_HI=(92,112,84,255); SKIN=(72,96,70,255); SKIN_HI=(141,158,93,255); BLOOD=(80,41,50,255); BLOOD_HI=(142,67,54,255)
def dark(c,f=.72): return (int(c[0]*f),int(c[1]*f),int(c[2]*f),255)
def mask_from(drawfn):
    big=Image.new('L',(48*S,48*S),0); d=ImageDraw.Draw(big); drawfn(d)
    sm=big.resize((48,48),Image.BOX)
    return sm.point(lambda v:255 if v>=120 else 0)
def capsule(d,p0,p1,w0,w1):
    n=12
    for i in range(n+1):
        t=i/n; x=p0[0]+(p1[0]-p0[0])*t; y=p0[1]+(p1[1]-p0[1])*t; r=(w0+(w1-w0)*t)/2*S
        d.ellipse((x*S-r,y*S-r,x*S+r,y*S+r),fill=255)
def leg_layers(hip,a,far):
    # a = phase 0..2pi for this leg; thigh swing + knee flex
    th=math.radians(10+46*math.sin(a))
    flex=math.radians(14+78*max(0,math.cos(a))**1.3)
    L1,L2=5.2,5.0
    K=(hip[0]+L1*math.sin(th),hip[1]+L1*math.cos(th))
    sa=th-flex
    A=(K[0]+L2*math.sin(sa),K[1]+L2*math.cos(sa))
    # foot: flat when planted (cos<0), toe-down while swinging
    fa=math.radians(8+30*max(0,math.cos(a)))
    F=(A[0]+3.6*math.cos(fa),A[1]+3.6*math.sin(fa))
    thigh=mask_from(lambda d:capsule(d,hip,K,4.2,3.4))
    shin=mask_from(lambda d:capsule(d,K,A,3.2,2.6))
    foot=mask_from(lambda d:capsule(d,(A[0]-.6,A[1]+.3),F,2.8,2.2))
    return thigh,shin,foot,(K,A)
def paint(canvas,hip,a,far):
    thigh,shin,foot,_=leg_layers(hip,a,far)
    f=(lambda c:dark(c)) if far else (lambda c:c)
    allm=Image.new('L',(48,48),0)
    for m in (thigh,shin,foot): allm=Image.composite(m,allm,m)
    ap=allm.load(); cp=canvas.load()
    # outline ring
    for y in range(48):
        for x in range(48):
            if ap[x,y]==0:
                if any(0<=x+dx<48 and 0<=y+dy<48 and ap[x+dx,y+dy] for dx,dy in((1,0),(-1,0),(0,1),(0,-1))): cp[x,y]=OUT
    def fill(m,base,hi,extra=None):
        mp=m.load()
        for y in range(48):
            for x in range(48):
                if mp[x,y]:
                    c=base
                    if y>0 and not mp[x,y-1]: c=hi
                    elif x>0 and not mp[x-1,y] and (x+y)%2==0: c=hi
                    cp[x,y]=f(c)
    fill(shin,SHIN,SHIN_HI); fill(thigh,PANT,PANT_HI)
    # torn pant / blood speck on thigh
    tp=thigh.load()
    pts=[(x,y) for y in range(48) for x in range(48) if tp[x,y]]
    if pts:
        mx=sorted(pts)[len(pts)//2]; cp[mx]=f(BLOOD_HI); 
    fill(foot,SKIN,SKIN_HI)
def make_frames(body):
    fr=[]
    for i in range(N):
        p=2*math.pi*i/N
        c=Image.new('RGBA',(48,48),(0,0,0,0))
        paint(c,(19,34),p+math.pi,True)    # far leg
        paint(c,(24,34),p,False)           # near leg
        c.alpha_composite(body); fr.append(c)
    return fr
def bodyof(path,flip=False):
    im=Image.open(path).convert('RGBA')
    if flip: im=ImageOps.mirror(im)
    b=im.copy(); bp=b.load()
    for y in range(36,48):
        for x in range(48): bp[x,y]=(0,0,0,0)
    return b
be=bodyof('rz_running/running/rotations/east.png')
bw=bodyof('rz_running/running/rotations/west.png',True)
fe=make_frames(be); fw=[ImageOps.mirror(f) for f in make_frames(bw)]
base=Image.open('rz_base_sheet.png').convert('RGBA')
sheet=Image.new('RGBA',(48*(2+N),96),(0,0,0,0)); sheet.paste(base.crop((0,0,96,96)),(0,0))
for i in range(N):
    sheet.paste(fe[i],(48*(2+i),0)); sheet.paste(fw[i],(48*(2+i),48))
sheet.save('dead-horizon-fullscreen-v4/assets/enemies/runner_sheet.png')
strip=Image.new('RGBA',(48*4*4,48*4*2),(70,90,70,255))
for i,f in enumerate(fe): strip.alpha_composite(f.resize((192,192),Image.NEAREST),((i%4)*192,(i//4)*192))
strip.save('run_strip3.png')
