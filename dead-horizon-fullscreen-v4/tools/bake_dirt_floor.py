#!/usr/bin/env python3
"""Bakes assets/environment/tiles/dirt_floor.png: one continuous strip of dirt built from the six dirt blocks.
Block outlines are removed; neighbouring cells (left/right and rows above/below) are cross-faded with an ordered
dither so the ground reads as one continuous material instead of a grid of separate blocks.
Run from the project root:  python3 tools/bake_dirt_floor.py"""
from PIL import Image
import random, math
ROOT='assets/environment/tiles/'
NAMES=[f'dirt_block_{i}.png' for i in range(1,7)]   # 5 = grass top
GRASS=4
C=34            # cell size after the block outline is removed
BAND=8          # width of the dither cross-fade between cells
PAD=4           # transparent rows above the surface line (grass tufts)
ROWS=7          # rows of dirt under the surface (row 0 = surface)
WORLD=4000+80
NCOL=math.ceil(WORLD/C)
BAYER=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def bay(x,y): return (BAYER[y%4][x%4]+.5)/16
def ext(im):
    p=im.load(); w,h=im.size
    L=min(x for x in range(w) if p[x,h//2][3]); R=max(x for x in range(w) if p[x,h//2][3])
    T=min(y for y in range(h) if p[w//2,y][3]); B=max(y for y in range(h) if p[w//2,y][3])
    return L,R,T,B
class Blk: pass
blocks=[]
for n in NAMES:
    im=Image.open(ROOT+n).convert('RGBA'); L,R,T,B=ext(im); b=Blk(); b.im=im; b.L,b.R,b.T,b.B=L,R,T,B
    iw=(R-2)-(L+2)+1; ih=(B-2)-(T+2)+1
    ox=L+2+(iw-C)//2                    # centred C-wide window inside the outline
    oy=T+2+(ih-C)//2
    b.deep=im.crop((ox,oy,ox+C,oy+C))   # interior tile (no outline)
    b.top=im.crop((ox,T,ox+C,T+C))      # surface tile: keeps the top outline row + highlight lip
    b.tuft=im.crop((ox,T-PAD,ox+C,T))   # grass blades above the surface line
    blocks.append(b)
    print(n,'outline',L,R,T,B)
rnd=random.Random(2026)
grid=[[0]*NCOL for _ in range(ROWS)]
prev=None
for c in range(NCOL):
    g=rnd.random()<(.62 if prev==GRASS else .38)
    prev=GRASS if g else rnd.choice([0,1,2,3,5])
    grid[0][c]=prev
for r in range(1,ROWS):
    for c in range(NCOL):
        opts=[0,1,2,3,3,5,2,1]
        for _ in range(8):
            v=rnd.choice(opts)
            if v!=grid[r][c-1 if c else 0] or c==0 or len(set(opts))==1: break
        grid[r][c]=v
def mirror(i,n): 
    if i<0: i=-i-1
    if i>=n: i=2*n-1-i
    return min(max(i,0),n-1)
# 1) rows of cells, cross-faded horizontally
rows=[]
for r in range(ROWS):
    W=NCOL*C; img=Image.new('RGBA',(W,C)); op=img.load()
    tiles=[(blocks[grid[r][c]].top if r==0 else blocks[grid[r][c]].deep).load() for c in range(NCOL)]
    for y in range(C):
        for x in range(W):
            k=x//C; xb_l=k*C; xb_r=(k+1)*C
            # nearest boundary
            if x-xb_l < xb_r-x: xb=xb_l; kl,kr=k-1,k
            else: xb=xb_r; kl,kr=k,k+1
            u=x+.5-xb
            if abs(u)<BAND/2 and 0<=kl and kr<NCOL:
                wr=.5+u/BAND
                kk=kr if bay(x,y)<wr else kl
            else: kk=k
            lx=mirror(x-kk*C,C)
            op[x,y]=tiles[kk][lx,y]
    rows.append(img)
# 2) stack rows, cross-fade vertically (rows are mirror-extended)
H=ROWS*C; W=NCOL*C
tex=Image.new('RGBA',(W,PAD+H)); tp=tex.load()
rp=[r.load() for r in rows]
for y in range(H):
    k=y//C; yb_t=k*C; yb_b=(k+1)*C
    if y-yb_t < yb_b-y: yb=yb_t; kt,kb=k-1,k
    else: yb=yb_b; kt,kb=k,k+1
    u=y+.5-yb
    for x in range(W):
        kk=k
        if abs(u)<BAND/2 and 0<=kt and kb<ROWS:
            wb=.5+u/BAND
            kk=kb if bay(x,y)<wb else kt
        ly=mirror(y-kk*C,C)
        tp[x,PAD+y]=rp[kk][x,ly]
# 3) grass tufts above the surface line
for c in range(NCOL):
    if grid[0][c]==GRASS:
        t=blocks[GRASS].tuft; tt=t.load()
        for y in range(PAD):
            for x in range(C):
                if tt[x,y][3]: tp[c*C+x,y]=tt[x,y]
tex.save(ROOT+'dirt_floor.png')
print('baked',tex.size,'cells',NCOL,'x',ROWS)
