---
title: DOM-mutation timers — print in chunks, not per character
impact: MEDIUM
tags: javascript, setinterval, dom, typing, scroll
---

# Print in chunks, not per character

**Anti-pattern**: typewriter effect that appends one character per `setInterval` tick. For a 1000-character chatbot response, that's 1000 ticks × (style invalidation + layout + paint + scroll). At 25ms intervals that's 25 seconds of continuous DOM thrashing.

```js
// ❌ One character per 25ms tick — 40 forced layouts/sec
setInterval(() => {
  if (!queue.length) return;
  bubble.textContent += queue[0];     // DOM invalidation
  queue = queue.slice(1);             // creates new string each tick → GC pressure
  container.scrollTop = container.scrollHeight;  // forced reflow
}, 25);
```

Three problems compound:
1. 40 ticks/sec × layout/paint cycles
2. `queue.slice(1)` creates a new string every tick → Major GC pressure
3. Synchronous `scrollHeight` read after DOM write → forced reflow ([patterns/forced-reflow.md](forced-reflow.md))

## Fix: chunk size 3–5 chars, interval 30–40ms, RAF-batched scroll

```js
const TYPING_CHUNK = 5;
const TYPING_INTERVAL = 30;

function pumpTyping() {
  if (typingTimer) return;
  typingTimer = setInterval(() => {
    if (!queue.length) {
      clearInterval(typingTimer);
      typingTimer = null;
      return;
    }
    bubble.textContent += queue.slice(0, TYPING_CHUNK);
    queue = queue.slice(TYPING_CHUNK);
    scrollToBottom();  // RAF-batched, no forced reflow
  }, TYPING_INTERVAL);
}
```

5× fewer ticks. Visually identical (humans can't distinguish 40 vs 8 char/sec when content is meaningful prose). 5× fewer reflows, 5× less GC pressure.

## Better: use index pointer instead of string.slice

```js
let queue = '';
let queueIdx = 0;

function append(text) {
  queue += text;
}

setInterval(() => {
  if (queueIdx >= queue.length) return;
  const end = Math.min(queueIdx + TYPING_CHUNK, queue.length);
  bubble.textContent += queue.slice(queueIdx, end);
  queueIdx = end;
  scrollToBottom();
}, TYPING_INTERVAL);
```

No new string allocated per tick — `queue.slice(start, end)` is the same cost as `queue.slice(start)` but doesn't replace the full queue variable each time.

## When typing effect adds value vs hurts

- ✅ Streaming LLM responses where backend itself streams chunks — typing makes latency feel like progress
- ❌ Static text inserted instantly from cache — typing makes the page feel slower than just showing the text
