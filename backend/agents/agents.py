"""
Four AI agents that run in parallel to produce a stock analysis.

Each agent returns a typed dict; see individual function docstrings for
the exact shape. All external calls go through `_call_gemini` which
handles retry logic and multi-key rotation transparently.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Optional

import google.generativeai as genai

# Bring config into scope early so validate_config() can be called.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    GEMINI_MODEL,
    RETRIES_PER_CALL,
    INITIAL_BACKOFF_SECS,
    get_api_keys,
    validate_config,
    logger,
)

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
_key_manager: Optional[Any] = None  # Lazy-initialised; None = not yet tried.
_config_validated: bool = False

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_validated() -> None:
    """Call validate_config() exactly once, the first time an agent runs."""
    global _config_validated
    if not _config_validated:
        validate_config()
        _config_validated = True


def _get_key_manager() -> Optional[Any]:
    """
    Return the key-manager instance, initialising it on first call.

    Returns None if the key manager module is unavailable (e.g. running
    outside the full backend package) — callers must handle that case.
    """
    global _key_manager
    if _key_manager is not None:
        return _key_manager if _key_manager is not False else None

    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from utils.key_manager import get_key_manager as _gm
        _key_manager = _gm()
    except Exception as exc:
        logger.warning("Could not initialise key manager (%s); using single-key mode.", exc)
        _key_manager = False
    return _key_manager if _key_manager is not False else None


def _strip_code_fences(text: str) -> str:
    """Remove triple-backtick fences from LLM output if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 2 and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1])
    return text


def _call_gemini(prompt_text: str) -> str:
    """
    Send *prompt_text* to Gemini and return the response body.

    Handles:
    - Multi-key rotation via key_manager (when available)
    - Rate-limit (429) back-off and key switching
    - Generic retry with exponential back-off
    - Markdown code-fence stripping

    Raises:
        RuntimeError: after all retries are exhausted or no keys are available.
    """
    _ensure_validated()

    km = _get_key_manager()
    max_retries = RETRIES_PER_CALL
    backoff = INITIAL_BACKOFF_SECS

    for attempt in range(max_retries):
        try:
            # Ensure the active key is configured
            if km and not km.configure_genai():
                raise RuntimeError("All configured API keys are exhausted.")

            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt_text)
            result = response.text.strip()
            result = _strip_code_fences(result)

            if km:
                km.increment_usage()
            logger.debug("Gemini call succeeded (attempt %d)", attempt + 1)
            return result

        except Exception as exc:
            error_msg = str(exc)
            is_rate_limit = (
                "429" in error_msg
                or "quota" in error_msg.lower()
                or "rate" in error_msg.lower()
            )

            if is_rate_limit and km:
                retry_after: float = 3600.0
                m = re.search(r"(\d+(?:\.\d+)?)\s*s", error_msg)
                if m:
                    retry_after = float(m.group(1))
                km.mark_exhausted(retry_after)
                next_key = km.get_active_key()
                if next_key:
                    logger.warning("Rate limit hit; switching to next key.")
                    continue  # retry with new key

            if is_rate_limit and attempt < max_retries - 1:
                logger.warning(
                    "Rate limit hit, retrying in %.0fs (attempt %d/%d).",
                    backoff, attempt + 1, max_retries,
                )
                time.sleep(backoff)
                backoff *= 2
                continue

            logger.error("Gemini call failed: %s", exc)
            raise RuntimeError(f"Gemini call failed after {attempt + 1} attempt(s): {exc}") from exc

    raise RuntimeError(f"Gemini call failed after {max_retries} retries.")


def _safe_parse_json(raw: str, context: str = "response") -> dict[str, Any]:
    """
    Parse *raw* as JSON and return the dict.

    Falls back to an ``{'error': 'parse_failed', 'detail': ...}`` dict
    rather than raising, so callers can propagate a graceful error signal
    up the pipeline without crashing.
    """
    try:
        # Try stripping fences first
        cleaned = _strip_code_fences(raw)
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse error (%s): %s. Raw: %.200s", context, exc, raw)
        return {"error": "parse_failed", "detail": str(exc), "raw_preview": raw[:200]}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Agent implementations
# ---------------------------------------------------------------------------

