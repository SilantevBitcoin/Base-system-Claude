# Этапы 1–4 — От идеи до готового плана

> Ты здесь, когда идея ясна (`idea-doc` с `go` или пользователь пришёл с готовой) и нужно довести её
> до **PRD + дизайна + плана**, по которым можно кодить.

**Открой [`../spravochniki/dev-workflow-kb.md`](../spravochniki/dev-workflow-kb.md)** — он ведёт весь
поток. Там: таблица «этап → инструмент → артефакт» (§2), конвенция `docs/` (§3), шаблоны PRD/дизайн/ADR (§4).

Кратко последовательность: брейншторм (раскрытие + черновая техника, стоп перед планом) → PRD
(продуктовый срез) → **3a визуальный дизайн** ([`../spravochniki/design-kb.md`](../spravochniki/design-kb.md),
для UI/носителей — иначе пропуск) → **3b технический дизайн + ADR** (стек из
[`../spravochniki/saas-stack-kb.md`](../spravochniki/saas-stack-kb.md)) → план. Brainstorming в
`writing-plans` напрямую не уходит — сначала PRD/дизайн (для большой фичи). Инструмент на этап — из
таблицы §2.

> ⛔ **Перехват terminal-state (читай ДО запуска `brainstorming`).** `superpowers:brainstorming` в конце
> сам зовёт `writing-plans` — для **большой** фичи НЕ давай ему. Останови на одобренной спеке → доработай
> технику: PRD + дизайн/ADR (этапы 2–3, с готовыми `docs/` проекта как входом) → и только ПОТОМ `writing-plans`
> пишет финальный план поверх. **Одобрение спеки brainstorming ≠ команда писать план.** Для **малой** фичи
> середина пропускается — brainstorming уходит в `writing-plans` как есть.

**Публичный сайт/продукт?** Параллельно с PRD — маркетинг-вход (`~/.claude/rules/marketing.md`, этапы 1–4):
создать `.agents/product-marketing.md` (гейт-контекст), `site-architecture` (+ шаблоны типов сайтов),
`content-strategy`, план событий `analytics` — всё ДО кода.

**Выход:** заполненные `docs/` (`product.md` / `design.md` (для UI/носителей) / `tech-stack.md` / `decisions/` / `knowledge.md`) + план
задач. → Дальше: [`../2-realizaciya/`](../2-realizaciya/README.md)

Назад в оглавление: [`../CLAUDE.md`](../CLAUDE.md)
