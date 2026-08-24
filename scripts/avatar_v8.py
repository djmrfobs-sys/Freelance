#!/usr/bin/env python3
"""Blend white text on dark pill with original using numpy for precise control."""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v8.jpg"
    
    # Load as float array
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    h, w, _ = arr.shape
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font
    font_size = int(radius * 0.18)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        sys.exit("No font")
    font = ImageFont.truetype(font_path, font_size)
    
    # Measure
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (1,1)))
    bbox = tmp_draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    max_w = int(radius * 1.4)
    if tw > max_w:
        font_size = int(font_size * max_w / tw)
        font = ImageFont.truetype(font_path, font_size)
        bbox = tmp_draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    text_x = cx - tw // 2
    text_y = cy + int(radius * 0.35)
    if text_y + th > cy + radius:
        text_y = cy + radius - th - int(th * 0.3)
    
    # Create combined pill+text overlay as an RGBA image
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    
    # Dark pill - semi-transparent
    pad_x = int(tw * 0.12)
    pad_y = int(th * 0.7)
    odraw.rounded_rectangle(
        [(text_x - pad_x, text_y - pad_y),
         (text_x + tw + pad_x, text_y + th + pad_y)],
        radius=int(th),
        fill=(0, 0, 0, 160)  # 160/255 alpha
    )
    
    # White text - fully opaque
    odraw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Convert overlay to float array
    overlay_arr = np.array(overlay, dtype=np.float32)
    overlay_rgb = overlay_arr[:,:,:3]
    overlay_alpha = overlay_arr[:,:,3:4] / 255.0  # shape (h, w, 1)
    
    # For each pixel:
    # result = original * (1 - alpha) + overlay_pixel * alpha
    result_arr = arr * (1.0 - overlay_alpha) + overlay_rgb * overlay_alpha
    
    result = Image.fromarray(result_arr.astype(np.uint8), "RGB")
    result.save(output_path, "JPEG", quality=97)
    
    # Verify
    check = Image.open(output_path)
    text_px = check.getpixel((cx, text_y + th//2))
    bg_px = check.getpixel((cx, text_y + th + 15))
    bg_orig_px = img.getpixel((cx, text_y + th + 15))
    orig_text_px = img.getpixel((cx, text_y + th//2))
    print(f"Font: {font_size}px")
    print(f"Original text area: {orig_text_px}")
    print(f"Result text: {text_px}")
    print(f"Result bg:   {bg_px}")
    print(f"Original bg: {bg_orig_px}")
    print(f"Contrast: {abs(sum(text_px)-sum(bg_px)):.0f}")

if __name__ == "__main__":
    main()
