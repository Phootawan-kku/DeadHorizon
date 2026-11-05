#!/usr/bin/env python3
"""Bake the Crawler sprite sheet from assets/enemies/_crawler_source.png.

The source is ONE strip with 8 crawl poses (low, up, up, low, up, up, up, low) that overlap each other horizontally and have a
checkerboard baked into the pixels (it is not real transparency). This tool
  1. removes the checkerboard (neutral-grey regions, flood-filled so the figure's own pixels survive, plus the grey edge fringe),
  2. splits the 8 figures with a marker watershed (seeds = strongly eroded bodies, flooded through the silhouette),
  3. gives the few reaching hand tips that the watershed handed to a neighbour back to the right frame,
  4. aligns every frame on a shared ground line and body centre and packs them into equal cells.
Outputs (assets/enemies/): crawler_sheet.png (8 cells), crawler_sheet.json, hires/crawler.png (static sprite for the corpse + bestiary).
Frames face RIGHT, body centred in the cell; the game mirrors for facing left.
Run from the game folder:  python3 tools/bake_crawler.py
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'assets/enemies/_crawler_source.png')
OUT = os.path.join(ROOT, 'assets/enemies')
K = 0.6                  # sheet scale relative to the source strip
GAME_W, GAME_H = 72, 40  # on-screen size used by the game (VIS.crawler); the static sprite has this aspect ratio
MARGIN = 6

# ------------------------------------------------------------------ 1. remove the baked checkerboard
rgb = np.array(Image.open(SRC).convert('RGB')).astype(int)
g = rgb.mean(2); sat = rgb.max(2) - rgb.min(2)
bglike = (sat < 12) & (g > 92) & (g < 192)
lab, n = ndi.label(bglike)
sizes = ndi.sum(bglike, lab, range(1, n + 1))
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.zeros(n + 1, bool)
for i in range(1, n + 1):
    if i in border or sizes[i - 1] > 40: bg[i] = True
fg = ~bg[lab]
fg = ndi.binary_opening(fg, structure=np.ones((2, 2)))
l2, n2 = ndi.label(fg, structure=np.ones((3, 3))); s2 = ndi.sum(fg, l2, range(1, n2 + 1))
fg = np.isin(l2, [i + 1 for i in range(n2) if s2[i] >= 25])
holes = ndi.binary_fill_holes(fg) & ~fg
hl, hn = ndi.label(holes); hs = ndi.sum(holes, hl, range(1, hn + 1))
fg |= np.isin(hl, [i + 1 for i in range(hn) if hs[i] <= 6])
for _ in range(2):                                  # grey anti-aliasing fringe along the silhouette
    edge = fg & ~ndi.binary_erosion(fg)
    fg &= ~(edge & (sat < 14) & (g > 95) & (g < 190))

# ------------------------------------------------------------------ 2. split the 8 figures
er = ndi.binary_erosion(fg, structure=np.ones((3, 3)), iterations=8)
sl, sn = ndi.label(er); ss = ndi.sum(er, sl, range(1, sn + 1))
ids = sorted([i + 1 for i in range(sn) if ss[i] > 120], key=lambda i: ndi.center_of_mass(er, sl, i)[1])
assert len(ids) == 8, f'expected 8 figures, found {len(ids)}'
markers = np.zeros_like(sl)
for k, i in enumerate(ids): markers[sl == i] = k + 1
owner = watershed(-ndi.distance_transform_edt(fg), markers, mask=fg)      # 0 = background, 1..8 = frame

# ------------------------------------------------------------------ 3. hand tips that overlap the next figure
bright = rgb.mean(2); tan = (bright > 100) & (rgb[..., 0] > rgb[..., 2] + 20)       # skin-coloured pixels
def give(x0, x1, y0, y1, src, dst, only_tan=True):
    box = np.zeros_like(fg); box[y0:y1, x0:x1] = True
    sel = box & (owner == src) & (tan if only_tan else True)
    owner[sel] = dst
give(176, 217, 324, 356, 2, 1, only_tan=False)      # frame 1: reaching forearm lies under frame 2's shin (clear part first,
give(217, 232, 324, 356, 2, 1)                      #   then only skin-coloured pixels where it overlaps the shin)
give(536, 570, 316, 348, 5, 4, only_tan=False)      # frame 4: forearm/hand lies under frame 5's knee
give(570, 596, 318, 346, 5, 4)
give(622, 652, 328, 352, 6, 5)                      # frame 5: planted hand sits in frame 6's blood
give(803, 820, 318, 352, 8, 7, only_tan=False)      # frame 7: planted forearm sits in frame 8's blood

# ------------------------------------------------------------------ 4. align + pack
crops = []
for k in range(1, 9):
    m = owner == k
    # drop stray bits that are not part of the main figure
    l3, n3 = ndi.label(m, structure=np.ones((3, 3)))
    if n3 > 1:
        s3 = ndi.sum(m, l3, range(1, n3 + 1)); m = np.isin(l3, [i + 1 for i in range(n3) if s3[i] >= 40])
    ys, xs = np.where(m)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    rgba = np.dstack([rgb.astype(np.uint8), (m * 255).astype(np.uint8)])[y0:y1, x0:x1]
    crops.append(dict(img=rgba, cx=xs.mean() - x0, w=x1 - x0, h=y1 - y0))

half = max(max(c['cx'], c['w'] - c['cx']) for c in crops) + MARGIN
CW_SRC = int(np.ceil(half * 2)); CH_SRC = max(c['h'] for c in crops) + MARGIN * 2
CW, CH = round(CW_SRC * K), round(CH_SRC * K)
GROUND = CH - round(MARGIN * K)
sheet = Image.new('RGBA', (CW * 8, CH), (0, 0, 0, 0))
for i, c in enumerate(crops):
    im = Image.fromarray(c['img']).resize((max(1, round(c['w'] * K)), max(1, round(c['h'] * K))), Image.LANCZOS)
    x = round(i * CW + CW / 2 - c['cx'] * K); y = GROUND - im.height
    sheet.alpha_composite(im, (x, y))
sheet.save(os.path.join(OUT, 'crawler_sheet.png'), optimize=True)

# static sprite (corpse + bestiary): frame 3 (kneeling, reaching) padded to the on-screen aspect ratio, native resolution, under hires/ (smoothed)
c = crops[2]; ar = GAME_W / GAME_H
pw = max(c['w'], int(round(c['h'] * ar))); ph = int(round(pw / ar))
st = Image.new('RGBA', (pw, max(ph, c['h'])), (0, 0, 0, 0))
st.alpha_composite(Image.fromarray(c['img']), ((pw - c['w']) // 2, st.height - c['h']))
st.save(os.path.join(OUT, 'hires/crawler.png'), optimize=True)

ref_w = max(round(c['w'] * K) for c in crops)
meta = dict(note='Crawler sheet generated by tools/bake_crawler.py. 8 frames facing RIGHT, body centred, feet on groundY.',
            frameW=CW, frameH=CH, groundY=GROUND, frames=8, refW=ref_w,
            order=['low', 'up', 'up (hand forward)', 'low', 'up', 'up (reaching)', 'up (reaching far)', 'low (reaching)'],
            walkLoop=[0, 1, 2, 3, 4, 5, 6, 7], idleFrame=4, attackFrames=dict(windup=4, reach=5, strike=6, drop=7),
            ingame=dict(width=GAME_W, height=GAME_H))
json.dump(meta, open(os.path.join(OUT, 'crawler_sheet.json'), 'w'), indent=1)
print(json.dumps(meta))
