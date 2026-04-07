from __future__ import annotations

from driftshell.config.loader import get_config
from driftshell.memory.store import get_recent


def build_context_block() -> str:
    cfg = get_config()
    records = get_recent(cfg.memory_window)
    if not records:
        return ""

    lines = ["Recent command history (for context):"]
    for i, rec in enumerate(records, 1):
        lines.append(f"  {i}. \"{rec.nl_query}\" → `{rec.shell_command}`")
    return "\n".join(lines)
