from datetime import datetime
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from model.result import Result

console = Console()


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log_stage(step: str, title: str, subtitle: str = "") -> None:
    content = subtitle if subtitle else ""
    console.print(Panel(
        content,
        title=f"[bold cyan]{step}[/bold cyan] [bold white]{title}[/bold white]",
        border_style="cyan",
        padding=(0, 1),
    ))


def log_success(msg: str) -> None:
    console.print(f"[{_now()}] [bold green]✓[/bold green] {msg}")


def log_error(msg: str) -> None:
    console.print(f"[{_now()}] [bold red]✗[/bold red] {msg}")


def log_info(msg: str) -> None:
    console.print(f"[{_now()}] [bold blue]·[/bold blue] {msg}")


def log_warning(msg: str) -> None:
    console.print(f"[{_now()}] [bold yellow]![/bold yellow] {msg}")


def print_summary(databases_result: List[Result], db_names: List[str]) -> None:
    table = Table(box=box.ROUNDED, border_style="cyan", show_header=True, header_style="bold cyan")
    table.add_column("Banco", style="white", min_width=20)
    table.add_column("Status", justify="center", min_width=8)
    table.add_column("Linhas", justify="right", min_width=8)
    table.add_column("Erro", style="dim", min_width=20)

    total_rows = 0
    successes = 0
    failures = 0

    for name, result in zip(db_names, databases_result):
        if result.collected:
            rows = len(result.data)
            total_rows += rows
            successes += 1
            table.add_row(name, "[green]✓[/green]", str(rows), "—")
        else:
            failures += 1
            error_msg = result.error or "erro desconhecido"
            table.add_row(name, "[red]✗[/red]", "—", f"[red]{error_msg}[/red]")

    footer = (
        f"[bold]Total:[/bold] {len(databases_result)} banco(s)  |  "
        f"[green]{successes} sucesso[/green]  |  "
        f"[red]{failures} falha[/red]  |  "
        f"[cyan]{total_rows} linhas[/cyan]"
    )

    console.print(Panel(
        table,
        title="[bold cyan][5/5][/bold cyan] [bold white]Resumo[/bold white]",
        border_style="cyan",
        subtitle=footer,
        padding=(0, 1),
    ))
