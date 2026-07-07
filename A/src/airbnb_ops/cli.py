from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.table import Table

from airbnb_ops.config import PipelineConfig
from airbnb_ops.extract import read_csv_checked
from airbnb_ops.pii import handle_pii
from airbnb_ops.transform import build_neighbourhood_summary
from airbnb_ops.validate import validate_summary

console = Console()

# needed because 'run' clashes with typer's own run method
run_app = typer.Typer(invoke_without_command=True)
app = typer.Typer(no_args_is_help=True)
app.add_typer(run_app, name="run")


def _generate_report(config, summary_rows, neighbourhoods, start_time, end_time):
    duration = (end_time - start_time).total_seconds()
    report = f"""# HW01-A Run Report

**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}

## Pipeline Summary

| Metric | Value |
|--------|-------|
| Input listings path | `{config.listings_path}` |
| Input segments path | `{config.segments_path}` |
| Output path | `{config.output_path}` |
| Neighbourhoods | {summary_rows} |
| Duration (s) | {duration:.2f} |

## Neighbourhoods

"""
    for n in neighbourhoods:
        report += f"- {n}\n"
    report += "\n## Validation\n\nAll validation checks passed.\n"
    return report


@run_app.callback()
def execute_pipeline():
    config = PipelineConfig()
    start_time = datetime.now(timezone.utc)

    console.print("[bold blue]Airbnb Ops Pipeline[/bold blue]")
    console.print(f"Reading listings from [green]{config.listings_path}[/green]")
    listings = read_csv_checked(config.listings_path)

    console.print(f"Reading segments from [green]{config.segments_path}[/green]")
    segments = read_csv_checked(config.segments_path)

    console.print("[yellow]Handling PII...[/yellow]")
    clean = handle_pii(listings)

    console.print("[yellow]Building neighbourhood summary...[/yellow]")
    summary = build_neighbourhood_summary(clean, segments)

    console.print("[yellow]Validating output...[/yellow]")
    validate_summary(summary)
    console.print("[green]Validation passed.[/green]")

    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.output_path, index=False)
    console.print(f"Output written to [green]{config.output_path}[/green]")

    end_time = datetime.now(timezone.utc)
    neighbourhoods = summary["neighbourhood"].tolist()
    report_content = _generate_report(
        config, len(summary), neighbourhoods, start_time, end_time
    )

    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    config.report_path.write_text(report_content)
    console.print(f"Report written to [green]{config.report_path}[/green]")

    table = Table(title="Neighbourhood Summary")
    for col in summary.columns:
        table.add_column(col, style="cyan")
    for _, row in summary.iterrows():
        table.add_row(*[str(v) for v in row])
    console.print(table)