import pytest

from driftshell.core.limiter import (
    LimitExceededError,
    check_command_limit,
    check_exec_limit,
    increment_command,
    increment_exec,
)


def test_command_limit_not_exceeded():
    check_command_limit()  # should not raise with 0 commands


def test_command_limit_exceeded(monkeypatch):
    from driftshell.config.loader import get_config
    from driftshell.models.schemas import DriftConfig

    cfg = DriftConfig(daily_limit=2)
    monkeypatch.setattr("driftshell.core.limiter.get_config", lambda: cfg)

    increment_command()
    increment_command()

    with pytest.raises(LimitExceededError):
        check_command_limit()


def test_exec_limit_exceeded(monkeypatch):
    from driftshell.models.schemas import DriftConfig

    cfg = DriftConfig(exec_limit=1)
    monkeypatch.setattr("driftshell.core.limiter.get_config", lambda: cfg)

    increment_exec()

    with pytest.raises(LimitExceededError):
        check_exec_limit()
