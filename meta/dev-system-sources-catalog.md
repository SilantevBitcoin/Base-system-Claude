# Каталог источников для глобальной системы разработчика

> **Что это.** Полный каталог собранного при сборке универсальной системы разработчика на базе
> Claude Code. Не привязан к проекту (LPH — лишь один из случаев применения). Цель — карта того,
> что существует в экосистеме, чтобы решать, что брать в систему, что выкинуть.
>
> **Звёзды проверены** через GitHub API 2026-06-05 (✓). Дата сбора: 2026-06-05.
>
> **Легенда слоёв:** `[ядро]` дисциплина написания кода (микро, наш текущий фокус) · `[роли]` агенты-
> специализации · `[метод]` методология/процесс (макро, «общая система») · `[оркестр]` multi-agent ·
> `[авто-инж]` автономные AI-инженеры · `[память]` контекст/память · `[MCP]` инструменты · `[мега]`
> всё-в-одном коллекции.
>
> **Приоритет изучения:** 🔴 высокий · 🟡 средний · ⚪ справочно.

---

## ЧАСТЬ 0. Что уже изучено (источники) — кратко

| Источник | Вердикт | Куда |
|---|---|---|
| **cdeust/Cortex** (45⭐) | ядро дисциплины кода — `engineer.md` Moves 1-7 (layer/contract/refusals/stakes/self-verify), security-audit, incident, optimize + образец оформления. Брать ядро, резать зететику/genius/инфраструктуру | `[ядро]` |
| **github/spec-kit** (109k⭐) | макро: spec→plan→tasks pipeline. Для нашего слоя — образец `implement`-потока + формат задач + coverage-gap + constitution-as-gates. Остальное → общая система | `[метод]` |
| **vercel-labs/agent-skills** (—) | апстрим наших же скиллов; новое: writing-guidelines, vercel-cli-with-tokens, vercel-optimize | стек-модуль |
| **coreyhaines31/marketingskills** (—) | ✅ **внедрён** как модуль «публичный сайт»: 3 яруса (текст глобально · сайт-рост `rules/marketing.md` · промо по запросу); copy-editing, seo-audit, ai-seo, content-strategy, site-architecture, cro, schema | тип-продукт-модуль |

---

## ЧАСТЬ 1. Anthropic official — платформа (фундамент)

### 1A. Must-read статьи (то, чего мы НЕ читали — изучить первыми)

| 🔴 | Статья | URL |
|---|---|---|
| 🔴 | **Lessons from building Claude Code: How we use skills** (2026-06-03) — 9 категорий скиллов, внутренняя практика | claude.com/blog/lessons-from-building-claude-code-how-we-use-skills |
| 🔴 | **A harness for every task: dynamic workflows** (2026-06-02) — 8 паттернов оркестрации (`ultracode`) | claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code |
| 🔴 | **Best practices for Claude Code** (офиц. док) — explore-plan-code, verify, subagents | code.claude.com/docs/en/best-practices |
| 🔴 | **CC Advanced Patterns: Subagents, MCP, Scaling** (PDF, 2026-03-24) | resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns... |
| 🟡 | **Writing effective tools for agents** (2025-09-11) — как проектировать tools | anthropic.com/engineering/writing-tools-for-agents |
| 🟡 | **Code execution with MCP** (2025-11-04) — MCP как code API, −98.7% токенов | anthropic.com/engineering/code-execution-with-mcp |
| 🟡 | **Building agents with Skills** — сдвиг: specialized agents → skills | claude.com/blog/building-agents-with-skills-equipping-agents-for-specialized-work |
| 🟡 | **Seeing like an agent** (2026-04-10) — дизайн инструментов «глазами модели» | claude.com/blog/seeing-like-an-agent |
| 🟡 | **Building agents with the Claude Agent SDK** | anthropic.com/engineering/building-agents-with-the-claude-agent-sdk |
| 🟡 | **Advanced tool use** (API beta) — Tool Search Tool, Programmatic Tool Calling | anthropic.com/engineering/advanced-tool-use |
| ⚪ | **Making CC more secure: sandboxing** (2025-10-20) | anthropic.com/engineering/claude-code-sandboxing |
| ⚪ | **Running an AI-native engineering org** (2026-06-03) | claude.com/blog/running-an-ai-native-engineering-org |
| ⚪ | **Scaling Agentic Coding Across Your Org** (PDF playbook) | resources.anthropic.com/hubfs/Scaling%20agentic%20coding... |
| ⚪ | **The Complete Guide to Building Skills** (PDF) | resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf |

### 1B. Новые фичи CC, которые мы НЕ используем (изучить)

