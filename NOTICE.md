# NOTICE — атрибуция и лицензии · attribution & licenses

## RU

Репозиторий распространяется под [MIT](LICENSE). Лицензия MIT покрывает **оригинальную часть системы**,
созданную автором:

- знание и маршруты: `CLAUDE.md`, `dev-system.md`, `0-ideya/`…`3-soprovozhdenie/`, `spravochniki/`, `meta/`;
- роль-агенты `runtime-copy/agents/`;
- правила-привязки и дисциплина `runtime-copy/rules/`;
- хук `runtime-copy/scripts/frontend_skill_reminder.py`;
- шаблон `runtime-copy/settings.example.json`.

### Сторонние скиллы (`runtime-copy/skills/`)

66 скиллов в `runtime-copy/skills/` — это **курированный набор**, собранный из открытых источников
(skill-маркетплейсы и репозитории сообщества). Каждый скилл **остаётся под лицензией своего автора**;
включение в этот набор не меняет его лицензию и не передаёт авторство. Скиллы отобраны, при
необходимости очищены от лишнего и привязаны к стадиям системы.

- Полный каталог изученных источников рынка — [`meta/dev-system-sources-catalog.md`](meta/dev-system-sources-catalog.md).
- Шаблоны роль-агентов выведены из **[cdeust/Cortex](https://github.com/cdeust/Cortex)** (MIT) и
  **[wshobson/agents](https://github.com/wshobson/agents)**; ряд скиллов — из агрегаторов сообщества.

Если вы автор одного из скиллов и хотите уточнить атрибуцию, лицензию или попросить удаление —
откройте issue, и мы поправим.

### Плагины

Плагины Claude Code **не входят** в репозиторий. Они устанавливаются из своих маркетплейсов (см.
`README.md`) и остаются под лицензиями своих авторов, обновляясь из первоисточника.

## EN

This repository is distributed under [MIT](LICENSE). The MIT license covers the **original part of the
system** authored here: the knowledge/routes (`CLAUDE.md`, `dev-system.md`, the stage folders,
`spravochniki/`, `meta/`), the role-agents (`runtime-copy/agents/`), the binding rules and discipline
(`runtime-copy/rules/`), the hook, and the settings template.

The 66 skills under `runtime-copy/skills/` are a **curated set** gathered from open sources (skill
marketplaces and community repositories). Each skill **remains under its author’s license**; bundling it
here does not change that license or claim authorship. See
[`meta/dev-system-sources-catalog.md`](meta/dev-system-sources-catalog.md) for the catalog of studied
sources. Role-agent templates are derived from [cdeust/Cortex](https://github.com/cdeust/Cortex) (MIT)
and [wshobson/agents](https://github.com/wshobson/agents). If you are an author and want attribution
fixed or content removed, please open an issue.

Claude Code **plugins are not bundled**; they are installed from their marketplaces and stay under their
authors’ licenses.