def technical_agent(stock_data: str) -> dict[str, Any]:
    """
    Analyse stock price / volume data and return a technical signal.

    Args:
        stock_data: Human-readable stock info, e.g.
            ``"NVIDIA: price=$118.50, change=+3.2%, volume=very high"``.

    Returns::

        {
            "signal": "BUY" | "SELL" | "HOLD",
            "signal_type": "technical_momentum",
            "confidence": float,          # 0.0 – 1.0
            "reasoning": str,
            "sources": [{"type": "market_data", "value": "…"}],
            "timestamp": ISO-8601 str,
        }
        On error: ``{"error": "…", "timestamp": …}``
    """
    logger.info("Running technical_agent")
    prompt = (
        f'Analyse stock data: {stock_data}.\n'
        'Return strict JSON with this structure: '
        '{"signal": "BUY|SELL|HOLD", "signal_type": "technical_momentum", '
        '"confidence": 0.0, "reasoning": "…", '
        '"sources": [{"type": "market_data", "value": "…"}]}\n'
        "Return ONLY the JSON object. No markdown formatting, no code fences."
    )
    try:
        raw = _call_gemini(prompt)
        parsed = _safe_parse_json(raw, "technical_agent")
        if "error" not in parsed:
            logger.info("technical_agent → signal=%s confidence=%.2f",
                        parsed.get("signal"), parsed.get("confidence"))
        parsed.setdefault("timestamp", _utc_now())
        return parsed
    except Exception as exc:  # pragma: no cover — caught by _safe_parse_json in normal path
        logger.error("technical_agent raised unhandled exception: %s", exc)
        return {"error": str(exc), "timestamp": _utc_now()}


def sentiment_agent(news_text: str) -> dict[str, Any]:
    """
    Analyse news headlines and return a sentiment signal.

    Args:
        news_text: News headline or summary, e.g.
            ``"NVIDIA beats earnings estimates on strong AI chip demand"``.

    Returns::

        {
            "signal": "bullish" | "bearish" | "neutral",
            "signal_type": "sentiment_news",
            "confidence": float,
            "reasoning": str,
            "sources": [{"type": "news", "value": "…"}],
            "timestamp": ISO-8601 str,
        }
        On error: ``{"error": "…", "timestamp": …}``
    """
    logger.info("Running sentiment_agent")
    prompt = (
        f'Analyse news sentiment: {news_text}.\n'
        'Return strict JSON with this structure: '
        '{"signal": "bullish|bearish|neutral", "signal_type": "sentiment_news", '
        '"confidence": 0.0, "reasoning": "…", '
        '"sources": [{"type": "news", "value": "…"}]}\n'
        "Return ONLY the JSON object. No markdown formatting, no code fences."
    )
    try:
        raw = _call_gemini(prompt)
        parsed = _safe_parse_json(raw, "sentiment_agent")
        if "error" not in parsed:
            logger.info("sentiment_agent → signal=%s confidence=%.2f",
                        parsed.get("signal"), parsed.get("confidence"))
        parsed.setdefault("timestamp", _utc_now())
        return parsed
    except Exception as exc:
        logger.error("sentiment_agent raised unhandled exception: %s", exc)
        return {"error": str(exc), "timestamp": _utc_now()}


def filings_agent(query: str, chunk: str, source: str) -> dict[str, Any]:
    """
    Query SEC filing excerpts and return an outlook signal.

    Args:
        query: The search question, e.g. ``"What is NVIDIA's revenue outlook?"``.
        chunk: The retrieved filing text snippet.
        source: Citation label from the retrieval layer, e.g. ``"NVIDIA_1"``.

    Returns::

        {
            "outlook": "positive" | "negative" | "neutral",
            "signal_type": "filings_outlook",
            "confidence": float,
            "reasoning": str,
            "source": str,                  # same as input *source*
            "retrieved_context": str,       # first 200 chars of *chunk*
            "sources": [{"type": "sec_filing", "value": "…"}],
            "timestamp": ISO-8601 str,
        }
        On error: ``{"error": "…", "timestamp": …}``
    """
    logger.info("Running filings_agent (source=%s)", source)
    prompt = (
        f"Query: {query}\n"
        f"Chunk: {chunk}\n"
        f'Source: {source}\n'
        'Return strict JSON with this structure: '
        '{"outlook": "positive|negative|neutral", "signal_type": "filings_outlook", '
        '"confidence": 0.0, "reasoning": "…", '
        '"source": "{source}", '
        '"retrieved_context": "…", '
        '"sources": [{"type": "sec_filing", "value": "{source}"}]}\n'
        "Return ONLY the JSON object. No markdown formatting, no code fences."
    )
    try:
        raw = _call_gemini(prompt)
        parsed = _safe_parse_json(raw, "filings_agent")
        if "error" not in parsed:
            logger.info("filings_agent → outlook=%s confidence=%.2f",
                        parsed.get("outlook"), parsed.get("confidence"))
        if "retrieved_context" not in parsed:
            parsed["retrieved_context"] = chunk[:200]
        parsed.setdefault("source", source)
        parsed.setdefault("timestamp", _utc_now())
        return parsed
    except Exception as exc:
        logger.error("filings_agent raised unhandled exception: %s", exc)
        return {"error": str(exc), "timestamp": _utc_now()}


