#!/usr/bin/env python3
"""Bakes the four AK-47 exports (48x48, gun already horizontal / facing right) into game assets.

default            -> assets/weapons/rifle.png (48x24 in-hand sprite, 1:1 pixels), rifle_icon.png (64x24 HUD icon),
                      skins/rifle_default_thumb.png (48x48 shop 'DEFAULT' preview)
rifle_neon_circuit / rifle_royal_bengal / rifle_arctic_ghost
                   -> assets/weapons/skins/<id>/body.png (48x24, drawn in hand), icon.png (64x24), thumb.png (48x48)

game.html measures the muzzle from the DEFAULT sprite (right-most opaque column, mean row of that column), so every skin is
shifted vertically until its barrel row matches the default's. All four exports already end on column 47.
Run from the project root:  python3 tools/bake_ak_skins.py
"""
import os
from PIL import Image
import numpy as np

SRC = 'tools/skin_sources/'
OUT = 'assets/weapons/'
SKINS = ['rifle_neon_circuit', 'rifle_royal_bengal', 'rifle_arctic_ghost']
CROP_TOP = 13            # 24 rows [13..36]: the default gun (rows 17..32) ends up centred on row 12

def tip_row(im):
    a = np.array(im)[:, :, 3]
    xs = np.where((a > 40).any(axis=0))[0]
    return np.where(a[:, xs.max()] > 40)[0].mean()

def bake(src, ref_tip):
    im = Image.open(src).convert('RGBA')
    dy = int(round(ref_tip - tip_row(im)))                  # rows to move the sprite so the barrel lines up with the default
    shifted = Image.new('RGBA', im.size, (0, 0, 0, 0)); shifted.paste(im, (0, dy), im)
    body = shifted.crop((0, CROP_TOP, 48, CROP_TOP + 24))
    icon = Image.new('RGBA', (64, 24), (0, 0, 0, 0)); icon.paste(body, (8, 0), body)
    return body, icon, im

ref = Image.open(SRC + 'rifle_default.png').convert('RGBA')
ref_tip = tip_row(ref)
body, icon, thumb = bake(SRC + 'rifle_default.png', ref_tip)
os.makedirs(OUT + 'skins', exist_ok=True)
body.save(OUT + 'rifle.png'); icon.save(OUT + 'rifle_icon.png'); thumb.save(OUT + 'skins/rifle_default_thumb.png')
for sid in SKINS:
    body, icon, thumb = bake(SRC + sid + '.png', ref_tip)
    d = OUT + 'skins/' + sid + '/'; os.makedirs(d, exist_ok=True)
    body.save(d + 'body.png'); icon.save(d + 'icon.png'); thumb.save(d + 'thumb.png')
    print(sid, 'tip row', round(tip_row(body), 2), 'vs default', round(tip_row(Image.open(OUT + 'rifle.png')), 2))
print('done')
