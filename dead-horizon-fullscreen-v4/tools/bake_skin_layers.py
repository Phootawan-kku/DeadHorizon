#!/usr/bin/env python3
"""Bakes the 48x48 diagonal exports (create_a_* rotations) of weapon SKINS into the layered in-hand rigs used by game.html.

Pistol skins (Glock rig, 48x24 canvas)  -> body.png, slide.png, mag.png   (slide kicks back, mag drops on reload)
Shotgun skins (pump rig, 54x20 canvas)  -> body.png, pump.png             (forend racks back after each shot)
Every skin also gets icon.png (64x24 HUD/armory icon) and thumb.png (48x48 shop preview = the original export).
Two default thumbs (pistol_default_thumb.png / shotgun_default_thumb.png) are baked from the existing default sprites
so the cosmetics screen can show DEFAULT vs PREVIEW.

Output: assets/weapons/skins/<skin_id>/*.png   (run from the project root)
Usage : python3 tools/bake_skin_layers.py            # uses SRC paths below (edit if your exports live elsewhere)

Geometry is aligned so the barrel tip lands on the same pixel as the default gun (game.html measures the muzzle from the
default sprite), i.e. flash / bullet origin stay correct for every skin.
"""
import math, os, sys
from PIL import Image
import numpy as np
from scipy import ndimage as ndi

OUT = 'assets/weapons/skins/'
W = 'assets/weapons/'
BLK = (1, 2, 5, 255)
SRC = {  # skin id -> exported 48x48 rotation PNG (kept in tools/skin_sources so the bake is reproducible)
    'pistol_redline':   'tools/skin_sources/pistol_redline.png',
    'pistol_ct':        'tools/skin_sources/pistol_ct.png',
    'shotgun_heirloom': 'tools/skin_sources/shotgun_heirloom.png',
    'shotgun_bluearc':  'tools/skin_sources/shotgun_bluearc.png',
}
# Pistol split lines are in the NATIVE 48x48 export's pixel rows/cols.
PISTOL = {
    'pistol_redline': dict(slide_top=8, slide_last=14, mag_first=31, mag_maxx=18),
    'pistol_ct':      dict(slide_top=10, slide_last=16, mag_first=33, mag_maxx=17),
}
# Shotgun forend rectangle (x0,x1,y0,y1 exclusive) in the baked 47-wide gun's own pixel coords, plus the tube colours.
SHOTGUN = {
    'shotgun_heirloom': dict(pump=(32, 41, 9, 13), tube=((190, 148, 92, 255), (122, 86, 52, 255)), shell_y=14),
    'shotgun_bluearc':  dict(pump=(32, 43, 8, 12), tube=((86, 100, 122, 255), (44, 50, 64, 255)), shell_y=15),
}

def salient(rgb):
    mx = rgb.max(-1); mn = rgb.min(-1)
    return ((mx - mn) >= 70) | (mx >= 215)

def reduce(img, tw, th, B=8):
    """Colour-preserving downscale of an RGBA image to tw x th. Thin saturated accent lines (red trim, blue glow,
    light lenses) survive instead of being averaged into the black outline."""
    up = np.array(img.convert('RGBA').resize((tw * B, th * B), Image.NEAREST))
    up = up.reshape(th, B, tw, B, 4).transpose(0, 2, 1, 3, 4).reshape(th, tw, B * B, 4).astype(float)
    op = up[..., 3] > 0
    n = op.sum(-1)
    sal = salient(up[..., :3]) & op
    ns = sal.sum(-1)
    out = np.zeros((th, tw, 4), np.uint8)
    wall = (up[..., :3] * op[..., None]).sum(2) / np.maximum(n, 1)[..., None]
    wsal = (up[..., :3] * sal[..., None]).sum(2) / np.maximum(ns, 1)[..., None]
    use_sal = (ns >= np.maximum(1, 0.12 * n))[..., None]
    rgb = np.where(use_sal, wsal, wall)
    keep = (n >= B * B * 0.5) | (ns >= 2)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(keep, 255, 0)
    return Image.fromarray(out)

