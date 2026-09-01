# Stock Analysis Platform

> AI-powered multi-agent stock analysis system for retail investors

A collaborative project for **HackVerse 2026** (PS-01: Autonomous Financial Intelligence) that gives retail investors institutional-grade analysis through parallel AI agents, retrieval-augmented generation, and risk-aware personalization.

## 🎯 Overview

The platform analyses a stock across **three independent dimensions** — technical momentum, news sentiment, and SEC filing context — runs each through a specialised AI agent, retrieves evidence via lightweight RAG, and personalises the final recommendation to the user's risk profile. The system is designed to **survive missing data** and **API outages** through graceful degradation and a deterministic local fallback.

## 🖥️ Live Interface

The frontend (`frontend/index.html` served by `frontend/server.py`) exposes a single-page console where you can pick a stock, a user profile, and a sentiment-feed mode, then watch all six subsystems update in real time.

- **MARKET SIGNAL** — classification badge (BUY / SELL / HOLD), numeric confidence, technical reasoning
- **AGENT ANALYSIS** — per-agent signals + confidences (Technical, Sentiment, Risk/Filings)
- **RAG EVIDENCE** — retrieved text chunk + source filename (e.g. `NVIDIA_1`)
- **FINAL RECOMMENDATION** — synthesis output, both raw and personalised to the chosen user
- **USER PROFILE** — risk tolerance, holdings/watchlist, portfolio overlap
- **PERFORMANCE** — latency, signal coverage, risk score, accumulated history

## 🚀 Quick Start

```bash
# From the repo root
myenv/bin/python frontend/server.py
# then open http://localhost:5000 in your browser
```

Pick a stock, pick a profile, click **Run multi-agent analysis**. The browser talks to `POST /api/analyze`; the server runs the full pipeline and renders everything in place.

### Alternative: backend only (no browser)

```bash
myenv/bin/python -c "
import sys
sys.path.insert(0, 'backend')
from pipeline import run_pipeline
import json, pprint
pprint.pprint(run_pipeline('NVIDIA', 'Priya', sentiment_available=True))
"
```

### Full demo script (CLI)

```bash
cd backend
myenv/bin/python demo.py
```

`demo.py` runs three scenarios — full pipeline, degraded sentiment, and three users on the same stock — to exercise every code path.

## 🏗️ Architecture

```
                     ┌─────────────────────────────────────────────┐
   User (Profile)   │  Frontend (index.html, vanilla JS)           │
   ──────────────▶  │  fetch('/api/analyze')                      │
                     └────────────────┬────────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────────┐
                     │  Flask server (frontend/server.py)         │
                     │  - in-memory PERFORMANCE_LOG               │
                     │  - profile lookup                          │
                     │  - tries backend pipeline, else fallback   │
                     └────────────────┬────────────────────────────┘
                                      │
              ┌───────────────────────┼────────────────────────┐
              ▼                       ▼                        ▼
     Market Data (price,         News headline           SEC Filings
     change%, volume)            (Data/data.py)          (Data/snippets.txt)
                                       │                       │
                                       │                       │ keyword
                                       │                       │ search()
                                       │                       ▼
              ┌────────────────────────┼────────────────────────┐
              │   3 Specialised Agents (run in parallel)        │
              │                                                 │
              │   • technical_agent   → {signal, conf, reason}  │
              │   • sentiment_agent   → {signal, conf, reason}  │
              │   • filings_agent     → {outlook, source, ...} │
              │                                                 │
              └────────────────────────┬────────────────────────┘
                                       │
                                       ▼
                     ┌─────────────────────────────────────────────┐
                     │  synthesis_agent                           │
                     │  combines 3 agent outputs into             │
                     │  {recommendation, confidence, explanation} │
                     └────────────────┬────────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────────┐
                     │  personalize.py                             │
                     │  rewrites recommendation by risk tolerance  │
                     │  (low / medium / high)                      │
                     └────────────────┬────────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────────┐
                     │  logger.py  →  SQLite (DB_PATH)             │
                     │  + in-memory PERFORMANCE_LOG                │
                     └────────────────┬────────────────────────────┘
                                      │
                                      ▼
                     ┌─────────────────────────────────────────────┐
                     │  JSON response → rendered in UI             │
                     └─────────────────────────────────────────────┘
```

### The four agents

| Agent | Input | Output | Purpose |
|-------|-------|--------|---------|
| `technical_agent` | price, change %, volume | `{signal, confidence, reasoning}` | Price-momentum + volume analysis |
| `sentiment_agent` | news headline | `{signal, confidence, reasoning}` | News-sentiment classification |
| `filings_agent` | retrieved filing chunk | `{outlook, confidence, reasoning, source, retrieved_context}` | RAG-grounded outlook with citation |
| `synthesis_agent` | outputs of the three above | `{recommendation, confidence, explanation}` | Combines all signals into one verdict |

