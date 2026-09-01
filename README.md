# Stock Analysis Platform

> AI-powered multi-agent stock analysis system for retail investors

A collaborative project for HackVerse 2026 (PS-01: Autonomous Financial Intelligence) that provides retail investors with institutional-grade stock analysis through a multi-agent AI system.

## 🎯 Overview

This platform uses parallel AI agents to analyze stocks from multiple angles:
- **Technical Analysis** - Price momentum, volume analysis, chart patterns
- **Sentiment Analysis** - News and market sentiment evaluation
- **SEC Filing Analysis** - RAG-based document analysis
- **Synthesis** - Combined recommendation with personalization

## 📁 Project Structure

```
hackverse-sprint1/
├── backend/                  # Python backend with Gemini AI agents
│   ├── agents/               # AI agent implementations
│   │   └── agents.py        # 4 parallel AI agents
│   ├── api/                 # REST API endpoints
│   ├── Data/                # Stock data, news, SEC filing snippets
│   │   ├── data.py          # Stock & news data
│   │   └── snippets.txt     # SEC filing excerpts
│   ├── utils/               # Helper utilities
│   │   └── key_manager.py   # Multi-key API rotation
│   ├── tests/               # Test suite
│   ├── integration.py       # Main pipeline
│   ├── demo.py              # Demo script
│   ├── requirements.txt     # Dependencies
│   └── README.md            # Backend documentation
├── frontend/                 # Frontend application (coming soon)
├── docs/                    # Documentation
└── data/                    # Data files and datasets
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google AI API key(s)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Run demo
python demo.py
```

### Frontend

Coming soon...

## 📊 Features

| Feature | Description |
|---------|-------------|
| Multi-Agent Analysis | 4 AI agents running in parallel |
| User Personalization | Risk-based recommendations (Low/Medium/High) |
| Graceful Degradation | System works even when data sources fail |
| Multi-Key Support | Auto-rotation across multiple API keys |
| Performance Tracking | Latency, confidence, and risk scoring |

## 👥 User Profiles

| Profile | Risk Tolerance | Strategy |
|---------|---------------|----------|
| Ramesh | Low | Cautious, conservative approach |
| Priya | Medium | Balanced risk-reward |
| Aakash | High | Aggressive positioning |

## 📈 Available Stocks

- **NVIDIA** - AI chip leader
- **TESLA** - EV manufacturer
- **TATAMOTORS** - Indian automotive giant

## 🛠️ Tech Stack

**Backend:**
- Python 3.10+
- Google Gemini AI (gemini-3.6-flash)
- Multi-key API rotation system

**Frontend:** (Coming soon)

## 🤝 Contributing

This is a collaborative HackVerse 2026 project. Please coordinate with team members before making major changes.

1. Create a feature branch for your work
2. Make your changes
3. Test thoroughly before submitting
4. Submit a pull request with a clear description

## 📄 License

This project was created for HackVerse 2026.

## 👨‍💻 Authors

HackVerse 2026 - Team

---

## 🏗️ Architecture

```text
User (Profile: Conservative / Medium / Aggressive)
 ↓
Market Data (price, change%, volume) + News + SEC Filing Retrieval (keyword search)
 ↓
3 Specialized Agents (run in parallel):
  • Technical Agent — price momentum, volume, signal + confidence + reasoning
  • Sentiment Agent — news sentiment, signal + confidence + reasoning
  • Risk/Filings Agent — RAG retrieval from snippets.txt, outlook + source + reasoning
 ↓
Synthesis Agent — combines 3 agent outputs into recommendation + confidence + explanation
 ↓
Personalization (personalize.py) — adjusts recommendation by risk profile
 ↓
Frontend (HTML/JS) — displays signal, agent reasoning, RAG source, recommendation, profile, metrics
```

### What each agent does
- **Technical Agent**: Reads stock price/volume and returns BUY/SELL/HOLD with confidence and reasoning.
- **Sentiment Agent**: Reads news text and returns bullish/bearish/neutral with confidence and reasoning.
- **Filings (RAG) Agent**: Searches `Data/snippets.txt` by keyword, returns the best text chunk with filename (`NVIDIA_1`, etc.) and a positive/negative/neutral outlook.
- **Synthesis Agent**: Combines the three outputs into a single recommendation with explanation.

### RAG
Simple keyword retrieval against `Data/snippets.txt`. No vector DB required. Source filename always reaches the UI.

### User profiling
Profiles (`users.py`): Ramesh (low), Priya (medium), Aakash (high). Same stock + same data → different recommendation text based on `risk_tolerance`.

### Graceful degradation
If sentiment is unavailable (`sentiment_available=False`), the pipeline skips the sentiment agent, continues with technical + filings, and shows a visible warning (`⚠ Degraded mode`).

### Performance logging
`personalize/logger.py` writes to SQLite (`DB_PATH`). Each run stores latency, confidence, risk score, degraded flag, signals used. `frontend/server.py` also keeps an in-memory history (`PERFORMANCE_LOG`) shown in the UI.
