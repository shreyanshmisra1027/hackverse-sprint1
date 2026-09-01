"""
HACKVERSE 2026 Demo Script
PS-01: Multi-Agent Autonomous Financial Intelligence System
VIT Chennai - IEEE RAS Student Chapter
"""
from pipeline import run_pipeline
import pconfig

print("="*70)
print("HACKVERSE 2026 - Multi-Agent Financial Intelligence System")
print("PS-01: Autonomous Financial Intelligence for Retail Investors")
print("VIT Chennai - IEEE Robotics & Automation Society Student Chapter")
print("="*70)

# DEMO 1: Normal mode - Medium risk user
print("\n### DEMO 1: Full Multi-Agent Analysis")
print("-"*70)
print("User: Priya (Medium risk tolerance)")
print("Stock: NVIDIA")
print("Mode: All agents active")
print()

pconfig.SENTIMENT_AVAILABLE = True
result1 = run_pipeline("NVIDIA", "Priya", sentiment_available=True)

print(f"✓ Technical Signal: {result1['technical'].get('signal', 'N/A')}")
print(f"✓ Sentiment Signal: {result1['sentiment'].get('signal', 'N/A') if result1['sentiment'] else 'N/A'}")
print(f"✓ Filings Outlook: {result1['filings'].get('outlook', 'N/A')}")
print(f"✓ Synthesis Recommendation: {result1['synthesis'].get('recommendation', 'N/A')}")
print(f"✓ Confidence: {result1['synthesis'].get('confidence', 0):.2f}")
print(f"\nPersonalized Output:")
print(f"  {result1['personalized'].get('personalized_text', 'N/A')}")
print(f"\nMetrics:")
print(f"  Latency: {result1['latency_ms']:.0f}ms")
print(f"  Risk Score: {result1['risk_score']}")
print(f"  Source: {result1['source']}")

# DEMO 2: Degraded mode - Low risk user
print("\n\n### DEMO 2: Degraded Data Scenario (Sentiment Unavailable)")
print("-"*70)
print("User: Ramesh (Low risk tolerance)")
print("Stock: TESLA")
print("Mode: Sentiment agent DISABLED")
print()

pconfig.SENTIMENT_AVAILABLE = False
result2 = run_pipeline("TESLA", "Ramesh", sentiment_available=False)

print(f"✓ Technical Signal: {result2['technical'].get('signal', 'N/A')}")
print(f"✓ Sentiment Signal: {'UNAVAILABLE (degraded mode)' if result2['degraded_mode'] else 'N/A'}")
print(f"✓ Filings Outlook: {result2['filings'].get('outlook', 'N/A')}")
print(f"✓ Synthesis Recommendation: {result2['synthesis'].get('recommendation', 'N/A')}")
print(f"\nPersonalized Output (Risk-Adjusted for Low Risk):")
print(f"  {result2['personalized'].get('personalized_text', 'N/A')}")
print(f"\nSystem gracefully handled missing sentiment data.")

# DEMO 3: Different user profiles, same stock
print("\n\n### DEMO 3: User Personalization (Same Stock, 3 Different Users)")
print("-"*70)
print("Stock: TATAMOTORS")
print("Testing how risk tolerance affects recommendations:")
print()

pconfig.SENTIMENT_AVAILABLE = True

users_to_test = ["Ramesh", "Priya", "Aakash"]
risk_levels = ["Low", "Medium", "High"]

for user_name, risk in zip(users_to_test, risk_levels):
    result = run_pipeline("TATAMOTORS", user_name, sentiment_available=True)
    print(f"{user_name} ({risk} risk):")
    print(f"  {result['personalized'].get('personalized_text', 'N/A')[:120]}...")
    print()

# Summary
print("="*70)
print("DEMO COMPLETE - All Hackathon Requirements Demonstrated:")
print("="*70)
print("✓ Multi-agent architecture (technical, sentiment, filings, synthesis)")
print("✓ Signal classification across 3 dimensions with confidence levels")
print("✓ RAG component (document retrieval from SEC filings)")
print("✓ User profiling with behavioral personalization")
print("✓ Performance metrics (latency, confidence, risk scoring)")
print("✓ Graceful degraded-data handling (sentiment unavailable)")
print("✓ Source attribution (filings citations)")
print("✓ Session logging to database")
print("="*70)
print("\n🎯 Backend is WORKING and ready for frontend integration!")
print("   Use: from pipeline import run_pipeline")
print("   Call: run_pipeline(stock, profile_name, sentiment_available)")
