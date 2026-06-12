---
title: RAF loop — stop when settled
impact: HIGH
tags: javascript, requestAnimationFrame, parallax, lerp, mouse
---

# RAF loop must stop when there's nothing to animate

**Anti-pattern**: LERP-based easing inside `requestAnimationFrame` that never reaches the target mathematically. RAF keeps ticking forever — even when the mouse is stationary and visually nothing moves.

```js
// ❌ Runs 60–120 times per second forever
function tick() {
  stageX += (targetX - stageX) * 0.06;   // asymptotic — never exactly reaches targetX
  stageY += (targetY - stageY) * 0.06;
  stage.style.setProperty('--stage-x', stageX + 'px');  // triggers compositing
  stage.style.setProperty('--stage-y', stageY + 'px');
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
```

Each tick: 2× `setProperty` → compositor invalidation → recompositing over whatever's behind (often 4K video) → GPU/CPU consumption on a perfectly idle page.

## Fix: stop when delta is below epsilon, restart on input

```js
let tickRunning = false;
const EPSILON = 0.05;  // subpixel — invisible

function startTick() {
  if (tickRunning) return;
  tickRunning = true;
  requestAnimationFrame(tick);
}

function tick() {
  const dx = targetX - stageX;
  const dy = targetY - stageY;
  if (Math.abs(dx) < EPSILON && Math.abs(dy) < EPSILON) {
    tickRunning = false;
    return;  // stop the loop
  }
  stageX += dx * 0.06;
  stageY += dy * 0.06;
  stage.style.setProperty('--stage-x', stageX + 'px');
  stage.style.setProperty('--stage-y', stageY + 'px');
  requestAnimationFrame(tick);
}

window.addEventListener('mousemove', (e) => {
  targetX = ...; targetY = ...;
  startTick();  // resume only when there's something to animate
}, { passive: true });
```

When the mouse stops, RAF settles within ~30 frames and goes quiet. When the user moves the mouse again, `startTick()` resumes. The visual effect is identical; idle CPU goes from continuous to zero.

## Same pattern applies to

- Smooth scroll-to-position animations
- Tilt/magnetic mouse effects
- Marquee or counter animations that converge
- Any `lerp(a, b, t)` based easing
