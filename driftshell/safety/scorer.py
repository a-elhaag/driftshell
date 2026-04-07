from __future__ import annotations

import re

import ollama

from driftshell.models.schemas import RiskResult

_SYSTEM_PROMPT = """\
You are a shell command safety evaluator. Rate the risk of the given shell command on a scale \
from 0 to 10, where:
  0 = completely safe, read-only (e.g. ls, cat, pwd)
  5 = modifies files but reversible
  7 = potentially destructive or affects system state
  10 = catastrophic, irreversible damage possible

Reply with ONLY a single integer (0-10). No explanation, no other text.
"""

_INT_RE = re.compile(r"\b([0-9]|10)\b")


def score(command: str, model: str) -> RiskResult:
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Command: {command}"},
            ],
        )
        raw = response["message"]["content"].strip()
    except Exception:
        return RiskResult(score=5, raw_response="scorer_unavailable")

    match = _INT_RE.search(raw)
    if match:
        return RiskResult(score=int(match.group(1)), raw_response=raw)

    return RiskResult(score=5, raw_response=raw)
