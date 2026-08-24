#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Надпись 'Макс-Нейро-Бро' дугой по ВЕРХНЕЙ окружности, буквы верхом НАРУЖУ,
читаются нормально слева направо. Для верхней дуги берём верх(центр)= -90°(-pi/2),
буква разворачивается так, чтобы верх смотрел наружу от центра."""
from PIL import Image, ImageDraw, ImageFont
import math, os

AV = "maksim_avatar.png"
OUT = "maksim_avatar_text.png"
TEXT = "Макс-Нейро-Бро"
SIZE = 1024

img = Image.open(AV).convert("RGBA")
overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(overlay)

cx, cy = SIZE/2, SIZE/2
radius = SIZE*0.46

def find_font(size):
    for c in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def total_w(f):
    return sum(d.textlength(c, font=f) for c in TEXT)

font_size = 80
font = find_font(font_size)
ARCS = 0.62  # доля верхней полуокружности, занятая текстом
while True:
    font = find_font(font_size)
    tw = total_w(font)
    needed = ARCS * math.pi * radius
    if tw > needed and font_size > 34:
        font_size -= 2
    else:
        break

font = find_font(font_size)
tw = total_w(font)
span_rad = tw / radius
# верх дуги в координатах изображения: y=cy-radius это НАД центром,
# угол в "матем. смысле" где верх = -pi/2 (cos=0, sin=-1 => y=cy-r).
# Идём от левого края (верх-слева) до правого (верх-справа):
# левый край = -pi/2 + span/2, правый = -pi/2 - span/2 (угол убывает)
# левый край = -pi/2 + span/2, идём направо, угол УВЕЛИЧИВАЕМ
start = -math.pi/2 - span_rad/2
ang = start
for ch in TEXT:
    chw = d.textlength(ch, font=font)
    x = cx + radius * math.cos(ang)
    y = cy + radius * math.sin(ang)
    tmp = Image.new("RGBA", (280, 280), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((140, 140), ch, font=font, fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=7, stroke_fill=(40, 25, 90, 255))
    # буква верхом наружу, наклон по дуге
    pt = math.degrees(ang) + 90
    tmp = tmp.rotate(-pt, resample=Image.BICUBIC, expand=True)
    bbox = tmp.getbbox()
    if bbox:
        tmp = tmp.crop(bbox)
        overlay.paste(tmp, (int(x - tmp.width/2), int(y - tmp.height/2)), tmp)
    ang += chw / radius

out = Image.alpha_composite(img, overlay)
out.convert("RGB").save(OUT, "PNG")
print("OK ->", OUT)
