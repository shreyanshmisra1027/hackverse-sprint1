"""
Integration layer between data sources and AI agents.
Fetches stock data, news, and filings, then runs agent analysis.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Data.data import stock_data, news, search
from agents.agents import run_all_agents
import json


def format_stock_data(ticker: str) -> str:
    """Format stock data dict into a readable string for the technical agent."""
    if ticker not in stock_data:
        return f"No data available for {ticker}"

    data = stock_data[ticker]
    return (f"{ticker}: price=${data['price']}, "
            f"change={data['change_pct']}%, "
            f"volume={data['volume']}")


def get_news_text(ticker: str) -> str:
    """Get news text for the sentiment agent."""
    return news.get(ticker, f"No news available for {ticker}")


def analyze_stock(ticker: str, filing_query: str = None, sentiment_available: bool = True):
    """
    Run full stock analysis for a given ticker.

    Args:
        ticker: Stock symbol (e.g., "NVIDIA", "TESLA", "TATAMOTORS")
        filing_query: Optional specific query for filings search (defaults to generic query)
        sentiment_available: Whether to include sentiment analysis

    Returns:
        Dict with technical, sentiment, filings, and synthesis analysis
    """
    # Prepare data for agents
    stock_info = format_stock_data(ticker)
    news_text = get_news_text(ticker)

    # Search filings
    if filing_query is None:
        filing_query = f"What is {ticker}'s financial outlook and guidance?"

    chunk, source = search(filing_query)

    if chunk is None:
        chunk = f"No filing data found for query: {filing_query}"
        source = "N/A"

    # Run all agents
    result = run_all_agents(
        stock_data=stock_info,
        news_text=news_text,
        filing_query=filing_query,
        chunk=chunk,
        source=source,
        sentiment_available=sentiment_available
    )

    # Add metadata
    result["ticker"] = ticker
    result["query"] = filing_query

    return result


def analyze_multiple_stocks(tickers: list, sentiment_available: bool = True, delay_between_stocks: float = 3.0):
    """
    Analyze multiple stocks at once.

    Args:
        tickers: List of stock symbols
        sentiment_available: Whether to include sentiment analysis
        delay_between_stocks: Seconds to wait between stocks to avoid rate limits

    Returns:
        Dict mapping ticker to analysis results
    """
    results = {}
    for i, ticker in enumerate(tickers):
        print(f"Analyzing {ticker}...")
        results[ticker] = analyze_stock(ticker, sentiment_available=sentiment_available)

        # Add delay between stocks (except after the last one)
        if i < len(tickers) - 1:
            print(f"Waiting {delay_between_stocks}s to avoid rate limits...")
            time.sleep(delay_between_stocks)

    return results


if __name__ == "__main__":
    print("=== Single Stock Analysis ===")
    result = analyze_stock("NVIDIA")
    print(json.dumps(result, indent=2))

    print("\n\n=== Multiple Stock Analysis ===")
    results = analyze_multiple_stocks(["NVIDIA", "TESLA", "TATAMOTORS"])
    for ticker, analysis in results.items():
        synthesis = analysis.get('synthesis', {})
        if 'recommendation' in synthesis:
            print(f"\n{ticker}: {synthesis['recommendation']} "
                  f"(confidence: {synthesis['confidence']})")
        else:
            print(f"\n{ticker}: Error - {synthesis.get('error', 'unknown error')}")
