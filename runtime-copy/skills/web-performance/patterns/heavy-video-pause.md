---
title: Pause off-screen and chat-occluded videos
impact: MEDIUM
tags: html, video, gpu, compositing, intersectionobserver
---

# Pause videos the user isn't looking at

**Anti-pattern**: page with multiple `<video autoplay loop muted playsinline>` elements (hero, section backgrounds, day/night swaps). Each playing video runs its own decode pipeline. With 4K HEVC at ~70 Mbps, 2–3 simultaneous decoders can saturate the GPU on integrated graphics.

The browser does NOT auto-pause videos that are scrolled off-screen — it keeps decoding to keep playback position accurate. Even videos hidden behind an open modal/chat panel keep decoding.

## Fix: IntersectionObserver to play only what's visible

```js
const videos = document.querySelectorAll('video[data-autoplay-when-visible]');
const visibility = new Map();

const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    const v = entry.target;
    if (entry.isIntersecting) {
      v.play().catch(() => {});  // resume
    } else {
      v.pause();  // free the decoder
    }
  }
}, { threshold: 0.05 });  // 5% visible is enough to start

videos.forEach(v => observer.observe(v));
```

Mark videos in HTML:
```html
<video data-autoplay-when-visible loop muted playsinline preload="metadata"
       src="hero.mp4"></video>
```

## Preload strategy

```html
<!-- Hero (above the fold) — load enough to start instantly -->
<video preload="auto" autoplay loop muted playsinline src="hero.mp4"></video>

<!-- Below the fold — load metadata only; decoder starts on IntersectionObserver -->
<video preload="metadata" loop muted playsinline src="section2.mp4"
       data-autoplay-when-visible></video>

<!-- Don't preload at all if it's a reverse/swap variant rarely used -->
<video preload="none" muted playsinline src="section2-reverse.mp4"></video>
```

## Pause behind open overlays

When a chat panel, modal, or full-screen menu opens over the hero, pause the hero video too:

```js
function setChatOpen(open) {
  document.querySelector('.chat-panel').classList.toggle('open', open);
  heroVideo[open ? 'pause' : 'play']();
}
```

Users won't notice — the panel covers it. GPU saturates 30%+ less.

## Codec and resolution sanity check

- **HEVC (H.265)** decoders are not universal; on hardware without HW HEVC, Chrome falls back to software → severe CPU load. Provide H.264 fallback if you care about non-Mac.
- **4K** for a 1080p viewport is wasted bandwidth and decode work. Serve `<source media>` based on viewport width.
- **Bitrate** above 30 Mbps for hero loops is rarely visually justified — try 15–20 Mbps first.
