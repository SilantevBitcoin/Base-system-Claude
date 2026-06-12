#!/usr/bin/env python3
"""
UserPromptSubmit hook for Claude Code — dev-direction reminder.

(Filename kept for settings.json compatibility; scope is now all directions,
not only frontend.)

Scans the user's prompt for signals of each development direction of the dev
system — Frontend/UI, TypeScript/Node, Python, DB, AI/data, Backend/infra — by
keyword (EN+RU) and file extension. On match, injects a silent reminder telling
Claude to engage the matching role-agent and follow its stage 0-6 discipline;
the binding rules/<dir>.md is already auto-loaded, the shared rail is
rules/coding-discipline.md. Frontend additionally drives web-performance /
react skills (original behavior preserved). karpathy-guidelines is always-on.

The reminder goes into the model's context only — it does NOT appear in the
user-visible transcript. False-positive cost = one extra abstract line;
false-negative cost = code written without the column's discipline. Triggers
are kept conservative but covering.
"""
import json
import re
import sys


def main() -> int:
    # CC sends JSON as UTF-8; Windows-Python defaults stdin to cp1251, which
    # breaks the Cyrillic triggers. Force UTF-8.
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass
    # stdout too: Windows-Python defaults to cp1251, which cannot encode the
    # arrow/em-dash in the reminder text → UnicodeEncodeError on print.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    prompt = (data.get("prompt") or "").lower()
    if not prompt.strip():
        return 0

    # --- Frontend (original behavior: also drives web-performance / react) ---
    frontend_kw = [
        # English
        "landing", "chat widget", "animation", "animate ", "scroll",
        "parallax", "mousemove", "mouse parallax", "eventsource", " sse ",
        "video background", "background video", "typing effect", "frontend",
        "vanilla js", "css animation", "optimize web", "web performance",
        "page speed", "hangs", "freeze", "freezes", "freezing", "slow page",
        "janky", "choppy", "laggy", "low fps", "high fps", "layout shift",
        "forced reflow", "repaint", "compositing", "will-change",
        # Russian
        "лендинг", "чат-виджет", "чат виджет", "анимаци", "скролл",
        "прокрутк", "параллакс", "мышк", "видео-фон", "фон-видео",
        "фронтенд", "оптимизаци", "медленно", "тормозит", "лагает",
        "виснет", "висит", "зависает", "плавно ", "фпс",
    ]
    react_kw = [
        "react", " tsx", " jsx", "usestate", "useeffect", "usememo",
        "usecallback", "useref", "next.js", "nextjs", "компонент",
    ]
    # Unambiguously-frontend extensions. `.js`/`.ts` excluded — also backend.
    frontend_ext = re.compile(r"\.(jsx|tsx|css|scss|sass|html?|vue|svelte)\b")

    # --- Other directions: keyword (EN+RU) + file-extension signals ---
    python_kw = [
        "fastapi", "django", "flask", "asyncio", "pydantic", "pytest",
        " uv ", "ruff", "mypy", "celery", " python ", "питон", "воркер",
    ]
    typescript_kw = [
        "typescript", "nodejs", "node.js", " node ", "fastify", "express",
        "nestjs", " hono ", " zod ", "vitest", "pnpm", " tsc ", "eslint",
        "biome", "ts/node",
    ]
    db_kw = [
        "postgres", "postgresql", " sql ", "миграци", "migration",
        " schema ", "индекс", " index ", " query ", "prisma", "drizzle",
        " orm ", "база данных", " бд ", " table ", "таблиц",
    ]
    ai_kw = [
        " llm ", " rag ", "embedding", "эмбеддинг", "vector db", "vectordb",
        "prompt engineering", " eval ", "langchain", "pandas", "numpy",
        "scikit", "pytorch", "машинн", "обучени модел",
    ]
    backend_kw = [
        "docker", "kubernetes", " k8s ", "ci/cd", "deploy", "деплой",
        "redis", "kafka", "rabbitmq", "rate limit", "rate-limit",
        "secrets management", "observability", "очеред", "контейнер",
    ]

    def hit(keywords, ext=None):
        # Padded keys (" node ") want a whole-token match, but a bare substring
        # check misses them at prompt start/end or next to punctuation. Match
        # those by a non-word-char boundary; keep bare keys as substring so RU
        # morphology still works (миграци → миграцию, контейнер → контейнеры).
        for k in keywords:
            if k != k.strip():
                kw = k.strip()
                if kw and re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", prompt):
                    return True
            elif k in prompt:
                return True
        return bool(ext.search(prompt)) if ext else False

    m_frontend = hit(frontend_kw, frontend_ext)
    m_react = hit(react_kw)

    directions = []  # (label, role-agent, rules-file)
    if m_frontend or m_react:
        directions.append(("Frontend/UI", "frontend-engineer", "rules/frontend.md"))
    if hit(python_kw, re.compile(r"\.py\b")):
        directions.append(("Python", "python-engineer", "rules/python.md"))
    if hit(typescript_kw, re.compile(r"\.ts\b")):
        directions.append(("TS/Node", "typescript-engineer", "rules/typescript.md"))
    if hit(db_kw, re.compile(r"\.sql\b")):
        directions.append(("DB", "dba", "rules/db.md"))
    if hit(ai_kw):
        directions.append(("AI/data", "data-scientist / mlops", "rules/ai.md"))
    if hit(backend_kw):
        directions.append(("Backend/infra", "devops-engineer", "rules/backend.md"))

    # Always-on skills (matches prior behavior); frontend adds perf/react.
    skills = ["`andrej-karpathy-skills:karpathy-guidelines`"]
    if m_frontend:
        skills.append("`web-performance`")
    if m_react:
        skills.append("`vercel:react-best-practices`")

    # Reminder is injected into EVERY prompt — kept terse on purpose (~30-60
    # tokens): the imperative + names; the principles live in the skill body.
    parts = [
        "\n\n[hook] Before writing/editing/reviewing code, invoke via Skill "
        "tool: " + ", ".join(skills) + ". Do not skip."
    ]
    if m_frontend:
        parts.append(" Frontend: apply web-performance patterns to all output.")
    if directions:
        lines = "; ".join(
            f"{lbl} → {role} ({rules})" for lbl, role, rules in directions
        )
        parts.append(
            " Direction(s): " + lines + " — stage 0-6 discipline, rail "
            "rules/coding-discipline.md."
        )
    reminder = "".join(parts)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": reminder,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
