"""
Prompt templates for the Email Generation Assistant.

Techniques used:
  - Role-Playing     : LLM is assigned a specific expert persona
  - Few-Shot Examples: 2 worked examples anchor expected quality
  - Chain-of-Thought : model is told to reason before writing
"""

# ─────────────────────────────────────────────
# ADVANCED SYSTEM PROMPT  (Model A — GPT-4o)
# ─────────────────────────────────────────────
SYSTEM_PROMPT_ADVANCED = """You are Alex Chen, a senior business communication specialist \
with 15 years of experience writing professional emails for Fortune 500 companies. \
Your emails are consistently praised for being clear, persuasive, and perfectly \
calibrated to the requested tone.

When writing an email you ALWAYS:
1. THINK first — consider the relationship context and desired outcome.
2. STRUCTURE — Subject line → Greeting → Body (all facts woven in naturally) → CTA → Sign-off.
3. CALIBRATE — Match vocabulary, sentence length, and formality exactly to the requested tone.
4. VERIFY — Every key fact from the input MUST appear naturally in the final email.
"""

# ─────────────────────────────────────────────
# FEW-SHOT EXAMPLES BLOCK
# ─────────────────────────────────────────────
FEW_SHOT_EXAMPLES = """
Below are two examples of excellent emails. Study them before writing your own.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLE 1
Intent : Follow up after a product demo
Facts  : Demo on March 5 | Product: ProjectPilot v2.0 | Pricing from $299/month | Free trial available
Tone   : casual

Subject: Quick follow-up on ProjectPilot 🚀

Hi Sarah,

Really enjoyed showing you ProjectPilot v2.0 last Tuesday! It was great to see how \
it could slot right into your team's workflow.

Just wanted to make sure you had everything you need — pricing kicks off at $299/month, \
and there's a free trial ready whenever you want to give it a proper spin with your team.

Any questions at all, just ping me.

Cheers,
Alex
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLE 2
Intent : Request a project deadline extension
Facts  : Current deadline June 30 | Requesting extension to July 15 | Reason: regulatory review delay | Project: Phase 2 Compliance Audit
Tone   : formal

Subject: Request for Extension — Phase 2 Compliance Audit

Dear Mr. Thompson,

I am writing with regard to the Phase 2 Compliance Audit, currently scheduled for \
completion on 30 June.

Due to an unforeseen delay in the external regulatory review process — a factor \
outside our direct control — I would like to respectfully request a two-week extension, \
moving the final delivery date to 15 July. This additional time will allow us to ensure \
all compliance documentation meets the highest standards of accuracy.

I remain fully committed to delivering a thorough and high-quality report and am happy \
to discuss this at your convenience.

Yours sincerely,
Alex Chen
Senior Compliance Specialist
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ─────────────────────────────────────────────
# ADVANCED USER PROMPT BUILDER  (Model A)
# ─────────────────────────────────────────────
def build_advanced_prompt(intent: str, facts: list[str], tone: str) -> str:
    facts_str = "\n".join(f"  • {f}" for f in facts)
    return f"""{FEW_SHOT_EXAMPLES}
Now it is your turn. Write an email for the following brief:

Intent : {intent}
Facts  :
{facts_str}
Tone   : {tone}

Before writing, reason through these steps (briefly):
  1. Who is likely receiving this email and what is our relationship?
  2. What specific vocabulary and sentence length signals a '{tone}' tone?
  3. How will I weave every fact into the email naturally?

Now write the complete email (include Subject line):
"""

# ─────────────────────────────────────────────
# SIMPLE SYSTEM PROMPT  (Model B — GPT-4o-mini zero-shot)
# ─────────────────────────────────────────────
SYSTEM_PROMPT_SIMPLE = (
    "You are a helpful assistant that writes professional emails."
)


def build_simple_prompt(intent: str, facts: list[str], tone: str) -> str:
    facts_str = "\n".join(f"- {f}" for f in facts)
    return f"""Write a professional email with the following details:

Intent: {intent}
Key facts to include:
{facts_str}
Tone: {tone}

Write the complete email including subject line:
"""
