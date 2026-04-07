from unittest.mock import patch

from driftshell.safety.scorer import score
from driftshell.models.schemas import RiskResult


def _mock_chat(score_str: str):
    return {"message": {"content": score_str}}


def test_scorer_parses_integer():
    with patch("ollama.chat", return_value=_mock_chat("3")):
        result = score("ls -la", "test-model")
    assert result.score == 3


def test_scorer_parses_integer_in_sentence():
    with patch("ollama.chat", return_value=_mock_chat("I'd rate this a 7 out of 10.")):
        result = score("rm -rf ./dist", "test-model")
    assert result.score == 7


def test_scorer_fallback_on_parse_failure():
    with patch("ollama.chat", return_value=_mock_chat("this is risky")):
        result = score("some command", "test-model")
    assert result.score == 5


def test_scorer_fallback_on_connection_error():
    with patch("ollama.chat", side_effect=Exception("connection refused")):
        result = score("ls", "test-model")
    assert result.score == 5
    assert result.raw_response == "scorer_unavailable"
