"""
Model comparison report.

Reads reports/evaluation_results.json and prints:
  • A rich comparison table (per-metric averages for each model)
  • Winner / underperformer summary
  • Biggest failure scenario of the lower-performing model

Usage:
    python comparison/compare.py
"""

import json
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

REPORTS_DIR = Path(__file__).parent.parent / "reports"
JSON_PATH = REPORTS_DIR / "evaluation_results.json"

console = Console()

METRICS = [
    ("fact_fidelity", "Fact Fidelity"),
    ("communication_nuance", "Communication Nuance"),
    ("structural_clarity", "Structural Clarity"),
    ("avg_score", "Overall Average"),
]




def load_results() -> list[dict] | None:
    if not JSON_PATH.exists():
        console.print(
            f"[bold red]No results found at {JSON_PATH}.\n"
            "Run  python -m evaluation.evaluator  from the backend/ directory first.[/bold red]"
        )
        return None
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def compute_averages(results: list[dict]) -> dict[str, dict]:
    """Return per-model average scores across all metrics."""
    stats: dict[str, dict[str, list]] = {}
    for r in results:
        mn = r["model_name"]
        if mn not in stats:
            stats[mn] = {k: [] for k, _ in METRICS}
        for k, _ in METRICS:
            val = r.get(k)
            if val is not None and val != "":
                stats[mn][k].append(float(val))
    return {
        mn: {k: round(sum(v) / len(v), 4) if v else None for k, v in data.items()}
        for mn, data in stats.items()
    }


def find_worst_scenario(results: list[dict], model_name: str) -> dict:
    losing_results = [r for r in results if r["model_name"] == model_name]
    return min(losing_results, key=lambda r: r["avg_score"])


def print_comparison() -> None:
    results = load_results()
    if not results:
        sys.exit(1)

    averages = compute_averages(results)
    model_names = list(averages.keys())

    # ── Comparison Table ──────────────────────────────────────────
    table = Table(
        title="Email Generation Assistant - Model Comparison",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Metric", style="bold white", no_wrap=True, min_width=28)
    for mn in model_names:
        table.add_column(mn, justify="center", min_width=20)

    for metric_key, metric_label in METRICS:
        row_scores = [averages[mn].get(metric_key) for mn in model_names]
        valid_scores = [s for s in row_scores if s is not None]
        best_val = max(valid_scores) if valid_scores else None
        
        cells = []
        for score in row_scores:
            if score is None:
                cells.append("[dim]N/A[/dim]")
            elif score == best_val:
                cells.append(f"[bold green]{score:.4f}[/bold green]")
            else:
                cells.append(f"[dim]{score:.4f}[/dim]")
                
        if valid_scores:  # Only add if at least one model has score
            table.add_row(metric_label, *cells)

    console.print()
    console.print(table)

    # ── Winner / Loser Analysis ───────────────────────────────────
    winner = max(averages, key=lambda mn: averages[mn].get("avg_score") or 0.0)
    loser = min(averages, key=lambda mn: averages[mn].get("avg_score") or 0.0)
    worst = find_worst_scenario(results, loser)

    gap = round(
        (averages[winner].get("avg_score") or 0.0) - (averages[loser].get("avg_score") or 0.0), 4
    )

    console.print(
        Panel.fit(
            f"[bold green]Winner:[/bold green] {winner}\n"
            f"   Overall avg: [green]{averages[winner].get('avg_score') or 0:.4f}[/green]\n\n"
            f"[bold red]Underperformer:[/bold red] {loser}\n"
            f"   Overall avg: [red]{averages[loser].get('avg_score') or 0:.4f}[/red]  "
            f"(gap: {gap:.4f})\n\n"
            f"[bold yellow]Biggest failure of '{loser}':[/bold yellow]\n"
            f"   Scenario #{worst['scenario_id']}: \"{worst['intent']}\"\n"
            f"   Tone: {worst['tone']} | "
            f"Fact Fidelity: {worst['fact_fidelity']} | "
            f"Communication Nuance: {worst['communication_nuance']} | "
            f"Structural Clarity: {worst['structural_clarity']} | "
            f"[bold cyan]Production Recommendation:[/bold cyan]\n"
            f"   Use [bold]{winner}[/bold]. Advanced prompting (Role-Play + Few-Shot + CoT)\n"
            f"   consistently yields higher fact recall and tone fidelity, which are\n"
            f"   the most critical quality signals for professional email generation.",
            title="[bold]Analysis Summary[/bold]",
            border_style="bright_blue",
        )
    )
    console.print()


if __name__ == "__main__":
    print_comparison()
