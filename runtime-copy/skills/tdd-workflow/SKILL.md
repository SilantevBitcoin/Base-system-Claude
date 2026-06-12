---
name: tdd-workflow
description: >
  Test-driven development workflow for TypeScript / Node with Vitest or Jest —
  red-green-refactor cycle, unit and integration test patterns, mocking external
  services, coverage thresholds, and common testing mistakes. Use when writing new
  features, fixing bugs, refactoring, or adding API endpoints in a TS/Node codebase.
---

# Test-Driven Development Workflow (TypeScript / Node)

Ensures TS/Node code development follows TDD with comprehensive test coverage. Runner-agnostic across **Vitest** and **Jest** (near-identical APIs).

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code
- Adding API endpoints or service methods

## Core Principles

1. **Tests BEFORE code** — write the test first, then implement to make it pass.
2. **Coverage** — target 80%+ (statements/branches/functions/lines); cover edge cases, error scenarios, boundaries.
3. **Test types**
   - **Unit** — pure functions, helpers, single modules in isolation.
   - **Integration** — API route handlers, DB operations, service interactions, external API calls (with mocks/fakes).

## TDD Cycle (Red → Green → Refactor)

### Step 1: Write the test cases (they should fail)

```typescript
import { describe, it, expect } from 'vitest' // or 'jest'

describe('Semantic Search', () => {
  it('returns relevant markets for query', async () => { /* ... */ })
  it('handles empty query gracefully', async () => { /* ... */ })
  it('falls back to substring search when index unavailable', async () => { /* ... */ })
  it('sorts results by similarity score', async () => { /* ... */ })
})
```

```bash
npm test        # tests fail — nothing implemented yet
```

### Step 2: Implement minimal code to pass

```typescript
export async function searchMarkets(query: string): Promise<Market[]> {
  // minimal implementation guided by the failing tests
}
```

### Step 3: Run tests again (green)

```bash
npm test        # tests now pass
```

### Step 4: Refactor while green

Remove duplication, improve naming, optimize — tests stay green.

### Step 5: Verify coverage

```bash
npm run test:coverage   # verify 80%+ threshold met
```

## Unit Test Pattern (AAA)

```typescript
import { describe, it, expect } from 'vitest'
import { calculateCosineSimilarity } from './similarity'

describe('calculateCosineSimilarity', () => {
  it('returns 0 for orthogonal vectors', () => {
    // Arrange
    const a = [1, 0, 0]
    const b = [0, 1, 0]
    // Act
    const result = calculateCosineSimilarity(a, b)
    // Assert
    expect(result).toBe(0)
  })
})
```

## API Integration Test Pattern

Test the handler as a unit of behavior — assert status + response shape, not internals.

```typescript
import { describe, it, expect } from 'vitest'
import { handleGetMarkets } from './markets.handler'

describe('GET /api/markets', () => {
  it('returns markets successfully', async () => {
    const res = await handleGetMarkets({ query: {} })
    expect(res.status).toBe(200)
    expect(res.body.success).toBe(true)
    expect(Array.isArray(res.body.data)).toBe(true)
  })

  it('returns 400 for invalid query params', async () => {
    const res = await handleGetMarkets({ query: { limit: 'invalid' } })
    expect(res.status).toBe(400)
  })
})
```

## Mocking External Services

```typescript
import { vi } from 'vitest' // Jest: use jest.fn() / jest.mock()

// Mock a DB client module
vi.mock('@/lib/db', () => ({
  db: {
    markets: {
      findMany: vi.fn(async () => [{ id: '1', name: 'Test Market' }]),
    },
  },
}))

// Mock an external API client
vi.mock('@/lib/embeddings', () => ({
  generateEmbedding: vi.fn(async () => new Array(1536).fill(0.1)),
}))
```

## Coverage Thresholds

```jsonc
// vitest.config.ts → test.coverage.thresholds, OR jest config:
{
  "coverageThreshold": {
    "global": { "branches": 80, "functions": 80, "lines": 80, "statements": 80 }
  }
}
```

## Common Testing Mistakes

| Wrong | Correct |
|---|---|
| Testing internal state: `expect(svc._cache).toBe(...)` | Test observable behavior / return value |
| No isolation — tests depend on each other | Each test sets up its own data/fixtures |
| Asserting many unrelated things in one test | One behavior per test |
| Mocking everything, including the unit under test | Mock only external dependencies |

```typescript
// WRONG: tests depend on shared mutable state
test('creates user', () => { /* mutates global */ })
test('updates same user', () => { /* relies on previous test */ })

// CORRECT: independent
test('creates user', () => { const u = makeTestUser(); /* ... */ })
test('updates user', () => { const u = makeTestUser(); /* ... */ })
```

## Continuous Testing

```bash
npm test -- --watch          # re-run on file change during dev
npm test && npm run lint     # pre-commit gate
```

```yaml
# CI (GitHub Actions)
- name: Run Tests
  run: npm test -- --coverage
```

## Best Practices

1. Write tests first (TDD).
2. Arrange-Act-Assert structure.
3. Descriptive test names that state the expected behavior.
4. Mock external dependencies; isolate the unit.
5. Test edge cases (null, undefined, empty, large) and error paths, not just happy paths.
6. Keep unit tests fast (< 50ms each); clean up side effects.
7. Review coverage reports to find gaps.

---

**Remember**: Tests are the safety net that enables confident refactoring and rapid development. (UI component tests and browser E2E live in the frontend testing skill, not here.)
