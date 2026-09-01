"""
Backend configuration module.

Loads environment variables from .env and validates required settings.
Must be imported before any API calls are made.
"""
from __future__ import annotations

import logging
import os
import sys

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("stock_analysis")


def _load_env() -> None:
    """Load .env file if present; silently skip if missing."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    loaded = load_dotenv(env_path)
    if loaded:
        logger.debug("Loaded environment from %s", env_path)
    else:
        logger.debug("No .env file found at %s", env_path)


_load_env()


# ---------------------------------------------------------------------------
# Model settings
# ---------------------------------------------------------------------------
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
"""Gemini model name used for all agent calls."""

RETRIES_PER_CALL: int = int(os.getenv("RETRIES_PER_CALL", "3"))
"""Number of retry attempts on transient API errors."""

INITIAL_BACKOFF_SECS: float = float(os.getenv("INITIAL_BACKOFF_SECS", "2.0"))
"""Initial backoff delay for retries (doubles each retry)."""


# ---------------------------------------------------------------------------
# API key helpers
# ---------------------------------------------------------------------------
def _get_key_env_vars() -> list[str]:
    """Return all GOOGLE_API_KEY env-var names to check."""
    keys = []
    if os.getenv("GOOGLE_API_KEY"):
        keys.append("GOOGLE_API_KEY")
    for i in range(1, 20):  # Check up to 20 extra keys
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if key:
            keys.append(f"GOOGLE_API_KEY_{i}")
    return keys


def get_api_keys() -> list[str]:
    """
    Return all configured Google API keys, in priority order.

    Raises:
        EnvironmentError: if no keys are found.
    """
    keys = _get_key_env_vars()
    if not keys:
        raise EnvironmentError(
            "No Google API key found. Set GOOGLE_API_KEY (and optionally "
            "GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, …) in your .env file. "
            "See https://ai.google.dev/ to obtain a key."
        )
    logger.info("Found %d configured API key(s)", len(keys))
    return keys


def validate_config() -> None:
    """
    Validate that at least one API key is present.

    Call this once at application startup. Raises EnvironmentError
    with a clear message if validation fails.
    """
    get_api_keys()
    logger.info("Configuration validated successfully.")


# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_ROOT, "Data")
SNIPPETS_PATH = os.path.join(DATA_DIR, "snippets.txt")
DB_PATH = os.path.join(BACKEND_ROOT, "sessions.db")
