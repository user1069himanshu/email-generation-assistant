"""
Email generator — wraps OpenAI chat completions.
Supports two strategies:
  advanced   : Role-Play + Few-Shot + CoT         (recommended, Model A)
  thoughtful : Structured CoT + Constraints       (baseline, Model B)
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

from .schemas import EmailBlueprint, GeneratedEmail

from .prompts import (
    SYSTEM_PROMPT_ADVANCED,
    SYSTEM_PROMPT_THOUGHTFUL,
    build_advanced_prompt,
    build_thoughtful_prompt,
    SYSTEM_PROMPT_PLANNER,
    SYSTEM_PROMPT_WRITER,
    build_blueprint_prompt,
    build_writer_prompt,
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_email(
    intent: str,
    facts: list[str],
    tone: str,
    model: str = "gpt-4o",
    strategy: str = "advanced",
    context_email: str = "",
) -> str:
    """
    Generate a professional email.

    Args:
        intent   : Core purpose of the email.
        facts    : List of key facts to include.
        tone     : Desired tone (formal, casual, urgent, empathetic, …).
        model    : OpenAI model name.
        strategy : "advanced" or "thoughtful".

    Returns:
        Generated email text (subject line included).
    """
    if strategy == "chained":
        # --- STEP 1: GENERATE BLUEPRINT (Structured) ---
        blueprint_resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_PLANNER.format(tone=tone)},
                {"role": "user", "content": build_blueprint_prompt(intent, context_email, tone)},
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        blueprint_json = blueprint_resp.choices[0].message.content.strip()
        blueprint_obj = EmailBlueprint.model_validate_json(blueprint_json)

        # --- STEP 2: GENERATE FINAL EMAIL (Structured) ---
        writer_resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_WRITER},
                {"role": "user", "content": build_writer_prompt(blueprint_obj.model_dump_json(), tone)},
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        email_json = writer_resp.choices[0].message.content.strip()
        email_obj = GeneratedEmail.model_validate_json(email_json)
        
        return f"Subject: {email_obj.subject}\n\n{email_obj.body}".strip()

    elif strategy == "advanced":
        system_prompt = SYSTEM_PROMPT_ADVANCED
        user_prompt = build_advanced_prompt(intent, facts, tone)
    else:
        system_prompt = SYSTEM_PROMPT_THOUGHTFUL
        user_prompt = build_thoughtful_prompt(intent, facts, tone)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=900,
    )
    content = response.choices[0].message.content.strip()
    # Strip out any pre-written reasoning by finding the start of the email
    if "Subject:" in content:
        content = "Subject:" + content.split("Subject:", 1)[1]
    return content.strip()
