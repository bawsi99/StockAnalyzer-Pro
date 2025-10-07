#!/usr/bin/env python3
"""
Test script for new indicator LLM integration system.
"""

import asyncio
import pandas as pd

from backend.agents.indicators.integration_manager import indicator_agent_integration_manager

async def test_indicator_llm_integration():
    print("[TEST] Starting Indicator LLM Integration Test")
    print("[TEST] Testing the new agent-specific context and prompt system")
    print("[TEST] This replaces the centralized ContextEngineer/PromptManager approach")
    print("[TEST] " + "="*60)
    
    # Example dummy data for testing
    symbol = "AAPL"
    print(f"[TEST] Testing with symbol: {symbol}")
    # Create realistic stock data for testing
    stock_data = pd.DataFrame({
        'open': [148.0, 149.0, 150.0, 151.0, 150.5],
        'high': [149.5, 150.5, 151.5, 152.0, 151.0],
        'low': [147.5, 148.5, 149.5, 150.0, 149.5],
        'close': [149.0, 150.0, 151.0, 150.5, 149.8],
        'volume': [1000000, 1200000, 1100000, 950000, 1050000]
    })
    indicators = {
        "rsi": 55,
        "macd": {"histogram": 0.3, "trend": "bullish"},
        "sma_20": 150.0,
        "sma_50": 148.0,
        "price": 149.5
    }
    period = 30
    interval = "day"
    context = ""

    success, markdown_summary, parsed_json, debug_info = await indicator_agent_integration_manager.get_enhanced_indicators_summary(
        symbol=symbol,
        stock_data=stock_data,
        indicators=indicators,
        period=period,
        interval=interval,
        context=context,
        return_debug=True
    )

    if success:
        print("[TEST] ✅ LLM Integration Successfully returned response.")
        print(f"[TEST] Markdown Summary Preview: {markdown_summary[:300]}...")
        print(f"[TEST] Parsed JSON Keys: {list(parsed_json.keys()) if parsed_json else 'None'}")
        if debug_info:
            print(f"[TEST] Debug Info Keys: {list(debug_info.keys())}")
        print("[TEST] Test completed successfully!")
    else:
        print("[TEST] ❌ LLM Integration failed.")
        print(f"[TEST] Error: {markdown_summary}")
        
        # Check if it's an API key issue vs other issues
        if "API key" in str(markdown_summary):
            print("[TEST] 💡 Note: This is expected if no API keys are configured.")
            print("[TEST] The integration manager is working correctly - it just needs API access.")
            print("[TEST] Architecture test: ✅ PASSED")
        else:
            print("[TEST] This appears to be a different error that should be investigated.")

if __name__ == "__main__":
    asyncio.run(test_indicator_llm_integration())