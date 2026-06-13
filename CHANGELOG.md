# Changelog

Все заметные изменения публичной копии системы разработки фиксируются здесь.
Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/), версии — [SemVer](https://semver.org/lang/ru/).

## [1.1] — 2026-06-14

### Добавлено
- **Диспетчер ленивой загрузки rules** (`scripts/dev_dispatcher.py` + `dev_routing.json` +
  `claudeMdExcludes` в `settings.example.json`): привязки направлений и дисциплина грузятся в контекст
  по словам в запросе и по стадии (план/код), а не все сразу — постоянный налог на контекст снят.
  Гайд — `meta/dev-dispatcher-guide.md`.
- **Модуль «Маркетинг»** (`rules/marketing.md`): ярус роста публичного сайта (SEO/CRO/контент),
  встроенный в маршрут (этапы идея/план/сопровождение). Скиллы — через install внешнего набора
  `coreyhaines31/marketingskills` (плейсхолдер `<MARKETING>`), не в репозитории.
- **Модуль «Визуальный дизайн»** (`spravochniki/design-kb.md` + `rules/design.md` + шаблон
  Brand & Design Core в `dev-workflow-kb`): этап 3 разделён на **3a** (визуальный дизайн) +
  **3b** (технический дизайн + ADR) — де-факто 9 шагов процесса.
- **LSP impact-анализ в дисциплину кода**: blast-radius до правки символа («кого сломаю» через
  `incomingCalls`/`findReferences`) в `rules/coding-discipline.md`; стадия 0 в `rules/python.md`
  и `rules/typescript.md` использует LSP, иначе Grep.
- **LSP-страж** (`scripts/lsp_fix_guard.py`, `SessionStart`-хук): идемпотентно переприменяет
  node-запуск LSP-серверов в официальном `marketplace.json`, если его затёрло авто-обновлением
  маркетплейса (в основном Windows). Путь к npm-модулям — через env `LSP_FIX_NPM_MODULES`.
- **`MAINTAINING.md`** — руководство по подготовке публичной копии из приватной системы
  (правила адаптации путей/имён, сверка, публикация).

### Изменено
- README: актуализированы install-инструкции — хук переехал на `dev_dispatcher.py`, добавлена
  заметка про LSP-страж, обновлено описание `runtime-copy/scripts/`.

### Исправлено
- README ссылался на устаревший хук `frontend_skill_reminder.py` — заменён на `dev_dispatcher.py`
  (в обеих локалях RU/EN).

## [1.0] — 2026-06-12

### Добавлено
- Первая публикация системы разработки: конвейер «идея → план → реализация → сопровождение»
  (тонкие маршруты этапов + справочники по темам), 6 колонок-направлений
  (фронтенд · TS/Node · Python · БД · AI · бэкенд) — 66 скиллов-инструментов и 7 роль-агентов,
  рельс дисциплины кода, `runtime-copy/` для установки в `~/.claude/`, двуязычный README, MIT + NOTICE.
