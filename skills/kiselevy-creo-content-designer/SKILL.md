---
name: "kiselevy-creo-content-designer"
description: "Generate branded posts with reference photos for KISELEVY CREO Telegram channels"
---

# KISELEVY CREO Content Designer

A skill for generating branded visual content for two Telegram channels:
- **@kiselevy_creo_digital** — AI/automation/vibecoding
- **@ecstatic_dance_mantra** — mantras/ecstatic dance/spirituality

## Workflow

### Step 1: Reference Images
Use the following reference photos stored in `references/`:
- `references/fobs_keti_1.jpg` (1024x1024) — MR. FOBS + Keti together
- `references/fobs_keti_2.jpg` (960x1280) — MR. FOBS + Keti together
- `references/keti_reference.jpg` (854x1280) — Keti solo
- `references/mantra_ref_1.jpg` through `mantra_ref_6.jpg` — various poses for mantra channel

### Step 2: Image Generation Rules
1. **DO NOT change faces** — keep the person(s) identical to the reference
2. Can change **background** to match post topic
3. Can change **clothing** to match style (tech/business for @kiselevy_creo_digital, spiritual/flowy for @ecstatic_dance_mantra)
4. Use `image_generate` with reference images as `images` parameter
5. Aspect ratio defaults: 1024x1024 square (works well for both channels)

### Step 3: Channel-Specific Styling

#### @kiselevy_creo_digital
- Background themes: AI tech, data centers, glowing circuits, modern offices, abstract digital art
- Clothing: smart casual, techwear, business minimal
- Mood: confident, futuristic, clean
- Color palette: dark blues, purples, neon accents, white

#### @ecstatic_dance_mantra
- Background themes: nature, sunset, ocean, mandalas, zen gardens, sacred geometry, stars
- Clothing: natural fabrics, flowy, earth tones, white/cream
- Mood: calm, spiritual, warm
- Color palette: warm golds, earth tones, soft greens, sunset oranges

### Step 4: Delivery
After generating the image, send it to the appropriate Telegram channel:
- **@kiselevy_creo_digital** — chat_id: -1004292661967
- **@ecstatic_dance_mantra** — chat_id: -1003710808648

Use `exec` with curl to send the image alongside the post text.

## Post Format Reminders
- short dashes (–), not em-dashes (—)
- Only monochrome/vector emojis
- No markdown formatting (use HTML parse_mode)
- Always include Instagram mention: @kiselevy_creo

## Error Handling
- If image generation fails, post text-only and note the error
- If API limit reached, try different model via `image_generate` with model parameter