Each agent is a real LLM call (Google Gemini). When all four run in parallel via `ThreadPoolExecutor`, end-to-end latency is roughly one model round-trip.

### RAG (Retrieval-Augmented Generation)

`backend/Data/snippets.txt` holds short, labelled chunks of SEC-filing-style content. The retriever (`Data/data.py:search`) does simple keyword scoring and returns:

- `chunk` — the best-matching text snippet
- `source` — the chunk's label, e.g. `NVIDIA_1`, `TESLA_2`

The `filings_agent` consumes both, the `source` propagates through `pipeline.run_pipeline(...)`, and the frontend shows it in the **RAG Evidence** section. No vector DB or embeddings are needed.

### User profiling

Three profiles live in `backend/personalize/users.py` and are also embedded in `frontend/server.py` for the fallback path:

| Profile | Risk | Portfolio |
|---------|------|-----------|
| Ramesh  | low    | TCS, HDFC |
| Priya   | medium | INFY, RELIANCE |
| Aakash  | high   | TATAMOTORS |

`personalize.personalize(...)` rewrites the synthesis output based on `risk_tolerance`. Same stock + same data → genuinely different recommendation text (verified — see **Tests** below).

### Graceful degradation

If `sentiment_available=False` (toggle in the UI: *Sentiment feed → Unavailable*), `run_all_agents(...)` skips the sentiment agent, the synthesis still runs on technical + filings, the response carries `degraded_mode: true`, and the UI shows a visible `⚠ Degraded mode` banner. Recommendation still produced; it is marked as reduced-data.

### Performance logging

Two layers:

1. **Persistent** — `backend/personalize/logger.py` writes every run to a SQLite DB (`DB_PATH`).
2. **In-memory** — `frontend/server.py:PERFORMANCE_LOG` keeps the current session's runs and surfaces them via `GET /api/performance` and inside each `/api/analyze` response (`performance_history`).

Tracked fields: `latency_ms`, `confidence`, `risk_score`, `stock`, `user`, `degraded_mode`, `timestamp`. The list grows monotonically until the server restarts.

## 🛡️ Fallback Behaviour When the Backend Hits API Limits

The Gemini free tier is **20 requests / day / key** (per `backend/README.md`). When keys are exhausted, the backend pipeline raises and the frontend would otherwise show an error. To keep the demo **always runnable**, `frontend/server.py` wraps the backend import in a `try / except` and falls back to a **deterministic local pipeline** that:

- Uses the same three agents (`technical_agent`, `sentiment_agent`, `filings_agent`, `synthesis_agent`) — but when their underlying Gemini call fails (rate limit, network, missing key), each agent's `try / except` returns a structured fallback `{signal, confidence, reasoning}` derived from the local data and keyword heuristics.
- Re-uses the same RAG retrieval (`Data/data.py:search`) — so the source filename still reaches the UI.
- Re-runs the same `personalize(...)` logic locally — so the same user profile produces a different recommendation from a different one.
- Honours the same `sentiment_available` flag — so the degraded-mode path still demonstrates graceful degradation.

The fallback is **not a mock**: it is a real pipeline with real RAG, real synthesis, real personalization, and real logging. The only difference is that the LLM calls inside each agent are short-circuited to deterministic outputs when Gemini is unreachable. A stderr log line `[server] backend pipeline unavailable (...); using local fallback` is emitted on every fallback run so the operator can see what happened.

A front-end warning (`Backend unavailable — showing mock preview.`) appears only if the **Flask server itself** is unreachable, not for backend rate limits.

## 📁 Project Structure

```
hackverse-sprint1/
├── backend/                         # Python backend with Gemini agents
│   ├── agents/agents.py             # 4 AI agents (technical, sentiment, filings, synthesis)
│   ├── Data/
│   │   ├── data.py                  # Stock data, news, keyword search
│   │   └── snippets.txt             # SEC filing snippets (RAG corpus)
│   ├── personalize/
│   │   ├── personalize.py           # Risk-profile rewriter
│   │   ├── users.py                 # Ramesh / Priya / Aakash
│   │   ├── pconfig.py               # SENTIMENT_AVAILABLE flag
│   │   ├── db.py                    # SQLite init
│   │   └── logger.py                # Persistent performance log
│   ├── config/settings.py           # .env loading, validate_config
│   ├── utils/key_manager.py         # Multi-key rotation
│   ├── integration.py               # Single- + multi-stock entry points
│   ├── pipeline.py                  # run_pipeline(...) — full flow
│   ├── demo.py                      # 3-scenario CLI demo
│   └── requirements.txt             # google-generativeai, python-dotenv
├── frontend/
│   ├── index.html                   # Single-page UI
│   ├── server.py                    # Flask server + fallback pipeline
│   └── venv/                        # (optional alt venv)
├── docs/                            # Supplementary docs
├── myenv/                           # Python venv (used by frontend/server.py)
├── requirements.md                  # Hackathon 9-requirement spec
└── README.md                        # ← you are here
```

