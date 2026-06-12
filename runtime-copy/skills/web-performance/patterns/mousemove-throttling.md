---
title: Throttle mousemove via requestAnimationFrame
impact: MEDIUM
tags: javascript, mouse, events, throttling, passive
---

# Throttle mousemove via RAF, not setTimeout

`mousemove` fires 60–200 times per second on a fast pointer. If your handler reads layout (`getBoundingClientRect`) or writes CSS on multiple elements, you'll generate 60–200 layout/paint cycles per second.

## Anti-pattern: synchronous updates on every event

```js
// ❌ Each move triggers N getBoundingClientRect calls (forced layout) + N setProperty calls
window.addEventListener('mousemove', (e) => {
  tiltCards.forEach(card => updateTilt(card, e.clientX, e.clientY));  // N reads + writes
  updateMagnetic(button, e.clientX, e.clientY);
});
```

## Fix: store last position, update in RAF

```js
let mouseX = 0, mouseY = 0;
let pendingUpdate = false;

window.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  if (pendingUpdate) return;
  pendingUpdate = true;
  requestAnimationFrame(() => {
    tiltCards.forEach(card => updateTilt(card, mouseX, mouseY));
    updateMagnetic(button, mouseX, mouseY);
    pendingUpdate = false;
  });
}, { passive: true });  // browser doesn't wait for preventDefault — keeps scroll smooth
```

Max 60 (or refresh-rate) updates per second regardless of pointer speed. Coalesces multiple `mousemove` events that land in the same frame into one update.

## Even better: only update elements within range

`updateTilt` checks distance and short-circuits when the card is far from cursor — but `getBoundingClientRect()` was already called (the costly part). Skip the read for far-from-cursor elements:

```js
const cardBounds = new Map();  // cache rects, refresh on scroll/resize only

function refreshBounds() {
  cardBounds.clear();
  for (const card of tiltCards) cardBounds.set(card, card.getBoundingClientRect());
}
window.addEventListener('scroll', refreshBounds, { passive: true });
window.addEventListener('resize', refreshBounds);
refreshBounds();

function updateTilt(card, mx, my) {
  const r = cardBounds.get(card);
  if (!r) return;
  const cx = r.left + r.width / 2;
  const cy = r.top + r.height / 2;
  // ... no getBoundingClientRect in mousemove hot path
}
```

Trades a small memory cache for zero layout reads during mouse movement.

## Always pass `{ passive: true }` for

- `mousemove`, `mouseover`, `mouseout` (when you don't call `preventDefault`)
- `touchstart`, `touchmove`, `touchend`
- `wheel`, `scroll`

Without `passive: true`, the browser must wait for your handler to potentially call `preventDefault()` before scrolling — adding latency on every event.
