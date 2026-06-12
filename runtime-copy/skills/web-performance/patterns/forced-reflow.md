---
title: Forced reflow — DOM write then immediate read
impact: HIGH
tags: javascript, dom, layout, reflow, scrolling
---

# Forced reflow

**Anti-pattern**: writing to the DOM, then immediately reading a layout property. The browser cannot serve the read from the cached layout, so it forces a **synchronous** layout recalculation right there.

```js
// ❌ Every interval tick: textContent invalidates layout, then scrollHeight forces reflow
setInterval(() => {
  bubble.textContent += nextChar;
  container.scrollTop = container.scrollHeight;  // forced reflow
}, 25);
```

Chrome DevTools surfaces this as `Forced reflow is a likely performance bottleneck` in the Performance Insights panel. At 25ms interval × long content, you get 40 forced layouts per second.

## Fix: batch the read into requestAnimationFrame

```js
let scrollPending = false;
function scrollToBottom() {
  if (scrollPending) return;
  scrollPending = true;
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;  // coalesces with scheduled layout
    scrollPending = false;
  });
}

setInterval(() => {
  bubble.textContent += nextChar;
  scrollToBottom();  // no immediate read
}, 25);
```

RAF runs **after** style/layout already happen for the frame, so `scrollHeight` is free — no extra reflow.

## Other forms of the same anti-pattern

```js
// ❌ Read between writes
el.style.width = '100px';
const w = el.offsetWidth;        // forced reflow
el.style.height = '200px';

// ✅ All writes, then read once
el.style.width = '100px';
el.style.height = '200px';
const { width } = el.getBoundingClientRect();
```

```js
// ❌ In a loop
items.forEach(item => {
  item.style.width = computed + 'px';
  computed = container.offsetWidth;  // forced reflow per iteration
});

// ✅ Read once, then write all
const w = container.offsetWidth;
items.forEach(item => { item.style.width = w + 'px'; });
```

## Layout-forcing properties to avoid reading after a DOM mutation

Reading any of these forces synchronous layout: `offsetTop`, `offsetLeft`, `offsetWidth`, `offsetHeight`, `clientTop`, `clientLeft`, `clientWidth`, `clientHeight`, `scrollTop`, `scrollLeft`, `scrollWidth`, `scrollHeight`, `getBoundingClientRect()`, `getClientRects()`, `getComputedStyle()`, `innerText`.

Full list: [Paul Irish's gist](https://gist.github.com/paulirish/5d52fb081b3570c81e3a).
