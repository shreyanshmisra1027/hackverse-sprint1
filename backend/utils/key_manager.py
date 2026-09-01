"""
API Key Manager with automatic rotation on rate limits.
Supports multiple Gemini API keys and switches when one is exhausted.
"""

import os
import time
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import google.generativeai as genai


@dataclass
class APIKey:
    """Represents an API key with its quota status."""
    key: str
    name: str
    is_exhausted: bool = False
    exhausted_until: Optional[datetime] = None
    request_count: int = 0


class APIKeyManager:
    """Manages multiple API keys with automatic rotation."""

    def __init__(self, keys: List[dict]):
        """
        Initialize with list of API keys.

        Args:
            keys: List of dicts with 'key' and 'name' fields
                  Example: [{"key": "AIza...", "name": "key1"}, ...]
        """
        self.keys = [APIKey(key=k['key'], name=k['name']) for k in keys]
        self.current_index = 0

        if not self.keys:
            raise ValueError("At least one API key must be provided")

    def get_active_key(self) -> Optional[APIKey]:
        """Get the current active API key that's not exhausted."""
        # First, check if any exhausted keys have recovered
        now = datetime.now()
        for key in self.keys:
            if key.is_exhausted and key.exhausted_until and now >= key.exhausted_until:
                key.is_exhausted = False
                key.exhausted_until = None
                print(f"✓ API key '{key.name}' quota recovered")

        # Try current key first
        if not self.keys[self.current_index].is_exhausted:
            return self.keys[self.current_index]

        # Find first non-exhausted key
        for i, key in enumerate(self.keys):
            if not key.is_exhausted:
                self.current_index = i
                print(f"→ Switched to API key '{key.name}'")
                return key

        # All keys exhausted
        return None

    def mark_exhausted(self, retry_after_seconds: float = 3600):
        """Mark current key as exhausted and try to switch."""
        current_key = self.keys[self.current_index]
        current_key.is_exhausted = True
        current_key.exhausted_until = datetime.now() + timedelta(seconds=retry_after_seconds)

        print(f"✗ API key '{current_key.name}' exhausted (retry after {retry_after_seconds}s)")

        # Try to switch to another key
        next_key = self.get_active_key()
        if next_key:
            print(f"✓ Using API key '{next_key.name}'")
        else:
            print("⚠ All API keys exhausted!")

    def configure_genai(self) -> bool:
        """Configure genai with an active key. Returns True if successful."""
        active_key = self.get_active_key()
        if active_key:
            genai.configure(api_key=active_key.key)
            return True
        return False

    def increment_usage(self):
        """Track request count for current key."""
        if 0 <= self.current_index < len(self.keys):
            self.keys[self.current_index].request_count += 1

    def get_status(self) -> dict:
        """Get status of all keys."""
        return {
            "keys": [
                {
                    "name": k.name,
                    "exhausted": k.is_exhausted,
                    "requests": k.request_count,
                    "recovers_at": k.exhausted_until.isoformat() if k.exhausted_until else None
                }
                for k in self.keys
            ],
            "active": self.keys[self.current_index].name if self.get_active_key() else None
        }


# Global key manager instance
_key_manager: Optional[APIKeyManager] = None


def initialize_key_manager():
    """Initialize the global key manager from environment variables."""
    global _key_manager

    # Load keys from .env
    # Format: GOOGLE_API_KEY_1=..., GOOGLE_API_KEY_2=..., etc.
    from dotenv import load_dotenv
    load_dotenv()

    keys = []

    # Check for primary key
    primary_key = os.getenv('GOOGLE_API_KEY')
    if primary_key:
        keys.append({"key": primary_key, "name": "primary"})

    # Check for numbered keys
    i = 1
    while True:
        key = os.getenv(f'GOOGLE_API_KEY_{i}')
        if not key:
            break
        keys.append({"key": key, "name": f"key_{i}"})
        i += 1

    if not keys:
        raise ValueError("No API keys found in environment. Set GOOGLE_API_KEY or GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, etc.")

    _key_manager = APIKeyManager(keys)
    print(f"✓ Initialized with {len(keys)} API key(s)")

    return _key_manager


def get_key_manager() -> APIKeyManager:
    """Get the global key manager instance."""
    global _key_manager
    if _key_manager is None:
        initialize_key_manager()
    return _key_manager


if __name__ == "__main__":
    # Test the key manager
    print("Testing API Key Manager...\n")

    try:
        manager = initialize_key_manager()
        print("\nKey Status:")
        import json
        print(json.dumps(manager.get_status(), indent=2))

        print("\nTesting API call...")
        if manager.configure_genai():
            model = genai.GenerativeModel('gemini-3.6-flash')
            response = model.generate_content('Say hello')
            print(f"Response: {response.text[:100]}")
            manager.increment_usage()
        else:
            print("No active keys available")

        print("\nFinal Status:")
        print(json.dumps(manager.get_status(), indent=2))

    except Exception as e:
        print(f"Error: {e}")
