# HACKVERSE Backend - Ready for Submission

## ✅ What's Built and Working

### Core Files Created:
1. **`pipeline.py`** - Main orchestration function
   - `run_pipeline(stock, profile_name, sentiment_available)` 
   - Wires together: data retrieval → agents → personalization → logging
   - Returns complete analysis dict for frontend

2. **`demo.py`** - Complete demonstration script
   - Shows 3 required scenarios
   - Demonstrates all hackathon requirements
   - Ready to present to judges

3. **`README.md`** - Updated with quick start guide

### Existing Components (Already Working):
- ✅ `agents/agents.py` - 4 AI agents (technical, sentiment, filings, synthesis)
- ✅ `Data/data.py` - Stock data, news, SEC filing search
- ✅ `personalize.py` - User profiling with 3 risk levels
- ✅ `logger.py` + `db.py` - Session logging to SQLite
- ✅ `users.py` - 3 user profiles (Ramesh, Priya, Aakash)
- ✅ `pconfig.py` - Degraded mode flag
- ✅ `utils/key_manager.py` - Multi-key API rotation

## 🎯 Hackathon Requirements Met

✅ **Signal classification** - 3+ dimensions (technical, sentiment, filings)  
✅ **RAG component** - Document retrieval from SEC filings with citations  
✅ **Multi-agent architecture** - 4 specialized agents with defined roles  
✅ **User profiling** - Risk-based personalization (low/medium/high)  
✅ **Performance metrics** - Latency, confidence, risk scoring  
✅ **Degraded data handling** - Graceful fallback when sentiment unavailable  
✅ **Session logging** - Tracks all metrics to SQLite database  
✅ **End-to-end demo** - `demo.py` shows all 3 scenarios  

## 🚀 How to Run

```bash
cd backend
source venv/bin/activate
python demo.py
```

**Note**: If API rate limits hit, wait a few minutes or add more API keys to `.env`

## 📦 For Frontend Integration

```python
from pipeline import run_pipeline

result = run_pipeline("NVIDIA", "Priya", sentiment_available=True)

# Use result dict:
# - result['synthesis']['recommendation'] - BUY/SELL/HOLD
# - result['personalized']['personalized_text'] - User-specific advice
# - result['technical'], result['sentiment'], result['filings'] - Agent outputs
# - result['latency_ms'], result['risk_score'] - Metrics
```

## 📊 Available Data

**Stocks**: NVIDIA, TESLA, TATAMOTORS  
**Users**: Ramesh (low risk), Priya (medium risk), Aakash (high risk)

## ⚡ Quick Test (Alternative to full demo)

```python
# Quick single test
from pipeline import run_pipeline
result = run_pipeline("NVIDIA", "Priya")
print(result['synthesis']['recommendation'])
```

## 🎓 Presentation Points

1. **Multi-agent orchestration** - 4 specialized AI agents working together
2. **Personalization** - Same signal, different advice per user risk profile
3. **Explainability** - Source citations, confidence scores, reasoning chains
4. **Resilience** - Graceful degradation when data sources fail
5. **Production-ready** - Logging, metrics, multi-key rotation

## 📝 Architecture Summary

```
Data Sources → Retrieval → [Technical Agent]  ─┐
                          [Sentiment Agent]  ─┼→ Synthesis → Personalization → User Output
                          [Filings Agent]    ─┘
                                    ↓
                            Session Logging (SQLite)
```

---

**Backend is COMPLETE and WORKING!** Frontend can be built to consume `run_pipeline()`.
