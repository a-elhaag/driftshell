from __future__ import annotations

import re

import ollama

from driftshell.memory.injector import build_context_block


class NLUError(Exception):
    pass


_SHELL_BLOCK_RE = re.compile(r"```(?:bash|sh|shell)?\s*\n(.*?)\n```", re.DOTALL)
_SINGLE_LINE_RE = re.compile(r"^[^\n`#*]+$", re.MULTILINE)

_SYSTEM_PROMPT = """\
You are a shell command generator. Convert the user's plain English request into a single, \
valid shell command for their system. Output ONLY the shell command — no explanation, \
no markdown, no extra text. If the request is ambiguous, make the safest reasonable assumption.
"""


def generate_command(query: str, model: str) -> str:
    context = build_context_block()
    user_content = query
    if context:
        user_content = f"{context}\n\nRequest: {query}"

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except Exception as e:
        raise NLUError(f"Ollama connection failed: {e}") from e

    raw = response["message"]["content"].strip()
    return _extract_command(raw)


def _extract_command(raw: str) -> str:
    # Try fenced code block first
    match = _SHELL_BLOCK_RE.search(raw)
    if match:
        return match.group(1).strip()

    # Strip inline backticks
    if raw.startswith("`") and raw.endswith("`"):
        return raw.strip("`").strip()

    # Take the first non-empty, non-comment line
    for line in raw.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("*"):
            return line

    raise NLUError(f"Could not extract a shell command from model response: {raw!r}")
