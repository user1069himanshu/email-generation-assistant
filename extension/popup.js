/**
 * popup.js — Chrome Extension popup logic
 * Talks to the FastAPI backend at localhost:8000
 */

const API_BASE = "http://localhost:8000";

// ── DOM refs ──────────────────────────────────────────────────────
const intentInput    = document.getElementById("intent");
const factsInput     = document.getElementById("facts");
const toneChips      = document.querySelectorAll(".chip");
const btnGenerate    = document.getElementById("btn-generate");
const btnText        = btnGenerate.querySelector(".btn-text");
const spinner        = document.getElementById("spinner");
const errorBox       = document.getElementById("error-box");
const errorMsg       = document.getElementById("error-msg");
const outputSection  = document.getElementById("output-section");
const outputBox      = document.getElementById("output-box");
const btnCopy        = document.getElementById("btn-copy");
const btnInsert      = document.getElementById("btn-insert");

// Metric elements
const metricRecall   = document.getElementById("metric-recall");
const metricTone     = document.getElementById("metric-tone");
const metricClarity  = document.getElementById("metric-clarity");
const metricAvg      = document.getElementById("metric-avg");

// ── State ─────────────────────────────────────────────────────────
let selectedTone     = "formal";
let lastEmail        = "";
let lastFacts        = [];

// ── Tone chip selection ───────────────────────────────────────────
toneChips.forEach(chip => {
  chip.addEventListener("click", () => {
    toneChips.forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
    selectedTone = chip.dataset.tone;
  });
});

// ── Helpers ───────────────────────────────────────────────────────
function setLoading(isLoading) {
  btnGenerate.disabled = isLoading;
  btnText.textContent  = isLoading ? "Generating…" : "Generate Email";
  spinner.classList.toggle("hidden", !isLoading);
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.classList.add("hidden");
}

function setMetric(cardEl, value) {
  const valEl = cardEl.querySelector(".metric-value");
  const pct = Math.round(value * 100);
  valEl.textContent = `${pct}%`;

  // Color coding
  if (pct >= 80)       valEl.style.color = "#34d399"; // green
  else if (pct >= 55)  valEl.style.color = "#f59e0b"; // amber
  else                 valEl.style.color = "#f87171"; // red
}

// ── generate ─────────────────────────────────────────────────────
btnGenerate.addEventListener("click", async () => {
  hideError();

  const intent = intentInput.value.trim();
  const rawFacts = factsInput.value.trim();

  if (!intent) { showError("Please enter an intent."); return; }
  if (!rawFacts) { showError("Please enter at least one key fact."); return; }

  const facts = rawFacts
    .split("\n")
    .map(f => f.trim())
    .filter(Boolean);

  lastFacts = facts;
  setLoading(true);
  outputSection.classList.add("hidden");

  try {
    // 1. Generate
    const genRes = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        intent,
        facts,
        tone: selectedTone,
        model: "gpt-4o",
        strategy: "advanced",
      }),
    });

    if (!genRes.ok) {
      const err = await genRes.json();
      throw new Error(err.detail || "Generation failed.");
    }

    const { email } = await genRes.json();
    lastEmail = email;

    // Show output
    outputBox.textContent = email;
    outputSection.classList.remove("hidden");

    // Reset metric cards
    [metricRecall, metricTone, metricClarity, metricAvg].forEach(el => {
      el.querySelector(".metric-value").textContent = "…";
    });

    // 2. Evaluate (non-blocking)
    fetch(`${API_BASE}/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, facts, tone: selectedTone }),
    })
      .then(r => r.json())
      .then(m => {
        setMetric(metricRecall,  m.fact_recall);
        setMetric(metricTone,    m.tone_accuracy);
        setMetric(metricClarity, m.clarity_conciseness);
        setMetric(metricAvg,     m.avg_score);
      })
      .catch(() => {
        [metricRecall, metricTone, metricClarity, metricAvg].forEach(el => {
          el.querySelector(".metric-value").textContent = "—";
        });
      });

  } catch (err) {
    showError(err.message || "Could not connect to backend. Is it running?");
  } finally {
    setLoading(false);
  }
});

// ── Copy ─────────────────────────────────────────────────────────
btnCopy.addEventListener("click", async () => {
  if (!lastEmail) return;
  try {
    await navigator.clipboard.writeText(lastEmail);
    btnCopy.textContent = "✓ Copied!";
    setTimeout(() => { btnCopy.textContent = "⧉ Copy"; }, 1800);
  } catch {
    btnCopy.textContent = "Failed";
  }
});

// ── Insert into Gmail ─────────────────────────────────────────────
btnInsert.addEventListener("click", async () => {
  if (!lastEmail) return;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab || !tab.url?.includes("mail.google.com")) {
    showError("Open Gmail and click Compose first, then try Insert.");
    return;
  }

  chrome.tabs.sendMessage(
    tab.id,
    { action: "INSERT_EMAIL", text: lastEmail },
    response => {
      if (chrome.runtime.lastError || !response?.success) {
        showError("Could not insert. Make sure a Gmail compose window is open.");
      } else {
        btnInsert.textContent = "✓ Inserted!";
        setTimeout(() => { btnInsert.textContent = "↗ Insert"; }, 2000);
      }
    }
  );
});
