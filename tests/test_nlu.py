from unittest.mock import patch

import pytest

from driftshell.core.nlu import NLUError, _extract_command, generate_command


def test_extract_from_fenced_block():
    raw = "Sure!\n```bash\nls -la /tmp\n```\nThat lists files."
    assert _extract_command(raw) == "ls -la /tmp"


def test_extract_plain_command():
    raw = "ls -la /tmp"
    assert _extract_command(raw) == "ls -la /tmp"


def test_extract_inline_backticks():
    raw = "`find . -name '*.py'`"
    assert _extract_command(raw) == "find . -name '*.py'"


def test_extract_raises_on_empty():
    with pytest.raises(NLUError):
        _extract_command("### \n* \n")


def test_generate_command_success():
    mock_response = {"message": {"content": "ls -la /tmp"}}
    with patch("ollama.chat", return_value=mock_response):
        cmd = generate_command("list all files in tmp", "test-model")
    assert cmd == "ls -la /tmp"


def test_generate_command_ollama_failure():
    with patch("ollama.chat", side_effect=Exception("connection refused")):
        with pytest.raises(NLUError):
            generate_command("do something", "test-model")
