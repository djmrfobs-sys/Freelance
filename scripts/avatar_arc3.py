#!/usr/bin/env python3
"""Add arc-shaped white text to image for Telegram circular avatar.
Uses direct pixel blend for crisp text."""

from PIL import Image, ImageDraw, ImageFont
import os, sys, math

def draw_arc_text(draw, text, cx, cy, radius, font, fill=(255,255,255)):
    """Draw text along a bottom arc centered at bottom of circle."""
    n = len(text)
    if n == 0:
        return
    
    # Measure each character
    char_widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        char_widths.append(bbox[2] - bbox[0])
    
    total_width = sum(char_widths)
    spacing = 2  # pixels between characters
    
    # Calculate arc angle
    arc_length = total_width + (n - 1) * spacing
    arc_angle_rad = arc_length / radius
    arc_angle_deg = arc_angle_rad * (180 / math.pi)
    
    # Start from the left side, going clockwise to right
    # Arc centered at bottom (270°)
    start_angle = 270 - arc_angle_deg / 2
    
    # Track arc length to position each char
    current_arc = 0
    for i, ch in enumerate(text):
        cw = char_widths[i]
        char_angle = cw / radius
        mid_angle = start_angle + math.degrees(current_arc + char_angle / 2)
        
        arad = math.radians(mid_angle)
        
        x = cx + radius * math.cos(arad)
        y = cy + radius * math.sin(arad)
        
        # Rotation: upright at bottom, tilting along arc
        rot = -(mid_angle - 270)
        
        # Create character image (fully opaque)
        bbox = draw.textbbox((0, 0), ch, font=font)
        cw_f = bbox[2] - bbox[0]
        ch_f = bbox[3] - bbox[1]
        
        pad = 5
        char_img = Image.new("RGBA", (cw_f + pad*2, ch_f + pad*2), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(char_img)
        cdraw.text((pad, pad), ch, fill=(255, 255, 255, 255), font=font)
        
        # Rotate
        char_img = char_img.rotate(rot, center=(cw_f//2 + pad, ch_f//2 + pad), expand=True, resample=Image.BICUBIC)
        
        # Paste onto overlay
        cw_r, ch_r = char_img.size
        paste_x = int(x - cw_r / 2)
        paste_y = int(y - ch_r / 2)
        draw._image.paste(char_img, (paste_x, paste_y), char_img)
        
        current_arc += (cw + spacing) / radius

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_arc3.jpg"
    
    original = Image.open(input_path).convert("RGB")
    w, h = original.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    # Work with RGB directly, no alpha confusion
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Font size
    font_size = int(radius * 0.1)
    
    font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        font = ImageFont.load_default()
    
    # Draw semi-transparent banner at bottom
    banner_radius = int(radius * 0.8)
    banner_thick = int(font_size * 1.6)
    banner_y = cy + int(radius * 0.55) - banner_thick // 2
    banner_w = int(radius * 1.3)
    
    draw.rounded_rectangle(
        [(cx - banner_w//2, banner_y), (cx + banner_w//2, banner_y + banner_thick)],
        radius=banner_thick // 2,
        fill=(0, 0, 0, 130)
    )
    
    # Draw text along arc
    text_radius = int(radius * 0.78)
    draw_arc_text(draw, text, cx, cy, text_radius, font)
    
    # Composite using alpha
    result = Image.alpha_composite(original.convert("RGBA"), overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=97)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    main()
