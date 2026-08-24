#!/usr/bin/env python3
"""Add text overlay to an image without altering original photo."""

from PIL import Image, ImageDraw, ImageFont
import sys, os

def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not input_path:
        sys.exit("Usage: add_text_avatar.py <image_path> [text]")
    
    text = sys.argv[2] if len(sys.argv) > 2 else "DJARVIS HELPER"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "avatar_output.jpg"
    
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    
    # Create a transparent overlay for text
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Find a good font size (responsive to image width)
    font_size = int(w * 0.065)
    
    # Try fonts in order of preference
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
    
    # Measure text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Position: bottom center, with padding
    pad = int(h * 0.06)
    x = (w - tw) // 2
    y = h - th - pad
    
    # Draw background pill behind text
    pill_pad_x = int(tw * 0.08)
    pill_pad_y = int(th * 0.3)
    draw.rounded_rectangle(
        [(x - pill_pad_x, y - pill_pad_y), 
         (x + tw + pill_pad_x, y + th + pill_pad_y)],
        radius=int(th * 0.5),
        fill=(0, 0, 0, 120)
    )
    
    # Draw text in white
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Composite
    result = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    result.save(output_path, "JPEG", quality=95)
    
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes, {w}x{h})")

if __name__ == "__main__":
    main()
