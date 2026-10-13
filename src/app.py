"""Bootstrap entry point for the ai-movie-trailer-generator desktop tool."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer
from rich.console import Console

from src.core.pipeline import TrailerPipeline
from src.core.project import TrailerProject
from src.utils.config import load_config
from src.utils.logging import configure_logging

app = typer.Typer(
    name="trailergen",
    help="Generate a scored, cut, captioned movie trailer from your media pool.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def build(
    project: Path = typer.Option(..., "--project", "-p", help="Path to a .trailerproj file."),
    config: Path = typer.Option(Path("config/default.toml"), "--config", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan stages without rendering."),
) -> None:
    """Run the full trailer pipeline for a project."""
    cfg = load_config(config)
    configure_logging(cfg.app.log_level)
    log = logging.getLogger("trailergen.app")

    proj = TrailerProject.load(project)
    console.print(f"[bold]Project:[/] {proj.title}  [dim]({len(proj.media)} media items)[/]")

    pipeline = TrailerPipeline(cfg, proj)
    result = pipeline.run(dry_run=dry_run)

    if result.ok:
        console.print(f"[green]Trailer written:[/] {result.output_path}")
    else:
        console.print(f"[red]Pipeline failed at stage[/] {result.failed_stage}: {result.error}")
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Print the tool version."""
    from src import __version__

    console.print(f"ai-movie-trailer-generator {__version__}")


def main() -> None:
    try:
        app()
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted.[/]")
        sys.exit(130)


if __name__ == "__main__":
    main()