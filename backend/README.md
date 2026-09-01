# Backend Module

Python backend for stock analysis using Gemini AI agents.

## Setup

1. Create virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

## Structure

- `agents/` - AI agent implementations
- `api/` - REST API endpoints
- `utils/` - Helper functions
- `config/` - Configuration files
- `tests/` - Test files

## Testing

```bash
source venv/bin/activate
python tests/test_agents.py
```