def synthesis_agent(
    technical: dict[str, Any],
    sentiment: Optional[dict[str, Any]],
    filings: dict[str, Any],
    sentiment_available: bool,
) -> dict[str, Any]:
    """
    Combine all agent outputs into a final investment recommendation.

    Args:
        technical: Output from :func:`technical_agent`.
        sentiment: Output from :func:`sentiment_agent`, or ``None`` if disabled.
        filings:   Output from :func:`filings_agent`.
        sentiment_available: Whether the sentiment agent ran.

    Returns::

        {
            "recommendation": str,
            "confidence": float,
            "explanation": str,
        }
        On error: ``{"error": "…"}``
    """
    logger.info("Running synthesis_agent (sentiment_available=%s)", sentiment_available)
    prompt = (
        f"Synthesize: technical={technical}, sentiment={sentiment}, "
        f"filings={filings}, sentiment_available={sentiment_available}.\n"
        'Return strict JSON: '
        '{"recommendation": "…", "confidence": 0.0, "explanation": "…"}\n'
        "Return ONLY the JSON object. No markdown formatting, no code fences."
    )
    try:
        raw = _call_gemini(prompt)
        parsed = _safe_parse_json(raw, "synthesis_agent")
        if "error" not in parsed:
            logger.info("synthesis_agent → recommendation=%s confidence=%.2f",
                        parsed.get("recommendation"), parsed.get("confidence"))
        return parsed
    except Exception as exc:
        logger.error("synthesis_agent raised unhandled exception: %s", exc)
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Public pipeline entry point
# ---------------------------------------------------------------------------

def run_all_agents(
    stock_data: str,
    news_text: str,
    filing_query: str,
    chunk: str,
    source: str,
    sentiment_available: bool = True,
) -> dict[str, Any]:
    """
    Run all four agents in parallel and return a combined result dict.

    Args:
        stock_data:       Formatted stock-market data string.
        news_text:        News headline / summary string.
        filing_query:     Question to ask the filings retrieval layer.
        chunk:            Retrieved filing text snippet.
        source:           Citation label for the retrieved snippet.
        sentiment_available: Pass ``False`` to skip the sentiment agent.

    Returns::

        {
            "technical": <dict from technical_agent>,
            "sentiment": <dict from sentiment_agent> | None,
            "filings":   <dict from filings_agent>,
            "synthesis": <dict from synthesis_agent>,
        }
    """
    logger.info(
        "run_all_agents started (sentiment_available=%s, source=%s)",
        sentiment_available, source,
    )

    results: dict[str, Any] = {
        "technical": {"error": "not_run"},
        "sentiment": None,
        "filings": {"error": "not_run"},
        "synthesis": {"error": "not_run"},
    }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(technical_agent, stock_data): "technical",
            executor.submit(filings_agent, filing_query, chunk, source): "filings",
            executor.submit(synthesis_agent,
                            results["technical"], None, results["filings"],
                            sentiment_available): "synthesis",
        }
        if sentiment_available:
            futures[
                executor.submit(sentiment_agent, news_text)
            ] = "sentiment"

        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                logger.error("Agent '%s' raised: %s", key, exc)
                results[key] = {"error": str(exc)}

    # Synthesis needs the actual agent outputs, not error dicts — re-run if needed
    if results["synthesis"].get("error"):
        logger.warning("Re-running synthesis_agent with final agent results.")
        results["synthesis"] = synthesis_agent(
            results["technical"],
            results["sentiment"],
            results["filings"],
            sentiment_available,
        )

    logger.info("run_all_agents completed.")
    return results


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Running agents smoke test...")
    result = run_all_agents(
        stock_data="AAPL: price=$175, RSI=58, MACD=bullish, volume=high",
        news_text="Apple announces strong Q3 earnings, beating analyst expectations.",
        filing_query="What is the revenue outlook?",
        chunk="Q3 revenue grew 12% YoY to $95B. Management projects continued growth.",
        source="10-K Q3 2026",
        sentiment_available=True,
    )
    print("\n=== Results ===")
    print(json.dumps(result, indent=2))