| 🔴 | Фича | Что | Док |
|---|---|---|---|
| 🔴 | **Dynamic Workflows** | Claude пишет JS-harness на лету, оркеструет subagents (fan-out, adversarial, tournament). `ultracode` | code.claude.com/docs/en/workflows.md |
| 🔴 | **LSP / Code Intelligence плагины** | typescript-lsp, pyright-lsp, gopls, rust-analyzer + 9 языков — символьная навигация вместо grep, live type errors | `/plugin install <lang>-lsp@claude-plugins-official` |
| 🔴 | **pr-review-toolkit** | 6 агентов (comments/tests/silent-failures/types/code/simplify) — полнее чем code-review | claude-plugins-official |
| 🟡 | **Agent Teams** (preview) | несколько CC-сессий с общим task list + messaging | code.claude.com/docs/en/agent-teams.md |
| 🟡 | **Routines** | scheduled remote agents (cron/API/GitHub events) | code.claude.com/docs/en/routines.md |
| 🟡 | **hookify** | генерация custom hooks из паттернов разговора | claude-plugins-official |
| 🟡 | **agent-sdk-dev** | dev kit для Claude Agent SDK (`/new-sdk-app`) | claude-plugins-official |
| 🟡 | **Output Styles** | explanatory / learning режимы (SessionStart хук) | code.claude.com/docs/en/output-styles.md |
| ⚪ | **Sandboxing** | sandboxed Bash, −84% permission prompts | code.claude.com/docs/en/sandboxing.md |
| ⚪ | **ralph-loop** | autonomous iteration до завершения | claude-plugins-official |

### 1C. Официальные репозитории Anthropic

| ⭐ | Репо | Что |
|---|---|---|
| 147k | **anthropics/skills** | официальные Agent Skills (17 шт — все у нас есть через document-skills) + стандарт agentskills.io |
| 29k | **anthropics/claude-plugins-official** | официальный marketplace (~119 плагинов; используем ~15) |
| 19k | **anthropics/knowledge-work-plugins** | 11 плагинов-ролей (Data/Product/Finance/Marketing/Legal…) — **образец структуры плагина-роли** |
| 5k | **anthropics/claude-code-security-review** | GitHub Action: авто security-review PR (OWASP Top 10) |
| 2k | **anthropics/mcpb** | .mcpb формат — упаковка MCP в portable пакеты |

---

## ЧАСТЬ 2. Мега-коллекции «всё-в-одном» (изучить как готовые системы)

| ⭐ | Репо | Что внутри | Слой |
|---|---|---|---|
| **208k** | 🔴 **affaan-m/everything-claude-code** | 251 skills, 63 субагента, hooks на все события, rules по языкам, «continuous learning» (паттерны из сессий → skills с confidence-scoring) | `[мега][ядро]` |
| **107k** | 🔴 **garrytan/gstack** (CEO YC) | 23 роли-инструмента = виртуальная инженерная команда + Conductor (10-15 параллельных сессий) | `[мега][роли]` |
| **63k** | 🟡 **ComposioHQ/awesome-claude-skills** | 1000+ skills, 78+ SaaS-интеграций, great_cto (7 субагентов SDLC) | `[мега]` |
| **56k** | 🔴 **shanraisshan/claude-code-best-practice** | 83 совета + все паттерны (Research→Plan→Execute→Review→Ship), ссылки на топ-коллекции | `[метод]` |
| **46k** | 🟡 **hesreallyhim/awesome-claude-code** | главный awesome-индекс экосистемы (точка входа) | `[мега]` |
| **40k** | 🟡 **sickn33/antigravity-awesome-skills** | 1508+ skills, npm-инсталлер, cross-platform | `[мега]` |
| **17k** | 🟡 **alirezarezvani/claude-skills** | 337 skills, 129 engineering (RAG, chaos eng, K8s, CI/CD), 533 Python CLI | `[ядро]` |
| **24k** | 🟡 **VoltAgent/awesome-agent-skills** | 1424 skills от официальных команд (Stripe/Google/Anthropic) — верифицированные | `[мега]` |
| 2k | ⚪ **rohitg00/awesome-claude-code-toolkit** | 135 agents + 176 plugins + 14 MCP — наиболее комплектный набор | `[мега]` |
| — | ⚪ **claudemarketplaces.com** | директория: 20k+ skills, 9.9k+ MCP — discovery-слой | дискавери |

---

## ЧАСТЬ 3. Роли-агенты (специализация реализации)

