---
name: postgres-patterns
description: PostgreSQL database patterns for query optimization, schema design, indexing, concurrency, security (RLS), and performance diagnostics. Quick reference for index types, data types, EXPLAIN ANALYZE workflow, deadlock prevention, and anti-pattern detection. Use when writing SQL, designing schemas, troubleshooting slow queries, or reviewing database code. Based on Supabase best practices.
---

# PostgreSQL Patterns

Quick reference for PostgreSQL best practices: schema design, indexing, query
optimization, concurrency, and security.

## When to Activate

- Writing SQL queries or migrations
- Designing database schemas
- Troubleshooting slow queries (EXPLAIN ANALYZE)
- Implementing Row Level Security
- Preventing deadlocks / tuning concurrency
- Setting up connection pooling

## Schema Design

### Data Type Quick Reference

| Use Case | Correct Type | Avoid |
|----------|-------------|-------|
| IDs | `bigint` (IDENTITY) or UUIDv7 | `int`, random UUIDv4 as PK |
| Strings | `text` | `varchar(255)` without reason |
| Timestamps | `timestamptz` | `timestamp` (no timezone) |
| Money | `numeric(10,2)` | `float` |
| Flags | `boolean` | `varchar`, `int` |

Rules:
- Use `lowercase_snake_case` identifiers (avoid quoted mixed-case).
- Define constraints explicitly: PK, FK with `ON DELETE`, `NOT NULL`, `CHECK`.
- Index every foreign key — always, no exceptions.

## Indexing

### Index Cheat Sheet

| Query Pattern | Index Type | Example |
|--------------|------------|---------|
| `WHERE col = value` | B-tree (default) | `CREATE INDEX idx ON t (col)` |
| `WHERE col > value` | B-tree | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Composite | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| Time-series ranges | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

**Composite Index Order** — equality columns first, then range columns:
```sql
CREATE INDEX idx ON orders (status, created_at);
-- Works for: WHERE status = 'pending' AND created_at > '2024-01-01'
```

**Covering Index** — avoid a table lookup:
```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- Serves SELECT email, name, created_at from the index alone
```

**Partial Index** — smaller, only relevant rows:
```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- Only active users (soft-delete pattern)
```

## Common Query Patterns

**UPSERT:**
```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

**Cursor Pagination** (O(1) vs OFFSET which is O(n)):
```sql
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;
```

**Queue Processing** (SKIP LOCKED — ~10x throughput for worker patterns):
```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

## Concurrency & Transactions

- **Short transactions** — never hold locks during external API calls.
- **Consistent lock ordering** — always acquire rows in the same order
  (`ORDER BY id FOR UPDATE`) to prevent deadlocks between concurrent transactions.
- **SKIP LOCKED for queues** — lets multiple workers pull disjoint rows without
  blocking each other (see Queue Processing above).
- **Batch inserts** — use multi-row `INSERT` or `COPY`; never loop single-row
  inserts inside a transaction.

## Performance Diagnostics

Run these against a live database to find problems before optimizing blindly.

```bash
psql $DATABASE_URL

# Slowest queries (requires pg_stat_statements)
psql -c "SELECT query, mean_exec_time, calls
         FROM pg_stat_statements
         ORDER BY mean_exec_time DESC LIMIT 10;"

# Largest tables
psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
         FROM pg_stat_user_tables
         ORDER BY pg_total_relation_size(relid) DESC;"

# Index usage (idx_scan = 0 means unused index)
psql -c "SELECT indexrelname, idx_scan, idx_tup_read
         FROM pg_stat_user_indexes
         ORDER BY idx_scan DESC;"
```

### EXPLAIN ANALYZE Workflow

1. Run `EXPLAIN ANALYZE` on complex / slow queries.
2. Look for **Seq Scan** on large tables → the WHERE/JOIN column likely needs an index.
3. Verify composite index column order matches the query (equality first, then range).
4. Watch for N+1 query patterns in application code — batch-fetch instead of querying per row.

### Anti-Pattern Detection Queries

```sql
-- Find unindexed foreign keys
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Check table bloat
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

## Security

**Row Level Security (optimized)** — wrap the auth call in `SELECT` so the planner
evaluates it once per query instead of once per row, and index the policy column:
```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- Wrap in SELECT!

CREATE INDEX idx_orders_user_id ON orders (user_id);  -- Index policy column
```

**Least privilege** — never `GRANT ALL` to application users; revoke public schema:
```sql
REVOKE ALL ON SCHEMA public FROM public;
```

**Parameterized queries only** — never concatenate user input into SQL (injection
risk). Use `$1`-style placeholders or the query builder / ORM binding.

## Configuration Template

```sql
-- Connection limits (adjust for RAM)
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeouts
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- Monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Security defaults
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

## Review Checklist

- [ ] All WHERE/JOIN columns indexed
- [ ] Composite indexes in correct column order (equality, then range)
- [ ] Proper data types (bigint, text, timestamptz, numeric)
- [ ] Foreign keys have indexes
- [ ] No `SELECT *` in production code
- [ ] No OFFSET pagination on large tables (use cursor pagination)
- [ ] No N+1 query patterns
- [ ] EXPLAIN ANALYZE run on complex queries (no unexpected Seq Scans)
- [ ] Transactions kept short; consistent lock ordering
- [ ] RLS enabled on multi-tenant tables, policies use `(SELECT auth.uid())`, policy columns indexed
- [ ] No `GRANT ALL` to application users; public schema revoked
- [ ] All queries parameterized (no string concatenation)

## Related

- Skill: `database-migrations` — safe, reversible schema changes

---

*Based on Supabase Agent Skills (credit: Supabase team) (MIT License). Performance
diagnostics, EXPLAIN workflow, and concurrency principles consolidated from the ECC
`database-reviewer` agent.*
