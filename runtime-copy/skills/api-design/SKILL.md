---
name: api-design
description: >
  REST API design conventions for TypeScript/Node services — resource naming,
  HTTP method/status-code semantics, success/error response envelopes, offset vs
  cursor pagination, filtering/sorting/sparse-fieldsets, versioning strategy, and
  zod boundary validation. Use when designing or reviewing API endpoints and contracts.
---

# REST API Design Patterns

Conventions for designing consistent, developer-friendly REST APIs in TypeScript/Node.

## When to Activate

- Designing new API endpoints
- Reviewing existing API contracts
- Adding pagination, filtering, or sorting
- Planning an API versioning strategy
- Building public or partner-facing APIs

> Auth depth (JWT/sessions/OAuth/RBAC) and rate-limiting implementation live in the
> dedicated auth and rate-limiting skills — this skill only covers how they appear in
> the API contract (status codes, headers).

## Resource Design

### URL Structure

```
# Resources are nouns, plural, lowercase, kebab-case
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

# Sub-resources for relationships
GET    /api/v1/users/:id/orders

# Actions that don't map to CRUD (use verbs sparingly)
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
```

### Naming Rules

```
# GOOD
/api/v1/team-members          # kebab-case for multi-word resources
/api/v1/orders?status=active  # query params for filtering
/api/v1/users/123/orders      # nested resources for ownership

# BAD
/api/v1/getUsers              # verb in URL
/api/v1/user                  # singular (use plural)
/api/v1/team_members          # snake_case in URLs
```

## HTTP Methods and Status Codes

| Method | Idempotent | Safe | Use For |
|--------|-----------|------|---------|
| GET | Yes | Yes | Retrieve resources |
| POST | No | No | Create resources, trigger actions |
| PUT | Yes | No | Full replacement of a resource |
| PATCH | No* | No | Partial update of a resource |
| DELETE | Yes | No | Remove a resource |

*PATCH can be made idempotent with proper implementation.

### Status Code Reference

```
# Success
200 OK                    — GET, PUT, PATCH (with response body)
201 Created               — POST (include Location header)
204 No Content            — DELETE, PUT (no response body)

# Client Errors
400 Bad Request           — Validation failure, malformed JSON
401 Unauthorized          — Missing or invalid authentication
403 Forbidden             — Authenticated but not authorized
404 Not Found             — Resource doesn't exist
409 Conflict              — Duplicate entry, state conflict
422 Unprocessable Entity  — Semantically invalid (valid JSON, bad data)
429 Too Many Requests     — Rate limit exceeded (include Retry-After)

# Server Errors
500 Internal Server Error — Unexpected failure (never expose details)
502 Bad Gateway           — Upstream service failed
503 Service Unavailable   — Temporary overload, include Retry-After
```

### Common Mistakes

```
# BAD: 200 for everything
{ "status": 200, "success": false, "error": "Not found" }

# GOOD: use HTTP status codes semantically
HTTP/1.1 404 Not Found
{ "error": { "code": "not_found", "message": "User not found" } }

# BAD: 500 for validation errors  → GOOD: 400 or 422 with field-level details
# BAD: 200 for created resources  → GOOD: 201 with Location header
```

## Response Format

### Success / Collection (with pagination)

```jsonc
// single resource
{ "data": { "id": "abc-123", "email": "alice@example.com" } }

// collection
{
  "data": [ { "id": "abc-123", "name": "Alice" } ],
  "meta": { "total": 142, "page": 1, "per_page": 20, "total_pages": 8 },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "next": "/api/v1/users?page=2&per_page=20"
  }
}
```

### Error Response

```jsonc
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Must be a valid email address", "code": "invalid_format" }
    ]
  }
}
```

### Response Envelope (typed)

```typescript
interface ApiResponse<T> {
  data: T
  meta?: PaginationMeta
  links?: PaginationLinks
}

interface ApiError {
  error: { code: string; message: string; details?: FieldError[] }
}
```

## Pagination

### Offset-Based (simple)

```
GET /api/v1/users?page=2&per_page=20
```
**Pros:** easy, supports "jump to page N". **Cons:** slow on large offsets, inconsistent with concurrent inserts.

### Cursor-Based (scalable)

```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20
```
```jsonc
{ "data": [], "meta": { "has_next": true, "next_cursor": "eyJpZCI6MTQzfQ" } }
```
**Pros:** consistent performance regardless of position, stable with concurrent inserts. **Cons:** cannot jump to an arbitrary page; cursor is opaque.

| Use Case | Pagination Type |
|----------|----------------|
| Admin dashboards, small datasets (<10K) | Offset |
| Infinite scroll, feeds, large datasets | Cursor |
| Public APIs | Cursor (default) with offset (optional) |
| Search results (page numbers expected) | Offset |

## Filtering, Sorting, Search

```
# Simple equality
GET /api/v1/orders?status=active&customer_id=abc-123

# Comparison operators (bracket notation)
GET /api/v1/products?price[gte]=10&price[lte]=100

# Multiple values (comma-separated)
GET /api/v1/products?category=electronics,clothing

# Sorting (prefix - for descending; comma for multiple)
GET /api/v1/products?sort=-featured,price,-created_at

# Full-text search
GET /api/v1/products?q=wireless+headphones

# Sparse fieldsets (reduce payload)
GET /api/v1/users?fields=id,name,email
```

## Versioning

### URL Path Versioning (recommended)

```
/api/v1/users
/api/v2/users
```
**Pros:** explicit, easy to route, cacheable. **Cons:** URL changes between versions.

### Strategy

```
1. Start with /api/v1/ — don't version until you need to.
2. Maintain at most 2 active versions (current + previous).
3. Deprecation: announce → add Sunset header → return 410 Gone after sunset.
4. Non-breaking (no new version): adding fields, optional params, new endpoints.
5. Breaking (new version): removing/renaming fields, changing types/URL/auth.
```

## Boundary Validation (zod) — TypeScript

```typescript
import { z } from "zod"

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
})

// Framework-agnostic handler shape
export async function createUser(body: unknown) {
  const parsed = createUserSchema.safeParse(body)

  if (!parsed.success) {
    return {
      status: 422,
      body: {
        error: {
          code: "validation_error",
          message: "Request validation failed",
          details: parsed.error.issues.map(i => ({
            field: i.path.join("."),
            message: i.message,
            code: i.code,
          })),
        },
      },
    }
  }

  const user = await saveUser(parsed.data) // parsed.data is fully typed
  return { status: 201, headers: { Location: `/api/v1/users/${user.id}` }, body: { data: user } }
}
```

## Rate-Limit Headers (contract only)

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# When exceeded
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{ "error": { "code": "rate_limit_exceeded", "message": "Try again in 60 seconds." } }
```

## API Design Checklist

- [ ] Resource URL follows naming conventions (plural, kebab-case, no verbs)
- [ ] Correct HTTP method (GET for reads, POST for creates, etc.)
- [ ] Appropriate status codes (not 200 for everything)
- [ ] Input validated with a schema (zod) at the boundary
- [ ] Error responses follow the standard envelope with codes and messages
- [ ] Pagination implemented for list endpoints (cursor or offset)
- [ ] Authentication required (or explicitly marked public); authorization checked (ownership)
- [ ] Response does not leak internal details (stack traces, SQL errors)
- [ ] Consistent field naming across endpoints (camelCase vs snake_case)
- [ ] Documented (OpenAPI/Swagger spec updated)
