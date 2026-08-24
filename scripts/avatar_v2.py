#!/usr/bin/env python3
"""Add text to image for circular telegram avatar - improved version."""

from PIL import Image, ImageDraw, ImageFont
import os, sys

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_v2.jpg"
    
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Font: large enough to be visible
    font_size = int(radius * 0.2)
    
    font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        font = ImageFont.load_default()
    
    # Measure text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    print(f"Text size: {tw}x{th}, font_size={font_size}")

    # Position: bottom arc, centered
    # Text should be inside circle. Circle goes from y=cy-radius to y=cy+radius
    # Place text at y = cy + radius - text_height - some margin
    text_y = cy + int(radius * 0.55)  # bottom portion of circle
    text_x = cx - tw // 2
    
    # Semi-transparent background pill
    pad_x = int(tw * 0.06)
    pad_y = int(th * 0.35)
    
    # Draw pill background
    draw.rounded_rectangle(
        [(text_x - pad_x, text_y - pad_y),
         (text_x + tw + pad_x, text_y + th + pad_y)],
        radius=int(th * 0.6),
        fill=(0, 0, 0, 140)
    )
    
    # Draw text in white with slight shadow for readability
    # Shadow
    draw.text((text_x+1, text_y+1), text, fill=(0, 0, 0, 100), font=font)
    # Main text
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 240), font=font)
    
    print(f"Text placed at: ({text_x}, {text_y}) to ({text_x+tw}, {text_y+th})")
    print(f"Circle: center=({cx},{cy}), radius={radius}")
    print(f"Text bottom edge: {text_y+th}, Circle bottom: {cy+radius}")
    
    # Composite
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
