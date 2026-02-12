"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path


def _load_env_file(env_path: str | Path = ".env") -> None:
    """Load KEY=VALUE pairs from a .env file without overriding existing env vars."""
    path = Path(env_path)
    if not path.exists() or not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        os.environ.setdefault(key, value)


def _parse_simple_yaml(path: str | Path) -> dict:
    """Parse a small subset of YAML mappings used by local config files."""
    cfg_path = Path(path)
    if not cfg_path.exists() or not cfg_path.is_file():
        return {}

    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]

    for raw_line in cfg_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, raw_value = raw_line.strip().split(":", 1)
        value = raw_value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root

        if not value:
            node: dict = {}
            parent[key] = node
            stack.append((indent, node))
            continue

        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        parent[key] = value

    return root


def _cfg_get(cfg: dict, *keys: str) -> str:
    node = cfg
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return ""
        node = node[key]
    return str(node) if node is not None else ""


_load_env_file()
_LOCAL_CFG = _parse_simple_yaml("config/local.yaml")

NOTION_TOKEN = os.getenv("NOTION_TOKEN") or _cfg_get(_LOCAL_CFG, "notion", "token")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID") or _cfg_get(_LOCAL_CFG, "notion", "page_id")
REPORT_TITLE = os.getenv("REPORT_TITLE") or _cfg_get(_LOCAL_CFG, "report", "title") or "A股日交易分析报告"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or _cfg_get(_LOCAL_CFG, "telegram", "bot_token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or _cfg_get(_LOCAL_CFG, "telegram", "chat_id")
