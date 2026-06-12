---
name: coding-standards
description: >
  TypeScript/JavaScript coding standards and patterns — naming, immutability,
  type safety (no `any` at boundaries), async/await discipline, file organization,
  and code-smell detection. Use when starting a TS module, reviewing TS code for
  quality, enforcing conventions, or onboarding contributors.
---

# TypeScript Coding Standards

Universal TypeScript/JavaScript coding standards applicable across all projects.

## When to Activate

- Starting a new TypeScript project or module
- Reviewing code for quality and maintainability
- Refactoring existing code to follow conventions
- Enforcing naming, formatting, or structural consistency
- Setting up linting, formatting, or type-checking rules

## Code Quality Principles

1. **Readability first** — code is read more than written; clear names; self-documenting over comments.
2. **KISS** — simplest solution that works; no premature optimization; understandable > clever.
3. **DRY** — extract common logic; share utilities; avoid copy-paste.
4. **YAGNI** — don't build features before needed; avoid speculative generality.

## Variable & Function Naming

```typescript
// GOOD: descriptive names
const marketSearchQuery = 'election'
const isUserAuthenticated = true

// BAD: unclear names
const q = 'election'
const flag = true
```

```typescript
// GOOD: verb-noun pattern
async function fetchMarketData(marketId: string) {}
function isValidEmail(email: string): boolean {}

// BAD: noun-only / unclear
async function market(id: string) {}
function email(e) {}
```

## Immutability (CRITICAL)

```typescript
// ALWAYS use spread / non-mutating ops
const updatedUser = { ...user, name: 'New Name' }
const updatedArray = [...items, newItem]

// NEVER mutate directly
user.name = 'New Name'  // BAD
items.push(newItem)     // BAD (unless deliberately documented for perf)
```

## Type Safety

```typescript
// GOOD: proper types, discriminated unions for state
interface Market {
  id: string
  name: string
  status: 'active' | 'resolved' | 'closed'
  createdAt: Date
}

function getMarket(id: string): Promise<Market> { /* ... */ }

// BAD: `any` erases all safety
function getMarket(id: any): Promise<any> { /* ... */ }
```

Rule: `any` must never cross a module/layer boundary. Prefer `unknown` + a type guard at the edge, then narrow.

## Async/Await Best Practices

```typescript
// GOOD: parallel when independent
const [users, markets, stats] = await Promise.all([
  fetchUsers(),
  fetchMarkets(),
  fetchStats(),
])

// BAD: sequential when unnecessary
const users = await fetchUsers()
const markets = await fetchMarkets()
const stats = await fetchStats()
```

Never leave a `catch` block empty. Every async call surfaces errors to the caller or handles them — no silent fire-and-forget.

## File Organization

```
src/
├── api/                   # API clients / route handlers
├── services/              # business logic
├── lib/                   # utilities and configs
│   ├── utils/
│   └── constants/
└── types/                 # shared TypeScript types
```

### File Naming

```
services/marketService.ts    # camelCase for modules
lib/formatDate.ts            # camelCase for utilities
types/market.types.ts        # camelCase with .types suffix
```

## Comments & Documentation

```typescript
// GOOD: explain WHY, not WHAT
// Exponential backoff to avoid overwhelming the API during outages
const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)

// BAD: stating the obvious
// Increment counter by 1
count++
```

### JSDoc for Public APIs

```typescript
/**
 * Searches markets using semantic similarity.
 *
 * @param query - Natural language search query
 * @param limit - Maximum number of results (default: 10)
 * @returns Array of markets sorted by similarity score
 * @throws {Error} If the upstream embedding service fails
 */
export async function searchMarkets(query: string, limit = 10): Promise<Market[]> {
  // Implementation
}
```

## Testing Standards

### AAA Pattern

```typescript
test('calculates similarity correctly', () => {
  // Arrange
  const vector1 = [1, 0, 0]
  const vector2 = [0, 1, 0]
  // Act
  const similarity = calculateCosineSimilarity(vector1, vector2)
  // Assert
  expect(similarity).toBe(0)
})
```

### Test Naming

```typescript
// GOOD: descriptive
test('returns empty array when no markets match query', () => {})
test('throws error when API key is missing', () => {})

// BAD: vague
test('works', () => {})
```

## Code Smell Detection

### Long Functions
```typescript
// BAD: function > 50 lines doing everything
// GOOD: split into named steps
function processMarketData(input: RawData) {
  const validated = validateData(input)
  const transformed = transformData(validated)
  return saveData(transformed)
}
```

### Deep Nesting → Early Returns
```typescript
// BAD: 5+ levels of nesting
// GOOD: guard clauses
if (!user) return
if (!user.isAdmin) return
if (!market?.isActive) return
// ... do work
```

### Magic Numbers → Named Constants
```typescript
// BAD
if (retryCount > 3) {}
setTimeout(cb, 500)

// GOOD
const MAX_RETRIES = 3
const DEBOUNCE_DELAY_MS = 500
if (retryCount > MAX_RETRIES) {}
setTimeout(cb, DEBOUNCE_DELAY_MS)
```

**Remember**: Code quality is not negotiable. Clear, maintainable code enables rapid development and confident refactoring.
