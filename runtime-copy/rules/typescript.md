# TypeScript / Node — инструменты по стадиям

**ОСНОВНОЙ язык стека.** Колонка = ОБЩАЯ TS-дисциплина + NODE-бэкенд + shared TS. Границы: React/UI/JSX/компоненты/хуки/CSS/a11y/браузер — `frontend-engineer` (садится ПОВЕРХ); Python — `python-engineer`; данные/SQL/миграции — `dba`; инфра/деплой/наблюдаемость — `devops-engineer`; distributed-бэк (auth/rate-limit/saga/cqrs/redis/tracing) — бэк-скиллы (ты потребитель, не автор). Объявил «TS/Node» → действуешь по таблице.

**Роль-агент:** `typescript-engineer` (`~/.claude/agents/`) — зеркало `python-engineer` на TS/Node-стеке (Moves 1–7: слой · контракт · 7-запретов · корень-бага · concerns · self-verify · ставки). Ведёт стадии 0–6, дёргает скиллы как руки; React/UI передаёт `frontend-engineer`.

## Привязка

| Стадия | Инструменты |
|---|---|
| 0 Сориентироваться | `typescript-engineer` (структура/git/конвенции) · semantic code-intel / TS-LSP если есть, иначе Grep |
| 1 Оформить | `typescript-engineer` (слой + контракт + ставки) · `typescript-advanced-types` (типы границ) · `hexagonal-architecture` (ports&adapters) · `api-design` (HTTP-контракт) · `nodejs-best-practices` (выбор фреймворка, think-first) |
| 2 Написать (TDD) | `tdd-workflow` (vitest, тест первым) · `coding-standards`/`typescript-advanced-types` (идиоматика/типы) · `modern-javascript-patterns` (ESM/async) · `error-handling` (Result/typed) · `zod-validation-expert` (валидация на boundary) · Node-фреймворк: `hono` (edge) / `nestjs-patterns` (enterprise) |
| 3 Проверить | gate ↓: `tsc --noEmit` (strict) + `eslint`/`biome` + `vitest` зелёные · `typescript-expert` (tsc-диагностика / perf типов) |
| 4 Отладить | `superpowers:systematic-debugging` · `modern-javascript-patterns` (async/event-loop races) · `typescript-engineer` (root-cause Move 4) · профайл `node --cpu-prof`/`clinic` |
| 5 Ревью | `typescript-engineer` (self-verify 6-pass / refusal-conditions) · `coding-standards` · security-гейт ↓ |
| 6 Завершить | `typescript-engineer` (Change Report) · `bun-runtime` / сборка-гейт ↓ |

## Гейты (пишем сами — рынок dedicated-скилла не дал; зеркало ruff/mypy у Python)

### Тип + линт + тесты (стадии 3 / 6) — критерий «готово»
- `tsc --noEmit` под `strict: true` (+ `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `verbatimModuleSyntax`) → ноль ошибок типов. `any` / непроверенный `as` / `@ts-ignore` НЕ пересекают границу слоя.
- `eslint .` (flat config) или `biome check .` → ноль ошибок (`@typescript-eslint/no-explicit-any`, `no-floating-promises` строго).
- `vitest run` (+ coverage по критичности) → зелёные; type-тесты `expectTypeOf` где нетривиальный тип.
- **Гейт «готово»: `tsc --noEmit` + `eslint`/`biome` + `vitest` зелёные.**

### Упаковка / ESM (стадия 2) — T7 / T2
- Пакеты через `pnpm` (lockfile `pnpm-lock.yaml` committed; workspaces для моно). `bun` — допустимая альтернатива при коммите проекта на неё (`bun-runtime`).
- ESM по умолчанию (`"type":"module"`, `.js`-расширения в относит. импортах под NodeNext, `exports`-map в публикуемых пакетах); ESM↔CJS dual-package hazard учтён до смешивания.

### Безопасность (стадия 5) — High
- Валидация ВСЕГО внешнего ввода через `zod` на границе (HTTP body/query, env, внешние API, payload очередей); тип из `z.infer`, не дублировать руками.
- Секреты только из env, не в коде; auth/authz — бэк-скилл `auth-implementation-patterns`. Чувствительное (деньги/auth/данные) → `/security-review`.

### Сборка / бандлинг (стадии 2/6) — T10
- Библиотека → `tsup` (esbuild + `.d.ts`); приложение → бандлер фреймворка; `tsc --noEmit` отдельно как type-gate; `bun build` где проект на Bun.