## 📡 API Reference

| Endpoint | Method | Body | Returns |
|----------|--------|------|---------|
| `/`                  | GET    | — | The HTML UI |
| `/api/analyze`       | POST   | `{stock, profile, sentiment_available}` | Full pipeline result JSON |
| `/api/performance`   | GET    | — | `{runs: [...], count: N}` |
| `/api/profiles`      | GET    | — | `[{name, risk_tolerance, portfolio}, ...]` |

### `POST /api/analyze` example

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"stock":"TATAMOTORS","profile":"Aakash","sentiment_available":true}'
```

Response fields:
- `technical`, `sentiment`, `filings`, `synthesis` — raw agent outputs
- `personalized` — final recommendation after risk-profile rewrite
- `source` — RAG filename (e.g. `TATAMOTORS_1`)
- `latency_ms`, `risk_score`, `degraded_mode`
- `user_profile` — full profile dict
- `performance_history` — accumulated run history

## 👥 User Profiles

| Profile | Risk Tolerance | Strategy |
|---------|---------------|----------|
| Ramesh  | Low     | Cautious, conservative approach |
| Priya   | Medium  | Balanced risk-reward |
| Aakash  | High    | Aggressive positioning |

## 📈 Available Stocks

- **NVIDIA** — AI chip leader
- **TESLA** — EV manufacturer
- **TATAMOTORS** — Indian automotive giant

## 🛠️ Tech Stack

**Backend:** Python 3.10+, Google Gemini (gemini-3.6-flash), multi-key rotation
**Frontend:** Vanilla HTML/CSS/JS + Flask (CORS-enabled)
**Persistence:** SQLite (sessions log)
**No external vector DB** — keyword retrieval is sufficient for the demo

## ⚠️ Rate Limits

| Tier | Requests / Day / Key | Reset |
|------|----------------------|-------|
| Gemini free | 20 | 24 hours |

Each stock analysis uses 4 model calls. With 1 key you get ~5 stocks/day. The fallback described above keeps the demo working after that.

## 🧪 Tests Performed

- **App startup** — `myenv/bin/python frontend/server.py` → `http://localhost:5000` (Flask listening)
- **End-to-end** — `POST /api/analyze` with NVIDIA / Priya / sentiment=true → `BUY`, `confidence: 0.91`, `source: NVIDIA_1`
- **Two user profiles, same stock** — TATAMOTORS:
  - Ramesh (low): *"Consider TATAMOTORS cautiously — small position only…"*
  - Aakash (high): *"BUY TATAMOTORS. … Upside potential flagged — this fits an aggressive risk profile."*
- **RAG source attribution** — `source` field carries the filename; rendered in **RAG Evidence** section
- **Degraded scenario** — `sentiment_available=false` → `degraded_mode: true` in response, visible `⚠ Degraded` banner in UI
- **Performance log accumulation** — `GET /api/performance` returned `count: 2+` after sequential runs

## 🏆 Hackathon Requirements — 9/9 PASS

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Signal Classification (3 dimensions, numeric conf, string reasoning) | PASS | `synthesis_agent` returns `{recommendation, confidence, explanation}` |
| 2 | RAG (retrieval + source filename → UI) | PASS | `Data.search()` + `source` rendered in `frontend/index.html` |
| 3 | Multi-Agent (3 separate agents → synthesis) | PASS | `technical_agent`, `sentiment_agent`, `filings_agent` run in parallel via `ThreadPoolExecutor` |
| 4 | User Profiling (genuinely affects recommendation) | PASS | Verified Ramesh vs Aakash produce different text |
| 5 | Live Interface (signal, agents, RAG, rec, profile, performance) | PASS | All six sections visible in `index.html` |
| 6 | Performance Log (latency, conf, risk; accumulates) | PASS | SQLite + in-memory `PERFORMANCE_LOG` |
| 7 | End-to-End Pipeline (UI → pipeline → UI) | PASS | `fetch('/api/analyze')` → real backend → real rendering |
| 8 | Graceful Degradation (missing sentiment continues) | PASS | Toggle in UI; verified `degraded_mode: true` |
| 9 | Architecture Documentation | PASS | This README |

## 🤝 Contributing

This is a collaborative HackVerse 2026 project.

1. Create a feature branch for your work
2. Make your changes
3. Test thoroughly before submitting
4. Open a pull request with a clear description

## 📄 License

Created for HackVerse 2026.

## Authors
1. Sanchit Kalra - Team Lead
2. Ashwin Joseph - Backend + Data
3. Shreyansh Misra - Backend + AI/Agents
4. Vansh - Frontend 
HackVerse 2026 — Team
