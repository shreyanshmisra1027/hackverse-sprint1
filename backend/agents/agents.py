import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def _call_gemini(prompt_text):
    model = genai.GenerativeModel('gemini-3.6-flash')
    response = model.generate_content(prompt_text)
    result = response.text.strip()
    # Remove markdown code blocks if present
    if result.startswith('```'):
        lines = result.split('\n')
        result = '\n'.join(lines[1:-1]) if len(lines) > 2 else result
    return result

def technical_agent(stock_data):
    prompt = f"Analyze stock data: {stock_data}. Return strict JSON matching test.json format: {{'signal':'...','confidence':0.0,'reasoning':'...'}}"
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def sentiment_agent(news_text):
    prompt = f"Analyze news sentiment: {news_text}. Return strict JSON matching test.json format: {{'signal':'...','confidence':0.0,'reasoning':'...'}}"
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def filings_agent(query, chunk, source):
    prompt = f"Query: {query}\nChunk: {chunk}\nSource: {source}. Return strict JSON matching test.json format: {{'outlook':'...','confidence':0.0,'reasoning':'...','source':'...'}}"
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}

def synthesis_agent(technical, sentiment, filings, sentiment_available):
    prompt = f"Synthesize technical={technical}, sentiment={sentiment}, filings={filings}, sentiment_available={sentiment_available}. Return strict JSON matching test.json format: {{'recommendation':'...','confidence':0.0,'explanation':'...'}}"
    try:
        result = _call_gemini(prompt)
        return json.loads(result)
    except Exception:
        return {'error': 'parse_failed'}
