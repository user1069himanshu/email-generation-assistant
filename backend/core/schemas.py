from typing import List
from pydantic import BaseModel, Field

# --- CALL 1: PLANNER OUTPUT SCHEMA ---
class EmailBlueprint(BaseModel):
    recipient_name: str = Field(..., description="The name of the person being replied to. Use 'Team' if unknown or generic.")
    context_analysis: str = Field(..., description="Analysis of the incoming email and user intent.")
    tone_calibration: str = Field(..., description="Description of the specific vocabulary and style to use.")
    core_arguments: List[str] = Field(..., description="List of specific points that MUST be included in the reply.")
    narrative_flow: List[str] = Field(..., description="Step-by-step sequence of the email sections (e.g., Opening, Body, CTA).")

# --- CALL 2: WRITER OUTPUT SCHEMA ---
class GeneratedEmail(BaseModel):
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The full body of the email, excluding the subject line and any signature.")
