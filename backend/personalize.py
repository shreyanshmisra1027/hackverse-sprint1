import pconfig  # instead of: from pconfig import SENTIMENT_AVAILABLE

def personalize(synthesis_output: dict, user_profile: dict) -> dict:
    out = dict(synthesis_output)
    risk = user_profile["risk_tolerance"]
    stock = out.get("stock", "")
    rec = out.get("recommendation", "hold")
    reasoning = out.get("reasoning", "")
    signals_used = list(out.get("signals_used", ["price_momentum", "volume_anomaly", "sentiment"]))

    degraded = not pconfig.SENTIMENT_AVAILABLE   # <-- look it up live, not a stale copy
    if degraded and "sentiment" in signals_used:
        signals_used.remove("sentiment")
    out["signals_used"] = signals_used

    # portfolio overlap
    portfolio_overlap = stock in user_profile.get("portfolio", [])
    out["portfolio_overlap"] = portfolio_overlap

    # risk-based rewrite
    if risk == "low":
        if rec == "buy":
            text = f"Consider {stock} cautiously — small position only. {reasoning}"
        elif rec == "sell":
            text = f"Consider trimming {stock} gradually rather than exiting fully. {reasoning}"
        else:
            text = f"Hold {stock} — no urgent action needed. {reasoning}"
        text += " Note: this signal carries volatility risk; size positions conservatively."
        out["risk_adjusted_flag"] = "cautioned"

    elif risk == "high":
        text = f"{rec.upper()} {stock}. {reasoning}"
        if rec == "buy":
            text += " Upside potential flagged — this fits an aggressive risk profile."
        out["risk_adjusted_flag"] = "amplified"

    else:  # medium
        text = f"{rec.capitalize()} {stock} — moderate conviction. {reasoning}"
        out["risk_adjusted_flag"] = "neutral"

    if portfolio_overlap:
        text += f" You already hold {stock} — this signal adds to an existing position."

    if degraded:
        text = f"[Based on {len(signals_used)} of 3 signals — sentiment data unavailable] " + text

    out["personalized_text"] = text
    return out


if __name__ == "__main__":
    from users import users
    import pconfig   # <-- must be pconfig here too, not config

    sample_synthesis = {
        "stock": "TCS",
        "recommendation": "buy",
        "confidence": 0.78,
        "reasoning": "Strong momentum with volume confirmation.",
        "sources": [{"agent": "momentum_agent", "claim": "20-day MA breakout", "citation": "NSE feed"}],
        "signals_used": ["price_momentum", "volume_anomaly", "sentiment"],
    }

    print("=== Same signal, 3 different user profiles ===")
    for uid, profile in users.items():
        result = personalize(sample_synthesis, profile)
        print(f"\nUser {uid} ({profile['risk_tolerance']}): {result['personalized_text']}")

    print("\n=== Degraded data test (SENTIMENT_AVAILABLE True vs False) ===")
    pconfig.SENTIMENT_AVAILABLE = True
    print("ON: ", personalize(sample_synthesis, users[2])["personalized_text"])
    pconfig.SENTIMENT_AVAILABLE = False
    print("OFF:", personalize(sample_synthesis, users[2])["personalized_text"])
