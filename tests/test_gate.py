from unittest.mock import patch

from driftshell.models.schemas import GateDecision, RiskResult
from driftshell.safety.gate import evaluate


def test_auto_exec_whitelisted_low_risk():
    risk = RiskResult(score=1, raw_response="1")
    result = evaluate("ls -la /tmp", risk)
    assert result == GateDecision.AUTO_EXEC


def test_auto_exec_whitelisted_with_score_2():
    risk = RiskResult(score=2, raw_response="2")
    result = evaluate("cat README.md", risk)
    assert result == GateDecision.AUTO_EXEC


def test_mid_risk_prompts_user_confirmed():
    risk = RiskResult(score=5, raw_response="5")
    with patch("typer.confirm", return_value=True):
        result = evaluate("mv file.txt backup.txt", risk)
    assert result == GateDecision.CONFIRMED


def test_mid_risk_prompts_user_aborted():
    risk = RiskResult(score=5, raw_response="5")
    with patch("typer.confirm", return_value=False):
        result = evaluate("mv file.txt backup.txt", risk)
    assert result == GateDecision.ABORTED


def test_high_risk_confirmed():
    risk = RiskResult(score=8, raw_response="8")
    with patch("typer.confirm", return_value=True):
        result = evaluate("rm -rf ./node_modules", risk)
    assert result == GateDecision.CONFIRMED


def test_high_risk_aborted():
    risk = RiskResult(score=9, raw_response="9")
    with patch("typer.confirm", return_value=False):
        result = evaluate("rm -rf ./dist", risk)
    assert result == GateDecision.ABORTED
