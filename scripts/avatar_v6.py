#!/usr/bin/env python3
"""Draw white text directly on RGB image - no alpha compositing."""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v6.jpg"
    
    # Work in RA mode (float) for clean blending
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img, dtype=np.float32) / 255.0
    h, w = arr.shape[:2]
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font
    font_size = int(radius * 0.18)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        sys.exit("No font")
    font = ImageFont.truetype(font_path, font_size)
    
    # Measure text
    tmp = ImageDraw.Draw(Image.new("RGB", (1,1)))
    bbox = tmp.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    max_w = int(radius * 1.4)
    if tw > max_w:
        font_size = int(font_size * max_w / tw)
        font = ImageFont.truetype(font_path, font_size)
        bbox = tmp.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    print(f"Font: {font_size}px, Text: {tw}x{th}")
    
    text_x = cx - tw // 2
    text_y = cy + int(radius * 0.35)
    if text_y + th > cy + radius:
        text_y = cy + radius - th - int(th * 0.3)
    
    # Create a mask image: black bg, white text
    mask_img = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask_img)
    
    # Draw dark pill background
    pad_x = int(tw * 0.12)
    pad_y = int(th * 0.7)
    mdraw.rounded_rectangle(
        [(text_x - pad_x, text_y - pad_y),
         (text_x + tw + pad_x, text_y + th + pad_y)],
        radius=int(th),
        fill=120  # medium-dark
    )
    
    # White text on mask
    mdraw.text((text_x, text_y), text, fill=255, font=font)
    
    mask = np.array(mask_img, dtype=np.float32) / 255.0
    
    # Blend: result = original * (1 - mask) + white_text * mask
    # But we want: pill = dark background, text = white
    # For mask < 120: keep original
    # For mask >= 120 and < 248: it's pill area, darken
    # For mask >= 248: pure white text
    
    mask_pill = (mask > 0.1) & (mask < 0.97)  # pill background area
    mask_text = mask >= 0.97  # white text area
    
    # Darken pill area
    dark_amount = 0.35  # how much to darken
    for c in range(3):
        arr[:,:,c] = np.where(mask_pill, arr[:,:,c] * (1 - dark_amount), arr[:,:,c])
        arr[:,:,c] = np.where(mask_text, 1.0, arr[:,:,c])  # pure white
    
    result = Image.fromarray((arr * 255).astype(np.uint8), "RGB")
    result.save(output_path, "JPEG", quality=97)
    
    # Verify
    check = Image.open(output_path)
    text_px = check.getpixel((cx, text_y + th//2))
    bg_px = check.getpixel((cx, text_y + th + 15))
    print(f"Text: {text_px}, BG: {bg_px}, contrast: {abs(sum(text_px)-sum(bg_px)):.0f}")

if __name__ == "__main__":
    main()
