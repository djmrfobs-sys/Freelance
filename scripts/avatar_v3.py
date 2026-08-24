#!/usr/bin/env python3
"""Clean text overlay for circular Telegram avatar.
Places text directly inside the circle, no arc.
Uses PIL alpha composite properly with opaque white text."""

from PIL import Image, ImageDraw, ImageFont
import os, sys, math

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v3.jpg"
    
    original = Image.open(input_path).convert("RGB")
    w, h = original.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font size: proportional to circle radius
    font_size = int(radius * 0.17)
    
    font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        sys.exit("No font found")
    
    # Calculate text size
    overlay_check = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(overlay_check)
    bbox = cdraw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # If text wider than circle, scale down
    max_text_width = int(radius * 1.4)
    if tw > max_text_width:
        scale = max_text_width / tw
        font_size = int(font_size * scale)
        font = ImageFont.truetype(fp, font_size)
        bbox = cdraw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    
    # Position: bottom of circle, centered
    text_x = cx - tw // 2
    text_y = cy + int(radius * 0.35)
    
    # Ensure text bottom is inside circle
    text_bottom = text_y + th
    circle_bottom = cy + radius
    if text_bottom > circle_bottom:
        text_y = circle_bottom - th - int(th * 0.2)
    
    # Create overlay with text
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Semi-transparent pill
    pad_x = int(tw * 0.1)
    pad_y = int(th * 0.6)
    draw.rounded_rectangle(
        [(text_x - pad_x, text_y - pad_y),
         (text_x + tw + pad_x, text_y + th + pad_y)],
        radius=int(th * 0.8),
        fill=(0, 0, 0, 150)
    )
    
    # Draw text shadow for depth
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        draw.text((text_x+dx, text_y+dy), text, fill=(0, 0, 0, 80), font=font)
    
    # Draw white text (fully opaque)
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Composite
    result = Image.alpha_composite(original.convert("RGBA"), overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=97)
    
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")
    print(f"Font: {font_size}px, Text: {tw}x{th} at ({text_x},{text_y})")
    
    # Verify
    check = Image.open(output_path)
    text_px = check.getpixel((cx, text_y + th//2))
    bg_px = check.getpixel((cx, text_y + th + 10))
    print(f"Text px: {text_px}")
    print(f"BG px:   {bg_px}")
    print(f"Contrast: {abs(sum(text_px)-sum(bg_px)):.0f}")

if __name__ == "__main__":
    main()
