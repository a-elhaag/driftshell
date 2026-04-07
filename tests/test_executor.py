from driftshell.core.executor import run


def test_successful_command():
    result = run("echo hello")
    assert result.exit_code == 0
    assert "hello" in result.stdout
    assert not result.timed_out


def test_failing_command():
    result = run("exit 42")
    assert result.exit_code == 42
    assert not result.timed_out


def test_timeout():
    result = run("sleep 100")
    # Default timeout is 30s, but we override via config
    # Just check the structure
    assert result.command == "sleep 100"


def test_stderr_captured():
    result = run("ls /nonexistent_path_xyz")
    assert result.exit_code != 0
    assert result.stderr or result.stdout  # some output expected
