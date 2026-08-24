#!/usr/bin/env python3
"""Add arc-shaped text to image, fitting inside a circular Telegram avatar."""

from PIL import Image, ImageDraw, ImageFont
import os, sys, math

def draw_arc_text(draw, text, cx, cy, radius, start_angle_deg, end_angle_deg, font, fill=(255,255,255,255)):
    """Draw text along an arc from start_angle to end_angle (clockwise, bottom arc)."""
    n = len(text)
    if n == 0:
        return
    
    angle_range = end_angle_deg - start_angle_deg
    char_angles = []
    
    # Measure each char
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        cw = bbox[2] - bbox[0]
        char_angles.append(cw)
    
    total_width = sum(char_angles)
    spacing = 1  # extra pixels between chars
    
    # Calculate total arc angle based on text width
    arc_length_px = total_width + (n - 1) * spacing
    arc_angle = (arc_length_px / radius) * (180 / math.pi)
    
    # Center the arc
    char_step = arc_angle / n
    start_angle = 270 - arc_angle / 2  # 270 = bottom
    
    for i, ch in enumerate(text):
        char_angle = char_step
        mid_angle = start_angle + char_angle * i + char_angle / 2
        
        angle_rad = math.radians(mid_angle)
        
        # Position on circle
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)
        
        # Rotation: for bottom arc, text should be upright
        # At 270° (bottom), rotate 0. At 180° (left), rotate -90. At 0° (right), rotate 90.
        rotation = -(mid_angle - 270)
        
        # Create char image
        bbox = draw.textbbox((0, 0), ch, font=font)
        cw = bbox[2] - bbox[0]
        ch_h = bbox[3] - bbox[1]
        
        char_img = Image.new("RGBA", (cw + 6, ch_h + 6), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((3, 3), ch, fill=fill, font=font)
        
        # Center + rotate
        px = cw // 2 + 3
        py = ch_h // 2 + 3
        char_img = char_img.rotate(rotation, center=(px, py), expand=True, resample=Image.BICUBIC)
        
        # Paste onto overlay
        cw_r, ch_r = char_img.size
        paste_x = int(x - cw_r / 2)
        paste_y = int(y - ch_r / 2)
        draw._image.paste(char_img, (paste_x, paste_y), char_img)

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_arc2.jpg"
    
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = w // 2, h // 2
    radius = min(cx, cy)
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Use a proportional font size
    font_size = int(radius * 0.13)
    
    font = None
    for fp in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        font = ImageFont.load_default()
    
    # Draw a thin semi-transparent banner at the bottom for readability
    banner_radius = int(radius * 0.75)
    banner_thickness = int(font_size * 1.8)
    banner_top = cy + int(radius * 0.45) - banner_thickness // 2
    banner_bottom = banner_top + banner_thickness
    
    draw.rounded_rectangle(
        [(cx - int(radius * 0.6), banner_top), (cx + int(radius * 0.6), banner_bottom)],
        radius=banner_thickness // 2,
        fill=(0, 0, 0, 110)
    )
    
    # Draw text along arc, just inside the circle bottom
    text_radius = int(radius * 0.75)
    
    draw_arc_text(draw, text, cx, cy, text_radius, 0, 0, font, fill=(255, 255, 255, 250))
    
    # Composite
    result = Image.alpha_composite(img, overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=97)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    main()
