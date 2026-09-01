import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

MODEL_NAME = "gemini-3.6-flash"

def _call_gemini(prompt_text):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt_text)
    result = response.text.strip()
    # Remove markdown code blocks if present
    if result.startswith('```'):
        lines = result.split('\n')
        result = '\n'.join(lines[1:-1]) if len(lines) > 2 else result
    return result

def technical_agent(stock_data):
    prompt = f"""Analyze stock data: {stock_data}.
Return strict JSON with this structure: {{"signal": "...", "confidence": 0.0, "reasoning": "..."}}
Return ONLY the JSON object. No markdown formatting, no code fences, no explanation text before or after."""
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def sentiment_agent(news_text):
    prompt = f"""Analyze news sentiment: {news_text}.
Return strict JSON with this structure: {{"signal": "...", "confidence": 0.0, "reasoning": "..."}}
Return ONLY the JSON object. No markdown formatting, no code fences, no explanation text before or after."""
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def filings_agent(query, chunk, source):
    prompt = f"""Query: {query}
Chunk: {chunk}
Source: {source}
Return strict JSON with this structure: {{"outlook": "...", "confidence": 0.0, "reasoning": "...", "source": "..."}}
Return ONLY the JSON object. No markdown formatting, no code fences, no explanation text before or after."""
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def synthesis_agent(technical, sentiment, filings, sentiment_available):
    prompt = f"""Synthesize technical={technical}, sentiment={sentiment}, filings={filings}, sentiment_available={sentiment_available}.
Return strict JSON with this structure: {{"recommendation": "...", "confidence": 0.0, "explanation": "..."}}
Return ONLY the JSON object. No markdown formatting, no code fences, no explanation text before or after."""
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def run_all_agents(stock_data, news_text, filing_query, chunk, source, sentiment_available=True):
    technical = technical_agent(stock_data)
    sentiment = sentiment_agent(news_text) if sentiment_available else None
    filings = filings_agent(filing_query, chunk, source)
    synthesis = synthesis_agent(technical, sentiment, filings, sentiment_available)
    return {
        "technical": technical,
        "sentiment": sentiment,
        "filings": filings,
        "synthesis": synthesis,
    }

if __name__ == "__main__":
    print("Running smoke test...")
    result = run_all_agents(
        stock_data="AAPL: price=$175, RSI=58, MACD=bullish, volume=high",
        news_text="Apple announces strong Q3 earnings, beating analyst expectations.",
        filing_query="What is the revenue outlook?",
        chunk="Q3 revenue grew 12% YoY to $95B. Management projects continued growth.",
        source="10-K Q3 2026",
        sentiment_available=True
    )
    print("\n=== Results ===")
    print(json.dumps(result, indent=2))
