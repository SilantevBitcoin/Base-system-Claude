---
name: postgres-best-practices
description: "Postgres performance, schema, concurrency, and security best practices from Supabase. 30 rules across 8 categories, each with incorrect vs correct SQL and impact rating. Use when writing, reviewing, or optimizing Postgres queries, schemas, indexes, locking, or RLS."
---

# Postgres Best Practices

Performance, schema, concurrency, and security optimization rules for Postgres, maintained by Supabase. Each rule gives a brief rationale, an incorrect SQL example, a correct SQL example, and (where useful) EXPLAIN output or metrics. Rules are split into individual files in `rules/` so you can read only the ones relevant to the task.

## Use this skill when

- Writing SQL queries or designing schemas
- Implementing indexes or query optimization
- Reviewing database performance issues
- Configuring connection pooling or scaling
- Managing concurrency, locking, or transactions
- Working with Row-Level Security (RLS) or privileges

## Rule categories by priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Query Performance | CRITICAL | `query-` |
| 2 | Connection Management | CRITICAL | `conn-` |
| 3 | Security & RLS | CRITICAL | `security-` |
| 4 | Schema Design | HIGH | `schema-` |
| 5 | Concurrency & Locking | MEDIUM-HIGH | `lock-` |
| 6 | Data Access Patterns | MEDIUM | `data-` |
| 7 | Monitoring & Diagnostics | LOW-MEDIUM | `monitor-` |
| 8 | Advanced Features | LOW | `advanced-` |

See `rules/_sections.md` for category descriptions.

## How to use

Read individual rule files for detailed explanations and SQL examples, selecting by the prefix
of the category you need. Examples:

```
rules/query-missing-indexes.md      rules/lock-deadlock-prevention.md
rules/schema-foreign-key-indexes.md rules/security-rls-basics.md
rules/data-n-plus-one.md            rules/monitor-explain-analyze.md
```

Available rules:

- **query-**: missing-indexes, composite-indexes, covering-indexes, partial-indexes, index-types
- **conn-**: pooling, limits, idle-timeout, prepared-statements
- **security-**: rls-basics, rls-performance, privileges
- **schema-**: primary-keys, data-types, foreign-key-indexes, partitioning, lowercase-identifiers
- **lock-**: deadlock-prevention, short-transactions, advisory, skip-locked
- **data-**: n-plus-one, batch-inserts, pagination, upsert
- **monitor-**: explain-analyze, pg-stat-statements, vacuum-analyze
- **advanced-**: jsonb-indexing, full-text-search
