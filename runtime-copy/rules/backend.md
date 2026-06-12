# Бэкенд — инструменты по стадиям

**ТОНКАЯ delta-колонка** поверх app-колонок (TS/Node + Python) и БД. App-код пишут `typescript-engineer` (TS/Node — **основной стек**: Node-фреймворк, contract-first, in-service resilience, DDD) или `python-engineer` (Python-воркеры/AI: FastAPI/ASGI, async, structured-log+correlation-id); `dba` — данные (схема/SQL/миграции/индексы/БД-транзакции). Эта колонка добавляет ТОЛЬКО распределённое/инфра, чего там нет: messaging · кэш · gateway/rate-limit · auth-паттерны · межсервис · деплой/контейнеры · prod-наблюдаемость. Объявил «бэк» → действуешь по таблице, **НЕ пересобирая** python-engineer/dba.

**Роль-агенты:** написание app-кода — `typescript-engineer` (TS/Node, основной стек) или `python-engineer` (Python-воркеры/AI); данные — `dba`; ML-serving — `mlops`. **`devops-engineer`** (`~/.claude/agents/`) — ИНФРА-дисциплина (как деплоить/наблюдать/масштабировать/секреты/capacity; 6 Moves: rollback-first · observability-before-deploy · blast-radius · IaC · secrets-audit · capacity+idempotency), НЕ пишет бизнес-логику. Отдельного «пишущего» бэк-агента нет (был бы дубль `python-engineer`).

## Привязка

| Стадия | Инструменты |
|---|---|
| 0 Сориентироваться | `devops-engineer` (blast-radius/capacity при инфра-изменении) · прочитать сервис/топологию/деплой |
| 1 Оформить | `saga-orchestration`/`cqrs-implementation` (границы межсервиса, event-driven) · `devops-engineer` (blast-radius/capacity); app-контракт ведёт `typescript-engineer`/`python-engineer` |
| 2 Написать | по ячейке: `django-celery`/`redis-patterns` (очереди/Streams B1) · `redis-patterns` (кэш B2) · `api-rate-limiting` (B3) · `auth-implementation-patterns` (B4 — TS-reference) · `saga-orchestration` (B5 — межсервисный контракт) · `docker-expert`/`deployment-patterns` (контейнер/12-factor B6) · `secrets-management` (секреты B6). App-код — `typescript-engineer`/`python-engineer` (TDD/типы) |
| 3 Проверить | `distributed-tracing` (OTel-инструментация B7) · `slo-implementation` (SLI/SLO/error-budget) · `devops-engineer` (observability-before-deploy) |
| 4 Отладить | `distributed-tracing` (трейс cross-service) · `redis-patterns` (кэш/lock debug) · `devops-engineer` (incident) · `superpowers:systematic-debugging` |
| 5 Ревью | `devops-engineer` (rollback-plan / secrets-audit) · `auth-implementation-patterns` (authz-обзор) · security-гейт ↓ |
| 6 Завершить | `devops-engineer` (Deployment Plan: rollback/blast-radius/observability) · `deployment-patterns` (canary/blue-green) · гейты ↓ |

## Гейты (пробелы рынка — гейт-инструкция, не выдуманный скилл)

### B1 Messaging-инфра (стадии 1/2)
- `django-celery`/`redis-patterns` дают task-queue + Streams. Native-брокеры (Kafka/RabbitMQ/SQS topology, outbox, idempotent consumers, DLQ) — **гейт**: выбор at-least-once/exactly-once явный; DLQ обязателен; consumer идемпотентен; SLI = queue-depth + consumer-lag.

### Безопасность (стадия 5) — High
- Auth: токены/сессии валидируются server-side (PEP); refresh с revoke; RBAC/ABAC на каждом запросе (`auth-implementation-patterns`).
- Секреты: reference-not-embed (env/Vault/manager), никогда в коде/образе; pre-commit secret-scan (`secrets-management`); committed secret = compromised → rotate.
- Rate-limit на edge/gateway (не в app-логике); 429 + Retry-After (`api-rate-limiting`).
- Чувствительное → дополнительно `/security-review`.

### Деплой (стадия 6) — High
- Rollback протестирован ДО деплоя; миграции additive-only/backward-compatible (`devops-engineer` + `dba`); blast-radius откалиброван (canary/blue-green по ставкам).
- Observability ДО деплоя: SLI/SLO названы, дашборд/алерт в PR (`devops-engineer` + `slo-implementation`).

## Примечание по применению
- **Язык-reference:** `auth-implementation-patterns` (TS) и `django-celery` (Python/Celery) — паттерны агностичны, код illustrative: транскрибируй идиомы в стек проекта.
- **Heavy-devops** (IaC/Terraform · GitOps/ArgoCD · k8s · service-mesh · prometheus): дисциплину несёт `devops-engineer` (Moves blast-radius/IaC), не отдельные скиллы. Межсервисный контракт — `saga-orchestration`/`cqrs` (event-driven) + REST через `typescript-engineer`/`python-engineer`.
