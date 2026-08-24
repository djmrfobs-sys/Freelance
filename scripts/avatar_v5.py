#!/usr/bin/env python3
"""Add crisp white text on dark background - direct pixel manipulation."""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v5.jpg"
    
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    h, w = arr.shape[:2]
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font size
    font_size = int(radius * 0.18)
    
    font = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        sys.exit("No font")
    
    # Measure
    tmp = ImageDraw.Draw(Image.new("RGB", (1,1)))
    bbox = tmp.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    max_w = int(radius * 1.4)
    if tw > max_w:
        font_size = int(font_size * max_w / tw)
        font = ImageFont.truetype(fp, font_size)
        bbox = tmp.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    print(f"Font: {font_size}px, Text: {tw}x{th}")
    
    # Position
    text_x = cx - tw // 2
    text_y = cy + int(radius * 0.35)
    if text_y + th > cy + radius:
        text_y = cy + radius - th - int(th * 0.3)
    
    # Create separate image with white text on transparent
    text_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_layer)
    
    # Draw semi-transparent background pill
    pad_x = int(tw * 0.12)
    pad_y = int(th * 0.7)
    tdraw.rounded_rectangle(
        [(text_x - pad_x, text_y - pad_y),
         (text_x + tw + pad_x, text_y + th + pad_y)],
        radius=int(th),
        fill=(0, 0, 0, 180)
    )
    
    # White text
    tdraw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Convert text_layer to numpy
    overlay_arr = np.array(text_layer, dtype=np.uint8)  # RGBA
    
    # For each pixel: if overlay alpha > 128, use overlay color
    # Else keep original
    mask = overlay_arr[:, :, 3] > 128
    
    # Blend: for pill area (dark bg), blend with original
    # For text area (white), use pure white
    is_white = (overlay_arr[:, :, 0] > 200) & (overlay_arr[:, :, 1] > 200) & (overlay_arr[:, :, 2] > 200) & mask
    
    # Dark pill areas: mix original with dark
    is_pill = mask & ~is_white
    
    # Dark pill: 40% original + 60% dark
    alpha_bg = overlay_arr[:, :, 3].astype(np.float32) / 255.0
    alpha_bg = np.clip(alpha_bg * 0.6, 0, 0.6)  # max 60% darkening
    
    for c in range(3):
        # Dark pill areas: blend
        pill_blend = (arr[:, :, c].astype(np.float32) * (1 - alpha_bg) + 
                      0 * alpha_bg)  # dark = 0
        arr[:, :, c] = np.where(is_pill, pill_blend.astype(np.uint8), arr[:, :, c])
        
        # White text: set to 248 (near white, not 255 to avoid clipping)
        arr[:, :, c] = np.where(is_white, 248, arr[:, :, c])
    
    result = Image.fromarray(arr, "RGB")
    result.save(output_path, "JPEG", quality=97)
    print(f"Saved: {output_path}")
    
    # Verify
    check = Image.open(output_path)
    text_px = check.getpixel((cx, text_y + th//2))
    bg_px = check.getpixel((cx, text_y + th + 15))
    print(f"Text: {text_px}, BG: {bg_px}, contrast: {abs(sum(text_px)-sum(bg_px)):.0f}")

if __name__ == "__main__":
    main()
