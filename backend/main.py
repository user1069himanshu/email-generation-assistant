"""
FastAPI backend for the Email Generation Assistant Chrome Extension.

Endpoints:
  GET  /health       — health check
  POST /generate     — generate an email
  POST /evaluate     — score a given email against metrics
"""

import sys
from pathlib import Path

# Ensure backend/ is on the path when run from repo root
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.generator import generate_email
from evaluation.metrics import compute_all_metrics

app = FastAPI(
    title="Email Generation Assistant API",
    description="GPT-4o powered email generator with custom evaluation metrics.",
    version="1.0.0",
)

# Allow Chrome extension origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ─── Request / Response models ────────────────────────────────────

class GenerateRequest(BaseModel):
    intent: str
    facts: list[str]
    tone: str
    model: str = "gpt-4o"
    strategy: str = "advanced"


class GenerateResponse(BaseModel):
    email: str
    model: str
    strategy: str


class EvaluateRequest(BaseModel):
    email: str
    facts: list[str]
    tone: str


# ─── Endpoints ────────────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
def health_check():
    return {"status": "ok", "service": "Email Generation Assistant API"}


@app.post("/generate", response_model=GenerateResponse, tags=["Generation"])
def generate(req: GenerateRequest):
    """Generate a professional email from intent, facts, and tone."""
    try:
        email = generate_email(
            intent=req.intent,
            facts=req.facts,
            tone=req.tone,
            model=req.model,
            strategy=req.strategy,
        )
        return GenerateResponse(email=email, model=req.model, strategy=req.strategy)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/evaluate", tags=["Evaluation"])
def evaluate(req: EvaluateRequest):
    """Score an email with the 3 custom metrics."""
    try:
        return compute_all_metrics(req.email, req.facts, req.tone)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
