# Backend Documentation

Complete guide for the stock analysis backend with AI agents and multi-key management.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Multi-Key System](#multi-key-system)
4. [Data Integration](#data-integration)
5. [API Reference](#api-reference)
6. [Testing](#testing)

---

## Quick Start

### Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys
```

### Basic Usage

```python
from integration import analyze_stock

# Analyze a single stock
result = analyze_stock("NVIDIA")
print(result['synthesis']['recommendation'])  # BUY/SELL/HOLD
print(result['synthesis']['confidence'])       # 0.0-1.0
```

---

## Architecture

### Data Flow

```
Data Sources          Integration          AI Agents           Output
─────────────        ─────────────        ─────────────       ──────────
stock_data    →      format()      →      technical_agent     signal
news          →      prepare()     →      sentiment_agent  →  confidence
snippets.txt  →      search()      →      filings_agent       reasoning
                                   →      synthesis_agent     recommendation
```

### File Structure

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
├── requirements.txt           # Python dependencies
├── .env                       # API keys (gitignored)
└── README.md                  # This file
```

---

## Multi-Key System

### Why Multiple Keys?

**Single Key Limits:**
- Free tier: 20 requests/day
- System stops when exhausted
- 24-hour wait for reset

**Multiple Keys Benefits:**
- 4 keys = 80 requests/day (4 × 20)
- Auto-switches on rate limits
- Continuous availability
- Keys auto-recover after cooldown

### Setup Multiple Keys

Edit `.env`:
```bash
# Primary key
GOOGLE_API_KEY=AIzaSyC...abc123

# Additional keys (auto-rotation)
GOOGLE_API_KEY_1=AIzaSyC...def456
GOOGLE_API_KEY_2=AIzaSyC...ghi789
GOOGLE_API_KEY_3=AIzaSyC...jkl012
```

### How It Works

1. System starts with primary key
2. On rate limit (429 error), marks key as exhausted
3. Automatically switches to next available key
4. Tracks recovery time for each key
5. Keys become available again after cooldown

### Monitoring

Watch console for rotation messages:
```
✓ Initialized with 4 API key(s)
✗ API key 'primary' exhausted (retry after 3600s)
→ Switched to API key 'key_1'
✓ API key 'primary' quota recovered
```

### Getting More Keys

1. Create multiple Google accounts
2. Visit https://ai.google.dev/ with each
3. Generate API key for each account
4. Add all keys to `.env`

---

## Data Integration

### Available Data Sources

**Stock Data** (`Data/data.py`)
```python
stock_data = {
    "NVIDIA": {"price": 118.50, "change_pct": 3.2, "volume": "very high"},
    "TESLA": {"price": 245.30, "change_pct": -1.5, "volume": "high"},
    "TATAMOTORS": {"price": 950.00, "change_pct": 4.5, "volume": "normal"}
}
```

**News** (`Data/data.py`)
```python
news = {
    "NVIDIA": "NVIDIA beats earnings estimates on strong AI chip demand",
    "TESLA": "Tesla deliveries fall short of analyst expectations",
    "TATAMOTORS": "Tata Motors reports record EV sales"
}
```

**SEC Filings** (`Data/snippets.txt`)
- Searchable text chunks from SEC filings
- Simple keyword matching via `search(query)` function

### Adding New Data

**Add a Stock:**
Edit `Data/data.py`:
```python
stock_data["NEWSYMBOL"] = {"price": 100.0, "change_pct": 2.5, "volume": "high"}
news["NEWSYMBOL"] = "Company announces major product launch"
```

**Add Filing Snippets:**
Edit `Data/snippets.txt`:
```
NEWSYMBOL_1
Company Q2 revenue grew 20% YoY with strong guidance.

NEWSYMBOL_2
Management highlighted improving margins and cost efficiency.
```

---

## API Reference

### analyze_stock()

Analyze a single stock with all agents.

```python
from integration import analyze_stock

result = analyze_stock(
    ticker="NVIDIA",
    filing_query="What is the revenue outlook?",  # Optional
    sentiment_available=True                      # Optional
)
```

**Returns:**
```json
{
  "ticker": "NVIDIA",
  "query": "What is NVIDIA's financial outlook?",
  "technical": {
    "signal": "BUY",
    "confidence": 0.85,
    "reasoning": "..."
  },
  "sentiment": {
    "signal": "bullish",
    "confidence": 0.95,
    "reasoning": "..."
  },
  "filings": {
    "outlook": "...",
    "confidence": 0.95,
    "reasoning": "...",
    "source": "NVIDIA_1"
  },
  "synthesis": {
    "recommendation": "BUY",
    "confidence": 0.92,
    "explanation": "..."
  }
}
```

### analyze_multiple_stocks()

Analyze multiple stocks with automatic delays.

```python
from integration import analyze_multiple_stocks

results = analyze_multiple_stocks(
    tickers=["NVIDIA", "TESLA", "TATAMOTORS"],
    sentiment_available=True,
    delay_between_stocks=3.0  # Seconds between stocks
)

for ticker, analysis in results.items():
    print(f"{ticker}: {analysis['synthesis']['recommendation']}")
```

### run_all_agents()

Low-level function to run all agents with custom data.

```python
from agents.agents import run_all_agents

result = run_all_agents(
    stock_data="AAPL: price=$175, RSI=58, MACD=bullish",
    news_text="Apple announces strong Q3 earnings",
    filing_query="What is the revenue outlook?",
    chunk="Q3 revenue grew 12% YoY to $95B",
    source="10-K Q3 2026",
    sentiment_available=True
)
```

---

## Testing

### Test Key Manager
```bash
python utils/key_manager.py
```
Shows number of keys and current status.

### Test Simple Integration
```bash
python tests/test_integration_simple.py
```
Tests data retrieval and agent pipeline for NVIDIA.

### Test Full Integration
```bash
python integration.py
```
Runs analysis on all 3 stocks (NVIDIA, TESLA, TATAMOTORS).

### Test Individual Agents
```bash
python agents/agents.py
```
Runs smoke test with dummy data.

---

## Rate Limits & Quotas

**Free Tier (per key):**
- Model: gemini-3.6-flash
- Limit: 20 requests/day
- Reset: Daily (24 hours)

**With Multiple Keys:**
- 2 keys = 40 requests/day
- 4 keys = 80 requests/day
- 10 keys = 200 requests/day

**Each Stock Analysis Uses:**
- 4 API calls (technical, sentiment, filings, synthesis)

**Example:**
- 4 keys = 80 requests/day
- 80 ÷ 4 = 20 stocks/day

---

## Troubleshooting

### "All API keys exhausted"
- **Cause:** All keys hit daily quota
- **Fix:** Wait for reset (24h) or add more keys

### "No API keys found"
- **Cause:** `.env` missing or misconfigured
- **Fix:** Check `.env` exists and has proper format

### "parse_failed" errors
- **Cause:** Rate limit or invalid JSON from AI
- **Fix:** Keys exhausted or temporary AI issue, retry later

### Keys not rotating
- **Cause:** All keys invalid or misconfigured
- **Fix:** Test each key individually with `tests/check_api.py`

---

## Next Steps

**For Development:**
1. Add 2-3 more API keys to `.env`
2. Replace hardcoded data with live APIs
3. Add more stocks to `Data/data.py`

**For Production:**
1. Integrate real-time data (Yahoo Finance, Alpha Vantage)
2. Add database for historical analysis
3. Create REST API endpoints
4. Implement caching layer
5. Upgrade to paid API tiers for higher quotas

---

## Security

✅ `.env` is gitignored  
✅ API keys never logged  
✅ Use `.env.example` as template  
✅ Rotate keys if exposed  

---

## Support

- Check logs for detailed error messages
- Test with `check_api.py` to validate keys
- Monitor key rotation in console output
- See test files in `tests/` for examples
