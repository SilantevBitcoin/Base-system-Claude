# БД — инструменты по стадиям

Привязка инструментов к стадиям спины (`dev-coding-process-kb.md`) для работы с БД (схема / миграции / запросы / индексы / транзакции). Объявил направление «БД» → действуешь по этой таблице. Движок по умолчанию — **PostgreSQL**; скиллы PG-фокусные, принципы агностичны (переносятся на MySQL/SQLite/Mongo).

**Роль-агент:** `dba` (`~/.claude/agents/`) ведёт стадии 0–6 и дёргает скиллы ниже как руки.

## Привязка

| Стадия | Инструменты |
|---|---|
| 0 Сориентироваться | `dba` (определить движок+версию, прочитать схему/миграции/конвенции) · semantic code-intel если подключён, иначе Grep |
| 1 Оформить | `database-design` (моделирование, выбор БД/ORM, decision-trees) · `postgresql` (типы/ключи/constraints PG) · `postgres-best-practices` (планирование индексов/ограничений) · `dba` Moves 5/2/3/4 (3NF, классификация миграции, индекс, граница транзакции) |
| 2 Написать | `database-migrations` (versioned/reversible миграция + rollback, expand-migrate-contract, batched backfill) · `sql-optimization-patterns` (запросы) · `postgres-best-practices` (lock/tx правила) · `dba` Move 4 (транзакции) |
| 3 Проверить | `dba` Move 1 (`EXPLAIN ANALYZE` на prod-sized данных — артефакт) · `sql-optimization-patterns` · `postgres-patterns` (diagnostic SQL) · гейт тест-БД ↓ |
| 4 Отладить | `postgres-patterns` (диагностические запросы: bloat / unindexed-FK / slow-query / index-usage) · `sql-optimization-patterns` · `superpowers:systematic-debugging` (app-измерение) · `python-performance-optimization` (app-перф) |
| 5 Ревью | `postgres-best-practices` (incorrect-vs-correct правила: index/lock/RLS/privileges) · `dba` `<refusal-conditions>` · security-гейт ↓ |
| 6 Завершить | `dba` output (Migration / Query-Plan report) · гейты ↓ как gate |

## Гейты (пишем сами — рынок БД-скиллом не закрыл; по методичке §1.5 — гейт-инструкция, не выдуманный скилл)

### C6 Тестирование БД (стадии 3 / 6)
- Тесты БД-кода идут на **реальном движке** (testcontainers / `pytest-postgresql` / Docker-PG), не на моке.
- **Транзакционная фикстура с rollback** на каждый тест — состояние не течёт между тестами.
- Миграции прогоняются в setup тестовой БД; seed/factory детерминированы.
- Слой поверх `python-testing` (pytest-механика). Гейт «готово»: БД-тесты на реальном движке, откатываются, изолированы.

### C7 Бэкап/восстановление + PII (стадии 5 / 6) — High
- Бэкап-стратегия названа (`pg_dump` / PITR) с RPO/RTO; **restore протестирован** («untested backup = no backup»).
- PII-поля классифицированы: шифрование at-rest/in-transit, маскирование/анонимизация в не-прод.
- Секреты БД только из env (`DATABASE_URL`), никогда в коде.

### C3 ORM-уровень (стадии 2 / 5)
- ORM-запросы без N+1 (eager / selectin / batch load); явный список колонок, не `SELECT *` через ORM.
- Параметризация (нет конкатенации ввода); граница сессии/транзакции явная.
- Слой поверх `python-engineer` (типы на границах, нет голых `dict`/`Any`).

### Безопасность (стадия 5) — High
- Параметризованные запросы (`$1`/`?`/`%s`); динамические идентификаторы — только через allow-list.
- RLS / least-privilege где мультитенантность; нет хардкод-секретов.
- Деструктивный DDL на проде (`DROP`/`TRUNCATE`/`DELETE` без `WHERE`) — только при свежем протестированном бэкапе + 2 аппрува + окно (см. `dba` `<refusal-conditions>`).
- Чувствительное (деньги / auth / PII) → дополнительно `/security-review`.

## Примечание по применению
- **vector / pgvector:** `vector-index-tuning` закреплён за AI-колонкой (`rules/ai.md`); базовый `pgvector` как тип — в `postgresql`.
- **Не-PG движки** (MySQL/SQLite/Mongo): `dba` engine-agnostic, скиллы PG-фокусные — переноси принципы на синтаксис движка.