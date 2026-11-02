#!/usr/bin/env python3
"""Bake the Venom (cobra, replaces the old Spitter) sprites from assets/enemies/_venom_source/{idle,walk,attack}.png.

Source art: idle = coiled cobra (faces left), walk = stretched snake (faces RIGHT, flipped here so everything faces left),
attack = rearing cobra spitting (faces left, spit blob baked into the art).
This tool cleans the art (stray grey patch in the coil hole, detached outline fragments), then animates it procedurally:
  venom_idle.png    8 frames   neck / hood sway
  venom_walk.png    8 frames   slither: a body wave travels from head to tail
  venom_attack.png  6 frames   ready, rear back, strike (mouth open), SPIT (jet + blob), recover, settle
  hires/spitter.png static sprite for the corpse + website bestiary
  venom_sheet.json  geometry for the game code
Everything faces LEFT with the body centred in its cell; the game mirrors it for facing right.
Run from the game folder:  python3 tools/bake_venom.py
"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets/enemies/_venom_source')
OUT = os.path.join(ROOT, 'assets/enemies')
K = 0.5                      # sheet scale relative to the 512x286 source art
Y0, CH_SRC = 10, 256         # cell vertical window in source px (leaves room above the head for rearing)
GROUND_SRC = 251             # y of the ground line in the source art (bottom of the coil)
PAD = 60

def load(name):
    return np.array(Image.open(os.path.join(SRC, name)).convert('RGBA')).astype(np.float64)

def remove_small(a, min_area):
    lab, n = ndi.label(a[..., 3] > 10, structure=np.ones((3, 3)))
    sizes = ndi.sum(a[..., 3] > 10, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool); keep[1:] = sizes >= min_area
    a[~keep[lab] & (a[..., 3] > 0)] = 0
    return a

def clear_grey(a, x0, y0, x1, y1):
    """neutral grey leftovers (old checkerboard) inside the box become transparent"""
    sub = a[y0:y1, x0:x1]
    mx, mn = sub[..., :3].max(2), sub[..., :3].min(2)
    sub[((mx - mn) < 18) & (mx >= 70) & (mx <= 215) & (sub[..., 3] > 0)] = 0
    return a

idle = clear_grey(load('idle.png'), 270, 186, 330, 214)
attack_full = clear_grey(load('attack.png'), 270, 186, 330, 214)
walk = remove_small(load('walk.png')[:, ::-1].copy(), 150)          # flip: head now on the left

# the attack art without the spit effect: "mouth open" pose used for strike / recover frames
atk_open = attack_full.copy()
atk_open[:132, :212] = 0                 # blob, smoke and jet
atk_open[78:91, 212:224] = 0             # end of the jet where it enters the mouth
atk_open[238:, :205] = 0                 # ground splatter
atk_open = remove_small(atk_open, 120)   # specks left over from the spit effect
atk_full = attack_full.copy()

def bbox(a):
    ys, xs = np.where(a[..., 3] > 10); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
ib = bbox(idle); wb = bbox(walk)
XC = (ib[0] + ib[2]) / 2                  # body centre of the coiled pose
WXC = (wb[0] + wb[2]) / 2
FIG_W = (ib[2] - ib[0]) * K; FIG_H = (ib[3] - ib[1]) * K
print('idle bbox', ib, 'walk bbox', wb)

def premult(a):
    p = a.copy(); p[..., :3] *= (p[..., 3:4] / 255.0); return p
def unpremult(p):
    a = p.copy(); al = np.maximum(a[..., 3:4], 1e-6); a[..., :3] = np.where(a[..., 3:4] > 0, a[..., :3] / (al / 255.0), 0)
    return np.clip(a, 0, 255)

def warp(a, dxf=None, dyf=None):
    """resample with per-pixel offsets (positive dx moves content right, positive dy moves it down); premultiplied bilinear"""
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    sx = xx - (dxf(yy, xx) if dxf else 0); sy = yy - (dyf(yy, xx) if dyf else 0)
    p = premult(a); out = np.zeros_like(p)
    for c in range(4): out[..., c] = ndi.map_coordinates(p[..., c], [sy, sx], order=1, mode='constant', cval=0)
    return unpremult(out)

def cell(a, xc, w_src, dy=0):
    """crop a fixed cell window from the source frame and scale it to the sheet resolution"""
    big = np.zeros((a.shape[0] + 2 * PAD, a.shape[1] + 2 * PAD, 4)); big[PAD:PAD + a.shape[0], PAD:PAD + a.shape[1]] = a
    box = (xc - w_src / 2 + PAD, Y0 - dy + PAD, xc + w_src / 2 + PAD, Y0 - dy + CH_SRC + PAD)
    return Image.fromarray(big.astype(np.uint8)).resize((round(w_src * K), round(CH_SRC * K)), Image.LANCZOS, box=box)

# ---- neck weight: 0 at the coil, 1 at the head
NECK_TOP, COIL_Y = 28, 172
def w_neck(y): return np.clip((COIL_Y - y) / (COIL_Y - NECK_TOP), 0, 1) ** 1.6

def sway_frame(a, sway, lift=0):
    return warp(a, dxf=lambda y, x: sway * w_neck(y), dyf=lambda y, x: -lift * w_neck(y))

# ---------------------------------------------------------------- idle sheet (8)
IW_SRC = 260
idle_frames = []
for i in range(8):
    th = 2 * math.pi * i / 8
    idle_frames.append(cell(sway_frame(idle, 6 * math.sin(th), 2.5 * (.5 + .5 * math.sin(2 * th + 1))), XC, IW_SRC))

# ---------------------------------------------------------------- walk sheet (8): travelling body wave, head steady
WW_SRC = 368
walk_frames = []
for i in range(8):
    th = 2 * math.pi * i / 8
    def dy(y, x, th=th):
        r = np.clip((x - (wb[0] + 60)) / ((wb[2]) - (wb[0] + 60)), 0, 1)      # 0 at the head, 1 at the tail tip
        amp = 3 + 17 * r
        return -amp * (.5 + .5 * np.sin(2 * math.pi * x / 150 - th))           # only lifts, never sinks below the ground
    f = warp(walk, dyf=dy)
    walk_frames.append(cell(f, WXC, WW_SRC, dy=GROUND_SRC - wb[3]))

# ---------------------------------------------------------------- attack sheet (6)
AW_SRC = 360
atk = [
    (idle, 0, 0),                    # 0 ready
    (idle, 24, 9),                   # 1 rear back (telegraph)
    (atk_open, -28, -2),             # 2 strike: lunge forward, mouth open
    (atk_full, -16, 0),              # 3 SPIT: jet + blob
    (atk_open, 3, 1),                # 4 recover, mouth still open
    (idle, -3, 0),                   # 5 settle
]
atk_frames = [cell(sway_frame(a, s, l), XC, AW_SRC) for a, s, l in atk]

def strip(frames):
    w, h = frames[0].size; s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(f, (i * w, 0))
    return s
strip(idle_frames).save(os.path.join(OUT, 'venom_idle.png'), optimize=True)
strip(walk_frames).save(os.path.join(OUT, 'venom_walk.png'), optimize=True)
strip(atk_frames).save(os.path.join(OUT, 'venom_attack.png'), optimize=True)

# static sprite (corpse + bestiary): neutral idle tight crop, 3x the in-game width, smoothed down via hires/
GAME_W = 64; GAME_H = round(GAME_W * (ib[3] - ib[1]) / (ib[2] - ib[0]))
st = Image.fromarray(idle.astype(np.uint8)).crop(ib)
st.resize((GAME_W * 3, GAME_H * 3), Image.LANCZOS).save(os.path.join(OUT, 'hires/spitter.png'), optimize=True)

mouth_dx = (XC - 215) * K       # mouth offset from body centre (sheet px, toward facing)
meta = dict(note='Venom (ex-Spitter). Generated by tools/bake_venom.py. All frames face LEFT, body centred in the cell.',
            cellH=round(CH_SRC * K), groundY=round((GROUND_SRC - Y0) * K), figW=round(FIG_W, 1), figH=round(FIG_H, 1),
            mouthFromCentre=round(mouth_dx, 1), mouthHeight=round((GROUND_SRC - 85) * K, 1),
            idle=dict(file='venom_idle.png', frameW=round(IW_SRC * K), frames=8),
            walk=dict(file='venom_walk.png', frameW=round(WW_SRC * K), frames=8),
            attack=dict(file='venom_attack.png', frameW=round(AW_SRC * K), frames=6,
                        sequence=['ready', 'rear back', 'strike (mouth open)', 'SPIT', 'recover', 'settle'], spitFrame=3),
            ingame=dict(width=GAME_W, height=GAME_H))
json.dump(meta, open(os.path.join(OUT, 'venom_sheet.json'), 'w'), indent=1)
print(json.dumps(meta))
