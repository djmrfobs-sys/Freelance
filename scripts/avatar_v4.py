#!/usr/bin/env python3
"""Add crisp white text on dark pill background. Uses paste() for opacity."""

from PIL import Image, ImageDraw, ImageFont
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v4.jpg"
    
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font size responsive to circle
    font_size = int(radius * 0.17)
    
    font = None
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        sys.exit("No font")
    
    # Measure
    tmp = ImageDraw.Draw(Image.new("RGBA", (1,1)))
    bbox = tmp.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    # Scale down if too wide
    max_w = int(radius * 1.4)
    if tw > max_w:
        font_size = int(font_size * max_w / tw)
        font = ImageFont.truetype(fp, font_size)
        bbox = tmp.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    
    print(f"Font: {font_size}px, Text: {tw}x{th}")
    
    # Position inside circle bottom
    text_x = cx - tw // 2
    text_y = cy + int(radius * 0.35)
    text_bottom = text_y + th
    circle_bottom = cy + radius
    if text_bottom > circle_bottom:
        text_y = circle_bottom - th - int(th * 0.3)
    
    # Create pill texture: dark semi-transparent
    pad_x = int(tw * 0.12)
    pad_y = int(th * 0.6)
    pill_left = text_x - pad_x
    pill_top = text_y - pad_y
    pill_right = text_x + tw + pad_x
    pill_bottom = text_y + th + pad_y
    pill_w = pill_right - pill_left
    pill_h = pill_bottom - pill_top
    
    # Create pill image with fully opaque dark bg and white text
    pill_img = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pill_img)
    
    # Draw filled rounded rect with alpha 150
    pdraw.rounded_rectangle(
        [(0, 0), (pill_w-1, pill_h-1)],
        radius=int(th * 0.8),
        fill=(0, 0, 0, 150)
    )
    
    # Draw white text
    text_local_x = pad_x
    text_local_y = pad_y
    pdraw.text((text_local_x, text_local_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Paste pill onto image using alpha
    img.paste(pill_img, (pill_left, pill_top), pill_img)
    
    img.convert("RGB").save(output_path, "JPEG", quality=97)
    print(f"Saved: {output_path}")
    
    # Verify
    check = Image.open(output_path)
    px = check.getpixel((cx, text_y + th//2))
    bg = check.getpixel((cx, text_y + th + 10))
    print(f"Text: {px}, BG: {bg}, contrast: {abs(sum(px)-sum(bg)):.0f}")

if __name__ == "__main__":
    main()
