#!/usr/bin/env python3
"""Generic walk-cycle baker: turns a transparent 2x4 (8 frame) sprite sheet into assets/enemies/<name>_sheet.png
(8 cells of 128x172, facing RIGHT) plus the 96x144 portrait assets/enemies/<name>.png used by the website and as fallback.

  python3 tools/bake_walk_sheet.py <name> <source.png> <idleFrame 0-7>
  e.g.  python3 tools/bake_walk_sheet.py screamer tools/ui_sources/screamer_walk_source.png 7

All frames share ONE scale, the lowest boot/foot pixel of every frame lands on ground y=168, and each frame is centred
on its own alpha centroid. Frames are read in reading order (row 1 left->right, then row 2 left->right).
REMEMBER: a new sheet must also be listed in art.js (ART.get only returns preloaded images) and given a spec + dispatch in game.html.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

name, SRC, IDLE = sys.argv[1], sys.argv[2], int(sys.argv[3])
OUT, FW, FH, GROUND, FIG_H = 'assets/enemies/', 128, 172, 168, 150

src = Image.open(SRC).convert('RGBA')
a = np.array(src)
a[..., 3] = np.where(a[..., 3] < 20, 0, a[..., 3])          # drop faint haze around the sprites
src = Image.fromarray(a, 'RGBA')
al = a[..., 3]
lab, n = ndi.label(ndi.binary_dilation(al > 40, iterations=6))
boxes = [(o[1].start, o[0].start, o[1].stop, o[0].stop) for o in ndi.find_objects(lab)]
assert len(boxes) == 8, 'expected 8 sprites, found %d' % len(boxes)
boxes.sort(key=lambda b: (0 if b[1] < 300 else 1, b[0]))
k = FIG_H / float(np.median([b[3] - b[1] for b in boxes]))

sheet = Image.new('RGBA', (FW * 8, FH), (0, 0, 0, 0))
for i, (x0, y0, x1, y1) in enumerate(boxes):
    f = src.crop((x0, y0, x1, y1))
    ys, xs = np.nonzero(np.array(f)[..., 3] > 40)
    f = f.crop((0, 0, f.width, ys.max() + 1))                 # bottom edge = lowest foot pixel
    w, h = max(1, round(f.width * k)), max(1, round(f.height * k))
    g = f.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA')   # premultiplied resize: no dark fringes
    sheet.alpha_composite(g, (round(i * FW + FW / 2 - xs.mean() * k), GROUND - h))
sheet.save(OUT + name + '_sheet.png')

p = sheet.crop((IDLE * FW, 0, (IDLE + 1) * FW, FH)); p = p.crop(p.getbbox())
s = min(96 / p.width, 144 / p.height); w, h = round(p.width * s), round(p.height * s)
ic = Image.new('RGBA', (96, 144), (0, 0, 0, 0)); ic.alpha_composite(p.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA'), ((96 - w) // 2, 144 - h))
ic.save(OUT + name + '.png')
m = np.array(sheet)[..., 3] > 24
print('%s: scale %.3f' % (name, k), ' '.join('f%d x%d-%d y%d-%d' % (i, *(lambda xs: (xs.min(), xs.max()))(np.nonzero(m[:, i*FW:(i+1)*FW])[1]), *(lambda ys: (ys.min(), ys.max()))(np.nonzero(m[:, i*FW:(i+1)*FW])[0])) for i in range(8)))
