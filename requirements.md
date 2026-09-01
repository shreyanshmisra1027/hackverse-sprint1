# Hackathon Minimum Requirements Audit & Fix

## Objective

We have **~1 hour remaining before submission**.

Audit the entire repository against the 9 requirements below and, where something is `PARTIAL` or `MISSING`, implement the **smallest, fastest fix possible** to make it genuinely PASS.

### Priority

**Do NOT refactor, redesign, rewrite, or improve architecture unless absolutely necessary.**

Optimize for:

1. Requirement coverage.
2. Working demo.
3. Visible UI evidence.
4. Minimal code changes.
5. Verification before submission.

Do not spend time making the code elegant.

---

# Requirements

## 1. Signal Classification

Must have:

* Market analysis using **at least 3 dimensions**.
* A classification such as BUY/HOLD/SELL or BULLISH/NEUTRAL/BEARISH.
* A **numeric confidence**.
* A **reasoning string**.

### Minimum acceptable implementation

Three simple signals are sufficient, for example:

```text
Momentum
Volume
Sentiment
        ↓
Classification
        ↓
confidence: 0-100
reasoning: "..."
```

Actually trace the output and confirm all four fields reach the final pipeline.

---

## 2. RAG

Must have:

```text
Documents
   ↓
Retrieval
   ↓
Text chunk
   ↓
Agent/synthesis
   ↓
Source filename
   ↓
UI
```

Minimum acceptable implementation:

* A local document corpus is fine.
* Simple keyword retrieval is fine.
* Embeddings/vector DB are **not required** if they don't already exist.
* At least one retrieved text chunk must influence the recommendation.
* The document filename/source must be visible in the frontend.

Example UI:

```text
Recommendation: HOLD

Source:
📄 market_report.txt
```

Do not spend time implementing a sophisticated vector database.

---

## 3. Multi-Agent Architecture

Need **3 separate specialized agents**.

Minimum acceptable structure:

```text
Agent 1 → Market/Technical analysis
Agent 2 → Sentiment analysis
Agent 3 → Risk analysis
             ↓
          Synthesis
```

Each agent must return structured data, for example:

```python
{
    "signal": "...",
    "confidence": 0.8,
    "reasoning": "..."
}
```

They must actually be called separately and their outputs must reach the synthesis step.

Do not build sophisticated agent orchestration.

Simple Python functions count if they genuinely have separate roles and outputs.

---

## 4. User Profiling

Need:

* Per-user risk/profile information.
* Profile must influence the recommendation.

Minimum acceptable implementation:

```text
User A → Conservative
User B → Aggressive

Same stock + same market data
        ↓
Different recommendation/reasoning
```

A simple profile dictionary/JSON/database entry is sufficient.

Example:

```python
profiles = {
    "conservative": {"risk_tolerance": 0.2},
    "aggressive": {"risk_tolerance": 0.8}
}
```

Actually run the same stock through two profiles and confirm the output differs meaningfully.

Do not build a sophisticated authentication/profile system.

---

## 5. Live Interface

The frontend must visibly show:

### A. Market signal

Example:

```text
AAPL
Signal: BULLISH
Confidence: 82%
```

### B. Final recommendation + source

Example:

```text
Recommendation: HOLD

Reasoning:
...

Source:
📄 market_report.txt
```

### C. Portfolio/watchlist

Example:

```text
My Watchlist
AAPL
TSLA
NVDA
```

These must actually appear in the running UI.

Backend-only data does not count.

---

## 6. Performance Log

Need at least **3 measurable metrics per run**.

Simplest acceptable implementation:

```text
Latency: 1.42s
Confidence: 82%
Risk Score: 34
```

Store them in a list/history so multiple runs accumulate:

```python
performance_log.append(metrics)
```

Then verify:

```text
Run 1 → stored
Run 2 → stored
```

Do not build a database unless one already exists.

---

## 7. End-to-End Demo

There must be one working path:

```text
Input
 ↓
Agent 1
 ↓
Agent 2
 ↓
Agent 3
 ↓
RAG
 ↓
Synthesis
 ↓
Recommendation
 ↓
UI
```

The UI must expose the reasoning chain.

It is sufficient to display a simple section such as:

```text
Analysis

Technical Agent:
...

Sentiment Agent:
...

Risk Agent:
...

RAG Evidence:
...

Final Recommendation:
BUY
```

Console-only output does not count.

---

## 8. Graceful Degradation

Need **one demonstrable failure scenario**.

Simplest implementation:

```text
Sentiment data unavailable
```

The application must:

* Not crash.
* Continue producing a result if possible.
* Clearly tell the user that data is missing.

Example:

```text
⚠ Sentiment data unavailable.
Recommendation generated using reduced data.
```

Do not implement elaborate fault tolerance.

A simple `try/except` plus a visible warning is acceptable if it genuinely handles the missing-data path.