| ⭐ | Репо | Агенты | Примечание |
|---|---|---|---|
| **36k** | 🔴 **wshobson/agents** | 191 агент, 16 оркестраторов | де-факто эталон: frontmatter + «Use PROACTIVELY when» + Workflow Position + модельные тиры (Opus/Sonnet/Haiku) |
| **21k** | 🟡 **VoltAgent/awesome-claude-code-subagents** | 154 агента, 10 категорий | категория 09-meta-orchestration; ставится как plugin |
| 715 | 🟡 **carlrannaberg/claudekit** | 32 агента | **triage-маршрутизатор** + параллельный 6-аспектный code review; NPM |
| 1.6k | ⚪ **lst97/claude-code-sub-agents** | 33 агента | задокументированные паттерны оркестрации (Sequential/Parallel/Validation) |
| 0 | ⚪ **devjarus/coding-agent** | 5 агентов + 54 skills | **образец чистого пайплайна**: Orchestrator/Architect/Implementor/Evaluator/Debugger с gate-точками |

> **Де-факто стандарт оформления субагента** (консенсус): файл `.claude/agents/<имя>.md`, YAML frontmatter
> (`name` обязателен, `description` с триггером «Use PROACTIVELY when…», `model`, `tools`), тело =
> Behavioral Traits + Workflow Position (After/Complements/Enables) + Response Approach.

---

## ЧАСТЬ 4. Методологии и процесс (макро — «общая система»)

| ⭐ | Репо | Подход | Слой |
|---|---|---|---|
| **109k** | 🟡 **github/spec-kit** | Spec-Driven Dev: constitution→specify→plan→tasks→implement (уже изучили) | `[метод]` |
| **49k** | 🔴 **bmad-code-org/BMAD-METHOD** | 12+ агент-персон (BA/PM/Architect/Dev/QA), 34+ workflows, Party Mode, full lifecycle | `[метод][оркестр]` |
| 13k | 🟡 **coleam00/context-engineering-intro** | context engineering: CLAUDE.md, PRPs (Product Requirement Prompts) | `[метод]` |
| 5k | 🟡 **buildermethods/agent-os** | инъекция стандартов кодовой базы в агентов (discover/deploy/shape/index) | `[метод][ядро]` |
| 27k | 🟡 **eyaltoledano/claude-task-master** | PRD → авто-задачи с приоритетами/зависимостями; внутри IDE | `[метод]` PRD→tasks |

---

## ЧАСТЬ 5. Оркестрация (multi-agent)

| ⭐ | Репо | Подход |
|---|---|---|
| **58k** | 🔴 **ruvnet/ruflo** (=claude-flow) | meta-harness: 100+ агентов, SPARC, swarm-топологии, векторная память, GOAP; 84.8% SWE-bench |
| **53k** | 🟡 **crewAIInc/crewAI** | role-playing агенты + Flows; быстрый multi-agent прототип (независим от LangChain) |
| **34k** | 🟡 **langchain-ai/langgraph** | graph-based stateful workflow; audit trails, human-in-the-loop; enterprise-стандарт |
| 8k | 🟡 **smtg-ai/claude-squad** | параллельные CC/Codex/Aider-сессии в tmux, каждая = git worktree |
| 11k | ⚪ **humanlayer/humanlayer** | human-in-the-loop approval (Slack/email) + CodeLayer IDE |

---

## ЧАСТЬ 6. Автономные AI-инженеры (альтернативные харнессы)

| ⭐ | Репо | Что |
|---|---|---|
| **76k** | 🟡 **OpenHands/OpenHands** | end-to-end AI-инженер: план→код→тесты→PR; SOTA на SWE-bench (open-source) |
| **46k** | 🟡 **Aider-AI/aider** | terminal pair-programmer, git-нативный (каждое изменение = commit), 75+ LLM |
| 19k | ⚪ **SWE-agent/swe-agent** | академический (Princeton): GitHub issue → фикс; mini-версия 100 строк, 74% SWE-bench |

---

## ЧАСТЬ 7. Память и контекст (инфраструктура)

| ⭐ | Репо | Что |
|---|---|---|
| **58k** | 🟡 **mem0ai/mem0** | universal memory layer (User/Session/Agent), hybrid vector+graph, cross-platform |
| **27k** | 🟡 **getzep/graphiti** | temporal knowledge graph — факты с временным окном валидности; MCP-native |
| 45 | ⚪ **cdeust/Cortex** (память-часть) | neuroscience-based persistent memory, PostgreSQL+pgvector, 100% local, LongMemEval 98.4% |

---

## ЧАСТЬ 8. Dev-MCP инструменты

