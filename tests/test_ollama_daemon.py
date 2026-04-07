from unittest.mock import MagicMock, patch

from driftshell.core.ollama_daemon import _is_installed, _is_running, ensure_ollama


def test_skips_install_if_already_installed():
    with patch("driftshell.core.ollama_daemon._is_installed", return_value=True), \
         patch("driftshell.core.ollama_daemon._is_running", return_value=True), \
         patch("driftshell.core.ollama_daemon._ensure_model") as mock_model:
        ensure_ollama("gemma4:e4b")
    mock_model.assert_called_once_with("gemma4:e4b")


def test_starts_daemon_if_not_running():
    with patch("driftshell.core.ollama_daemon._is_installed", return_value=True), \
         patch("driftshell.core.ollama_daemon._is_running", return_value=False), \
         patch("driftshell.core.ollama_daemon._start_daemon") as mock_start, \
         patch("driftshell.core.ollama_daemon._ensure_model"):
        ensure_ollama("gemma4:e4b")
    mock_start.assert_called_once()


def test_installs_if_not_found():
    with patch("driftshell.core.ollama_daemon._is_installed", return_value=False), \
         patch("driftshell.core.ollama_daemon._install") as mock_install, \
         patch("driftshell.core.ollama_daemon._is_running", return_value=True), \
         patch("driftshell.core.ollama_daemon._ensure_model"):
        ensure_ollama("gemma4:e4b")
    mock_install.assert_called_once()


def test_is_running_returns_false_on_connection_error():
    with patch("ollama.list", side_effect=Exception("refused")):
        assert _is_running() is False


def test_windows_install_downloads_and_runs_installer():
    import os
    from driftshell.core.ollama_daemon import _install_windows

    with patch("subprocess.run") as mock_run, \
         patch("driftshell.core.ollama_daemon.console"), \
         patch.dict(os.environ, {"LOCALAPPDATA": "C:\\Users\\test\\AppData\\Local", "PATH": ""}):
        _install_windows()

    # Should have made exactly 2 subprocess calls: Invoke-WebRequest + /S installer
    assert mock_run.call_count == 2
    first_call_args = mock_run.call_args_list[0][0][0]
    assert "powershell" in first_call_args[0].lower()
    assert "Invoke-WebRequest" in " ".join(first_call_args)


def test_start_daemon_windows_uses_detached_flags():
    with patch("platform.system", return_value="Windows"), \
         patch("subprocess.Popen") as mock_popen, \
         patch("driftshell.core.ollama_daemon._is_running", return_value=True), \
         patch("driftshell.core.ollama_daemon.console"):
        from driftshell.core.ollama_daemon import _start_daemon
        _start_daemon()

    kwargs = mock_popen.call_args[1]
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    assert kwargs["creationflags"] == DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP


def test_ensure_model_skips_if_present():
    mock_list = MagicMock(return_value={"models": [{"model": "gemma4:e4b"}]})
    with patch("ollama.list", mock_list), \
         patch("ollama.pull") as mock_pull:
        from driftshell.core.ollama_daemon import _ensure_model
        _ensure_model("gemma4:e4b")
    mock_pull.assert_not_called()