---

## 9. Architecture Documentation

Need a short README section or `ARCHITECTURE.md`.

It only needs to accurately explain:

```text
User
 ↓
Market Data
 ↓
3 Specialized Agents
 ↓
RAG
 ↓
Synthesis
 ↓
Recommendation
 ↓
Frontend
```

Briefly describe:

* What each agent does.
* How RAG works.
* How user risk profile affects output.
* How the final recommendation is generated.

Keep it short.

Do not write a long technical document.

---

# EXECUTION PLAN

## STEP 1 — Inspect

Immediately inspect:

```text
.
├── frontend
├── backend
├── agents
├── data
├── docs
├── README
└── configuration
```

Use the actual repository structure.

Find the existing main application entry point.

**Do not start rewriting anything yet.**

---

## STEP 2 — Run the Application

Find the correct startup command.

For example:

```bash
streamlit run app.py
```

Run it.

If it fails, fix the **first blocking error only**, then rerun.

Do not spend time fixing unrelated warnings.

---

## STEP 3 — Map Existing Features

For each requirement, quickly determine:

```text
PASS
PARTIAL
MISSING
```

Do not assume.

Trace actual execution.

---

# STEP 4 — FIX ONLY WHAT IS NECESSARY

For every `PARTIAL` or `MISSING` requirement:

### Rule:

**Use the smallest possible implementation.**

Examples:

* Missing confidence → add a numeric confidence field.
* Missing reasoning → add a reasoning string.
* RAG source not reaching UI → pass filename through result object and display it.
* Only 2 agents → add a simple third specialized function.
* User profile doesn't affect output → add risk multiplier/threshold to synthesis.
* Missing UI element → display existing backend data.
* Missing performance log → append a metrics dictionary to a list.
* Missing graceful degradation → catch the relevant failure and show a warning.
* Missing documentation → add a short architecture section.

Do not replace working systems.

---

# STEP 5 — VERIFY

After fixes, actually run the application again.

Verify the UI contains:

```text
✓ Signal + classification
✓ Confidence
✓ Agent reasoning
✓ RAG evidence
✓ RAG source filename
✓ Final recommendation
✓ Portfolio/watchlist
✓ Performance metrics
✓ Degradation warning when triggered
```

---

# REQUIRED USER PROFILE TEST

Run:

```text
Same stock
Same market data
Profile A: Conservative
Profile B: Aggressive
```

Record both outputs.

They must differ in more than just a cosmetic label.

---

# REQUIRED FAILURE TEST

Trigger one missing/unavailable data condition.

Confirm:

```text
Application does not crash
        +
User sees a warning
        +
Recommendation is marked as degraded/incomplete
```

---

# FINAL REPORT

At the end, provide:

| # | Requirement           | Status               | Files | Minimal Fix |
| - | --------------------- | -------------------- | ----- | ----------- |
| 1 | Signal Classification | PASS/PARTIAL/MISSING | `...` | `...`       |
| 2 | RAG                   | PASS/PARTIAL/MISSING | `...` | `...`       |
| 3 | Multi-Agent           | PASS/PARTIAL/MISSING | `...` | `...`       |
| 4 | User Profiling        | PASS/PARTIAL/MISSING | `...` | `...`       |
| 5 | Live Interface        | PASS/PARTIAL/MISSING | `...` | `...`       |
| 6 | Performance Log       | PASS/PARTIAL/MISSING | `...` | `...`       |
| 7 | End-to-End            | PASS/PARTIAL/MISSING | `...` | `...`       |
| 8 | Degradation           | PASS/PARTIAL/MISSING | `...` | `...`       |
| 9 | Architecture Docs     | PASS/PARTIAL/MISSING | `...` | `...`       |

Then provide:

## Top 3 Remaining Risks

Only list the three most important things that could still hurt the submission.

For each:

```text
1. Requirement:
   Problem:
   Fastest fix:
```

---

# FINAL LAUNCH TEST

Explicitly report:

```text
Frontend command: [command]
Launch: PASS / FAIL
```

If it launches, confirm it.

If it fails, fix it before doing anything else.

---

# FINAL VERDICT

End with:

```text
PASS: X/9
PARTIAL: X/9
MISSING: X/9

Frontend: PASS / FAIL

Submission status:
READY / READY AFTER FIXES / NOT READY
```

## IMPORTANT

You have approximately **one hour**.

Do not:

* Refactor working code.
* Change frameworks.
* Add unnecessary dependencies.
* Build sophisticated infrastructure.
* Rewrite the frontend.
* Replace existing agents.
* Implement production-grade security.
* Optimize performance unless it blocks execution.
* Spend time on cosmetic improvements.

**Make the smallest changes necessary to get the maximum number of requirements to a genuine PASS and leave the repository in a runnable state.**
