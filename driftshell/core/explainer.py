from __future__ import annotations

import ollama

_SYSTEM_PROMPT = """\
You are a shell command explainer. Given a shell command, provide a concise plain-English breakdown:
1. What the command does overall (one sentence)
2. Each flag/argument explained briefly
3. Risk level: Safe / Moderate / Dangerous — and why

Be concise. Use plain language, no jargon.
"""


def explain(command: str, model: str) -> str:
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Command: {command}"},
            ],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"(Explanation unavailable: {e})"
