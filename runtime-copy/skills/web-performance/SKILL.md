---
name: web-performance
description: Web performance best practices for writing or reviewing frontend code (vanilla JS, React, CSS, HTML). Use when editing landing pages, chat widgets, scroll or mouse animations, video backgrounds, SSE/EventSource clients, parallax effects, typing effects, or any DOM-update loop on an interval. Prevents forced reflow, layout thrashing, never-settling RAF loops, unbounded EventSource reconnects, GPU compositing stress from multiple videos or CSS variables updated every frame.
---

# Web performance — runtime guidelines

This skill prevents the most common runtime perf footguns when writing frontend code: forced reflow, layout thrashing, infinite RAF loops, EventSource spam-reconnect, GPU compositing overload, and DOM-mutation timers. Triggers on landing pages, chat widgets, video backgrounds, scroll/mouse interactions, SSE clients.

Each numbered rule is a discrete pattern. Apply the relevant ones before writing code, not after. See `patterns/` for deep-dive examples on each.

## Core rules

1. **Never read layout immediately after writing DOM.** `el.scrollTop = el.scrollHeight` right after `textContent +=` is a forced reflow. Batch the read into `requestAnimationFrame` so it coalesces with the already-scheduled layout. → [patterns/forced-reflow.md](patterns/forced-reflow.md)

2. **Stop RAF loops when state is settled.** Naive LERP (`current += (target - current) * 0.06`) never reaches target — RAF tick runs forever even when nothing visually moves. Add an epsilon check + `tickRunning` flag, restart on input. → [patterns/raf-loop-stop-when-settled.md](patterns/raf-loop-stop-when-settled.md)

3. **EventSource needs explicit backoff on error.** Default browser auto-reconnect fires only after a connection has been OPEN. On `ERR_CONNECTION_REFUSED` (server down) Chrome retries **immediately**, spamming hundreds of failed requests per second until the tab freezes. Always close + retry with exponential backoff in `onerror`. → [patterns/eventsource-backoff.md](patterns/eventsource-backoff.md)

4. **DOM-mutation timers — print in chunks, not per character.** A `setInterval(fn, 25)` writing one character + scrolling = 40 forced layouts/sec for the entire response. Print 3–5 chars per tick at 30ms — visually identical, 5× less work. → [patterns/dom-batched-typing.md](patterns/dom-batched-typing.md)

5. **Don't autoplay multiple `<video>` elements.** Each playing video runs its own decode pipeline; 4K HEVC × N = GPU saturation. Pause off-screen videos via `IntersectionObserver`, use `preload="metadata"` for non-hero clips, and `playsinline` for mobile. → [patterns/heavy-video-pause.md](patterns/heavy-video-pause.md)

6. **Throttle mousemove via RAF.** Raw `mousemove` fires 60–200×/sec. If your handler updates CSS on many elements (`.forEach(updateTilt)`), batch into one RAF callback per frame instead. Use `{ passive: true }`. → [patterns/mousemove-throttling.md](patterns/mousemove-throttling.md)

7. **Use CSS `transform` + `opacity` for animations, not `width`/`top`/`left`.** Only `transform` and `opacity` are compositor-only — others trigger layout + paint. For continuous animations promote layer with `will-change: transform` but **remove it** after the animation ends (otherwise the layer stays uploaded forever).

8. **Passive event listeners on touch/scroll/wheel.** `addEventListener('scroll', fn, { passive: true })` — browser doesn't wait for `preventDefault`, scrolling stays smooth.

9. **One CSS animation per visual group, not per child.** Three `.dot` keyframes with stagger via `animation-delay` create 3 parallel compositing requests. Prefer a single animation on the wrapper (`::before` / pseudo-element) when possible.

10. **Don't write to `style.setProperty('--x', ...)` every frame for static targets.** CSS variables invalidate compositing on every change. If the LERP delta is < 0.05px (subpixel), skip the write.

## Verification

After writing perf-sensitive code, instruct the user to verify:

1. **Chrome DevTools → Performance → ⏺ Record → reproduce → ⏹ Stop**
2. **Bottom-Up sorted by Total Time** — top entries should NOT be: `Forced reflow`, `Timer fired`, `Recalculate Style` > 15%, or your code's `Function call` > 20%.
3. **Insights panel → Forced reflow** — should be empty. If Chrome lists `Forced reflow is a likely perf bottleneck`, find and fix the DOM-write-then-read.
4. **GPU process / VideoFrameCompositor** in Main thread — heavy continuous activity = too many playing videos.

If [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) is installed, run an automated trace instead of asking the user.

## What not to do

- **Don't use `setInterval` for animation.** Use `requestAnimationFrame` — it skips ticks when tab is hidden and syncs to refresh rate.
- **Don't measure perf in DevTools Performance mode without disabling Profiling overhead** — the overhead itself shows up as 10–15%.
- **Don't add `backdrop-filter: blur()` over a playing video** — combined compositing cost is brutal on integrated GPUs.
- **Don't trust `landing.js?v=N` cache busting** without verifying in Network panel — Chrome aggressively caches; require user to enable "Disable cache" + hard reload (Ctrl+Shift+R).
- **Don't add fallback retry without bound.** Backoff must cap (e.g. 30s), and after N failed reconnects drop stale state (e.g. `sessionStorage.removeItem('chat_id')`).

## References

- [Paul Irish — What forces layout/reflow](https://gist.github.com/paulirish/5d52fb081b3570c81e3a) — definitive list of layout-forcing properties
- [CSS Triggers](https://csstriggers.com/) — which property changes invalidate layout/paint/composite
- [Vercel react-best-practices](https://github.com/vercel-labs/agent-skills) — React-specific batching rules
- [Addy Osmani web-quality-skills](https://github.com/addyosmani/web-quality-skills) — framework-agnostic perf checklist
- [Web Vitals](https://web.dev/vitals/) — LCP, INP, CLS targets

Project-specific memories may override or extend these — always check project memory before applying.
