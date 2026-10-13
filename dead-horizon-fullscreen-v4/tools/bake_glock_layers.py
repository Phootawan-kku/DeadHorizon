#!/usr/bin/env python3
"""Builds the Glock hand sprites used by the pistol animation rig from the original 48x48 export.
Outputs (assets/weapons): pistol.png (assembled, idle), pistol_body.png, pistol_mag.png, pistol_slide.png on a CW x CH canvas.
Change S to resize the in-hand pistol (also update weaponDims('pistol') in game.html to CW x CH and the slide/mag travel in drawPistolRig).
Usage: python3 tools/bake_glock_layers.py path/to/create_a_glock_19_gun.png"""
import sys
from PIL import Image
import numpy as np
SRC=sys.argv[1]
S=0.51; CW,CH=48,24; X0,Y0=5,6
SLIDE_NATIVE_LAST=13; MAG_NATIVE_FIRST=31; MAG_NATIVE_MAXX=18
OUT='assets/weapons/'
src=Image.open(SRC).convert('RGBA'); bb=src.getbbox(); crop=src.crop(bb)
w=round(crop.width*S); h=round(crop.height*S)
a=np.array(crop).astype(float); al=a[:,:,3:4]/255.
chs=[np.array(Image.fromarray((a[:,:,i]*al[:,:,0]).astype(np.float32),mode='F').resize((w,h),Image.BOX)) for i in range(3)]
A=np.array(Image.fromarray(al[:,:,0].astype(np.float32),mode='F').resize((w,h),Image.BOX))
o=np.zeros((h,w,4),np.uint8); m=A>=.5
for i in range(3): o[:,:,i]=np.where(m,np.clip(chs[i]/np.maximum(A,1e-6),0,255),0)
o[:,:,3]=np.where(m,255,0)
small=Image.fromarray(o); cv=Image.new('RGBA',(CW,CH),(0,0,0,0)); cv.paste(small,(X0,Y0),small)
slide_y=Y0+int((SLIDE_NATIVE_LAST+1-bb[1])*S)-1          # last canvas row of the slide
mag_y=Y0+int(round((MAG_NATIVE_FIRST-bb[1])*S))           # first canvas row of the magazine
mag_x=X0+int((MAG_NATIVE_MAXX-bb[0])*S)
print('canvas',cv.size,'gun',small.size,'slide rows <=',slide_y,'mag rows >=',mag_y,'mag x <=',mag_x)
slide=Image.new('RGBA',(CW,CH),(0,0,0,0)); body=slide.copy(); mag=slide.copy(); p=cv.load(); sp,bp,mp=slide.load(),body.load(),mag.load()
for y in range(CH):
    for x in range(CW):
        c=p[x,y]
        if c[3]==0: continue
        if y<=slide_y: sp[x,y]=c
        elif y>=mag_y and x<=mag_x: mp[x,y]=c
        else: bp[x,y]=c
front=max(x for y in range(Y0,slide_y+1) for x in range(CW) if sp[x,y][3])
rows=[y for y in range(CH) if any(sp[x,y][3] for x in range(CW))]; top,bot=min(rows),max(rows)
BLK=(1,2,5,255); BAR_HI=(95,98,108,255); BAR=(62,64,73,255); BAR_LO=(35,37,45,255)
inner=list(range(top+1,bot))                                # barrel exposed under the slide
for x in range(front-2,front+2):
    bp[x,top]=BLK; bp[x,bot]=BLK
    for i,y in enumerate(inner): bp[x,y]=BAR_HI if i==0 else (BAR_LO if i==len(inner)-1 else BAR)
xs=[x for x in range(CW) if mp[x,mag_y][3]]
for x in range(min(xs),max(xs)+1): bp[x,mag_y-1]=(22,22,29,255); bp[x,mag_y]=BLK   # empty magazine well
cv.save(OUT+'pistol.png'); slide.save(OUT+'pistol_slide.png'); body.save(OUT+'pistol_body.png'); mag.save(OUT+'pistol_mag.png')
print('slide front x',front,'slide rows',top,bot)
