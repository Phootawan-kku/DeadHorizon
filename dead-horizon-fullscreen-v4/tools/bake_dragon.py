#!/usr/bin/env python3
"""Bake the Dragon boss sprite sheets from assets/enemies/_dragon_source.png.

Source layout (right-facing, transparent background):
  row 1 : 6 walk-cycle frames
  row 2 : 5 attack frames  (ready, mouth opens, FIRE BREATH, close, rest)

The source frames are not on a grid and the second row is drawn ~4% larger, so this tool
  1. splits every frame by connected component (stray sparks/flame bits join the nearest frame),
  2. rescales row 2 to the size of row 1,
  3. aligns all frames on a shared ground line and a shared body centre,
  4. packs them into fixed-size cells:
       dragon_walk.png    6 walk frames + 1 idle frame   (narrow cells)
       dragon_attack.png  5 attack frames                (wide cells, room for the flame)
  5. writes hires/boss.png (static sprite used for the corpse / bestiary) and dragon_sheet.json.
Everything is stored facing RIGHT with the body centred in the cell; the game mirrors it for facing left.

Run from the game folder:  python3 tools/bake_dragon.py
"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets/enemies/_dragon_source.png')
OUT = os.path.join(ROOT, 'assets/enemies')
K = 0.8            # global downscale of the (large) source art
ROW2_FIX = None    # measured below: row-2 frames are drawn slightly bigger than row-1 frames
MARGIN = 6         # transparent px kept under the feet / around the art
ALPHA_CUT = 10     # drop near-invisible fringe pixels

im = np.array(Image.open(SRC).convert('RGBA'))
solid = im[..., 3] > ALPHA_CUT
lab, n = ndi.label(solid, structure=np.ones((3, 3)))
sizes = ndi.sum(solid, lab, range(1, n + 1))
objs = ndi.find_objects(lab)
big = [i + 1 for i in range(n) if sizes[i] > 3000]
top = sorted([b for b in big if objs[b - 1][0].start < 400], key=lambda b: objs[b - 1][1].start)
bot = sorted([b for b in big if objs[b - 1][0].start >= 400], key=lambda b: objs[b - 1][1].start)
assert len(top) == 6 and len(bot) == 5, (len(top), len(bot))
order = top + bot

dist, (iy, ix) = ndi.distance_transform_edt(~np.isin(lab, big), return_indices=True)
owner = lab[iy, ix]

frames = []
for k, b in enumerate(order):
    sel = (owner == b) & solid & (dist < 60)
    rgba = np.zeros_like(im); rgba[sel] = im[sel]
    # "body" = the dragon without the flame / sparks (used for alignment)
    body = sel & (lab == b)
    if k == 8:                                   # fire frame: flame is attached to the head, cut it off at the snout
        xs = np.where(body)[1]
        snout = int(np.percentile(xs, 100) - 175)  # flame starts ~175px before the right-most pixel
        body &= (np.arange(im.shape[1])[None, :] <= snout)
    frames.append((rgba, sel, body))

def bbox(mask):
    ys, xs = np.where(mask); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

# row-2 size correction: compare body heights of row-1 vs row-2 frames
h_top = np.mean([bbox(frames[i][2])[3] - bbox(frames[i][2])[1] for i in range(6)])
h_bot = np.mean([bbox(frames[i][2])[3] - bbox(frames[i][2])[1] for i in (6, 7, 9, 10)])
ROW2_FIX = h_top / h_bot
print(f'row heights top={h_top:.1f} bottom={h_bot:.1f} -> row-2 scale {ROW2_FIX:.4f}')

prep = []   # (PIL image with the anchor info)
for k, (rgba, sel, body) in enumerate(frames):
    s = K * (ROW2_FIX if k >= 6 else 1.0)
    x0, y0, x1, y1 = bbox(sel)
    crop = Image.fromarray(rgba).crop((x0, y0, x1, y1))
    # body-only anchors in crop coordinates
    bys, bxs = np.where(body)
    cx = bxs.mean() - x0                     # centre of mass of the body
    foot = bys.max() + 1 - y0                # lowest foot pixel
    nw, nh = max(1, round(crop.width * s)), max(1, round(crop.height * s))
    crop = crop.resize((nw, nh), Image.LANCZOS)
    prep.append(dict(img=crop, cx=cx * s, foot=foot * s, w=nw, h=nh))

# cell geometry --------------------------------------------------------------------
above = max(p['foot'] for p in prep)                          # tallest art above the ground line
GROUND = math.ceil(above) + MARGIN                            # ground line y inside a cell
CH = GROUND + MARGIN
left_ext = max(p['cx'] for p in prep)
walk_right = max(p['w'] - p['cx'] for p in prep[:6] + [prep[6]])
atk_right = max(p['w'] - p['cx'] for p in prep[6:])
half_walk = math.ceil(max(left_ext, walk_right)) + MARGIN
half_atk = math.ceil(max(left_ext, atk_right)) + MARGIN
CW_WALK, CW_ATK = half_walk * 2, half_atk * 2
BODY_W = round(np.mean([bbox(frames[i][2])[2] - bbox(frames[i][2])[0] for i in range(6)]) * K)
print('ground', GROUND, 'cell h', CH, 'walk cell', CW_WALK, 'attack cell', CW_ATK, 'body width', BODY_W)

def paste(sheet, p, col, cw):
    x = round(col * cw + cw / 2 - p['cx'])
    y = round(GROUND - p['foot'])
    sheet.alpha_composite(p['img'], (x, y))

walk = Image.new('RGBA', (CW_WALK * 7, CH), (0, 0, 0, 0))
for i in range(6): paste(walk, prep[i], i, CW_WALK)
paste(walk, prep[6], 6, CW_WALK)                              # col 6 = idle (the 'ready' pose, so attack starts seamlessly)
atk = Image.new('RGBA', (CW_ATK * 5, CH), (0, 0, 0, 0))
for i in range(5): paste(atk, prep[6 + i], i, CW_ATK)
walk.save(os.path.join(OUT, 'dragon_walk.png'), optimize=True)
atk.save(os.path.join(OUT, 'dragon_attack.png'), optimize=True)

# flame reach: right-most opaque pixel of the fire frame, measured from the body centre
fire_img = np.array(atk.crop((CW_ATK * 2, 0, CW_ATK * 3, CH)))[..., 3] > 0
fire_right = np.where(fire_img.any(axis=0))[0].max() - CW_ATK / 2
print('flame reach from body centre (sheet px):', round(fire_right, 1))

# static sprite (corpse / bestiary): idle frame, tight crop, stored 2x of the in-game size under hires/ (smoothed down)
idle = walk.crop((CW_WALK * 6, 0, CW_WALK * 7, CH))
ib = idle.getbbox(); idle = idle.crop(ib)
GAME_W = 160
GAME_H = round(GAME_W * idle.height / idle.width)
idle.resize((GAME_W * 2, GAME_H * 2), Image.LANCZOS).save(os.path.join(OUT, 'hires/boss.png'), optimize=True)
print('boss.png (hires) ->', GAME_W * 2, GAME_H * 2, '  in-game size', GAME_W, GAME_H)

meta = {
    'note': 'Dragon boss. All frames face RIGHT with the body centred in the cell; the game mirrors for facing left. Generated by tools/bake_dragon.py',
    'groundY': GROUND, 'frameH': CH, 'bodyWidth': BODY_W, 'flameReach': round(float(fire_right), 1),
    'walk': {'file': 'dragon_walk.png', 'frameW': CW_WALK, 'frames': 6, 'idleFrame': 6},
    'attack': {'file': 'dragon_attack.png', 'frameW': CW_ATK, 'frames': 5,
               'sequence': ['ready', 'mouth open', 'fire breath', 'closing', 'rest'], 'fireFrame': 2},
    'ingame': {'width': GAME_W, 'height': GAME_H},
}
json.dump(meta, open(os.path.join(OUT, 'dragon_sheet.json'), 'w'), indent=1)
print(json.dumps(meta))
