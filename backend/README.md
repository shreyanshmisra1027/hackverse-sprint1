# Backend - Multi-Agent Financial Intelligence System

> HACKVERSE 2026 - PS-01: Autonomous Financial Intelligence for Retail Investors

## ⚡ Quick Start

```bash
cd backend
source venv/bin/activate
python demo.py
```

**That's it!** The demo showcases all 3 required scenarios:
1. Full multi-agent analysis with personalization
2. Degraded mode (sentiment unavailable)
3. Different user risk profiles

## 🔌 Frontend Integration

```python
from pipeline import run_pipeline

# Run full analysis pipeline
result = run_pipeline(
    stock="NVIDIA",           # Stock ticker
    profile_name="Priya",     # User name (Ramesh/Priya/Aakash)
    sentiment_available=True  # Enable/disable sentiment agent
)

# Returns complete dict with:
# - technical, sentiment, filings, synthesis (agent outputs)
# - personalized (user-specific recommendation)
# - latency_ms, risk_score, degraded_mode
# - source (filing citation)
```

## 🏗️ Architecture

**4 AI Agents** (parallel execution):
| Agent | Purpose |
|-------|---------|
| Technical Agent | Price momentum, volume analysis |
| Sentiment Agent | News sentiment analysis |
| Filings Agent | SEC filing analysis (RAG) |
| Synthesis Agent | Combines all signals |

**User Personalization**: Modifies recommendations based on risk tolerance (low/medium/high)

**Performance Logging**: Tracks latency, confidence, risk scores per session

**Graceful Degradation**: System works even when data sources unavailable

## 📂 File Structure

```
backend/
├── agents/
│   └── agents.py              # 4 AI agents (technical, sentiment, filings, synthesis)
├── Data/
│   ├── data.py                # Stock data, news, filing search
│   └── snippets.txt           # SEC filing excerpts
├── utils/
│   ├── __init__.py
│   └── key_manager.py         # Multi-key rotation system
├── tests/
│   ├── test_agents.py         # Agent unit tests
│   ├── test_integration_simple.py  # Simple integration test
│   ├── test.json              # Expected output format
│   └── check_api.py           # API key validator
├── integration.py             # Main integration layer
├── pipeline.py               # Pipeline orchestrator
├── demo.py                   # Demo script
├── requirements.txt           # Python dependencies
├── .env                       # API keys (gitignored)
└── README.md                  # This file
```

## 🔑 Multi-Key System

### Why Multiple Keys?

| Setup | Daily Requests | Analysis Capacity |
|-------|---------------|-------------------|
| Single key | 20 | ~5 stocks |
| 4 keys | 80 | ~20 stocks |
| 10 keys | 200 | ~50 stocks |

### Setup

```bash
# .env
GOOGLE_API_KEY=your_primary_key
GOOGLE_API_KEY_1=your_second_key
GOOGLE_API_KEY_2=your_third_key
GOOGLE_API_KEY_3=your_fourth_key
```

### How It Works

1. System starts with primary key
2. On rate limit (429), marks key as exhausted
3. Auto-switches to next available key
4. Keys recover after cooldown period

## 📊 Data Integration

### Available Data Sources

**Stock Data** (`Data/data.py`):
```python
stock_data = {
    "NVIDIA": {"price": 118.50, "change_pct": 3.2, "volume": "very high"},
    "TESLA": {"price": 245.30, "change_pct": -1.5, "volume": "high"},
    "TATAMOTORS": {"price": 950.00, "change_pct": 4.5, "volume": "normal"}
}
```

**News** (`Data/data.py`):
```python
news = {
    "NVIDIA": "NVIDIA beats earnings estimates on strong AI chip demand",
    "TESLA": "Tesla deliveries fall short of analyst expectations",
    "TATAMOTORS": "Tata Motors reports record EV sales"
}
```

**SEC Filings** (`Data/snippets.txt`):
- Searchable text chunks from SEC filings
- Simple keyword matching via `search(query)` function

### Adding New Stocks

Edit `Data/data.py`:
```python
stock_data["NEWSYMBOL"] = {"price": 100.0, "change_pct": 2.5, "volume": "high"}
news["NEWSYMBOL"] = "Company announces major product launch"
```

Edit `Data/snippets.txt`:
```
NEWSYMBOL_1
Company Q2 revenue grew 20% YoY with strong guidance.
```

## 📡 API Reference

### analyze_stock()

```python
from integration import analyze_stock

result = analyze_stock(
    ticker="NVIDIA",
    filing_query="What is the revenue outlook?",
    sentiment_available=True
)
```

### analyze_multiple_stocks()

```python
from integration import analyze_multiple_stocks

results = analyze_multiple_stocks(
    tickers=["NVIDIA", "TESLA", "TATAMOTORS"],
    sentiment_available=True,
    delay_between_stocks=3.0
)
```

### run_pipeline()

```python
from pipeline import run_pipeline

result = run_pipeline(
    stock="NVIDIA",
    profile_name="Priya",
    sentiment_available=True
)
```

## 🧪 Testing

```bash
# Validate API keys
python utils/key_manager.py

# Simple integration test
python tests/test_integration_simple.py

# Full demo
python demo.py

# Run all agents smoke test
python agents/agents.py
```

## ⚠️ Rate Limits

| Tier | Requests/Day | Reset |
|------|-------------|-------|
| Free (per key) | 20 | 24 hours |

Each stock analysis uses 4 API calls.

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "All API keys exhausted" | Wait 24h or add more keys |
| "No API keys found" | Check `.env` file exists and format |
| "parse_failed" errors | Temporary AI issue, retry later |
| Keys not rotating | Test with `tests/check_api.py` |

## 🚀 Next Steps

**Development:**
- [ ] Add more API keys to `.env`
- [ ] Replace hardcoded data with live APIs
- [ ] Add more stocks to `Data/data.py`

**Production:**
- [ ] Integrate real-time data (Yahoo Finance, Alpha Vantage)
- [ ] Add database for historical analysis
- [ ] Create REST API endpoints
- [ ] Implement caching layer
- [ ] Upgrade to paid API tiers

## 🔒 Security

- ✅ `.env` is gitignored
- ✅ API keys never logged
- ✅ Use `.env.example` as template
- ✅ Rotate keys if exposed
