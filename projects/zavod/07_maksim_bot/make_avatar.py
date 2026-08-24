#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает аватар для бота Максима из референса: круг-радиус, градиент, виньетка.
Кадрирование: лицо Макса ~59% ширины, ~31% высоты кадра."""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else None
_OUT = "maksim_avatar.png"
SIZE = 1024

if not SRC or not os.path.exists(SRC):
    sys.exit("Нет исходника")

img = Image.open(SRC).convert("RGB")
w, h = img.size

# --- Тесный кроп на лицо, чтобы оно стало крупным и по центру, рука ушла ---
# Лицо Макса: ~57% ширины, ~33% высоты. Подстраиваем: лицо хотим по центру.
# Смещаем центр кропа чуть левее и выше, чтобы центрировать лицо.
face_x = int(w * 0.55)
face_y = int(h * 0.35)
# Окно: ~58% ширины кадра, лицо по центру окна
win = int(w * 0.66)
left = face_x - win//2
if left < 0: left = 0
right = left + win
if right > w:
    right = w
    left = w - win
top = max(0, face_y - int(win*0.42))   # лицо чуть выше центра окна
bottom = top + win
if bottom > h:
    bottom = h
    top = h - win
crop = img.crop((left, top, right, bottom)).resize((SIZE, SIZE), Image.LANCZOS)

# Лёгкое улучшение
crop = ImageEnhance.Color(crop).enhance(1.1)
crop = ImageEnhance.Contrast(crop).enhance(1.05)

# ---------- Фон: размытый увеличенный снимок ----------
bg = crop.resize((SIZE, SIZE), Image.LANCZOS).filter(ImageFilter.GaussianBlur(60))
bg = ImageEnhance.Brightness(bg).enhance(0.72)
bg = ImageEnhance.Color(bg).enhance(1.2)
warm = Image.new("RGB", (SIZE, SIZE), (255, 158, 82))
bg = Image.blend(bg, warm, 0.15)

# ---------- Круглая маска ----------
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).ellipse((0, 0, SIZE, SIZE), fill=255)

# ---------- Композиция ----------
canvas = bg.convert("RGBA")
inner = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
inner.paste(crop, (0, 0))
inner.putalpha(mask)
canvas.paste(inner, (0, 0), inner)

# ---------- Кольцо-рамка ----------
ring = ImageDraw.Draw(canvas)
ring.ellipse((2, 2, SIZE-2, SIZE-2), outline=(80, 60, 130, 220), width=14)
ring.ellipse((14, 14, SIZE-14, SIZE-14), outline=(255, 255, 255, 200), width=3)

# ---------- Виньетка ----------
vig = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(vig).ellipse((0, 0, SIZE, SIZE), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(SIZE*0.28))
dark = Image.new("RGBA", (SIZE, SIZE), (10, 8, 20, 0))
dark.putalpha(vig.point(lambda p: int((255-p)*0.45)))
canvas = Image.alpha_composite(canvas, dark)

final = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
final.paste(canvas, (0, 0), mask)
final.save(_OUT, "PNG")
print("OK ->", _OUT, os.path.getsize(_OUT), "байт")
