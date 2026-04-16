"""
Evaluation orchestrator.

Runs all 10 test scenarios × 2 model configurations, computes metrics,
and saves results to reports/evaluation_results.{csv,json}.

Usage:
    cd backend
    python -m evaluation.evaluator
"""

import csv
import json
import sys
from pathlib import Path

from tqdm import tqdm

# Allow running as __main__ from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.generator import generate_email
from evaluation.metrics import compute_all_metrics
from evaluation.test_scenarios import SCENARIOS

# ─── Model configurations ─────────────────────────────────────────
MODELS = [
    {
        "name": "GPT-4o (Advanced Prompting)",
        "model": "gpt-4o",
        "strategy": "advanced",
    },
    {
        "name": "GPT-4o-mini (Zero-Shot)",
        "model": "gpt-4o-mini",
        "strategy": "simple",
    },
]

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"
CSV_PATH = REPORTS_DIR / "evaluation_results.csv"
JSON_PATH = REPORTS_DIR / "evaluation_results.json"

FIELDNAMES = [
    "scenario_id",
    "intent",
    "tone",
    "model_name",
    "model",
    "strategy",
    "fact_recall",
    "tone_accuracy",
    "clarity_conciseness",
    "avg_score",
    "generated_email",
]


def run_evaluation() -> list[dict]:
    """Run full evaluation and return list of result dicts."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    total = len(SCENARIOS) * len(MODELS)
    pbar = tqdm(total=total, desc="Evaluating", unit="run")

    for scenario in SCENARIOS:
        for cfg in MODELS:
            pbar.set_postfix(
                scenario=scenario["id"], model=cfg["name"][:20]
            )
            email = generate_email(
                intent=scenario["intent"],
                facts=scenario["facts"],
                tone=scenario["tone"],
                model=cfg["model"],
                strategy=cfg["strategy"],
            )
            metrics = compute_all_metrics(
                email, scenario["facts"], scenario["tone"]
            )
            results.append(
                {
                    "scenario_id": scenario["id"],
                    "intent": scenario["intent"],
                    "tone": scenario["tone"],
                    "model_name": cfg["name"],
                    "model": cfg["model"],
                    "strategy": cfg["strategy"],
                    **metrics,
                    "generated_email": email,
                }
            )
            pbar.update(1)

    pbar.close()

    # Save CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    # Save JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Evaluation complete!")
    print(f"   CSV  → {CSV_PATH}")
    print(f"   JSON → {JSON_PATH}")
    return results


if __name__ == "__main__":
    run_evaluation()
