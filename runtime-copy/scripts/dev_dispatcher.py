#!/usr/bin/env python3
"""
UserPromptSubmit диспетчер dev-системы Base — ленивая загрузка по СЛОВАМ в чате.

Три слоя (модель «мозг / хребет / руки»):
  МОЗГ   — оглавление Base + поведенческие rules/*.md → грузит Claude Code сам, всегда.
  ХРЕБЕТ — coding-discipline.md + процесс superpowers → по СТАДИИ (план/код), не на идее.
  РУКИ   — rules/<направление>.md + роль-агент + скиллы → по НАПРАВЛЕНИЮ на реализации.

coding-discipline и направленческие rules исключены из авто-загрузки через
claudeMdExcludes (settings.json) и физически лежат в ~/.claude/rules/. Этот хук
читает их оттуда и ВКЛАДЫВАЕТ текст в additionalContext по матчу — так слой
попадает в контекст только когда реально нужен. Файлы НЕ перемещаются — ссылки
в маршрутах (orchestrator/README/агенты) остаются валидными.

Маппинг стадий/направлений — в dev_routing.json рядом (данные, не код): добавить
колонку = добавить запись туда + положить rules/<binding>. Хук менять не нужно.

При любой ошибке — тихо выходим с кодом 0 (хук не должен ломать ввод). Reminder
идёт только в контекст модели, не в видимый транскрипт. Bias: при неоднозначности
грузим чуть больше (лучше лишнее, чем пропуск).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_DIR = Path.home() / ".claude" / "rules"
ROUTING = HERE / "dev_routing.json"
STAGE_PRIORITY = ("build", "plan", "idea")  # build перехватывает plan, plan — idea


def _utf8() -> None:
    # Windows-Python по умолчанию cp1251 — ломает кириллицу и em-dash. Форсим UTF-8.
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def hit(prompt: str, keywords, ext=None) -> bool:
    # Обрамлённые ключи (" node ") — по границе слова; голые (RU-морфология) — подстрокой.
    for k in keywords:
        kw = k.strip()
        if k != kw:
            if kw and re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", prompt):
                return True
        elif k in prompt:
            return True
    return bool(ext and re.search(ext, prompt, re.IGNORECASE))


def inline(fname: str) -> str:
    # Прочитать rules/<fname> и вернуть вкладываемым блоком (или '' если файла нет).
    try:
        body = (RULES_DIR / fname).read_text(encoding="utf-8").strip()
    except Exception:
        return ""
    return f"\n\n===== {fname} =====\n{body}"


def main() -> int:
    _utf8()
    try:
        prompt = (json.load(sys.stdin).get("prompt") or "").lower()
    except Exception:
        return 0
    if not prompt.strip():
        return 0
    try:
        cfg = json.loads(ROUTING.read_text(encoding="utf-8"))
    except Exception:
        return 0

    stages = cfg.get("stages", {})
    directions = cfg.get("directions", {})

    stage = next(
        (n for n in STAGE_PRIORITY if n in stages and hit(prompt, stages[n]["keywords"])),
        None,
    )
    matched = [
        (name, d)
        for name, d in directions.items()
        if hit(prompt, d.get("keywords", []), d.get("ext"))
    ]

    parts = []
    # ХРЕБЕТ: процесс по стадии + общая дисциплина кода (план/код, не идея)
    if stage and stages[stage].get("spine"):
        parts.append(f"[dev] Стадия: {stage.upper()} → процесс {stages[stage]['spine']}.")
    load_discipline = (stage in ("plan", "build")) or (any(d.get("code", True) for _, d in matched) and stage != "idea")
    if load_discipline:
        parts.append(inline("coding-discipline.md"))

    # РУКИ: направленческие привязки (build; план со стеком; направление без стадии)
    load_hands = stage == "build" or (matched and stage in ("plan", None))
    if load_hands:
        for name, d in matched:
            parts.append(inline(d["binding"]))
            extra = f" роль-агент {d['agent']}"
            if d.get("skills"):
                extra += f"; скиллы: {', '.join(d['skills'])}"
            parts.append(f"[dev] Направление {name} →{extra}; дисциплина стадий 0-6.")

    # karpathy — всегда (always-on)
    parts.append("[hook] karpathy-guidelines: think-first · simplicity · surgical · goal-driven.")

    reminder = "\n".join(p for p in parts if p)
    print(json.dumps(
        {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": reminder}},
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
