#!/usr/bin/env python3
"""Builds assets/enemies/armored_sheet.png (8 walk frames, 128x172 cells, facing RIGHT) from the supplied
transparent 2x4 sprite sheet tools/ui_sources/armored_walk_source.png (1536x1024).

Every frame gets the SAME scale (so the figure never pulses), its lowest boot pixel lands on ground y=168 in the cell,
and it is centred horizontally on its own alpha centroid (head jitter after alignment is ~1px).
Also writes the 96x144 portrait assets/enemies/armored.png (idle frame) used by the website cards / fallback.
Run from the project root:  python3 tools/bake_armored_sheet.py
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC, OUT = 'tools/ui_sources/armored_walk_source.png', 'assets/enemies/'
FW, FH, GROUND, FIG_H, IDLE = 128, 172, 168, 150, 7

src = Image.open(SRC).convert('RGBA')
a = np.array(src)
a[..., 3] = np.where(a[..., 3] < 20, 0, a[..., 3])          # drop faint haze around the sprites
src = Image.fromarray(a, 'RGBA')
al = a[..., 3]
lab, n = ndi.label(ndi.binary_dilation(al > 40, iterations=6))
boxes = [(o[1].start, o[0].start, o[1].stop, o[0].stop) for o in ndi.find_objects(lab)]
assert len(boxes) == 8, len(boxes)
boxes.sort(key=lambda b: (0 if b[1] < 300 else 1, b[0]))     # reading order: row 1 L->R, then row 2 L->R
k = FIG_H / float(np.median([b[3] - b[1] for b in boxes]))   # one scale for all frames

sheet = Image.new('RGBA', (FW * 8, FH), (0, 0, 0, 0))
for i, (x0, y0, x1, y1) in enumerate(boxes):
    f = src.crop((x0, y0, x1, y1))
    m = np.array(f)[..., 3] > 40
    ys, xs = np.nonzero(m)
    f = f.crop((0, 0, f.width, ys.max() + 1))                 # bottom edge = lowest boot pixel
    cx = xs.mean()
    w, h = max(1, round(f.width * k)), max(1, round(f.height * k))
    g = f.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA')   # premultiplied resize: no dark fringes
    ox = round(i * FW + FW / 2 - cx * k)
    sheet.alpha_composite(g, (ox, GROUND - h))
sheet.save(OUT + 'armored_sheet.png')

# portrait from the idle frame, tightly cropped, 96x144 (website shows it ~230px tall, so keep it crisp)
p = sheet.crop((IDLE * FW, 0, (IDLE + 1) * FW, FH)); p = p.crop(p.getbbox())
s = min(96 / p.width, 144 / p.height); w, h = round(p.width * s), round(p.height * s)
ic = Image.new('RGBA', (96, 144), (0, 0, 0, 0)); ic.alpha_composite(p.convert('RGBa').resize((w, h), Image.LANCZOS).convert('RGBA'), ((96 - w) // 2, 144 - h))
ic.save(OUT + 'armored.png')
print('scale %.3f  sheet %s  portrait %dx%d' % (k, sheet.size, w, h))
