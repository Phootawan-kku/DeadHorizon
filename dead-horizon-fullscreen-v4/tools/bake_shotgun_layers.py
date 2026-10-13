#!/usr/bin/env python3
"""Builds the pump-shotgun hand sprites used by the animation rig from the original diagonal 48x48 export.
Rotates the gun horizontal (RotSprite-style), scales it to LEN px, then writes (assets/weapons):
  shotgun.png (assembled idle sprite, used for the muzzle position), shotgun_body.png, shotgun_pump.png, shotgun_icon.png (64x24 HUD icon)
The pump (forend) is drawn as its own piece so it can slide; the magazine tube under it is painted into the body layer.
Usage: python3 tools/bake_shotgun_layers.py path/to/create_a_pump_shotgun.png"""
import sys, math
from PIL import Image
import numpy as np
SRC=sys.argv[1]; OUT='assets/weapons/'
K=8; LEN=48; CW,CH=54,20; X0,Y0=3,4
PUMP_X,PUMP_W=30,11; PUMP_ROW0=6
BLK=(1,2,5,255)
src=Image.open(SRC).convert('RGBA')
a=np.array(src)[:,:,3]>0; ys,xs=np.nonzero(a); pts=np.stack([xs,ys],1).astype(float); c=pts.mean(0)
v=np.linalg.svd(pts-c,full_matrices=False)[2][0]
if v[0]<0: v=-v
ang=math.degrees(math.atan2(-v[1],v[0]))
big=src.resize((src.width*K,src.height*K),Image.NEAREST).rotate(-ang,resample=Image.NEAREST,expand=True); big=big.crop(big.getbbox())
arr=np.array(big).astype(float); al=arr[:,:,3:4]/255.
w=LEN; h=max(1,round(big.height*LEN/big.width))
chs=[np.array(Image.fromarray((arr[:,:,i]*al[:,:,0]).astype(np.float32),mode='F').resize((w,h),Image.BOX)) for i in range(3)]
A=np.array(Image.fromarray(al[:,:,0].astype(np.float32),mode='F').resize((w,h),Image.BOX))
o=np.zeros((h,w,4),np.uint8); m=A>=.5
for i in range(3): o[:,:,i]=np.where(m,np.clip(chs[i]/np.maximum(A,1e-6),0,255),0)
o[:,:,3]=np.where(m,255,0)
gun=Image.fromarray(o); print('gun',gun.size,'axis',round(ang,1))
body=Image.new('RGBA',(CW,CH),(0,0,0,0)); body.paste(gun,(X0,Y0),gun); bp=body.load()
# paint the magazine tube where the pump normally covers it, then clear the old forend pixels
r0=Y0+PUMP_ROW0
for x in range(X0+PUMP_X-1,X0+PUMP_X+PUMP_W+6):
    for yy in range(r0,r0+4): bp[x,yy]=(0,0,0,0)
    bp[x,r0]=(70,73,81,255); bp[x,r0+1]=(40,42,50,255); bp[x,r0+2]=BLK
# the pump (forend): outline + dark body + grip grooves
pump=Image.new('RGBA',(CW,CH),(0,0,0,0)); pp=pump.load()
px0=X0+PUMP_X
for x in range(px0,px0+PUMP_W):
    for yy in range(r0,r0+4):
        if yy in (r0,r0+3) or x in (px0,px0+PUMP_W-1): pp[x,yy]=BLK
        elif yy==r0+1: pp[x,yy]=(92,96,108,255) if (x-px0)%3 else (12,13,18,255)
        else: pp[x,yy]=(12,13,18,255) if (x-px0)%3==0 else (44,46,56,255)
cv=body.copy(); cv.alpha_composite(pump)
cv.save(OUT+'shotgun.png'); body.save(OUT+'shotgun_body.png'); pump.save(OUT+'shotgun_pump.png')
icon=Image.new('RGBA',(64,24),(0,0,0,0)); bb=cv.getbbox(); ic=cv.crop(bb); icon.paste(ic,((64-ic.width)//2,(24-ic.height)//2),ic); icon.save(OUT+'shotgun_icon.png')
print('canvas',cv.size,'content bbox',bb)
