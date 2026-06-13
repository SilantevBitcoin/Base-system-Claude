#!/usr/bin/env python3
"""
SessionStart-страж LSP-фикса: переприменяет node-запуск LSP-серверов в официальном
marketplace.json, если он слетел после авто-обновления маркетплейса.

ЗАЧЕМ. На Windows Claude Code спавнит LSP-сервер по голому имени без shell → ENOENT.
Фикс: command="node", args=[<entrypoint>, "--stdio"] для typescript-lsp и pyright-lsp.
Официальный маркетплейс авто-обновляется при старте CC (GCS-снапшот) и ЗАТИРАЕТ правку
целиком (не git-merge). Этот хук при каждом старте детектит слёт и идемпотентно
переприменяет фикс; при срабатывании пишет в контекст, чтобы ассистент уведомил владельца.

В основном для Windows — на macOS/Linux LSP-серверы обычно запускаются штатно, и хук
молча выходит (чинить нечего). Перед использованием укажите путь к глобальным npm-модулям
через env LSP_FIX_NPM_MODULES (по умолчанию %APPDATA%/npm/node_modules — стандарт Windows).

КОНТРАКТ. Pre: marketplace.json существует и валиден JSON; серверы установлены в NPM_MODULES.
Действие: для плагинов из TARGETS привести lspServers.<lang>.command/args к node-запуску,
ТОЛЬКО если entrypoint реально существует (иначе сигнал «не найдено», без слепой правки).
Post: оба блока = node+entrypoint; правка пишется лишь при реальном изменении (идемпотентно).
FAILS_ON: файл отсутствует / не JSON / неожиданная структура / ошибка записи → тихий выход 0
(хук не должен ломать старт сессии). Молчит, когда фикс на месте (не засорять контекст).

Тест без риска для живого файла: LSP_FIX_MARKETPLACE_PATH=<копия> python lsp_fix_guard.py
"""
import json
import os
import sys
from pathlib import Path

# База установленных через npm -g серверов. По умолчанию — стандартный путь Windows
# (%APPDATA%/npm/node_modules); переопределяется env LSP_FIX_NPM_MODULES под свою ОС/установку.
# Реальное наличие проверяется .exists() ниже — слепой правки по несуществующему пути не делаем.
NPM_MODULES = Path(os.environ.get(
    "LSP_FIX_NPM_MODULES",
    str(Path(os.environ.get("APPDATA", str(Path.home()))) / "npm" / "node_modules"),
))

# name плагина → (ключ языка в lspServers, относительный entrypoint в node_modules)
TARGETS = {
    "typescript-lsp": ("typescript", "typescript-language-server/lib/cli.mjs"),
    "pyright-lsp": ("pyright", "pyright/langserver.index.js"),
}

DEFAULT_MP = (
    Path.home() / ".claude" / "plugins" / "marketplaces"
    / "claude-plugins-official" / ".claude-plugin" / "marketplace.json"
)


def _utf8() -> None:
    # Windows-Python по умолчанию cp1251 — print() кириллицы падает UnicodeEncodeError. Форсим UTF-8.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            try:
                reconfigure(encoding="utf-8")
            except Exception:
                pass


def emit(msg: str) -> None:
    # SessionStart-хук вкладывает текст в стартовый контекст ассистента через additionalContext.
    print(json.dumps(
        {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}},
        ensure_ascii=False,
    ))


def main() -> int:
    _utf8()
    mp_path = Path(os.environ.get("LSP_FIX_MARKETPLACE_PATH", str(DEFAULT_MP)))
    try:
        data = json.loads(mp_path.read_text(encoding="utf-8"))
    except Exception:
        return 0  # нет файла / не JSON — не наша ситуация, молча выходим

    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        return 0

    fixed, missing = [], []
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        name = plugin.get("name")
        if not isinstance(name, str):
            continue
        target = TARGETS.get(name)
        if not target:
            continue
        lang, rel_entry = target
        servers = plugin.get("lspServers")
        if not isinstance(servers, dict) or not isinstance(servers.get(lang), dict):
            continue
        cfg = servers[lang]
        entry = (NPM_MODULES / rel_entry).as_posix()
        # Фикс уже на месте → пропустить (идемпотентность).
        if cfg.get("command") == "node" and entry in (cfg.get("args") or []):
            continue
        # Чинить только если сервер реально установлен по ожидаемому пути.
        if not (NPM_MODULES / rel_entry).exists():
            missing.append(f"{name} (нет {rel_entry})")
            continue
        rest = [a for a in (cfg.get("args") or []) if a != entry and a != "--stdio"]
        cfg["command"] = "node"
        cfg["args"] = [entry] + rest + ["--stdio"]
        fixed.append(name)

    if fixed:
        try:
            mp_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        except Exception:
            return 0
        emit(
            "⚠️ LSP-ФИКС СЛЕТЕЛ и был автоматически переприменён в официальном marketplace.json "
            f"({', '.join(fixed)}). Причина: официальный маркетплейс перекачался (авто-update при старте CC). "
            "СООБЩИ ВЛАДЕЛЬЦУ: фикс восстановлен автоматически, LSP снова рабочий; ручных действий не требуется."
        )
    elif missing:
        emit(
            "⚠️ LSP-фикс слетел, переприменить НЕ удалось — сервер(ы) не найдены по ожидаемому пути: "
            f"{', '.join(missing)}. СООБЩИ ВЛАДЕЛЬЦУ проверить установку npm-серверов "
            "(typescript-language-server / pyright) или задать путь через env LSP_FIX_NPM_MODULES."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
