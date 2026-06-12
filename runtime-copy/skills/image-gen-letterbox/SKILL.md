---
name: image-gen-letterbox
description: Use when generating or editing images via Gemini / nano-banana / banana-pro / gemini-3-pro-image-preview and the target aspect ratio is NOT one of the standard ones the model accepts (16:9, 4:3, 1:1, 3:4, 9:16). Typical triggers — YouTube banners 2560×423, ultra-wide headers, vertical strips, any ratio ≥ 3:1 or ≤ 1:3. This skill teaches the letterbox-and-crop trick so Pro stops mangling the composition.
---

# Image generator letterbox trick

Image generation models (Gemini 3 Pro Image, nano-banana, gemini-2.5-flash-image, and other "Banana" family models) only accept a fixed set of **standard aspect ratios**: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`. Passing a non-standard size (e.g. `2560×423` ≈ 6:1 for a YouTube banner, or `768×2048` for a super-tall infographic) causes one of three failure modes:

1. The model silently picks the nearest supported ratio and ignores your intended framing.
2. The model regenerates the scene "creatively" and destroys any composition you tried to preserve.
3. Spatial instructions in the prompt ("top-left corner", "right third") stop working because the model thinks in terms of its own frame.

The fix is to **always work inside a standard ratio**: pad the inputs up to the nearest standard ratio, do the generation there, then crop back.

## When to trigger this skill

Trigger whenever you are about to call a Gemini image model AND the target output aspect ratio is not in `{1:1, 16:9, 9:16, 4:3, 3:4}`. Do not assume the model will handle anything else — it won't. Common real-world triggers:

- YouTube banners (2560×423, ≈ 6:1)
- Twitter / X headers (1500×500, 3:1)
- LinkedIn banners (1584×396, 4:1)
- Ultra-wide cinematic strips
- Tall vertical story strips that don't match 9:16
- Any target where `max(w,h) / min(w,h) > 1.78` (beyond 16:9)

If the user-requested dimensions map cleanly to a standard ratio (1920×1080, 1024×1024, 1080×1920, etc.), this skill does not apply — call the model directly.

## Algorithm

Given:
- Target output size `W_target × H_target` (non-standard)
- One or more input images at the target size (the scene to preserve, a style reference, etc.)
- A prompt describing the edit

Do this:

### 1. Pick the wrapping aspect ratio

Pick the standard ratio from `{16:9, 4:3, 1:1, 3:4, 9:16}` that contains `W_target × H_target` without cropping, with the smallest added padding. In practice:

- If the target is wider than 16:9 (w/h > 16/9 ≈ 1.78) → wrap into **16:9**, padding goes **top and bottom**.
- If the target is taller than 9:16 (h/w > 16/9) → wrap into **9:16**, padding goes **left and right**.
- Otherwise use 4:3 / 3:4 / 1:1 — whichever is closest without cropping.

### 2. Compute the letterbox canvas

For 16:9 with a wide target:
```python
W = W_target
H_lb = W * 9 // 16          # 2560 → 1440
pad_top = (H_lb - H_target) // 2
pad_bottom = H_lb - H_target - pad_top
```
For 9:16 with a tall target, mirror the math on the width axis.

The letterbox color should be **solid black** `(0, 0, 0)` unless the prompt specifically needs a different context color.

### 3. Wrap every input image

Every image passed to the model — the base scene, the style reference, any secondary references — must be letterboxed to the same standard canvas size. This is important: the model uses relative positions between inputs, so they must share one coordinate system.

```python
def letterbox(im, W, H_lb, pad_top):
    canvas = Image.new("RGB", (W, H_lb), (0, 0, 0))
    canvas.paste(im, (0, pad_top))
    return canvas
```

### 4. Write the prompt with letterbox awareness

Always tell the model explicitly:

- "The image is letterboxed with black bands at top and bottom (or left and right)."
- "Do NOT add anything into the black bands — they are padding, not content."
- "All new content must go ONLY inside the central bright band."
- If you have a reference image too: "The reference image is letterboxed the same way. Use it for layout / style but do NOT copy its content."

Without this, the model will happily draw into the black bars.

### 5. Call the model at the standard ratio

Use the **wrapping ratio** (e.g. `"16:9"`) in `aspect_ratio`, not the target.

```python
data = generate_image(
    prompt,
    inputs=[base_lb, style_ref_lb],
    model="gemini-3-pro-image-preview",
    aspect_ratio="16:9",
    image_size="2K",
)
```

### 6. Normalize the result

The model returns *some* 16:9 image, but not necessarily at your letterbox resolution — Gemini might give back 2048×1152, 2752×1536, or anything else in the same ratio. Resize it back to your letterbox canvas size before cropping:

```python
result = Image.open(BytesIO(data)).convert("RGB")
normalized = result.resize((W, H_lb), Image.LANCZOS)
```

### 7. Crop back to the target

Cut out the central strip (or column) that corresponds to the original unpadded region:

```python
final = normalized.crop((0, pad_top, W, pad_top + H_target))
final.save(out_path, "PNG")
```

Final size is now exactly `W_target × H_target`, ready to publish.

## Reference pipeline (YouTube banner case)

This was the working pipeline in the Youtube channel project — `preview/Claude-view/src/build_banner_text_pro.py` and `build_banner_bg.py`:

1. **Background** — generate at `21:9` (wide panorama), then crop the center horizontal strip to 2560×423. Not a letterbox job per se, but the same "standard ratio → crop back" idea.
2. **Face composite** — user did this themselves in a banana-pro web UI by feeding the right crop. Locally, the letterbox approach works: letterbox the 2560×423 banner into 2560×1440, feed into Pro with a style reference, crop back.
3. **Text overlay** — full letterbox pipeline:
   - `letterbox(bg_ready, 2560, 1440, 508)` → base
   - `letterbox(sample_banner_with_text_layout, 2560, 1440, 508)` → style/layout ref
   - Pro with `aspect_ratio="16:9"`, prompt explicitly warned about black padding bands
   - Result normalized to 2560×1440
   - Crop `(0, 508, 2560, 931)` → 2560×423 final

## Failure modes to watch for

- **Model fills the black bands.** → Make the prompt warning more aggressive: "The black top and bottom bands are padding. They must stay pure black. Draw absolutely nothing in them."
- **Model crops the preserved input.** → Add "Preserve every pixel of INPUT 1 exactly. Do not resize, do not reframe, do not recompose."
- **Text / element drifts outside the central strip.** → Lock it with "The text must sit entirely within the central bright band, at least N pixels from the top and bottom edges of that band."
- **Model returns at a different resolution.** → Always `resize((W, H_lb), LANCZOS)` before cropping. Never trust the returned resolution.
- **Reference image contents leak into the output.** → "Use INPUT 2 only for layout and style. Do NOT copy any pixels, figures, text, or shapes from it."

## Anti-patterns

- **Don't** try to hack aspect ratios the model doesn't advertise (`"6:1"`, `"21:9"` without verifying it's supported) — you'll get a validation error or silent fallback. The safe set is `{1:1, 16:9, 9:16, 4:3, 3:4}`. Some newer Pro builds accept `21:9`; verify with a cheap test before trusting it.
- **Don't** skip the letterbox on just the reference image. Both the base and the reference must share the same canvas, otherwise the model cannot align layouts.
- **Don't** crop the result before resizing to the known letterbox size. The model's returned resolution is not the letterbox resolution.
- **Don't** compose the face locally in PIL and then send the composite to Pro with "just add glow" — the model will repaint everything anyway. If you want Pro to relight, give it a standard-ratio crop that actually fits the model, let it work, then composite *its output* back into your non-standard canvas.
