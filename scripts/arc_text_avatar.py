#!/usr/bin/env python3
"""
Add arc-shaped text to an image, fitting within a circular crop.
Optimized for Telegram avatar (circle).
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, sys

def draw_arc_text(draw, text, center_x, center_y, radius, start_angle, font, fill=(255,255,255)):
    """Draw text along an arc (circle segment)."""
    char_spacing = 1.0  # spacing multiplier
    
    # Measure total width to calculate angle spread
    total_w = 0
    char_widths = []
    for i, ch in enumerate(text):
        bbox = draw.textbbox((0, 0), ch, font=font)
        cw = bbox[2] - bbox[0]
        char_widths.append(cw)
        total_w += cw
    
    # Extra spacing between chars
    total_w += (len(text) - 1) * 2
    
    # Angle per pixel of text arc length
    # Arc length = radius * angle_rad
    angle_rad_per_px = 1.0 / radius
    total_angle_deg = total_w * angle_rad_per_px * (180 / math.pi) * char_spacing
    
    # Start from start_angle (left side)
    current_angle = start_angle
    
    for i, ch in enumerate(text):
        cw = char_widths[i]
        # Angle for this character
        char_angle = cw * angle_rad_per_px * (180 / math.pi) * char_spacing
        
        mid_angle = current_angle + char_angle / 2
        angle_rad = math.radians(mid_angle)
        
        # Position on circle
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        
        # Rotate the character to be tangent to circle
        # For bottom arc, tangent points "up" from circle
        char_img = Image.new('RGBA', (cw + 4, font.size + 4), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((2, 2), ch, fill=fill, font=font)
        
        # Rotate so text is upright at bottom
        # At 270° (bottom), text should be upright -> rotation = 0
        # At 0° (right), text should be rotated 90° CW
        # For bottom arc going left: rotation = -(mid_angle - 270)
        rotation = -(mid_angle - 270)
        
        char_img = char_img.rotate(rotation, expand=True, center=(cw//2 + 2, font.size//2 + 2))
        
        # Paste
        char_w, char_h = char_img.size
        paste_x = int(x - char_w / 2)
        paste_y = int(y - char_h / 2)
        
        draw._image.paste(char_img, (paste_x, paste_y), char_img)
        
        current_angle += char_angle

def main():
    input_path = sys.argv[1]
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_arc_output.jpg"
    
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    
    # Circle center
    cx, cy = w // 2, h // 2
    avatar_radius = min(cx, cy)  # radius of circle crop
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Font size proportional to avatar
    font_size = int(avatar_radius * 0.22)
    
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, font_size)
            break
    if not font:
        font = ImageFont.load_default()
    
    # Draw text along bottom arc of the circle
    # Place it just inside the circle edge
    text_radius = int(avatar_radius * 0.78)  # radius for text arc
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    
    # Calculate arc length needed
    arc_angle_deg = (text_w / text_radius) * (180 / math.pi)
    
    # Center the arc at bottom (270°)
    # Start from right side going left
    start_angle = 270 - arc_angle_deg / 2  # right side start
    # Text goes from start_angle counterclockwise
    
    # Draw semi-transparent background pill/banner
    # Just use a thin banner at bottom
    banner_h = int(font_size * 1.5)
    banner_y = cy + int(avatar_radius * 0.5) - banner_h // 2
    draw.rounded_rectangle(
        [(cx - int(avatar_radius * 0.65), banner_y), 
         (cx + int(avatar_radius * 0.65), banner_y + banner_h)],
        radius=banner_h // 2,
        fill=(0, 0, 0, 100)
    )
    
    # Draw text along the arc
    # For bottom arc: text is inside circle at radius
    draw_arc_text(draw, text, cx, cy, text_radius, start_angle, font)
    
    # Composite
    result = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")
    print(f"Image: {w}x{h}, Circle radius: {avatar_radius}")

if __name__ == "__main__":
    main()
