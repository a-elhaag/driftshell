from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

# Brand color palette
DRIFT_THEME = Theme({
    "drift.blue": "#58a6ff",
    "drift.green": "#3fb950",
    "drift.amber": "#d29922",
    "drift.red": "#f85149",
    "drift.muted": "#8b949e",
})

console = Console(theme=DRIFT_THEME)

# ASCII logo
DRIFT_LOGO = """
██████╗ ██████╗ ██╗███████╗████████╗
██╔══██╗██╔══██╗██║██╔════╝╚══██╔══╝
██║  ██║██████╔╝██║█████╗     ██║
██║  ██║██╔══██╗██║██╔══╝     ██║
██████╔╝██║  ██║██║██║        ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝        ╚═╝
"""


def print_logo() -> None:
    """Print DRIFT ASCII logo in brand blue."""
    console.print(f"[drift.blue]{DRIFT_LOGO}[/drift.blue]")


def print_repl_banner() -> None:
    """Print REPL welcome banner."""
    print_logo()
    console.print("[drift.muted]Type your request. Ctrl+C or 'exit' to quit.[/drift.muted]\n")


def print_ai_prefix() -> None:
    """Print D > prefix for AI output."""
    console.print("[bold drift.blue]D >[/bold drift.blue]", end=" ")


def print_command(cmd: str) -> None:
    syntax = Syntax(cmd, "bash", theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title="[bold drift.blue]Command[/bold drift.blue]", border_style="drift.blue"))


def print_explain(explanation: str) -> None:
    console.print(Panel(explanation, title="[bold drift.green]Explanation[/bold drift.green]", border_style="drift.green"))


def print_risk(score: int) -> None:
    if score >= 7:
        color = "bold drift.red"
    elif score >= 4:
        color = "bold drift.amber"
    else:
        color = "bold drift.green"
    console.print(f"[{color}]Risk score: {score}/10[/{color}]")


def print_error(msg: str) -> None:
    console.print(f"[bold drift.red]Error:[/bold drift.red] {msg}")


def print_success(msg: str) -> None:
    console.print(f"[bold drift.green]✓[/bold drift.green] {msg}")


def print_warning(msg: str) -> None:
    console.print(f"[bold drift.amber]Warning:[/bold drift.amber] {msg}")


def print_blocked(pattern: str) -> None:
    console.print(
        Panel(
            f"[bold drift.red]Blocked:[/bold drift.red] matched destructive pattern [drift.amber]{pattern}[/drift.amber]",
            title="[bold drift.red]Safety Block[/bold drift.red]",
            border_style="drift.red",
        )
    )


def print_output(stdout: str, stderr: str, exit_code: int) -> None:
    if stdout:
        console.print(Text(stdout.rstrip()))
    if stderr:
        console.print(f"[dim drift.red]{stderr.rstrip()}[/dim drift.red]")
    if exit_code != 0:
        console.print(f"[dim]Exit code: {exit_code}[/dim]")
