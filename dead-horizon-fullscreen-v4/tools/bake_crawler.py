#!/usr/bin/env python3
"""Bake the Crawler sprite sheet from assets/enemies/_crawler_source/pose_1..8.png.

The sources are 8 separate poses (1024x572, facing right) of a torso-only crawler, each with a checkerboard baked into the pixels
(not real transparency) and, for some poses, a baked ground shadow. This tool
  1. removes the checkerboard (neutral-grey regions flood-filled from the border, then the grey fringe along the silhouette),
  2. removes the baked ground shadows (the game draws its own),
  3. rescales every pose so the head is the same size (the poses were drawn at slightly different zooms),
  4. aligns them on a shared ground line and body centre and packs them into equal cells.
Outputs (assets/enemies/): crawler_sheet.png (8 cells), crawler_sheet.json, hires/crawler.png (static sprite for corpse + bestiary).
Frames face RIGHT, body centred in the cell; the game mirrors for facing left.
Run from the game folder:  python3 tools/bake_crawler.py
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets/enemies/_crawler_source')
OUT = os.path.join(ROOT, 'assets/enemies')
K = 0.25                 # sheet scale relative to the 1024x572 sources
FIX = [.85, .94, 1.0, 1.07, 1.12, .94, 1.05, 1.0]   # per-pose zoom correction (so the head has the same size in every pose)
GAME_W, GAME_H = 90, 40  # on-screen size used by the game (VIS.crawler); the static sprite has this aspect ratio
MARGIN = 6

def clean(path):
    a = np.array(Image.open(path).convert('RGB')).astype(int)
    g = a.mean(2); sat = a.max(2) - a.min(2)
    bglike = (sat < 12) & (g > 95) & (g < 200)
    lab, n = ndi.label(bglike); sizes = ndi.sum(bglike, lab, range(1, n + 1))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.zeros(n + 1, bool)
    for k in range(1, n + 1):
        if k in border or sizes[k - 1] > 40: bg[k] = True
    fg = ~bg[lab]
    fg = ndi.binary_opening(fg, structure=np.ones((2, 2)))
    l2, n2 = ndi.label(fg, structure=np.ones((3, 3))); s2 = ndi.sum(fg, l2, range(1, n2 + 1))
    fg = np.isin(l2, [k + 1 for k in range(n2) if s2[k] >= 40])
    holes = ndi.binary_fill_holes(fg) & ~fg; hl, hn = ndi.label(holes); hs = ndi.sum(holes, hl, range(1, hn + 1))
    fg |= np.isin(hl, [k + 1 for k in range(hn) if hs[k] <= 6])
    for _ in range(2):
        edge = fg & ~ndi.binary_erosion(fg); fg &= ~(edge & (sat < 14) & (g > 95) & (g < 200))
    # ---- baked ground shadow: flat neutral-dark blobs right at the ground (outlines are thinner/darker, shading is tinted)
    cand = fg & (sat < 10) & (g < 118)
    ysb = np.where(fg)[0].max(); band = np.zeros_like(fg); band[ysb - 42:] = True
    dark = fg & band & (sat < 7) & (g >= 14) & (g < 52)
    keep = np.zeros_like(fg)
    core = ndi.binary_opening(dark, structure=np.ones((5, 5)))
    lab, n = ndi.label(core)
    for k in range(1, n + 1):
        if (lab == k).sum() > 500: keep |= lab == k
    core2 = ndi.binary_opening(cand, structure=np.ones((7, 7))); l3, n3 = ndi.label(core2)   # faint checker-like shadows
    for k in range(1, n3 + 1):
        m = l3 == k; ys, xs = np.where(m)
        if (xs.max() - xs.min() + 1) > 3 * (ys.max() - ys.min() + 1) and m.sum() > 200: keep |= m
    sh = ndi.binary_dilation(keep, structure=np.ones((3, 3)), iterations=5) & (((sat < 10) & (g < 70)) | ndi.binary_dilation(keep)) & fg
    sh |= ndi.binary_dilation(sh, iterations=2) & fg & (sat < 12) & (g < 125)
    fg &= ~sh
    l4, n4 = ndi.label(fg, structure=np.ones((3, 3))); s4 = ndi.sum(fg, l4, range(1, n4 + 1))
    fg = np.isin(l4, [k + 1 for k in range(n4) if s4[k] >= 40])
    ys, xs = np.where(fg); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    rgba = np.dstack([a.astype(np.uint8), (fg * 255).astype(np.uint8)])[y0:y1, x0:x1]
    return dict(img=rgba, cx=xs.mean() - x0, w=x1 - x0, h=y1 - y0)

frames = [clean(os.path.join(SRC, f'pose_{i}.png')) for i in range(1, 9)]
for f, z in zip(frames, FIX):                      # apply the zoom correction
    s = K * z
    f['img'] = np.array(Image.fromarray(f['img']).resize((max(1, round(f['w'] * s)), max(1, round(f['h'] * s))), Image.LANCZOS))
    f['cx'] *= s; f['w'], f['h'] = f['img'].shape[1], f['img'].shape[0]

half = max(max(f['cx'], f['w'] - f['cx']) for f in frames) + MARGIN
CW = int(np.ceil(half * 2)); CH = max(f['h'] for f in frames) + MARGIN * 2
GROUND = CH - MARGIN
sheet = Image.new('RGBA', (CW * 8, CH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    sheet.alpha_composite(Image.fromarray(f['img']), (round(i * CW + CW / 2 - f['cx']), GROUND - f['h']))
sheet.save(os.path.join(OUT, 'crawler_sheet.png'), optimize=True)

# static sprite (corpse + bestiary): pose 2 (up, snarling) padded to the on-screen aspect ratio; stored under hires/ (smoothed when drawn)
f = frames[1]; ar = GAME_W / GAME_H
pw = max(f['w'], int(round(f['h'] * ar))); ph = int(round(pw / ar))
st = Image.new('RGBA', (pw, max(ph, f['h'])), (0, 0, 0, 0))
st.alpha_composite(Image.fromarray(f['img']), ((pw - f['w']) // 2, st.height - f['h']))
st = st.resize((st.width * 2, st.height * 2), Image.LANCZOS)   # 2x so the downscale in game stays smooth
st.save(os.path.join(OUT, 'hires/crawler.png'), optimize=True)

ref_w = int(np.median([f['w'] for f in frames]))
meta = dict(note='Crawler sheet generated by tools/bake_crawler.py. 8 frames facing RIGHT, body centred, feet on groundY.',
            frameW=CW, frameH=CH, groundY=GROUND, frames=8, refW=ref_w,
            order=['kneel high, far reach', 'up, snarling', 'flat, both hands forward', 'low, arm reaching', 'lean, claw', 'lunge up', 'low reach', 'low flat reach'],
            idleFrame=1, attackFrames=dict(windup=1, recover=4, strike=5), ingame=dict(width=GAME_W, height=GAME_H))
json.dump(meta, open(os.path.join(OUT, 'crawler_sheet.json'), 'w'), indent=1)
print(json.dumps(meta)); print('frame sizes', [(f['w'], f['h']) for f in frames])
