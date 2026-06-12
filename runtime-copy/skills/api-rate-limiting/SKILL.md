---
name: api-rate-limiting
description: "Distributed API rate limiting and throttling: per-IP and per-user limits backed by a shared store (Redis), tiered quotas, sliding/fixed windows, 429 + Retry-After + X-RateLimit headers, and stricter limits on auth and expensive endpoints. Use PROACTIVELY when protecting an API from brute force / abuse / DDoS, enforcing per-tenant quotas, or adding rate limiting at a gateway or service edge."
---

# API Rate Limiting & Throttling

Rate limiting caps how many requests a client may make in a time window. It protects against brute-force attacks, DDoS, runaway clients, and noisy-neighbor abuse, and enforces fair usage / per-tier quotas. In any multi-instance deployment the counter **must live in a shared store** (Redis), not in process memory — otherwise each instance enforces its own partial limit and the real limit is `N × max`.

## Use this skill when

- Protecting endpoints from brute force, credential stuffing, or DDoS.
- Enforcing per-user / per-tenant request quotas (e.g. free vs pro vs enterprise tiers).
- Adding throttling at an API gateway or service edge.
- Stricter limits on sensitive endpoints (login, register, password-reset) or expensive operations (report generation, exports).

## Algorithms (pick per need)

| Algorithm | Behavior | Use |
| --- | --- | --- |
| **Fixed window** | Count per discrete window (e.g. per minute) | Simplest; allows bursts at window edges |
| **Sliding window** | Count over a rolling interval | Smoother; avoids the edge-burst of fixed windows |
| **Token bucket** | Tokens refill at a steady rate; each request spends one; bucket allows a burst up to capacity | Best when you want a steady rate but tolerate short bursts |
| **Leaky bucket** | Requests drain at a fixed rate; overflow is rejected | Smooths output to a constant rate |

The `INCR` + `EXPIRE` pattern below is a fixed/sliding window in Redis; a token bucket is implemented with a stored token count + last-refill timestamp (often via a Lua script for atomicity).

## Response contract

On limit exceeded, return **HTTP 429 Too Many Requests** with a `Retry-After` (seconds) and rate-limit headers so well-behaved clients can self-throttle:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1640000000
```

## Pattern 1: Distributed limit with a Redis store

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const Redis = require('ioredis');

const redis = new Redis({ host: process.env.REDIS_HOST, port: process.env.REDIS_PORT });

// General API limit — shared across all instances via Redis
const apiLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:api:' }),
  windowMs: 15 * 60 * 1000,            // 15 minutes
  max: 100,                            // 100 requests / window
  message: { error: 'Too many requests, please try again later', retryAfter: 900 },
  standardHeaders: true,               // emit X-RateLimit-* headers
  legacyHeaders: false,
  keyGenerator: (req) => req.user?.userId || req.ip,  // per-user when authed, else per-IP
});

// Strict limit for auth endpoints — blunt brute force
const authLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:auth:' }),
  windowMs: 15 * 60 * 1000,
  max: 5,                              // 5 attempts / 15 min
  skipSuccessfulRequests: true,        // only count failures
  message: { error: 'Too many login attempts, please try again later', retryAfter: 900 },
});

// Tight limit for expensive operations
const expensiveLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,           // 1 hour
  max: 10,
  message: { error: 'Rate limit exceeded for this operation' },
});

app.use('/api/', apiLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
app.post('/api/reports/generate', authenticateToken, expensiveLimiter, async (req, res) => {
  // expensive work
});
```

## Pattern 2: Tiered per-user quota (Redis INCR + EXPIRE)

```javascript
// Different limits by user tier, counted atomically in Redis
function createTieredRateLimiter() {
  const limits = {
    free:       { windowMs: 60 * 60 * 1000, max: 100 },
    pro:        { windowMs: 60 * 60 * 1000, max: 1000 },
    enterprise: { windowMs: 60 * 60 * 1000, max: 10000 },
  };

  return async (req, res, next) => {
    const user = req.user;
    const tier = user?.tier || 'free';
    const limit = limits[tier];

    const key = `rl:user:${user.userId}`;
    const current = await redis.incr(key);
    if (current === 1) {
      await redis.expire(key, limit.windowMs / 1000);  // set TTL on first hit of the window
    }

    if (current > limit.max) {
      return res.status(429).json({
        error: 'Rate limit exceeded',
        limit: limit.max,
        remaining: 0,
        reset: await redis.ttl(key),
      });
    }

    res.set({
      'X-RateLimit-Limit': limit.max,
      'X-RateLimit-Remaining': limit.max - current,
      'X-RateLimit-Reset': await redis.ttl(key),
    });
    next();
  };
}

app.use('/api/', authenticateToken, createTieredRateLimiter());
```

> Note: `INCR` then `EXPIRE` as two calls has a tiny race (a crash between them leaves a key without TTL). For strict correctness use a Lua script (or `SET key 1 EX <ttl> NX` then `INCR`) so the window TTL is set atomically with the first increment.

## Defense-in-depth

Rate limiting is one layer. Pair it with security response headers (Helmet/equivalent): Content-Security-Policy, `frameguard: deny` (clickjacking), `noSniff`, HSTS, and hide `X-Powered-By`. For true volumetric DDoS, terminate at an edge/CDN/WAF (Cloudflare, AWS WAF) before traffic reaches the app — app-level limiting protects logic and fairness, not raw bandwidth.

## Best practices

- Keep the counter in a **shared store** for any horizontally-scaled service.
- Key by user/tenant when authenticated, fall back to IP otherwise; beware shared NAT/proxy IPs (use `X-Forwarded-For` carefully and only behind a trusted proxy).
- Always return `429` + `Retry-After` + `X-RateLimit-*` so clients can back off.
- Set the **tightest** limits on auth and expensive/destructive endpoints.
- Make the limit configurable per environment; monitor 429 rate as a signal of abuse or a too-tight limit.

Works well with: `auth-implementation-patterns` (throttle login/refresh), distributed cache / Redis (the shared counter store), `prometheus-configuration` (alert on 429 spikes).
