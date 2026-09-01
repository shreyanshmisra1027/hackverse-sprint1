import json
import os
import sys
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Add utils to path for key_manager import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"

# Initialize key manager on first import
_key_manager = None

def _get_key_manager():
    """Get or initialize the key manager."""
    global _key_manager
    if _key_manager is None:
        try:
            from utils.key_manager import get_key_manager
            _key_manager = get_key_manager()
        except Exception as e:
            # Fallback to single key if key_manager fails
            print(f"Key manager initialization failed: {e}")
            print("Falling back to single API key mode")
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            _key_manager = False  # Mark as disabled
    return _key_manager if _key_manager is not False else None

def _call_gemini(prompt_text, retries=3, delay=2):
    """Call Gemini with retry logic and automatic key rotation."""
    key_manager = _get_key_manager()

    for attempt in range(retries):
        try:
            # Configure with active key if manager is available
            if key_manager and not key_manager.configure_genai():
                print("⚠ All API keys exhausted. Cannot make request.")
                raise Exception("All API keys exhausted")

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt_text)
            result = response.text.strip()

            # Track successful usage
            if key_manager:
                key_manager.increment_usage()

            # Remove markdown code blocks if present
            if result.startswith('```'):
                lines = result.split('\n')
                result = '\n'.join(lines[1:-1]) if len(lines) > 2 else result
            return result

        except Exception as e:
            error_msg = str(e)

            # Check if it's a rate limit / quota error
            if '429' in error_msg or 'quota' in error_msg.lower() or 'rate' in error_msg.lower():
                # Extract retry time if available
                retry_after = 3600  # Default 1 hour
                if 'retry' in error_msg.lower():
                    try:
                        import re
                        match = re.search(r'(\d+(?:\.\d+)?)\s*s', error_msg)
                        if match:
                            retry_after = float(match.group(1))
                    except:
                        pass

                # Mark current key as exhausted and try to switch
                if key_manager:
                    key_manager.mark_exhausted(retry_after)
                    if key_manager.get_active_key():
                        print(f"Retrying with next available key...")
                        continue  # Try again with new key

                # If no key manager or all keys exhausted, do exponential backoff
                if attempt < retries - 1:
                    wait_time = delay * (2 ** attempt)
                    print(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{retries}...")
                    time.sleep(wait_time)
                    continue

            # Re-raise if not rate limit or last attempt
            raise

    raise Exception("Max retries exceeded")

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
