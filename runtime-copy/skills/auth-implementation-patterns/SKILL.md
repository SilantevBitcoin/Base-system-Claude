---
name: auth-implementation-patterns
description: "Authentication and authorization patterns: JWT vs session strategies, refresh-token flow, OAuth2/OIDC social login, RBAC/permission/ABAC and resource-ownership checks, password security, and auth-endpoint rate limiting. Use PROACTIVELY when adding login/SSO, designing token or session lifecycle, building an authorization model, or reviewing auth code for security gaps."
---

# Authentication & Authorization Implementation Patterns

Build secure auth(N) and auth(Z) systems using standard patterns. **Authentication** answers "who are you" (verify identity, issue credentials); **authorization** answers "what may you do" (permission checks, RBAC/ABAC, resource ownership). Treat them as separate layers.

## Use this skill when

- Implementing user authentication (login, logout, registration).
- Securing REST / GraphQL APIs with tokens or sessions.
- Adding OAuth2 / social login / SSO.
- Designing session management, RBAC, or permission models.
- Debugging or reviewing authentication / authorization code.

## Choosing an auth strategy

| Strategy | When | Trade-off |
| --- | --- | --- |
| **Session-based** | Server can hold session state; first-party web app | Stateful — needs a shared session store (e.g. Redis) to scale horizontally; natural CSRF surface → use SameSite cookies |
| **Token-based (JWT)** | Stateless services, mobile, service-to-service | Self-contained and scales horizontally; can't be revoked before expiry → keep access tokens short-lived (15–30 min) + DB-backed refresh tokens |
| **OAuth2 / OIDC** | Delegated identity, social login, enterprise SSO | Offload credential handling to an IdP; more moving parts (redirects, callback, token exchange) |

## Authorization models

- **RBAC** — assign permissions to roles, roles to users; optionally a role hierarchy (admin ⊇ moderator ⊇ user).
- **Permission-based / ABAC** — check fine-grained permissions (`read:users`, `write:posts`), optionally derived from attributes/tier.
- **Resource ownership** — beyond role/permission, verify the caller actually owns the specific resource (and let admins bypass).

Always enforce authorization **server-side** at the policy enforcement point; client-side checks are UX only.

## Non-negotiable security rules

- **Never store plaintext passwords** — bcrypt/argon2 only (cost ≥ 12). Never log secrets, tokens, or credentials.
- **Short-lived access tokens** (15–30 min) + longer refresh tokens stored **hashed** in the DB, revocable per-token and per-user (logout-all-devices).
- **Secure cookies** — `httpOnly`, `secure`, `sameSite` for session/refresh cookies. Do not put JWTs in `localStorage` (XSS-exfiltrable).
- **Rate-limit auth endpoints** (login/register/refresh) to blunt brute force — see the `api-rate-limiting` skill.
- **Validate all input** (email format, password strength) and rotate JWT/session secrets.
- **CSRF protection** for cookie/session auth; **HTTPS** everywhere; **MFA** where the threat model warrants it.

## Common pitfalls

JWT in `localStorage` · no token expiry · client-side-only auth checks · weak password policy · insecure password-reset (use single-use expiring tokens) · no rate limiting · trusting any client-supplied identity/role claim.

## Implementation playbook

For runnable patterns — JWT generate/verify + auth middleware, the full refresh-token flow (hashed storage, rotate, revoke, revoke-all-devices), session-based auth with a Redis store and hardened cookies, OAuth2 social login with Passport (Google), RBAC with a role hierarchy, permission-based access control, resource-ownership middleware, password security (bcrypt + schema validation), and auth-endpoint rate limiting — see `resources/implementation-playbook.md`.

Works well with: `api-rate-limiting` (throttle auth endpoints + per-user quotas), `distributed-tracing` (correlate auth failures), distributed cache / Redis (session + refresh-token + rate-limit store).
