# AI / данные — инструменты по стадиям

Привязка инструментов к стадиям спины (`dev-coding-process-kb.md`) для AI/данных (Python: данные/ETL · EDA · LLM-интеграция · RAG · ML-моделирование · MLOps/serving · AI-агенты · eval). Объявил направление «AI» → действуешь по этой таблице.

**Роль-агенты** (`~/.claude/agents/`): `data-scientist` (данные/анализ/моделирование/RAG/eval — ЧТО данные есть, КАК моделировать, ЗАЩИТИМ ли результат) · `mlops` (serving/деплой/версионирование/дрифт — готова ли ML-система к train/serve/monitor). AI-код опирается на Python-колонку (`python-engineer` дисциплина + `python-testing`); хранение данных/фич/векторов — на `dba`.

## Привязка

| Стадия | Инструменты |
|---|---|
| 0 Сориентироваться | `data-scientist` (профилирование данных) · прочитать данные/задачу/конвенции |
| 1 Оформить | `data-scientist` (схема/распределения/feature-план; выбор подхода LLM vs ML vs детерминированное) · `regex-vs-llm-structured-text` (нужен ли LLM) · `rag-engineer` (RAG-дизайн, «retrieval-качество вперёд генерации») · `database-design`/`dba` (хранение данных/фич/векторов) |
| 2 Написать | по ячейке: `polars` (данные/ETL) · `matplotlib`/`seaborn` (EDA) · `prompt-engineering-patterns`/`llm-structured-output`/`cost-aware-llm-pipeline` (LLM) · `rag-implementation`/`embedding-strategies`/`vector-index-tuning` (RAG) · `scikit-learn`/`pytorch`/`mle-workflow` (ML) · `multi-agent-patterns`/`agent-harness-construction`/`iterative-retrieval` (агенты). Поверх Python-колонки (TDD, типы на границах) |
| 3 Проверить | `eval-harness`/`advanced-evaluation` (AI/LLM-eval, LLM-as-judge) · `data-quality-frameworks` (валидация данных) · `mle-workflow` (метрики/контракты) · `data-scientist` (leakage-audit / confidence-reporting) |
| 4 Отладить | `data-scientist` (leakage-audit) · `iterative-retrieval` (RAG-debug) · `agent-architecture-audit` (агент-системы) · `superpowers:systematic-debugging` (измерение) · `python-performance-optimization` |
| 5 Ревью | `data-scientist` (bias/leakage/confidence — защитимость вывода) · `mlops` (serving SLO/дрифт — готовность к проду) · `advanced-evaluation` (валидность eval) · security-гейт ↓ |
| 6 Завершить | `mlops` (training-contract/rollout/мониторинг → ML Deployment Plan) · `data-scientist` (Analysis Report) · гейты ↓ как gate |

## Гейты (пишем сами — рынок не закрыл / пробел)

### Eval-first для недетерминированного (стадии 3 / 6) — High
- Любой LLM/RAG/агент-вывод измеряется eval-набором ДО прода (`eval-harness`, EDD: eval пишется до фичи). Метрики названы (pass@k, тип grader'а); LLM-as-judge — с защитой от bias (`advanced-evaluation`).
- «Работает на трёх примерах» — не eval. Гейт «готово»: eval-набор + пороги + регресс-прогон.

### Данные на границах (стадии 2 / 3)
- Данные, входящие в модель/RAG, валидируются контрактом (`data-quality-frameworks`: pandera/pydantic/Great Expectations) на границе слоя. Типы — как в `python-engineer` (нет голых `dict`/`Any`).
- Утечка (leakage): fit трансформов только на train-сплите; GroupKFold/TimeSeriesSplit где есть группы/время (`data-scientist`).

### Безопасность AI (стадия 5) — High
- Prompt-injection: недоверенный ввод в LLM изолирован/санитизирован; инструменты агента — allow-list, не произвольное исполнение.
- PII: классификация, редакция в логах/трейсах; ключи/секреты провайдеров только из env.
- Model-safety: модерация ввода/вывода где публично; защита от data-exfiltration через tool-use. Чувствительное → дополнительно `/security-review`.

### Serving (стадия 6)
- `mlops` + `mle-workflow` дают serving-контракт/SLO/rollout/дрифт-мониторинг. Deep serving-инфра (batching/autoscaling/GPU-шедулинг) — на уровне дисциплины `mlops`, отдельным скиллом не покрыта.

## Примечание по применению
- **Библиотеки** `polars`/`matplotlib`/`seaborn`/`scikit-learn`/`pytorch` (таблица стадии 2) — пишешь код напрямую, это библиотеки, не скилл-обёртки (через `Skill` не вызывать).
- **Не входит в AI-колонку:** data-platform ETL (airflow/dbt/spark) — отдельный data-engineering домен; agent-фреймворк (LangGraph/CrewAI/свой) выбирается на проекте; serving deep-инфра (batching/autoscaling/GPU) — через `mlops`+`mle-workflow` на уровне контракта/SLO/дрифта.
