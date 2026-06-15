# Dev System для Claude Code · Dev System for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **RU.** Универсальный конвейер «идея → продукт → сопровождение» для работы с Claude Code: один
> хребет процесса (этапы 0–7, закольцованные сопровождением), маршрут по намерению, дисциплина кода
> (стадии 0–6 с ядром-петлёй TDD) и 8 направлений — 6 колонок с роль-агентом (фронт · TS/Node · Python ·
> БД · AI · бэк) + лёгкие marketing · design. Контекст остаётся чистым — грузится только нужное.
>
> **EN.** A universal “idea → product → maintenance” pipeline for Claude Code: one process backbone
> (stages 0–7, looped back by maintenance), intent-based routing, coding discipline (the 0–6 stages with
> a TDD core loop), and 8 directions — 6 columns with a role-agent (frontend · TS/Node · Python · DB · AI ·
> backend) + lightweight marketing · design. The context stays clean — only what’s needed is loaded.

**Навигация · Contents:** [Для людей (RU)](#-для-людей--как-пользоваться) · [Для ИИ: установка (RU)](#-для-ии--установка-ru) · [For humans (EN)](#-for-humans--how-to-use) · [For AI: install (EN)](#-for-ai--installation-en)

---

## Полный путь · The full path

**RU.** Весь конвейер от мысли до отгрузки — и его закольцованность. Процесс идёт по **этапам 0–7**;
этап «Код» разворачивается в **стадии 0–6** «как кодим» с ядром-петлёй TDD (`Написать ⇄ Проверить ⇄
Отладить`); сопровождение возвращает готовый продукт обратно в цикл.

```
┌─▶ ИМПУЛЬС ─▶ ИДЕЯ ─▶ PRD ─▶ ДИЗАЙН (3a · 3b) ─▶ ПЛАН ─▶ КОД ─▶ ДОКИ ─▶ ФИНАЛ ─┐
│                                                                               │
└── СОПРОВОЖДЕНИЕ ◀── ремонт · развитие возвращают в цикл ◀─────────────────────┘

этап КОД ─▶ разворачивается в стадии «как кодим» (0–6):

0 Сориентироваться ─▶ 1 Оформить ─▶ 2 Написать(TDD) ⇄ 3 Проверить ⇄ 4 Отладить ─▶ 5 Ревью ─▶ 6 Завершить
                                    └ ядро-петля: red→green→refactor ┘
```
> 3a — визуальный дизайн (бренд/UI), 3b — технический дизайн + ADR. Малая фича идёт облегчённым путём
> (дизайн/PRD пропускаются); сопровождение — это тот же цикл «план → код» над готовым продуктом.

**EN.** The whole pipeline from thought to ship — and how it loops. The process runs through **stages
0–7**; the “Code” stage unfolds into the **0–6 “how we code” stages** with a TDD core loop (`Write ⇄
Check ⇄ Debug`); maintenance feeds the finished product back into the cycle.

```
┌─▶ IMPULSE ─▶ IDEA ─▶ PRD ─▶ DESIGN (3a · 3b) ─▶ PLAN ─▶ CODE ─▶ DOCS ─▶ FINISH ─┐
│                                                                                 │
└── MAINTENANCE ◀── repair · evolution feed back into the cycle ◀─────────────────┘

stage CODE ─▶ unfolds into the “how we code” stages (0–6):

0 Orient ─▶ 1 Frame ─▶ 2 Write(TDD) ⇄ 3 Check ⇄ 4 Debug ─▶ 5 Review ─▶ 6 Finish
                       └ core loop: red→green→refactor ┘
```
> 3a — visual design (brand/UI), 3b — technical design + ADR. A small feature takes the light path
> (design/PRD skipped); maintenance is the same “plan → code” cycle over a finished product.

---

# Часть I — Для людей · Part I — For humans

## 🇷🇺 Для людей — как пользоваться

### Что это

Система разработки — это **слой над Claude Code**, который превращает «поговорить с ассистентом» в
управляемый инженерный конвейер. Вместо того чтобы каждый раз заново объяснять, как вести проект,
вы один раз ставите систему — и Claude сам идёт по правильному маршруту в зависимости от того, что
вы делаете.

Система состоит из двух частей:

- **«Мозг» (знание)** — этот репозиторий: тонкие маршруты этапов + толстые справочники по темам +
  мета-раздел о том, как систему расширять. Ноль дублей: каждая тема живёт в одном месте.
- **«Руки» (runtime)** — папка `runtime-copy/`, которую вы копируете в `~/.claude/`: 7 роль-агентов,
  правила-привязки направлений, 66 скиллов-инструментов и хук-напоминалка. Их Claude Code подхватывает
  автоматически.

### Зачем это нужно

- **Чистый контекст.** Маршрут тонкий — по намерению вы попадаете в ОДИН нужный справочник, а не
  грузите всё сразу. Ассистент не «захлёбывается».
- **Дисциплина кода.** Общий рельс (слой → контракт → запреты → причина в корне → разделение
  concerns → самопроверка → строгость по ставкам) + гейты «готово» под каждое направление.
- **Один хребет процесса.** Идея → план/PRD → реализация → сопровождение. Без «хватания» случайных
  фреймворков.

### Как этим пользоваться

После установки (раздел «Для ИИ» ниже) просто скажите Claude, что делаете — по намерению:

| Вы говорите… | Система открывает |
|---|---|
| «есть сырая мысль», «стоит ли это делать» | раздел **идея** (`0-ideya/`) |
| «делаем PRD», «нужен дизайн / ADR», «составь план» | раздел **план** (`1-plan/`) |
| «кодим фичу», «реализуем по плану» | раздел **реализация** (`2-realizaciya/`) |
| «сломалось, почини», «как тут устроено», «развиваем продукт» | раздел **сопровождение** (`3-soprovozhdenie/`) |
| «расширить саму систему» (новое направление) | раздел **мета** (`meta/`) |

На этапе кода вы объявляете направление (фронт / TS / Python / БД / AI / бэк; + лёгкие marketing ·
design без роль-агента) — соответствующий роль-агент ведёт стадии 0–6 (Сориентироваться → Оформить →
Написать(TDD) ⇄ Проверить ⇄ Отладить → Ревью → Завершить) и дёргает нужные скиллы как инструменты.

### Структура репозитория

```
.
├── CLAUDE.md            ← оглавление системы (вход по намерению)
├── dev-system.md        ← указатель: копируется в проект, чтобы подключить систему
│
├── 0-ideya/             ← маршрут «идея»
├── 1-plan/              ← маршрут «план» (PRD/дизайн/ADR)
├── 2-realizaciya/       ← маршрут «реализация» (код + доки)
├── 3-soprovozhdenie/    ← маршрут «сопровождение» (ревью/финал + ремонт/развитие)
│       ↑ тонкие маршруты: что делать + куда идти
│
├── spravochniki/        ← КОНТЕНТ по темам (1 источник на тему):
│   ├── idea-kb.md               формирование идеи
│   ├── dev-workflow-kb.md       процесс + шаблоны PRD/ADR
│   ├── saas-stack-kb.md         выбор стека / архитектуры
│   └── dev-coding-process-kb.md спина «как кодим» (стадии 0–6)
│
├── meta/                ← как систему расширять (новая колонка-направление)
│
└── runtime-copy/        ← «руки» для установки в ~/.claude/:
    ├── agents/          7 роль-агентов
    ├── rules/           привязки 8 направлений + дисциплина кода + поведенческие правила
    ├── skills/          66 скиллов-инструментов
    ├── scripts/         хук-диспетчер ленивой загрузки rules + LSP-страж
    └── settings.example.json  шаблон конфига Claude Code
```

> **Три шкалы нумерации (не путать):** *этапы 0–7* — процесс проекта (этап 3 раздвоен на **3a**
> визуальный + **3b** технический дизайн); *стадии 0–6* — как кодим; *фазы роста 1–5* — эволюция стека
> по масштабу. Всегда называйте шкалу словом.

---

## 🤖 Для ИИ — установка (RU)

> Этот раздел — runbook для ассистента (или человека), который ставит систему на новую машину.
> Все шаги выполняются один раз.

### Предпосылки

- **Claude Code** установлен и работает.
- **git**, **bash** (на Windows — Git Bash, идёт с Claude Code), **python 3** (для хука-напоминалки).
- Каталог `~/.claude/` существует (создаётся при первом запуске Claude Code).

### Шаг 1 — клонировать репозиторий

```bash
git clone <URL-этого-репозитория> dev-system
cd dev-system
```

Запомните абсолютный путь к этой папке (например `C:/Users/<you>/dev-system` или
`/home/<you>/dev-system`) — он понадобится на шаге 5.

### Шаг 2 — установить «руки» в `~/.claude/`

Скопируйте компоненты runtime к себе (существующие файлы не затираются вслепую — это `cp` отдельных
наборов):

```bash
mkdir -p ~/.claude/agents ~/.claude/rules ~/.claude/skills ~/.claude/scripts
cp -r runtime-copy/agents/*  ~/.claude/agents/
cp -r runtime-copy/rules/*   ~/.claude/rules/
cp -r runtime-copy/skills/*  ~/.claude/skills/
cp -r runtime-copy/scripts/* ~/.claude/scripts/
```

Claude Code автоматически подхватывает `~/.claude/agents/*.md`, `~/.claude/rules/*.md` и
`~/.claude/skills/<name>/SKILL.md` при старте сессии — ставить отдельно ничего не нужно.

### Шаг 3 — настроить `settings.json`

`runtime-copy/settings.example.json` регистрирует хук-напоминалку, плагины и безопасные `permissions`.

- Если своего `~/.claude/settings.json` ещё нет — скопируйте шаблон:
  ```bash
  cp runtime-copy/settings.example.json ~/.claude/settings.json
  ```
- Если `settings.json` уже есть — **смержите** руками: перенесите блоки `hooks`, `enabledPlugins`,
  `extraKnownMarketplaces` и (при желании) `permissions`. Не затирайте свой конфиг целиком.

> **Хук (кроссплатформенно).** Шаблон вызывает хук как `python3 … || python …` с `"shell": "bash"`
> (macOS/Linux обычно `python3`, Windows — `python`), путь — `$HOME/.claude/scripts/dev_dispatcher.py`.
> Если хук не срабатывает — проверьте `which python3` / `which python` и при необходимости впишите
> абсолютный путь к интерпретатору и/или к скрипту.

> **LSP-страж (опционально, в основном Windows).** Шаблон также регистрирует `SessionStart`-хук
> `lsp_fix_guard.py`. На Windows Claude Code спавнит LSP-серверы (`pyright-lsp` / `typescript-lsp`, шаг 4)
> по голому имени без shell → ENOENT; фикс — запуск через `node`. Официальный маркетплейс авто-обновляется
> и затирает правку, поэтому хук при каждом старте идемпотентно её переприменяет. Перед использованием
> укажите путь к глобальным npm-модулям (env `LSP_FIX_NPM_MODULES`; по умолчанию `%APPDATA%/npm/node_modules`).
> На macOS/Linux обычно не нужен — молча выходит, если чинить нечего.

### Шаг 4 — установить плагины

Плагины НЕ входят в репозиторий (они внешние и обновляются из первоисточника). Установите их командами
Claude Code.

Сначала зарегистрируйте сторонние маркетплейсы:

```text
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin marketplace add anthropics/skills
/plugin marketplace add openai/codex-plugin-cc
```

Затем установите плагины (`claude-plugins-official` встроен — добавлять его не нужно):

```text
/plugin install superpowers@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
/plugin install context7@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install commit-commands@claude-plugins-official
/plugin install pyright-lsp@claude-plugins-official
/plugin install typescript-lsp@claude-plugins-official
/plugin install session-report@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install feature-dev@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
/plugin install vercel@claude-plugins-official
/plugin install code-simplifier@claude-plugins-official
/plugin install chrome-devtools-mcp@claude-plugins-official
/plugin install plugin-dev@claude-plugins-official
/plugin install playground@claude-plugins-official
/plugin install supabase@claude-plugins-official
/plugin install andrej-karpathy-skills@karpathy-skills
/plugin install document-skills@anthropic-agent-skills
/plugin install codex@openai-codex
/reload-plugins
```

> **Важно.** Поля `enabledPlugins` / `extraKnownMarketplaces` в `settings.json` только **активируют**
> уже установленные плагины и регистрируют маркетплейсы — сами они плагины **не скачивают**. Команды
> `/plugin install` выше нужны хотя бы один раз.
>
> **MCP-плагины** (`supabase`, `vercel`, `chrome-devtools-mcp`, `context7`, `codex`) для полной работы
> требуют своих MCP-серверов и/или токенов — настройте их по документации соответствующего плагина.
> Ключи и токены держите в переменных окружения, не в конфиге.

### Шаг 5 — подключить систему к рабочему проекту

В каждом проекте, где хотите пользоваться системой:

1. Скопируйте `dev-system.md` (из корня этого репозитория) в корень вашего проекта.
2. Откройте его и замените плейсхолдер `<ПУТЬ-К-СИСТЕМЕ>` на абсолютный путь из шага 1.
3. Подключите его:
   - если у проекта нет своего `CLAUDE.md` → переименуйте `dev-system.md` в `CLAUDE.md`;
   - если `CLAUDE.md` уже есть → добавьте в него строку `@dev-system.md`.
4. При первом запуске Claude Code один раз подтвердите импорт.

### Шаг 6 — проверить

- Перезапустите Claude Code.
- Команда `/` должна показывать установленные скиллы (`a11y-audit`, `tdd-workflow`, …).
- В рабочем проекте задайте задачу разработки — ассистент должен пойти по маршруту системы и
  предложить нужное направление/роль-агента.

---

# Часть II — For AI · Part II

## 🇬🇧 For humans — how to use

### What this is

This is a **layer on top of Claude Code** that turns “chatting with an assistant” into a managed
engineering pipeline. Instead of re-explaining how to run a project every time, you install the system
once — and Claude follows the right route based on what you are doing.

The system has two parts:

- **The “brain” (knowledge)** — this repository: thin stage-routes + thick topic references + a meta
  section on how to extend the system. Zero duplication: each topic lives in exactly one place.
- **The “hands” (runtime)** — the `runtime-copy/` folder you copy into `~/.claude/`: 7 role-agents,
  direction-binding rules, 66 tool-skills, and a reminder hook. Claude Code picks them up automatically.

### Why it helps

- **Clean context.** The route is thin — by intent you land in the ONE reference you need instead of
  loading everything.
- **Coding discipline.** A shared rail (layer → contract → prohibitions → root cause → separation of
  concerns → self-verify → stakes-based rigor) plus a “done” gate per direction.
- **One process backbone.** Idea → plan/PRD → implementation → maintenance. No framework-grabbing.

### How to use it

After installing (see the “For AI” section), just tell Claude what you’re doing — by intent:

| You say… | The system opens |
|---|---|
| “raw idea”, “is this worth doing” | **idea** route (`0-ideya/`) |
| “let’s write a PRD”, “need a design / ADR”, “make a plan” | **plan** route (`1-plan/`) |
| “let’s code the feature”, “implement the plan” | **implementation** route (`2-realizaciya/`) |
| “it broke, fix it”, “how does this work”, “evolve the product” | **maintenance** route (`3-soprovozhdenie/`) |
| “extend the system itself” (new direction) | **meta** route (`meta/`) |

While coding you declare a direction (frontend / TS / Python / DB / AI / backend; + lightweight
marketing · design without a role-agent) — the matching role-agent drives stages 0–6 (Orient → Frame →
Write(TDD) ⇄ Check ⇄ Debug → Review → Finish) and pulls the right skills as tools.

> Note: the system’s knowledge files are written in Russian (the author’s working language). The method
> is language-agnostic; this README’s English half mirrors the structure so you can navigate and install.

## 🤖 For AI — installation (EN)

> A one-time setup runbook for an assistant (or a human) installing the system on a new machine.

### Prerequisites

- **Claude Code** installed and working.
- **git**, **bash** (on Windows — Git Bash, ships with Claude Code), **python 3** (for the reminder hook).
- The `~/.claude/` directory exists (created on first Claude Code run).

### Step 1 — clone the repository

```bash
git clone <URL-of-this-repo> dev-system
cd dev-system
```

Remember the absolute path to this folder — you’ll need it in Step 5.

### Step 2 — install the “hands” into `~/.claude/`

```bash
mkdir -p ~/.claude/agents ~/.claude/rules ~/.claude/skills ~/.claude/scripts
cp -r runtime-copy/agents/*  ~/.claude/agents/
cp -r runtime-copy/rules/*   ~/.claude/rules/
cp -r runtime-copy/skills/*  ~/.claude/skills/
cp -r runtime-copy/scripts/* ~/.claude/scripts/
```

Claude Code auto-discovers `~/.claude/agents/*.md`, `~/.claude/rules/*.md`, and
`~/.claude/skills/<name>/SKILL.md` on session start — nothing else to register.

### Step 3 — configure `settings.json`

`runtime-copy/settings.example.json` registers the reminder hook, the plugins, and safe `permissions`.

- No existing `~/.claude/settings.json` → copy the template:
  ```bash
  cp runtime-copy/settings.example.json ~/.claude/settings.json
  ```
- Existing `settings.json` → **merge** by hand: bring over `hooks`, `enabledPlugins`,
  `extraKnownMarketplaces`, and optionally `permissions`. Don’t overwrite your whole config.

> **Hook (cross-platform).** The template runs the hook as `python3 … || python …` with `"shell": "bash"`
> (macOS/Linux usually `python3`, Windows `python`), path `$HOME/.claude/scripts/dev_dispatcher.py`.
> If it doesn’t fire, check `which python3` / `which python` and, if needed, use an absolute path to the
> interpreter and/or script.

> **LSP guard (optional, mostly Windows).** The template also registers a `SessionStart` hook
> `lsp_fix_guard.py`. On Windows, Claude Code spawns LSP servers (`pyright-lsp` / `typescript-lsp`, step 4)
> by bare name without a shell → ENOENT; the fix is launching them via `node`. The official marketplace
> auto-updates and overwrites the fix, so the hook idempotently re-applies it on every start. Set the path
> to your global npm modules first (env `LSP_FIX_NPM_MODULES`, default `%APPDATA%/npm/node_modules`).
> On macOS/Linux it’s usually unnecessary — it exits silently when there’s nothing to fix.

### Step 4 — install plugins

Plugins are NOT bundled (they’re external and update from their source). Install them with Claude Code.

Register the third-party marketplaces first:

```text
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin marketplace add anthropics/skills
/plugin marketplace add openai/codex-plugin-cc
```

Then install the plugins (`claude-plugins-official` is built in):

```text
/plugin install superpowers@claude-plugins-official
/plugin install security-guidance@claude-plugins-official
/plugin install context7@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install commit-commands@claude-plugins-official
/plugin install pyright-lsp@claude-plugins-official
/plugin install typescript-lsp@claude-plugins-official
/plugin install session-report@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install feature-dev@claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
/plugin install vercel@claude-plugins-official
/plugin install code-simplifier@claude-plugins-official
/plugin install chrome-devtools-mcp@claude-plugins-official
/plugin install plugin-dev@claude-plugins-official
/plugin install playground@claude-plugins-official
/plugin install supabase@claude-plugins-official
/plugin install andrej-karpathy-skills@karpathy-skills
/plugin install document-skills@anthropic-agent-skills
/plugin install codex@openai-codex
/reload-plugins
```

> **Important.** `enabledPlugins` / `extraKnownMarketplaces` in `settings.json` only **activate**
> already-installed plugins and register marketplaces — they do **not** download anything. The
> `/plugin install` commands above are required at least once.
>
> **MCP plugins** (`supabase`, `vercel`, `chrome-devtools-mcp`, `context7`, `codex`) need their own MCP
> servers and/or tokens for full functionality — configure them per each plugin’s docs. Keep keys and
> tokens in environment variables, never in the config.

### Step 5 — connect the system to a working project

In each project where you want the system:

1. Copy `dev-system.md` (from this repo’s root) into your project root.
2. Replace the `<ПУТЬ-К-СИСТЕМЕ>` (PATH-TO-SYSTEM) placeholder with the absolute path from Step 1.
3. Wire it up:
   - no project `CLAUDE.md` → rename `dev-system.md` to `CLAUDE.md`;
   - existing `CLAUDE.md` → add the line `@dev-system.md`.
4. Approve the import once on first run.

### Step 6 — verify

- Restart Claude Code.
- `/` should list the installed skills (`a11y-audit`, `tdd-workflow`, …).
- In a project, give a development task — the assistant should follow the system route and propose the
  right direction/role-agent.

---

## Автор · Author

**Egor Silantev** — [YouTube](https://www.youtube.com/@SilantevEgor) · [Telegram](https://t.me/AI_Silantev) · [silantev.online](https://silantev.online)

## Лицензия · License

[MIT](LICENSE) © Egor Silantev.

Сторонние скиллы в `runtime-copy/skills/` собраны из открытых источников и остаются под лицензиями
своих авторов — см. [NOTICE.md](NOTICE.md). Плагины не входят в репозиторий и устанавливаются из своих
маркетплейсов. · Third-party skills under `runtime-copy/skills/` are curated from open sources and
remain under their authors’ licenses — see [NOTICE.md](NOTICE.md).
