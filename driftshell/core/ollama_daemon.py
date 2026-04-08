from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager

from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns

from driftshell.utils.console import console, print_success, print_warning


# ── helpers ──────────────────────────────────────────────────────────────────

def _is_installed() -> bool:
    return shutil.which("ollama") is not None


def _is_running() -> bool:
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False


@contextmanager
def _first_time_spinner(message: str, note: str = ""):
    """Show a clean animated panel while a background task runs."""
    spinner = Spinner("dots", style="drift.blue")

    def _render():
        body = Text.assemble(
            (message + "\n", "bold"),
            (note, "dim") if note else ("", ""),
        )
        return Panel(
            Columns([spinner, body]),
            title="[bold drift.blue]First-time setup[/bold drift.blue]",
            border_style="drift.blue",
            padding=(0, 1),
        )

    with Live(_render(), console=console, refresh_per_second=12, transient=True) as live:
        yield live
        live.update(_render())


# ── install ───────────────────────────────────────────────────────────────────

def _install() -> None:
    system = platform.system()

    if system == "Darwin":
        if shutil.which("brew"):
            with _first_time_spinner(
                "Installing Ollama via Homebrew…",
                "This only happens once. Grab a coffee ☕",
            ):
                subprocess.run(
                    ["brew", "install", "ollama"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        else:
            console.print(
                "\n[yellow]Please install Ollama manually:[/yellow]\n\n"
                "  1. Install Homebrew: [cyan]https://brew.sh[/cyan]\n"
                "     then: [cyan]brew install ollama[/cyan]\n\n"
                "  2. Or download the macOS app: [cyan]https://ollama.com/download[/cyan]\n\n"
                "Re-run [cyan]drift[/cyan] after Ollama is installed."
            )
            sys.exit(1)

    elif system == "Linux":
        pkg_cmds = [
            (["snap", "install", "ollama", "--classic"], shutil.which("snap")),
            (["apt-get", "install", "-y", "ollama"], shutil.which("apt-get")),
        ]
        for cmd, available in pkg_cmds:
            if available:
                with _first_time_spinner(
                    f"Installing Ollama via {cmd[0]}…",
                    "This only happens once.",
                ):
                    subprocess.run(
                        cmd, check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                break
        else:
            console.print(
                "\n[yellow]Please install Ollama manually:[/yellow]\n\n"
                "  [cyan]https://ollama.com/download/linux[/cyan]\n\n"
                "Re-run [cyan]drift[/cyan] after Ollama is installed."
            )
            sys.exit(1)

    elif system == "Windows":
        with _first_time_spinner(
            "Installing Ollama…",
            "This only happens once.",
        ):
            _install_windows()

    else:
        console.print(
            f"[red]Unsupported platform: {system}. "
            "Install Ollama from https://ollama.com then re-run drift.[/red]"
        )
        sys.exit(1)

    if not _is_installed():
        console.print("[red]Ollama installation failed. Install manually from https://ollama.com[/red]")
        sys.exit(1)

    print_success("Ollama installed.")


# ── Windows install ───────────────────────────────────────────────────────────

def _install_windows() -> None:
    """
    Download the official OllamaSetup.exe via PowerShell and run it silently.
    Requires PowerShell 5+ (ships with Windows 10/11).
    """
    import tempfile
    from pathlib import Path

    installer = Path(tempfile.gettempdir()) / "OllamaSetup.exe"
    download_url = "https://ollama.com/download/OllamaSetup.exe"

    console.print("[dim]Downloading OllamaSetup.exe...[/dim]")
    subprocess.run(
        [
            "powershell", "-NoProfile", "-NonInteractive", "-Command",
            f"Invoke-WebRequest -Uri '{download_url}' -OutFile '{installer}' -UseBasicParsing",
        ],
        check=True,
    )

    console.print("[dim]Running installer silently...[/dim]")
    # /S = silent install (NSIS flag used by Ollama's Windows installer)
    subprocess.run([str(installer), "/S"], check=True)

    # Ollama adds itself to %LOCALAPPDATA%\Programs\Ollama — refresh PATH for this process
    local_app = os.environ.get("LOCALAPPDATA", "")
    ollama_bin = os.path.join(local_app, "Programs", "Ollama")
    if ollama_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ollama_bin + os.pathsep + os.environ.get("PATH", "")


# ── daemon ────────────────────────────────────────────────────────────────────

def _start_daemon() -> None:
    """Start `ollama serve` as a detached background process."""

    if platform.system() == "Windows":
        # On Windows use DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP so the
        # server keeps running after PowerShell closes the parent process.
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        )
    else:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    # Wait up to 10 s for the server to come up
    with _first_time_spinner("Starting Ollama in background…"):
        for _ in range(20):
            time.sleep(0.5)
            if _is_running():
                return

    print_warning("Ollama didn't respond in time. Run `ollama serve` manually if commands fail.")


# ── model pull ────────────────────────────────────────────────────────────────

def _ensure_model(model: str) -> None:
    import ollama as _ollama

    available = {m["model"] for m in _ollama.list().get("models", [])}
    # Normalise: ollama stores names like "gemma4:e4b", strip digest suffix
    available_base = {m.split("@")[0] for m in available}

    if model in available_base:
        return

    from rich.progress import Progress, BarColumn, DownloadColumn, TimeRemainingColumn, TextColumn

    progress = Progress(
        TextColumn("[bold drift.blue]Downloading {task.description}"),
        BarColumn(bar_width=32, style="drift.blue", complete_style="drift.green"),
        DownloadColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )

    console.print(
        Panel(
            f"[bold]Downloading model:[/bold] [cyan]{model}[/cyan]\n\n"
            "[dim]This only happens once — future runs start instantly.[/dim]",
            title="[bold drift.blue]First-time setup[/bold drift.blue]",
            border_style="drift.blue",
        )
    )

    with progress:
        task = progress.add_task(model, total=None)
        for chunk in _ollama.pull(model, stream=True):
            completed = chunk.get("completed")
            total = chunk.get("total")
            if total:
                progress.update(task, total=total, completed=completed or 0)

    print_success(f"Model {model} ready.")


# ── public entry point ────────────────────────────────────────────────────────

def ensure_ollama(model: str) -> None:
    """
    Called at bootstrap. Guarantees that:
      1. Ollama is installed
      2. Ollama daemon is running in the background
      3. The required model is pulled
    """
    if not _is_installed():
        _install()

    if not _is_running():
        _start_daemon()

    _ensure_model(model)
