---
title: EventSource — explicit backoff on error
impact: HIGH
tags: javascript, eventsource, sse, networking, reconnect
---

# EventSource needs explicit backoff

**Misconception**: `EventSource` auto-reconnects with a 3-second delay. That's only true **after** a successful initial OPEN. On `ERR_CONNECTION_REFUSED` (server not running) or `ERR_CONNECTION_RESET` (server immediately closed), the browser retries **with no delay** — spamming hundreds of failed requests per second until the tab becomes unresponsive.

The bug is invisible until the server goes down: client looks fine, then suddenly Chrome freezes when an old `chat_id` in `sessionStorage` triggers an `openSse()` call against a dead endpoint.

```js
// ❌ Looks correct, but the comment is a lie when server is down
function openSse() {
  eventSource = new EventSource(`/events?chat_id=${chatId}`);
  eventSource.onmessage = handleMessage;
  eventSource.onerror = () => { /* EventSource auto-reconnects */ };
}
```

## Fix: close on error + exponential backoff

```js
let sseRetryMs = 1000;
let sseRetryTimer = null;

function openSse() {
  if (sseRetryTimer) { clearTimeout(sseRetryTimer); sseRetryTimer = null; }
  if (eventSource) eventSource.close();
  eventSource = new EventSource(`/events?chat_id=${chatId}`);

  eventSource.onopen = () => { sseRetryMs = 1000; };  // reset on success
  eventSource.onmessage = handleMessage;
  eventSource.onerror = () => {
    if (eventSource) { eventSource.close(); eventSource = null; }
    sseRetryTimer = setTimeout(openSse, sseRetryMs);
    sseRetryMs = Math.min(sseRetryMs * 2, 30000);  // cap at 30s
  };
}
```

Behavior:
- First failure → retry in 1s
- Continued failures → 2s, 4s, 8s, 16s, 30s, 30s, ...
- On success → reset to 1s for next outage

## Additional safety

- **Drop stale state after N failures**. If `sseRetryMs >= 30000` after, say, 5 retries, remove `chat_id` from `sessionStorage` so a page reload starts fresh instead of hammering a dead endpoint forever.
- **Don't open SSE on page load just because `sessionStorage` has a `chat_id`.** Verify the channel is responsive first (cheap `HEAD` or `/health` ping).
- **Show a UI signal** when reconnecting. Silent infinite retry confuses users.

## Same pattern applies to

- WebSocket reconnection logic
- `fetch` with retry (use AbortController + bounded retries)
- Long-poll loops
