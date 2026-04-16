# Email Generation Assistant

> An AI-powered Chrome Extension that generates professional emails from a three-line brief — powered by GPT-4o with advanced prompt engineering.

---

## Features

- **Chrome Extension** with a polished dark-mode popup (works inside Gmail)
- **One-click Gmail insertion** — generated email drops straight into your compose window
- **Advanced prompting** — Role-Playing + Few-Shot Examples + Chain-of-Thought
- **Live evaluation scores** — Fact Recall, Tone Accuracy, Clarity & Conciseness
- **Model comparison pipeline** — GPT-4o vs GPT-4o-mini across 10 test scenarios

---

## Project Structure

```
email-generation-assistant/
├── backend/
│   ├── main.py                     # FastAPI server (/generate, /evaluate)
│   ├── core/
│   │   ├── prompts.py              # Prompt templates (advanced + simple)
│   │   └── generator.py            # generate_email() function
│   └── evaluation/
│       ├── test_scenarios.py       # 10 scenarios + reference emails
│       ├── metrics.py              # 3 custom metrics
│       └── evaluator.py            # Evaluation pipeline → CSV + JSON
├── comparison/
│   └── compare.py                  # Rich model comparison report
├── extension/
│   ├── manifest.json
│   ├── popup.html / popup.css      # Extension UI
│   ├── popup.js                    # Extension logic
│   └── content_script.js          # Gmail injection
├── reports/                        # ← gitignored (generated locally)
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/your-username/email-generation-assistant.git
cd email-generation-assistant
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Start the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 4. Load the Chrome Extension

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `extension/` folder

Click the extension icon in your toolbar to open the popup.

---

## Using the Extension

1. Fill in the **Intent** (what the email is about)
2. Add **Key Facts** (one per line — things the email must include)
3. Select a **Tone** (Formal / Casual / Urgent / Empathetic / Warm / Professional)
4. Click **Generate Email**
5. Review the generated email and live quality scores
6. Click **⧉ Copy** or **↗ Insert** (when Gmail compose is open)

---

## Evaluation Pipeline

### Custom Metrics

| # | Metric | Method | Range |
|---|--------|--------|-------|
| 1 | **Fact Recall** | Keyword matching — fraction of input facts found in email | 0–1 |
| 2 | **Tone Accuracy** | LLM-as-a-Judge (GPT-4o-mini rates tone match 1–10) | 0–1 |
| 3 | **Clarity & Conciseness** | Flesch Reading Ease + length penalty (≤200 words ideal) | 0–1 |

### Run the full evaluation (10 scenarios × 2 models)

```bash
cd backend
python -m evaluation.evaluator
```

Results saved to `reports/evaluation_results.csv` and `reports/evaluation_results.json`.

### Compare models

```bash
python comparison/compare.py
```

Prints a rich side-by-side table and analysis summary.

---

## Model Comparison

| Configuration | Model | Prompting Strategy |
|---|---|---|
| **Model A** | GPT-4o | Role-Playing + Few-Shot + Chain-of-Thought |
| **Model B** | GPT-4o-mini | Structured CoT + Constraints |

---

## Prompting Technique

The advanced prompt used in Model A combines three techniques:

1. **Role-Playing** — The LLM is assigned the persona of "Alex Chen, a senior business communication specialist", anchoring tone and quality expectations.
2. **Few-Shot Examples** — Two worked examples (one casual, one formal) demonstrate the expected structure and quality.
3. **Chain-of-Thought** — The model is instructed to reason about the recipient, tone signals, and fact placement *before* writing the email.

---

## Deliverables Checklist

- [x] Working email generator (Intent + Facts + Tone → email)
- [x] Advanced prompting technique documented
- [x] 10 test scenarios with human reference emails
- [x] 3 custom evaluation metrics implemented
- [x] Evaluation output: `reports/evaluation_results.csv` + `.json`
- [x] Model comparison analysis (`comparison/compare.py`)
- [x] Chrome Extension with Gmail integration
- [x] Clean GitHub repository with this README