**Реестры (точки входа):** registry.modelcontextprotocol.io (~9.6k) · smithery.ai (7.3k) · glama.ai (22-31k) · punkpeye/awesome-mcp-servers (88k⭐) · modelcontextprotocol/servers (эталоны Anthropic).

| 🔴 | MCP | Что даёт | Категория |
|---|---|---|---|
| 🔴 | **Serena** (25k⭐, oraios/serena) | LSP-семантическая навигация, 40+ языков — «IDE для агента» | код-анализ |
| 🔴 | **Sequential Thinking** (офиц.) | chain-of-thought как явные ревизируемые шаги | рассуждение |
| 🔴 | **Memory / Knowledge Graph** (офиц.) | персистентная память агента (entities + relations) | память |
| 🔴 | **GitHub MCP** (github/github-mcp-server) | issues/PR/Actions/security alerts | git/CI |
| 🟡 | **Desktop Commander** (wonderwhy-er) | терминал + процессы + ripgrep + code execution | filesystem |
| 🟡 | **E2B MCP** (e2b-dev) | code execution в изолированных microVM | sandbox/тесты |
| 🟡 | **Semgrep MCP** (semgrep/mcp) | static security scan на каждый diff | безопасность |
| 🟡 | **ast-grep-mcp** (414⭐) | структурный поиск/рефакторинг по AST | код-анализ |
| 🟡 | **Sentry MCP** | контекст ошибки + предлагаемый фикс | observability |
| ⚪ | **Cognee MCP** (topoteretes) | Graph-RAG поверх проектных доков | память |
| ⚪ | **mcp-ripgrep**, **Code Pathfinder**, **codedb** | быстрый поиск / call-graph / code intelligence | код-анализ |

> **Лимит:** ~40 активных инструментов на сессию. Группировать бандлами: code-analysis (Serena+ast-grep+ripgrep),
> memory (Knowledge Graph+Cognee), deploy (GitHub+Vercel+Sentry).

---

## ЧАСТЬ 9. Сквозные паттерны экосистемы (консенсус индустрии)

Все зрелые системы сходятся к одному — это ориентир для нашего дизайна:

1. **Spec-first обязателен** — никто не начинает с «пиши код»; всегда фаза spec/PRD/constitution.
2. **Persona-driven агенты** вместо монолитного LLM — разделение ролей (PM/Architect/Dev/QA) — стандарт.
3. **Память — отдельный слой инфраструктуры** (vector+graph+keyword hybrid), не «просто контекст».
4. **Git как источник истины** — каждое действие агента = traceable commit.
5. **Human-in-the-loop как design principle** — явные approval-точки на критических шагах.
6. **Context engineering > prompt engineering** — структурированный контекст (CLAUDE.md, standards, PRPs).
7. **Observability обязательна на prod** — session replays, cost tracking.

---

## ЧАСТЬ 10. Экспертные выводы (моя оценка)

**Где мы сейчас.** Наш стек — добротная база (superpowers + document-skills + vercel + karpathy + code-review).
Но используем малую долю даже **официального** арсенала Anthropic: не подключены LSP (символьная навигация
вместо grep — это объективный апгрейд), dynamic workflows, pr-review-toolkit, output styles, routines.

**Главный разрыв по слоям (что у нас слабо покрыто):**
- `[ядро]` дисциплина кода — закрываем Cortex'ом (хорошо).
- `[роли]` агенты-специализации — у нас почти нет; рынок богат (wshobson/agents эталон).
- `[память]` — не используем вообще; mem0/graphiti/Cortex — зрелые варианты.
- `[MCP код-анализа]` — Serena/ast-grep/sequential-thinking объективно усиливают реализацию.
- `[метод]` макро-процесс — это «общая система» (spec-kit/BMAD), следующий шаг.

**Приоритеты на изучение (мой ранг):**
1. 🔴 Anthropic must-read (dynamic workflows, lessons-from-skills, code-execution-MCP, Advanced Patterns PDF) — официально, низкий риск.
2. 🔴 LSP-плагины + Serena + sequential-thinking — прямой апгрейд слоя реализации.
3. 🔴 wshobson/agents — эталон ролей + стандарт оформления субагента.
4. 🔴 everything-claude-code (208k) + gstack (107k) — изучить как готовые системы (что брать/резать).
5. 🟡 BMAD-METHOD — самая зрелая методология полного цикла (для общей системы).
6. 🟡 mem0 / graphiti — память (для долгих проектов).

**Принцип отбора (твой):** даже у мега-коллекций берём НУЖНОЕ, режем лишнее. Звёзды ≠ качество для нас —
ориентир на соответствие нашей архитектуре (ядро + модули + методология + оркестрация + память + MCP).
