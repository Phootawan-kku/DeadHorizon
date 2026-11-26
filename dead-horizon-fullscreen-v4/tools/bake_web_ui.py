#!/usr/bin/env python3
"""Cuts the website UI kit (tools/ui_sources/web_ui_kit.png, 1376x768) into reusable pieces under assets/ui/web/:

  plate.png      one rusted steel plate, rounded corners, bullet holes inpainted out so it can be 9-sliced to ANY card size
  hole_1..4.png  the original bullet holes as small decals (CSS sprinkles them back on some cards)
  frame.png      the hazard/steel ring around the kit with a transparent middle (CSS border-image around the embedded game)
  bar.png        the top hazard + clamp bar (full width dividers: CTA band, footer, nav)
  hazard.png     a short clean hazard-tape strip (repeat-x underline under section titles)

Run from the project root:  python3 tools/bake_web_ui.py      (needs numpy, Pillow, opencv-python-headless)
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC, OUT = 'tools/ui_sources/web_ui_kit.png', 'assets/ui/web/'
kit = Image.open(SRC).convert('RGB')
A = np.array(kit)

# ---- plate: top-left tile, bbox measured from the sheet ----
PX0, PY0, PX1, PY1 = 82, 97, 466, 378
plate = A[PY0:PY1, PX0:PX1].copy()
h, w = plate.shape[:2]
lum = plate.mean(2)
mask = np.zeros((h, w), np.uint8)
inner = np.zeros((h, w), bool); inner[12:h - 12, 12:w - 12] = True          # keep rim/rivets untouched
for (cx0, cy0) in [(0, 0), (w - 34, 0), (0, h - 34), (w - 34, h - 34)]:
    inner[cy0:cy0 + 34, cx0:cx0 + 34] = False                              # never touch the corner rivets
mask[(lum < 30) & inner] = 255                                              # bullet holes are near-black
mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
clean = cv2.inpaint(plate, mask, 5, cv2.INPAINT_TELEA)
# rounded-corner alpha (the plate's dark outline sits on the dark gap, so a soft mask hides the square corners)
m = Image.new('L', (w * 4, h * 4), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), 11 * 4, fill=255)
alpha = m.resize((w, h), Image.LANCZOS)
p = Image.fromarray(clean).convert('RGBA'); p.putalpha(alpha); p.save(OUT + 'plate.png')

# ---- bullet-hole decals (absolute coords of 4 clear holes on the top-left plate) ----
for i, (cx, cy) in enumerate([(351, 164), (329, 184), (419, 206), (403, 323)], 1):
    r = 15
    c = np.array(kit.crop((cx - r, cy - r, cx + r, cy + r)).convert('RGBA'))
    yy, xx = np.mgrid[-r:r, -r:r]; d = np.sqrt(xx * xx + yy * yy)
    c[..., 3] = (np.clip((r - 1 - d) / 6.0, 0, 1) * 255).astype(np.uint8)    # soft round cutout
    Image.fromarray(c, 'RGBA').save(OUT + 'hole_%d.png' % i)

# ---- frame ring (transparent middle) ----
fr = kit.convert('RGBA'); fa = np.array(fr); fa[50:728, 42:1334, 3] = 0
Image.fromarray(fa, 'RGBA').save(OUT + 'frame.png')

# ---- bars ----
kit.crop((0, 0, 1376, 46)).save(OUT + 'bar.png')
kit.crop((850, 6, 972, 40)).save(OUT + 'hazard.png')       # 122x34 = 2 stripe periods (61px), hole-free, tiles seamlessly
print('baked plate %dx%d, 4 holes, frame, bar, hazard' % (w, h))
