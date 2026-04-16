"""
Custom evaluation metrics for the Email Generation Assistant.

Metric 1 — Fact Recall Score      (automated, keyword-matching)
Metric 2 — Tone Accuracy Score     (LLM-as-a-Judge via GPT-4o-mini)
Metric 3 — Clarity & Conciseness   (automated, textstat + length penalty)
"""

import os
import re

import textstat
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ──────────────────────────────────────────────────────────────────
# METRIC 1 : Fact Recall Score
# Logic: For each fact, extract meaningful keywords (≥4 chars).
#         A fact is "recalled" if ≥50% of its keywords appear in
#         the generated email (case-insensitive).
#         score = recalled_facts / total_facts  →  0.0 – 1.0
# ──────────────────────────────────────────────────────────────────
def fact_recall_score(email: str, facts: list[str]) -> float:
    """Fraction of input facts successfully recalled in the email."""
    if not facts:
        return 1.0

    email_lower = email.lower()
    matched = 0

    for fact in facts:
        keywords = [w.lower() for w in re.findall(r"\b\w{4,}\b", fact)]
        if not keywords:
            matched += 1  # trivially empty fact
            continue
        hits = sum(1 for kw in keywords if kw in email_lower)
        if hits / len(keywords) >= 0.5:
            matched += 1

    return round(matched / len(facts), 4)


# ──────────────────────────────────────────────────────────────────
# METRIC 2 : Tone Accuracy Score
# Logic: Ask GPT-4o-mini to rate how well the email matches the
#         requested tone on a 1-10 scale.
#         score = rating / 10  →  0.0 – 1.0
# ──────────────────────────────────────────────────────────────────
def tone_accuracy_score(email: str, tone: str) -> float:
    """LLM-as-a-Judge: how accurately does the email match the requested tone?"""
    prompt = (
        f"You are an expert in business communication.\n\n"
        f"Rate how accurately the following email matches a '{tone}' tone.\n"
        f"Respond with ONLY a single integer from 1 to 10:\n"
        f"  1 = completely wrong tone\n"
        f" 10 = perfectly matches the '{tone}' tone\n\n"
        f"Email:\n{email}\n\n"
        f"Rating (1-10):"
    )
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5,
        )
        raw = response.choices[0].message.content.strip()
        numbers = re.findall(r"\d+\.?\d*", raw)
        rating = float(numbers[0]) if numbers else 5.0
        rating = max(1.0, min(10.0, rating))
        return round(rating / 10.0, 4)
    except Exception:
        return 0.5  # neutral fallback on API error


# ──────────────────────────────────────────────────────────────────
# METRIC 3 : Clarity & Conciseness Score
# Logic:
#   a) Flesch Reading Ease (textstat) — higher = easier to read.
#      Normalised to 0–1 (clamped to 0–100 range).
#   b) Length penalty — ideal email is ≤200 words; score degrades
#      linearly for emails longer than 200 words, hitting 0 at 400.
#   Combined: 0.6 × flesch_norm + 0.4 × length_score  →  0.0 – 1.0
# ──────────────────────────────────────────────────────────────────
def clarity_conciseness_score(email: str) -> float:
    """Automated clarity (Flesch) + conciseness (length penalty)."""
    word_count = len(email.split())
    flesch = textstat.flesch_reading_ease(email)

    # Normalise Flesch score
    flesch_norm = max(0.0, min(100.0, flesch)) / 100.0

    # Length penalty
    if word_count <= 200:
        length_score = 1.0
    else:
        length_score = max(0.0, 1.0 - (word_count - 200) / 200.0)

    score = 0.6 * flesch_norm + 0.4 * length_score
    return round(score, 4)


# ──────────────────────────────────────────────────────────────────
# COMPOSITE HELPER
# ──────────────────────────────────────────────────────────────────
def compute_all_metrics(email: str, facts: list[str], tone: str) -> dict:
    """Run all three metrics and return a dict including the average."""
    fact_recall = fact_recall_score(email, facts)
    tone_acc = tone_accuracy_score(email, tone)
    clarity = clarity_conciseness_score(email)
    avg = round((fact_recall + tone_acc + clarity) / 3.0, 4)
    return {
        "fact_recall": fact_recall,
        "tone_accuracy": tone_acc,
        "clarity_conciseness": clarity,
        "avg_score": avg,
    }
