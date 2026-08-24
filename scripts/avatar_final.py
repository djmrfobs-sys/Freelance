#!/usr/bin/env python3
"""Draw text on image for Telegram circular avatar - direct pixel manipulation."""

from PIL import Image, ImageDraw, ImageFont
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_final.jpg"
    
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font sizing - make it bold and visible
    font_size = int(radius * 0.16)
    
    font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        font = ImageFont.load_default()
    
    # Create a separate RGBA layer for text + background
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Measure
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Position inside circle bottom area
    text_y = cy + int(radius * 0.55)  # inside circle bottom
    text_x = cx - tw // 2
    
    # Pill background
    pad_x = int(tw * 0.08)
    pad_y = int(th * 0.5)
    
    dr = int(cy + radius) - (text_y + th + pad_y)
    if dr < 0:
        # Text would go outside circle - move up
        text_y += dr
    
    pill_top = text_y - pad_y
    pill_bottom = text_y + th + pad_y
    pill_left = text_x - pad_x
    pill_right = text_x + tw + pad_x
    
    # Draw semi-transparent dark pill
    draw.rounded_rectangle(
        [(pill_left, pill_top), (pill_right, pill_bottom)],
        radius=int(th * 0.6),
        fill=(0, 0, 0, 160)
    )
    
    # Draw text with slight glow/shadow for visibility
    for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,2), (2,0), (-2,0), (0,-2)]:
        draw.text((text_x + ox, text_y + oy), text, fill=(255, 255, 255, 60), font=font)
    
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Composite: overlay onto original
    # For proper alpha blending: result = overlay over original
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=97)
    
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")
    print(f"Font: {font_size}px, Text: {tw}x{th} at ({text_x}, {text_y})")
    
    # Verify text visibility
    test = Image.open(output_path)
    text_center_px = test.getpixel((cx, text_y + th//2))
    bg_center_px = test.getpixel((cx, text_y + th + 20))
    print(f"Text area pixel: {text_center_px}")
    print(f"Background area pixel: {bg_center_px}")
    print(f"Contrast: diff={abs(sum(text_center_px)-sum(bg_center_px)):.0f}")

if __name__ == "__main__":
    main()
