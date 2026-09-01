"""
Flask server connecting frontend HTML to backend pipeline.

Run from repo root:
    myenv/bin/python frontend/server.py

Then open http://localhost:5000
"""
import os
import sys
import time

# Add backend directory to path so we can import pipeline modules
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, BACKEND_DIR)

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)


# ---------------------------------------------------------------------------
# In-memory performance log — accumulates across pipeline runs
# ---------------------------------------------------------------------------
PERFORMANCE_LOG: list[dict] = []


def _user_profile(name: str) -> dict:
    """Look up a user profile by name; default to medium risk if unknown."""
    profiles = {
        "Ramesh": {"name": "Ramesh", "risk_tolerance": "low", "portfolio": ["TCS", "HDFC"], "age_bracket": "45-60"},
        "Priya":  {"name": "Priya",  "risk_tolerance": "medium", "portfolio": ["INFY", "RELIANCE"], "age_bracket": "25-35"},
        "Aakash": {"name": "Aakash", "risk_tolerance": "high", "portfolio": ["TATAMOTORS"], "age_bracket": "20-30"},
    }
    return profiles.get(name, {"name": name, "risk_tolerance": "medium", "portfolio": [], "age_bracket": "unknown"})


def _run_pipeline(stock: str, profile_name: str, sentiment_available: bool) -> dict:
    """
    End-to-end pipeline: market data -> 3 agents -> RAG -> synthesis -> personalize.

    Uses the backend's run_pipeline if importable, else falls back to a
    deterministic local pipeline that still exercises every requirement.
    """
    start = time.time()
    user = _user_profile(profile_name)
    risk = user["risk_tolerance"]

    # Try the backend pipeline first (real Gemini agents).
    try:
        from pipeline import run_pipeline as _backend_run  # type: ignore
        result = _backend_run(stock, profile_name, sentiment_available)
        result.setdefault("user_profile", user)
        result.setdefault("stock", stock)
        result.setdefault("user", profile_name)
        result.setdefault("risk_tolerance", risk)
        return result
    except Exception as exc:
        # Backend pipeline unavailable (e.g. rate-limited, missing API key).
        # Fall through to deterministic local pipeline that still satisfies
        # every requirement.
        sys.stderr.write(f"[server] backend pipeline unavailable ({exc}); using local fallback\n")

    # ---------------- Local fallback pipeline ----------------
    from Data.data import search, stock_data, news
    from agents.agents import (
        technical_agent,
        sentiment_agent,
        filings_agent,
        synthesis_agent,
    )

    stock_info = stock_data.get(stock, {"price": 0, "change_pct": 0, "volume": "unknown"})
    news_text = news.get(stock, f"No news available for {stock}")
    query = f"{stock} outlook"
    chunk, source = search(query) or (f"No filings available for {stock}", f"{stock}_N/A")

    tech = technical_agent(f"{stock}: price=${stock_info['price']}, change={stock_info['change_pct']}%, volume={stock_info['volume']}")
    sent = sentiment_agent(news_text) if sentiment_available else None
    filings = filings_agent(query, chunk, source)

    synth = synthesis_agent(tech, sent, filings, sentiment_available)

    # Local personalize (mirrors backend/personalize/personalize.py)
    rec = (synth.get("recommendation") or "hold").lower()
    confidence = synth.get("confidence", 0.5) or 0.5
    reasoning = synth.get("explanation", "Multi-agent synthesis complete.")

    if risk == "low":
        if rec == "buy":
            ptext = f"Consider {stock} cautiously — small position only. {reasoning} Note: this signal carries volatility risk; size positions conservatively."
        elif rec == "sell":
            ptext = f"Consider trimming {stock} gradually rather than exiting fully. {reasoning} Note: size positions conservatively."
        else:
            ptext = f"Hold {stock} — no urgent action needed. {reasoning} Note: this signal carries volatility risk; size positions conservatively."
    elif risk == "high":
        ptext = f"{rec.upper()} {stock}. {reasoning}"
        if rec == "buy":
            ptext += " Upside potential flagged — this fits an aggressive risk profile."
    else:
        ptext = f"{rec.capitalize()} {stock} — moderate conviction. {reasoning}"

    if not sentiment_available:
        ptext = f"[Based on 2 of 3 signals — sentiment data unavailable] " + ptext

    latency_ms = (time.time() - start) * 1000

    # Risk score (0-1)
    risk_score = round(0.2 + (1 - confidence) * 0.5, 2) if not sentiment_available else round(0.2 + (1 - confidence) * 0.4, 2)

    return {
        "technical": tech,
        "sentiment": sent,
        "filings": filings,
        "synthesis": synth,
        "personalized": {
            "recommendation": rec,
            "confidence": confidence,
            "personalized_text": ptext,
            "signals_used": ["price_momentum", "volume_anomaly"] + (["sentiment"] if sentiment_available else []),
            "portfolio_overlap": stock in user.get("portfolio", []),
        },
        "source": source,
        "latency_ms": latency_ms,
        "stock": stock,
        "user": profile_name,
        "user_profile": user,
        "risk_tolerance": risk,
        "risk_score": "high" if risk_score > 0.6 else "medium" if risk_score > 0.4 else "low",
        "degraded_mode": not sentiment_available,
    }


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True, silent=True) or {}
    stock = data.get("stock", "NVIDIA")
    profile = data.get("profile", "Priya")
    sentiment_available = bool(data.get("sentiment_available", True))

    try:
        result = _run_pipeline(stock, profile, sentiment_available)
    except Exception as exc:
        return jsonify({"error": f"Pipeline failed: {exc}"}), 500

    # Append to in-memory performance log
    perf = {
        "latency_ms": result.get("latency_ms", 0),
        "confidence": (result.get("synthesis") or {}).get("confidence", 0.5),
        "risk_score": result.get("risk_score", "medium"),
        "stock": stock,
        "user": profile,
        "degraded_mode": result.get("degraded_mode", False),
        "timestamp": time.time(),
    }
    PERFORMANCE_LOG.append(perf)
    result["performance_history"] = list(PERFORMANCE_LOG)

    return jsonify(result)


@app.route("/api/performance", methods=["GET"])
def performance():
    """Return the in-memory performance history (requirement 6)."""
    return jsonify({"runs": list(PERFORMANCE_LOG), "count": len(PERFORMANCE_LOG)})


@app.route("/api/profiles", methods=["GET"])
def profiles():
    """Return the available user profiles for the UI dropdown."""
    return jsonify({
        "profiles": [
            {"name": "Ramesh", "risk_tolerance": "low", "portfolio": ["TCS", "HDFC"]},
            {"name": "Priya",  "risk_tolerance": "medium", "portfolio": ["INFY", "RELIANCE"]},
            {"name": "Aakash", "risk_tolerance": "high", "portfolio": ["TATAMOTORS"]},
        ]
    })


if __name__ == "__main__":
    print("=" * 60)
    print("Starting Hackverse Multi-Agent Financial Intelligence")
    print("Frontend: http://localhost:5000")
    print("API:      POST http://localhost:5000/api/analyze")
    print("=" * 60)
    app.run(debug=False, host="0.0.0.0", port=5000)
