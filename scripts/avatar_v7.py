#!/usr/bin/env python3
"""Draw dark pill with white text as a combined overlay on RGB image."""

from PIL import Image, ImageDraw, ImageFont
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v7.jpg"
    
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Font
    font_size = int(radius * 0.18)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        sys.exit("No font")
    font = ImageFont.truetype(font_path, font_size)
    
    # Measure text
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
    
    pad_x = int(tw * 0.12)
    pad_y = int(th * 0.7)
    pill_left = text_x - pad_x
    pill_top = text_y - pad_y
    pill_right = text_x + tw + pad_x
    pill_bottom = text_y + th + pad_y
    pill_w = pill_right - pill_left
    pill_h = pill_bottom - pill_top
    
    print(f"Font: {font_size}px, Pill: {pill_w}x{pill_h}, Text: {tw}x{th}")
    
    # Create COMPLETELY OPAQUE pill + text image
    # This image has dark bg with white text, ready to blend with original
    pill_full = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pill_full)
    
    # Draw dark pill background - fully opaque
    pdraw.rounded_rectangle(
        [(0, 0), (pill_w-1, pill_h-1)],
        radius=int(th),
        fill=(0, 0, 0, 180)  # semi-transparent dark
    )
    
    # Draw white text, fully opaque
    text_local_x = pad_x
    text_local_y = pad_y
    pdraw.text((text_local_x, text_local_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Now paste this pill onto the image using paste with alpha mask
    # This properly alpha-blends the dark pill + white text combo
    img.paste(pill_full, (pill_left, pill_top), pill_full)
    
    img.convert("RGB").save(output_path, "JPEG", quality=97)
    print(f"Saved: {output_path}")
    
    # Verify
    check = Image.open(output_path)
    text_px = check.getpixel((cx, text_y + th//2))
    bg_px = check.getpixel((cx, text_y + th + 15))
    print(f"Text: {text_px}, BG: {bg_px}, contrast: {abs(sum(text_px)-sum(bg_px)):.0f}")

if __name__ == "__main__":
    main()
