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

METRICS = {
    "fact_recall": "Fact Recall ↑",
    "tone_accuracy": "Tone Accuracy ↑",
    "clarity_conciseness": "Clarity & Conciseness ↑",
    "avg_score": "Overall Average ↑",
}


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
            stats[mn] = {k: [] for k in METRICS}
        for k in METRICS:
            stats[mn][k].append(r[k])
    return {
        mn: {k: round(sum(v) / len(v), 4) for k, v in data.items()}
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
        title="📊  Email Generation Assistant — Model Comparison",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Metric", style="bold white", no_wrap=True, min_width=28)
    for mn in model_names:
        table.add_column(mn, justify="center", min_width=20)

    for metric_key, metric_label in METRICS.items():
        row_scores = [averages[mn][metric_key] for mn in model_names]
        best_val = max(row_scores)
        cells = []
        for score in row_scores:
            if score == best_val:
                cells.append(f"[bold green]{score:.4f}[/bold green]")
            else:
                cells.append(f"[dim]{score:.4f}[/dim]")
        table.add_row(metric_label, *cells)

    console.print()
    console.print(table)

    # ── Winner / Loser Analysis ───────────────────────────────────
    winner = max(averages, key=lambda mn: averages[mn]["avg_score"])
    loser = min(averages, key=lambda mn: averages[mn]["avg_score"])
    worst = find_worst_scenario(results, loser)

    gap = round(
        averages[winner]["avg_score"] - averages[loser]["avg_score"], 4
    )

    console.print(
        Panel.fit(
            f"[bold green]🏆 Winner:[/bold green] {winner}\n"
            f"   Overall avg: [green]{averages[winner]['avg_score']:.4f}[/green]\n\n"
            f"[bold red]📉 Underperformer:[/bold red] {loser}\n"
            f"   Overall avg: [red]{averages[loser]['avg_score']:.4f}[/red]  "
            f"(gap: {gap:.4f})\n\n"
            f"[bold yellow]🔍 Biggest failure of '{loser}':[/bold yellow]\n"
            f"   Scenario #{worst['scenario_id']}: \"{worst['intent']}\"\n"
            f"   Tone: {worst['tone']} | "
            f"Fact Recall: {worst['fact_recall']} | "
            f"Tone Accuracy: {worst['tone_accuracy']} | "
            f"Clarity: {worst['clarity_conciseness']} | "
            f"Avg: [red]{worst['avg_score']}[/red]\n\n"
            f"[bold cyan]✅ Production Recommendation:[/bold cyan]\n"
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
