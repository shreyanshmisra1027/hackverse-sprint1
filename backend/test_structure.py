"""
Quick test without API calls - verifies the pipeline structure works
"""
from pipeline import run_pipeline
import pconfig

# Mock test - just verify imports and structure work
print("Testing pipeline structure...")
print("✓ Imports successful")
print("✓ Pipeline function loaded")

# Check data availability
from Data.data import stock_data, news
print(f"✓ Stock data available: {list(stock_data.keys())}")
print(f"✓ News data available: {list(news.keys())}")

from users import users
print(f"✓ User profiles: {[u['name'] for u in users.values()]}")

print("\n✅ Backend structure is valid!")
print("\nTo run full demo with API calls:")
print("  python demo.py")
print("\nNote: Requires API keys with available quota")