def cleanup(img):
    """Regenerate a crisp 1px black outline around the silhouette (the rotated source has a ragged one)."""
    o = np.array(img); h, w = o.shape[:2]; pad = 2
    P = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8); P[pad:-pad, pad:-pad] = o
    S = P[:, :, 3] > 0
    S = ndi.binary_fill_holes(ndi.binary_closing(S, structure=np.ones((3, 3))))
    lab, n = ndi.label(S, structure=np.ones((3, 3)))
    if n > 1: S = lab == (1 + int(np.argmax(ndi.sum(S, lab, range(1, n + 1)))))
    for _ in range(2):
        nb = ndi.convolve(S.astype(int), np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]), mode='constant')
        S = S & ~(nb <= 1)
    inner = ndi.binary_erosion(S, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    ring = S & ~inner
    out = P.copy(); dark = (P[:, :, :3].astype(int).max(2) <= 18) & (P[:, :, 3] > 0)
    good = inner & ~dark
    if good.any():
        idx = ndi.distance_transform_edt(~good, return_distances=False, return_indices=True)
        fix = (inner & dark & ndi.binary_dilation(ring, structure=np.ones((3, 3)))) | (inner & (P[:, :, 3] == 0))
        for c in range(3): out[:, :, c] = np.where(fix, P[idx[0], idx[1], c], out[:, :, c])
    out[:, :, 3] = np.where(S, 255, 0)
    for c, v in enumerate(BLK[:3]): out[:, :, c] = np.where(ring, v, out[:, :, c])
    ys, xs = np.nonzero(S)
    return Image.fromarray(out[ys.min():ys.max() + 1, xs.min():xs.max() + 1])

def horizontal(path, LEN=48):
    """Same RotSprite-style horizontalisation as tools/bake_shotgun_layers.py, then colour-preserving reduce + cleanup."""
    src = Image.open(path).convert('RGBA')
    a = np.array(src)[:, :, 3] > 0; ys, xs = np.nonzero(a); pts = np.stack([xs, ys], 1).astype(float); c = pts.mean(0)
    v = np.linalg.svd(pts - c, full_matrices=False)[2][0]
    if v[0] < 0: v = -v
    ang = math.degrees(math.atan2(-v[1], v[0])); K = 8
    big = src.resize((src.width * K, src.height * K), Image.NEAREST).rotate(-ang, resample=Image.NEAREST, expand=True)
    big = big.crop(big.getbbox()); h = max(1, round(big.height * LEN / big.width))
    return cleanup(reduce(big, LEN, h, B=6))

def paste_center(img, size, scale=1):
    img = img.crop(img.getbbox())
    if scale != 1: img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    cv = Image.new('RGBA', size, (0, 0, 0, 0)); cv.paste(img, ((size[0] - img.width) // 2, (size[1] - img.height) // 2), img); return cv

def default_tip(name):
    a = np.array(Image.open(W + name + '.png').convert('RGBA'))[:, :, 3] > 40
    mx = np.nonzero(a.any(0))[0].max(); ys = np.nonzero(a[:, mx])[0]
    return mx, ys.mean() + .5

def bake_pistol(sid, src_path):
    p = PISTOL[sid]; S = .5; CW, CH = 48, 24
    src = Image.open(src_path).convert('RGBA'); bb = src.getbbox(); crop = src.crop(bb)
    nat = np.array(src)[:, :, 3] > 0
    tw, th = round(crop.width * S), round(crop.height * S)
    small = reduce(crop, tw, th)
    tip_x, tip_y = default_tip('pistol')
    front_nat = max(x for y in range(p['slide_top'], p['slide_last'] + 1) for x in range(48) if nat[y, x])
    X0 = int(tip_x - ((front_nat + 1 - bb[0]) * S - 1))
    cen = (p['slide_top'] + p['slide_last'] + 1) / 2.
    Y0 = int(round(tip_y - (cen - bb[1]) * S))
    assert 0 <= Y0 and Y0 + th <= CH and X0 + tw <= CW, (sid, X0, Y0, tw, th)
    cv = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); cv.paste(small, (X0, Y0), small)
    slide_y = Y0 + int((p['slide_last'] + 1 - bb[1]) * S) - 1
    slide_top = Y0 + int((p['slide_top'] - bb[1]) * S)
    mag_y = Y0 + int(round((p['mag_first'] - bb[1]) * S))
    mag_x = X0 + int((p['mag_maxx'] - bb[0]) * S)
    slide = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); body = slide.copy(); mag = slide.copy()
    q = cv.load(); sp, bp, mp = slide.load(), body.load(), mag.load()
    for y in range(CH):
        for x in range(CW):
            c = q[x, y]
            if c[3] == 0: continue
            if y <= slide_y: sp[x, y] = c
            elif y >= mag_y and x <= mag_x: mp[x, y] = c
            else: bp[x, y] = c
    front = max(x for y in range(slide_top, slide_y + 1) for x in range(CW) if sp[x, y][3])
    BAR_HI, BAR, BAR_LO = (95, 98, 108, 255), (62, 64, 73, 255), (35, 37, 45, 255)
    inner = list(range(slide_top + 1, slide_y))               # barrel exposed under the slide when it kicks back
    for x in range(front - 2, front + 2):
        bp[x, slide_top] = BLK; bp[x, slide_y] = BLK
        for i, y in enumerate(inner): bp[x, y] = BAR_HI if i == 0 else (BAR_LO if i == len(inner) - 1 else BAR)
    xs = [x for x in range(CW) if mp[x, mag_y][3]]
    for x in range(min(xs), max(xs) + 1): bp[x, mag_y - 1] = (22, 22, 29, 255); bp[x, mag_y] = BLK   # empty magazine well
    d = OUT + sid + '/'; os.makedirs(d, exist_ok=True)
    body.save(d + 'body.png'); slide.save(d + 'slide.png'); mag.save(d + 'mag.png')
    # HUD icon: same 64x24 canvas the default icon uses, a touch larger than in-hand
    icon_src = reduce(crop, round(crop.width * .55), round(crop.height * .55))
    paste_center(icon_src, (64, 24)).save(d + 'icon.png')
    src.save(d + 'thumb.png')
    print(sid, 'canvas gun', (tw, th), 'X0,Y0', (X0, Y0), 'slide rows', slide_top, slide_y, 'mag', mag_y, mag_x, 'front', front)

def bake_shotgun(sid, src_path):
    p = SHOTGUN[sid]; CW, CH = 54, 20
    gun = horizontal(src_path)
    a = np.array(gun)[:, :, 3] > 0
    mx = np.nonzero(a.any(0))[0].max(); ys = np.nonzero(a[:, mx])[0]
    tip_x, tip_y = default_tip('shotgun')
    X0 = int(tip_x - mx); Y0 = int(round(tip_y - (ys.mean() + .5)))
    assert 0 <= Y0 and Y0 + gun.height <= CH and X0 >= 0, (sid, X0, Y0, gun.size)
    body = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); body.paste(gun, (X0, Y0), gun); bp = body.load()
    px0, px1, py0, py1 = p['pump']; px0 += X0; px1 += X0; py0 += Y0; py1 += Y0
    pump = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); pp = pump.load()
    for y in range(py0, py1):                                   # lift the forend into its own layer
        for x in range(px0, px1):
            if bp[x, y][3]: pp[x, y] = bp[x, y]
            bp[x, y] = (0, 0, 0, 0)
    hi, mid = p['tube']; right = X0 + mx - 2                     # magazine tube that the forend normally hides
    for x in range(px0 - 1, right):
        if bp[x, py0][3] == 0 or x >= px0 - 1:
            bp[x, py0] = hi; bp[x, py0 + 1] = mid; bp[x, py0 + 2] = BLK
    cv = body.copy(); cv.alpha_composite(pump)
    d = OUT + sid + '/'; os.makedirs(d, exist_ok=True)
    body.save(d + 'body.png'); pump.save(d + 'pump.png')
    paste_center(cv, (64, 24)).save(d + 'icon.png')
    Image.open(src_path).convert('RGBA').save(d + 'thumb.png')
    print(sid, 'gun', gun.size, 'X0,Y0', (X0, Y0), 'pump', (px0, px1, py0, py1), 'shell_y', p['shell_y'] + Y0 - 0)

def bake_defaults():
    for name, scale in (('pistol', 2), ('shotgun', 1)):
        im = Image.open(W + name + '.png').convert('RGBA')
        paste_center(im, (48, 48), scale).save(OUT + name + '_default_thumb.png')

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for sid, path in SRC.items():
        if not os.path.exists(path): sys.exit('missing source: ' + path)
        (bake_pistol if sid.startswith('pistol') else bake_shotgun)(sid, path)
    bake_defaults()
