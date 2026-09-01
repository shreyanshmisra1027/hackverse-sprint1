"""
Pipeline module - wires together retrieval, agents, personalization, and logging.
"""
import time
from Data.data import search, stock_data, news
from agents.agents import run_all_agents
from personalize import personalize
from users import users
from logger import log_session


def run_pipeline(stock: str, profile_name: str, sentiment_available: bool = True) -> dict:
    """
    Runs the full flow: retrieval -> agents -> personalization -> logging.

    Args:
        stock: Stock ticker (e.g., "NVIDIA", "TESLA", "TATAMOTORS")
        profile_name: User profile name (e.g., "Ramesh", "Priya", "Aakash")
        sentiment_available: Whether sentiment analysis is available

    Returns:
        Dict with everything the frontend needs to render:
        {
            "technical": {...},
            "sentiment": {...} or None,
            "filings": {...},
            "synthesis": {...},          # raw synthesis before personalization
            "personalized": {...},       # after personalize()
            "source": "<filename used for filings citation>",
            "latency_ms": <float>
        }
    """
    start_time = time.time()

    # 1. Build query and retrieve filings
    query = f"{stock} outlook"
    chunk, source = search(query)

    # 2. Get stock data and news
    stock_info = stock_data.get(stock, {})
    stock_text = f"{stock}: price=${stock_info.get('price', 0)}, change={stock_info.get('change_pct', 0)}%, volume={stock_info.get('volume', 'unknown')}"
    news_text = news.get(stock, f"No news available for {stock}")

    # 3. Run all agents
    agent_results = run_all_agents(
        stock_data=stock_text,
        news_text=news_text,
        filing_query=query,
        chunk=chunk,
        source=source,
        sentiment_available=sentiment_available
    )

    # 4. Get user profile by name
    user_profile = None
    for uid, profile in users.items():
        if profile['name'] == profile_name:
            user_profile = profile
            break

    if user_profile is None:
        raise ValueError(f"No user profile found with name '{profile_name}'")

    # 5. Personalize synthesis output
    synthesis = agent_results.get('synthesis', {})

    # Prepare input for personalize() - it expects specific fields
    to_personalize = {
        'stock': stock,
        'recommendation': synthesis.get('recommendation', 'hold'),
        'confidence': synthesis.get('confidence', 0.5),
        'reasoning': synthesis.get('explanation', ''),
        'sources': [],  # Could extract from agents if needed
        'signals_used': ['price_momentum', 'volume_anomaly', 'sentiment'] if sentiment_available else ['price_momentum', 'volume_anomaly']
    }

    personalized = personalize(to_personalize, user_profile)

    # 6. Calculate metrics
    latency_ms = (time.time() - start_time) * 1000
    confidence = synthesis.get('confidence', 0.5)

    # Simple risk score calculation
    if stock in user_profile.get('portfolio', []):
        risk_score = "high"
    elif confidence < 0.6:
        risk_score = "high"
    elif confidence < 0.8:
        risk_score = "medium"
    else:
        risk_score = "low"

    # 7. Log session
    log_session(
        stock=stock,
        latency_ms=latency_ms,
        confidence=confidence,
        risk_score=risk_score,
        signals_used=to_personalize['signals_used'],
        degraded_mode=not sentiment_available
    )

    # 8. Return complete package
    return {
        "technical": agent_results.get('technical', {}),
        "sentiment": agent_results.get('sentiment'),
        "filings": agent_results.get('filings', {}),
        "synthesis": synthesis,
        "personalized": personalized,
        "source": source,
        "latency_ms": latency_ms,
        "stock": stock,
        "user": profile_name,
        "risk_score": risk_score,
        "degraded_mode": not sentiment_available
    }


if __name__ == "__main__":
    # Quick test
    print("Testing pipeline...")
    result = run_pipeline("NVIDIA", "Priya", sentiment_available=True)
    print(f"\nStock: {result['stock']}")
    print(f"User: {result['user']}")
    print(f"Recommendation: {result['synthesis'].get('recommendation', 'N/A')}")
    print(f"Personalized: {result['personalized'].get('personalized_text', 'N/A')[:100]}...")
    print(f"Latency: {result['latency_ms']:.0f}ms")
    print(f"Risk Score: {result['risk_score']}")
    print("\n✓ Pipeline working!")
