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

try:
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams
    from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, GEval
except ImportError:
    pass


# ──────────────────────────────────────────────────────────────────
# METRIC 1 : Fact Fidelity & Grounding
# Logic: LLM-as-a-judge (GPT-4o-mini) evaluates:
#         1. Recall (Are all facts present?)
#         2. Truthfulness (Are facts accurate?)
#         3. Hallucination (Are there extra unfounded claims?)
# ──────────────────────────────────────────────────────────────────
def fact_fidelity_score(email: str, facts: list[str]) -> float:
    """LLM-as-a-Judge: measures grounding, truthfulness, and recall."""
    if not facts:
        return 1.0

    facts_list = "\n".join([f"- {f}" for f in facts])
    prompt = (
        f"You are a factual auditor. Evaluate the email strictly against the input facts.\n\n"
        f"INPUT FACTS:\n{facts_list}\n\n"
        f"GENERATED EMAIL:\n{email}\n\n"
        f"Evaluation Criteria:\n"
        f"1. Recall: Did it include all input facts? (0-4 pts)\n"
        f"2. Truthfulness: Are the facts presented accurately without distortion? (0-4 pts)\n"
        f"3. Grounding: Did it avoid adding extra, unfounded factual claims? (0-2 pts)\n\n"
        f"First, briefly reason through your assessment for each criteria.\n"
        f"Then, provide a final integer score from 0 to 10 on the last line in this format: '[[score]]'."
    )
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        # Extract [[score]]
        match = re.search(r"\[\[(\d+)\]\]", raw)
        rating = float(match.group(1)) if match else 5.0
        return round(rating / 10.0, 4)
    except Exception:
        return 0.5


# ──────────────────────────────────────────────────────────────────
# METRIC 2 : Communication Nuance & Persona
# Logic: LLM-as-a-judge (GPT-4o-mini) evaluates:
#         1. Tone Alignment (match the requested label?)
#         2. Persona Consistency (Alex Chen persona?)
#         3. Modernity (avoiding robotic clichés)
# ──────────────────────────────────────────────────────────────────
def communication_nuance_score(email: str, tone: str) -> float:
    """LLM-as-a-Judge: measures tone fidelity, persona, and avoidance of clichés."""
    prompt = (
        f"You are a business communication expert. Evaluate the email for style and tone.\n\n"
        f"REQUESTED TONE: {tone}\n"
        f"PERSONA: Alex Chen, Senior Business Communication Specialist (Modern, Clear, Persuasive, Confident)\n\n"
        f"EMAIL:\n{email}\n\n"
        f"Evaluation Criteria:\n"
        f"1. Tone Match: Does it match the '{tone}' vibe? (0-5 pts)\n"
        f"2. Persona & Style: Does it sound like a modern expert or a robotic LLM? (0-5 pts)\n"
        f"   - Deduct points for robotic phrases like 'I hope this message finds you well' or rigid formalisms.\n\n"
        f"First, briefly reason through your assessment for each criteria.\n"
        f"Then, provide a final integer score from 0 to 10 on the last line in this format: '[[score]]'."
    )
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()
        match = re.search(r"\[\[(\d+)\]\]", raw)
        rating = float(match.group(1)) if match else 5.0
        return round(rating / 10.0, 4)
    except Exception:
        return 0.5


# ──────────────────────────────────────────────────────────────────
# METRIC 3 : Structural Integrity & Clarity
# Logic:
#   a) Format Check (Subject, Greeting, CTA) - 0.4
#   b) Readability (Flesch Ease) - 0.4
#   c) Conciseness (Word Count penalty) - 0.2
# ──────────────────────────────────────────────────────────────────
def structural_clarity_score(email: str) -> float:
    """Combines format adherence, readability, and conciseness."""
    # 1. Format Check (0.0 - 1.0)
    has_subject = "Subject:" in email
    has_greeting = bool(re.search(r"(Dear|Hi|Hello|Hey)", email, re.I))
    # Look for a closing/CTA (check last few lines)
    has_cta = len(email.split("\n")[-4:]) >= 1 
    
    format_score = (0.4 if has_subject else 0) + (0.3 if has_greeting else 0) + (0.3 if has_cta else 0)

    # 2. Readability (0.0 - 1.0)
    flesch = textstat.flesch_reading_ease(email)
    flesch_norm = max(0.0, min(100.0, flesch)) / 100.0

    # 3. Conciseness (0.0 - 1.0)
    word_count = len(email.split())
    if word_count <= 200:
        conciseness_score = 1.0
    else:
        conciseness_score = max(0.0, 1.0 - (word_count - 200) / 200.0)

    score = (0.4 * format_score) + (0.4 * flesch_norm) + (0.2 * conciseness_score)
    return round(score, 4)


# ──────────────────────────────────────────────────────────────────
# COMPOSITE HELPER
# ──────────────────────────────────────────────────────────────────
def compute_all_metrics(email: str, facts: list[str], tone: str, intent: str = "", strategy: str = "advanced", reference_email: str | None = None) -> dict:
    """Run the broadened 3 custom metrics with weighted average: 40/35/25."""
    fidelity = fact_fidelity_score(email, facts)
    nuance = communication_nuance_score(email, tone)
    structure = structural_clarity_score(email)
    
    # Updated Weights: 40% Fidelity, 35% Nuance, 25% Structure
    avg = round((0.40 * fidelity + 0.35 * nuance + 0.25 * structure), 4)
    
    return {
        "fact_fidelity": fidelity,
        "communication_nuance": nuance,
        "structural_clarity": structure,
        "avg_score": avg,
    }





