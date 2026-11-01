#!/usr/bin/env python3
"""Bake the Creepoo (replaces the old Exploder) sprites from assets/enemies/_creepoo_source.png.

The source is a turn-around sheet; the FRONT view (left figure, with the face) is used. It is cut into
head / torso / two legs and re-posed procedurally, then every pose is downscaled into fixed cells.

Outputs (assets/enemies/):
  creepoo_sheet.png   10 cells: 0-7 walk cycle, 8 idle, 9 white "fuse" flash (used while the fuse burns)
  creepoo_blast.png   8-frame pixel-art explosion (fireball, shock ring, smoke, green block debris)
  hires/exploder.png  static sprite (corpse fade + website bestiary)
  creepoo_sheet.json  geometry for the game code

Run from the game folder:  python3 tools/bake_creepoo.py
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets/enemies/_creepoo_source.png')
OUT = os.path.join(ROOT, 'assets/enemies')

# ---- geometry of the front figure in the source image ----
HEAD_Y1 = 373          # head occupies y < 373
BODY_X0, BODY_X1, BODY_Y0, BODY_Y1 = 126, 421, 366, 739
LEG_L = (70, 664, 224, 900)   # x0,y0,x1,y1
LEG_R = (316, 664, 476, 900)
FIG_X, FIG_TOP, FIG_BOT = 272.5, 75, 891     # centre x, top and (exclusive) bottom of the figure
FIG_H_OUT = 124                               # figure height in the sheet (game draws it at 62px -> 2x)
K = FIG_H_OUT / (FIG_BOT - FIG_TOP)
CELL_W, CELL_H, GROUND = 84, 140, 134
PAD = 300

src = Image.open(SRC).convert('RGBA')
W, H = src.size
canvas_size = (W + 2 * PAD, H + 2 * PAD)

def layer(box):
    x0, y0, x1, y1 = box
    out = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    out.paste(src.crop((x0, y0, x1, y1)), (x0 + PAD, y0 + PAD))
    return out

head = layer((100, 70, 450, HEAD_Y1))
body = layer((BODY_X0, BODY_Y0, BODY_X1, BODY_Y1))
legL = layer(LEG_L)
legR = layer(LEG_R)

def rot(im, ang, pivot, move=(0, 0)):
    """rotate counter-clockwise by ang degrees about pivot (source coords), then translate."""
    return im.rotate(ang, resample=Image.BICUBIC, center=(pivot[0] + PAD, pivot[1] + PAD), translate=move)

def pose(lift_l=0, lift_r=0, rot_l=0, rot_r=0, bob=0, sway=0, head_rot=0):
    torso = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    torso.alpha_composite(body)
    torso.alpha_composite(rot(head, head_rot, (FIG_X, HEAD_Y1)))
    torso = rot(torso, sway, (FIG_X, 736), (0, bob))
    out = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    out.alpha_composite(torso)
    out.alpha_composite(rot(legL, rot_l, (150, 664), (0, -lift_l)))
    out.alpha_composite(rot(legR, rot_r, (396, 664), (0, -lift_r)))
    return out

def to_cell(im):
    x0 = FIG_X - CELL_W / 2 / K
    y0 = FIG_BOT - GROUND / K
    box = (x0 + PAD, y0 + PAD, x0 + PAD + CELL_W / K, y0 + PAD + CELL_H / K)
    return im.resize((CELL_W, CELL_H), Image.LANCZOS, box=box)

frames = []
N = 8
for i in range(N):
    th = 2 * math.pi * i / N
    s = math.sin(th)
    lift = 26
    ll, lr = max(0, s) * lift, max(0, -s) * lift
    frames.append(pose(lift_l=ll, lift_r=lr,
                       rot_l=-3.2 * ll / lift, rot_r=3.2 * lr / lift,    # lifted foot kicks outward
                       bob=-abs(s) * 5, sway=2.6 * s, head_rot=-1.4 * s))
idle = pose()
flash = idle.copy()
fa = np.array(flash).astype(float)
solid = fa[..., 3] > 0
fa[..., :3][solid] = fa[..., :3][solid] * .22 + 255 * .78
flash = Image.fromarray(fa.astype(np.uint8))

cells = [to_cell(f) for f in frames] + [to_cell(idle), to_cell(flash)]
sheet = Image.new('RGBA', (CELL_W * len(cells), CELL_H), (0, 0, 0, 0))
for i, c in enumerate(cells): sheet.alpha_composite(c, (i * CELL_W, 0))
sheet.save(os.path.join(OUT, 'creepoo_sheet.png'), optimize=True)

# static sprite for corpse + bestiary: idle pose, tight crop, 3x the in-game size (smoothed down in game via hires/)
GAME_W, GAME_H = 30, 62
st = idle.crop((int(75 + PAD - 6), int(FIG_TOP + PAD - 6), int(471 + PAD + 6), int(FIG_BOT + PAD + 6)))
bb = st.getbbox(); st = st.crop(bb)
st.resize((GAME_W * 3, GAME_H * 3), Image.LANCZOS).save(os.path.join(OUT, 'hires/exploder.png'), optimize=True)

# ------------------------------------------------------------------ explosion sheet
V = 80; UP = 3; NF = 8
rng = np.random.RandomState(11)
def vnoise(n):
    return np.array(Image.fromarray((rng.rand(n, n) * 255).astype(np.uint8)).resize((V, V), Image.BICUBIC)) / 255.0
noise = .55 * vnoise(8) + .30 * vnoise(16) + .15 * vnoise(32) - .5
noise2 = .6 * vnoise(10) + .4 * vnoise(24) - .5
yy, xx = np.mgrid[0:V, 0:V]
cx_, cy_ = V / 2, V / 2 + 2
dist = np.hypot(xx - cx_, (yy - cy_) * 1.05)
GREENS = [(47, 208, 26), (70, 227, 44), (29, 158, 18), (139, 234, 95), (20, 100, 14)]
chunks = []
for k in range(15):
    a = rng.uniform(0, 2 * math.pi); v = rng.uniform(30, 78)
    chunks.append(dict(a=a, v=v, s=int(rng.choice([2, 3, 3, 4])), c=GREENS[k % len(GREENS)], up=rng.uniform(10, 40)))
PALETTE = [(.78, (255, 247, 205)), (.58, (255, 214, 74)), (.40, (255, 140, 30)), (.24, (214, 70, 24)), (.10, (96, 56, 38))]
frames_b = []
for f in range(NF):
    u = f / (NF - 1)
    img = np.zeros((V, V, 4), np.uint8)
    R = 8 + 30 * (1 - (1 - u) ** 2.4)
    heat_scale = 1.0 if u < .3 else max(0.0, 1 - (u - .3) / .78)
    d = dist / R + noise * .55 * (.35 + u)
    # smoke (appears as the fire cools, drifts upward)
    sm_d = np.hypot(xx - cx_ + noise2 * 6, (yy - cy_ + 14 * u) * 1.1) / (R * (.95 + .25 * u)) + noise2 * .45
    sm_alpha = max(0.0, min(1.0, (u - .12) * 3)) * max(0.0, 1 - max(0, u - .78) * 3.2)
    smoke = (sm_d < 1.0) & (sm_alpha > .05)
    tone = (noise2 + .5) > .55
    img[smoke & tone] = (74, 62, 60, int(210 * sm_alpha))
    img[smoke & ~tone] = (46, 40, 40, int(220 * sm_alpha))
    heat = (1 - d) * 1.35 * heat_scale
    fire = heat > .10
    for thr, col in reversed(PALETTE):
        img[heat > thr] = (*col, 255)
    # shock ring
    if u < .5:
        rr = R * 1.28 + 3
        ring = np.abs(dist - rr) < 1.3
        a_ = int(230 * (1 - u / .5))
        img[ring & (rr < V / 2 + 2)] = (255, 255, 235, a_)
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    for c in chunks:                     # block debris, ballistic
        px_ = cx_ + math.cos(c['a']) * c['v'] * u
        py_ = cy_ + math.sin(c['a']) * c['v'] * u * .8 - c['up'] * u + 70 * u * u
        s = c['s']
        if u < .08: continue
        dr.rectangle([px_, py_, px_ + s - 1, py_ + s - 1], fill=(*c['c'], 255))
        dr.rectangle([px_, py_ + s - 1, px_ + s - 1, py_ + s - 1], fill=(8, 40, 8, 255))
    frames_b.append(im.resize((V * UP, V * UP), Image.NEAREST))
blast = Image.new('RGBA', (V * UP * NF, V * UP), (0, 0, 0, 0))
for i, im in enumerate(frames_b): blast.alpha_composite(im, (i * V * UP, 0))
blast.save(os.path.join(OUT, 'creepoo_blast.png'), optimize=True)

meta = dict(note='Creepoo (ex-Exploder). Generated by tools/bake_creepoo.py',
            sheet=dict(file='creepoo_sheet.png', cellW=CELL_W, cellH=CELL_H, groundY=GROUND, figureW=round((470 - 75) * K), figureH=FIG_H_OUT,
                       walkFrames=8, idleCol=8, flashCol=9),
            blast=dict(file='creepoo_blast.png', frame=V * UP, frames=NF),
            ingame=dict(width=GAME_W, height=GAME_H))
json.dump(meta, open(os.path.join(OUT, 'creepoo_sheet.json'), 'w'), indent=1)
print(json.dumps(meta))
