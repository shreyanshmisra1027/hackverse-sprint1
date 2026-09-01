"""Quick test of integration"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Data.data import stock_data, news, search
from agents.agents import run_all_agents

# Test data retrieval
ticker = "NVIDIA"
print(f"Testing {ticker}...")

# Get stock data
stock_info = f"{ticker}: price=${stock_data[ticker]['price']}, change={stock_data[ticker]['change_pct']}%, volume={stock_data[ticker]['volume']}"
print(f"Stock data: {stock_info}")

# Get news
news_text = news[ticker]
print(f"News: {news_text}")

# Search filings
query = "What is NVIDIA's outlook?"
chunk, source = search(query)
print(f"Filing chunk: {chunk}")
print(f"Source: {source}")

# Run agents
print("\nRunning agents...")
result = run_all_agents(
    stock_data=stock_info,
    news_text=news_text,
    filing_query=query,
    chunk=chunk,
    source=source,
    sentiment_available=True
)

print("\n=== Results ===")
import json
print(json.dumps(result, indent=2))
