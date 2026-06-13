# Python — инструменты по стадиям

Привязка инструментов к стадиям спины (`dev-coding-process-kb.md`) для Python-кода (бэк / скрипты / AI-glue). Объявил направление «Python» → действуешь по этой таблице.

**Роль-агент:** `python-engineer` (`~/.claude/agents/`) ведёт стадии 0–6 и дёргает скиллы ниже как руки.

## Привязка

| Стадия | Инструменты |
|---|---|
| 0 Сориентироваться | LSP `incomingCalls`/`findReferences`/`documentSymbol` (карта связей / «кого сломаю»; pyright), иначе Grep · чтение структуры пакета/git-log |
| 1 Оформить | python-patterns (Protocols / dataclasses / типы-контракты) · uv-package-manager (структура проекта/зависимости) |
| 2 Написать (TDD) | python-testing + superpowers:test-driven-development (тест первым) · python-patterns (идиоматика) · async-python-patterns (если async) · document-skills:claude-api (LLM-API) · document-skills:mcp-builder (MCP-серверы) |
| 3 Проверить | python-testing (pytest + cov) · линт-гейт ↓ · type-гейт ↓ |
| 4 Отладить | superpowers:systematic-debugging · python-performance-optimization (если перф/профайл) |
| 5 Ревью | security-гейт ↓ · python-patterns (анти-паттерны) |
| 6 Завершить | ruff + mypy + pytest зелёные ↓ как gate |

## Гейты (пишем сами — рынок Python-скилла не дал)

### Линт + типы (стадии 3 / 6) — ячейка 4
- `uv run ruff check .` и `uv run ruff format --check .` → ноль ошибок.
- `uv run mypy <pkg>` (или pyright) → ноль ошибок типов; нетипизированные `dict`/`Any` НЕ пересекают границу слоя.
- Гейт «готово»: ruff + mypy + pytest зелёные.

### Безопасность (стадия 5) — ячейка 7
- `uv run bandit -r <pkg>` → нет High/Medium без обоснования.
- Секреты только из env/`.env` (никогда в коде); проверить отсутствие хардкод-ключей.
- Чувствительное (auth / деньги / данные) → дополнительно `/security-review`.
- Частые Python-дыры: `eval`/`exec`/`pickle` недоверенного ввода · `subprocess(shell=True)` · SQL без параметров · YAML `load` без `SafeLoader` · path traversal.

## Примечание по применению
- **AI/данные** (pandas/numpy/ML-обучение/ноутбуки) — отдельное направление «AI» (`data-scientist`/`mlops`), не Python-колонка.
