#!/usr/bin/env python3
"""Test script for agents.py"""

from agents import technical_agent, sentiment_agent, filings_agent, synthesis_agent

print("Testing technical_agent...")
technical_result = technical_agent("AAPL stock: price=$150, RSI=65, MACD=bullish, volume=high")
print(f"Technical: {technical_result}\n")

print("Testing sentiment_agent...")
sentiment_result = sentiment_agent("Apple announces record profits. CEO optimistic about AI integration. Analysts raise price targets.")
print(f"Sentiment: {sentiment_result}\n")

print("Testing filings_agent...")
filings_result = filings_agent(
    query="What is the company's outlook?",
    chunk="Revenue increased 15% YoY. Management expects continued growth in cloud services.",
    source="10-K filing Q3 2026"
)
print(f"Filings: {filings_result}\n")

print("Testing synthesis_agent...")
synthesis_result = synthesis_agent(
    technical=technical_result,
    sentiment=sentiment_result,
    filings=filings_result,
    sentiment_available=True
)
print(f"Synthesis: {synthesis_result}\n")

print("=" * 50)
print("All tests completed!")
