---
name: database-design
description: "Database design decision-making: schema design, indexing strategy, ORM selection, database selection, migrations, query optimization. DB-agnostic thinking guide. Use when modeling a data layer or choosing database/ORM."
---

# Database Design

> **Learn to THINK, not copy SQL patterns.**

## Selective Reading Rule

**Read ONLY files relevant to the request.** Check the content map, find what you need.

| File | Description | When to Read |
|------|-------------|--------------|
| `database-selection.md` | PostgreSQL vs Neon vs Turso vs SQLite | Choosing database |
| `orm-selection.md` | Drizzle vs Prisma vs Kysely vs SQLAlchemy | Choosing ORM |
| `schema-design.md` | Normalization, PKs, relationships, FK actions | Designing schema |
| `indexing.md` | Index types, composite indexes | Performance tuning |
| `optimization.md` | N+1, EXPLAIN ANALYZE, optimization priorities | Query optimization |
| `migrations.md` | Safe zero-downtime migrations, serverless DBs | Schema changes |

---

## Core Principle

- ASK the user about database preferences when unclear.
- Choose database/ORM based on CONTEXT, not habit.
- Don't default to PostgreSQL for everything (though it is the standard choice for full relational features).

---

## Decision Checklist

Before designing schema:

- [ ] Asked user about database preference?
- [ ] Chosen database for THIS context?
- [ ] Considered deployment environment?
- [ ] Planned index strategy?
- [ ] Defined relationship types?

---

## Anti-Patterns

- Default to PostgreSQL for simple apps (SQLite may suffice).
- Skip indexing.
- Use `SELECT *` in production.
- Store JSON when structured data is better.
- Ignore N+1 queries.

---

## Validation Script

`scripts/schema_validator.py <project_path>` — read-only static check of Prisma schemas
(PascalCase models, missing `@id`, missing `createdAt`, suggested `@@index` on foreign keys).
Emits JSON; warnings only, never fails. Stdlib only, no network.

```bash
python scripts/schema_validator.py /path/to/project
```
