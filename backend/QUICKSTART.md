## Backend Quick Reference

### 🚀 Start Here
```bash
cd backend
source venv/bin/activate
python integration.py
```

### 📁 Key Files
- `integration.py` - Main entry point
- `agents/agents.py` - 4 AI agents
- `Data/data.py` - Stock data & news
- `utils/key_manager.py` - Multi-key rotation
- `README.md` - Full documentation

### 🔑 Add API Keys
Edit `.env`:
```bash
GOOGLE_API_KEY=your_key_here
GOOGLE_API_KEY_1=your_second_key
GOOGLE_API_KEY_2=your_third_key
```

### 📊 Analyze Stocks
```python
from integration import analyze_stock
result = analyze_stock("NVIDIA")
print(result['synthesis']['recommendation'])
```

### 🧪 Test Everything
```bash
python tests/check_api.py              # Verify API keys
python tests/test_integration_simple.py # Quick test
python integration.py                   # Full test
```

### 📈 Available Tickers
- NVIDIA
- TESLA
- TATAMOTORS

### ⚡ Rate Limits
- 1 key = 20 requests/day
- 4 keys = 80 requests/day
- Auto-rotation on exhaustion

### 📖 Full Docs
See `README.md` for complete documentation.
