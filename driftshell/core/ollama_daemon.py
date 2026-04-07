from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time

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


# ── install ───────────────────────────────────────────────────────────────────

def _install() -> None:
    system = platform.system()
    console.print("[bold cyan]Ollama not found — installing...[/bold cyan]")

    if system == "Darwin":
        # Prefer Homebrew if available
        if shutil.which("brew"):
            subprocess.run(["brew", "install", "ollama"], check=True)
        else:
            # Official install script
            subprocess.run(
                ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
                check=True,
            )

    elif system == "Linux":
        subprocess.run(
            ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
            check=True,
        )

    elif system == "Windows":
        _install_windows()

    else:
        console.print(f"[red]Unsupported platform: {system}. Install Ollama manually from https://ollama.com[/red]")
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
    console.print("[dim]Starting Ollama daemon in background...[/dim]")

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
    for _ in range(20):
        time.sleep(0.5)
        if _is_running():
            print_success("Ollama daemon started.")
            return

    print_warning(
        "Ollama daemon did not respond in time. "
        "Run `ollama serve` manually if commands fail."
    )


# ── model pull ────────────────────────────────────────────────────────────────

def _ensure_model(model: str) -> None:
    import ollama as _ollama

    available = {m["model"] for m in _ollama.list().get("models", [])}
    # Normalise: ollama stores names like "gemma4:e4b", strip digest suffix
    available_base = {m.split("@")[0] for m in available}

    if model in available_base:
        return

    console.print(f"[bold cyan]Model [yellow]{model}[/yellow] not found — pulling...[/bold cyan]")
    console.print("[dim](This only happens once)[/dim]")

    # Stream pull progress
    import ollama as _ollama
    for chunk in _ollama.pull(model, stream=True):
        status_msg = chunk.get("status", "")
        completed = chunk.get("completed")
        total = chunk.get("total")
        if completed and total:
            pct = int(completed / total * 100)
            console.print(f"[dim]{status_msg}: {pct}%[/dim]", end="\r")
        elif status_msg:
            console.print(f"[dim]{status_msg}[/dim]", end="\r")

    console.print()  # newline after progress
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
