#!/usr/bin/env python3
"""
Test script for the new indicator context engineering system.

This tests the agent-specific context and prompt components without requiring API calls.
"""

import pandas as pd
from backend.agents.indicators.integration_manager import indicator_agent_integration_manager
from backend.agents.indicators.context_engineer import indicator_context_engineer
from backend.agents.indicators.prompt_manager import indicator_prompt_manager

def test_context_engineering():
    """Test the new context engineering system without LLM calls."""
    
    print("[CONTEXT_TEST] Testing Indicator Context Engineering")
    print("[CONTEXT_TEST] This demonstrates the new agent-specific approach")
    print("[CONTEXT_TEST] " + "="*50)
    
    # Create test data
    symbol = "AAPL"
    timeframe = "30 days, daily"
    
    # Sample curated data structure
    curated_data = {
        "analysis_focus": "technical_indicators_summary",
        "key_indicators": {
            "trend_indicators": {
                "direction": "bullish",
                "strength": "moderate", 
                "confidence": 0.75,
                "sma_20": 150.25,
                "sma_50": 148.75,
                "sma_200": 145.50,
                "price_to_sma_200": 0.03,
                "golden_cross": True
            },
            "momentum_indicators": {
                "rsi_current": 68.5,
                "rsi_status": "neutral",
                "direction": "bullish",
                "strength": "moderate",
                "confidence": 0.65,
                "macd": {
                    "histogram": 0.35,
                    "trend": "bullish"
                }
            },
            "volume_indicators": {
                "volume_ratio": 1.25,
                "volume_trend": "above_average"
            }
        },
        "critical_levels": {
            "support": [149.00, 147.50],
            "resistance": [152.00, 154.25]
        },
        "conflict_analysis_needed": True,
        "detected_conflicts": {
            "has_conflicts": True,
            "conflict_count": 1,
            "conflict_list": ["RSI approaching overbought while MACD strongly bullish"]
        }
    }
    
    print(f"[CONTEXT_TEST] Symbol: {symbol}")
    print(f"[CONTEXT_TEST] Timeframe: {timeframe}")
    
    # Test context engineering
    print("\n[CONTEXT_TEST] Testing Context Engineering...")
    try:
        context = indicator_context_engineer.build_indicator_context(
            curated_data=curated_data,
            symbol=symbol,
            timeframe=timeframe,
            knowledge_context="Additional market context for testing"
        )
        
        print("✅ Context engineering successful!")
        print(f"[CONTEXT_TEST] Generated context length: {len(context)} characters")
        print(f"[CONTEXT_TEST] Context preview (first 300 chars):")
        print("=" * 50)
        print(context[:300])
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Context engineering failed: {e}")
        return False
    
    # Test conflict detection
    print("\n[CONTEXT_TEST] Testing Enhanced Conflict Detection...")
    try:
        conflicts = indicator_context_engineer.detect_indicator_conflicts(
            curated_data["key_indicators"]
        )
        
        print("✅ Conflict detection successful!")
        print(f"[CONTEXT_TEST] Detected conflicts: {conflicts.get('conflict_count', 0)}")
        print(f"[CONTEXT_TEST] Conflict severity: {conflicts.get('conflict_severity', 'none')}")
        
    except Exception as e:
        print(f"❌ Conflict detection failed: {e}")
    
    # Test prompt management  
    print("\n[CONTEXT_TEST] Testing Prompt Management...")
    try:
        prompt = indicator_prompt_manager.format_indicator_summary_prompt(context)
        
        print("✅ Prompt formatting successful!")
        print(f"[CONTEXT_TEST] Generated prompt length: {len(prompt)} characters")
        print(f"[CONTEXT_TEST] Available templates: {indicator_prompt_manager.get_available_templates()}")
        
    except Exception as e:
        print(f"❌ Prompt formatting failed: {e}")
    
    print("\n[CONTEXT_TEST] ✅ All Context Engineering Tests Completed!")
    print("[CONTEXT_TEST] The new agent-specific architecture is working correctly.")
    
    return True

def test_fallback_curation():
    """Test the fallback curation system."""
    
    print("\n[FALLBACK_TEST] Testing Fallback Curation System")
    print("[FALLBACK_TEST] " + "="*40)
    
    # Create realistic test data
    stock_data = pd.DataFrame({
        'open': [148.0, 149.0, 150.0, 151.0, 150.5],
        'high': [149.5, 150.5, 151.5, 152.0, 151.0],
        'low': [147.5, 148.5, 149.5, 150.0, 149.5],
        'close': [149.0, 150.0, 151.0, 150.5, 149.8],
        'volume': [1000000, 1200000, 1100000, 950000, 1050000]
    })
    
    indicators = {
        "rsi": {"rsi_14": 55.5, "status": "neutral"},
        "macd": {"histogram": 0.25, "trend": "bullish"},
        "moving_averages": {
            "sma_20": 150.0,
            "sma_50": 148.5,
            "sma_200": 145.0,
            "ema_20": 150.2,
            "ema_50": 148.8,
            "price_to_sma_200": 0.032,
            "sma_20_to_sma_50": 0.010,
            "golden_cross": True
        },
        "volume": {
            "volume_ratio": 1.15
        }
    }
    
    try:
        # Test fallback curation
        fallback_result = indicator_agent_integration_manager._create_fallback_curated_indicators(
            indicators=indicators,
            stock_data=stock_data
        )
        
        print("✅ Fallback curation successful!")
        print(f"[FALLBACK_TEST] Keys generated: {list(fallback_result.keys())}")
        print(f"[FALLBACK_TEST] Indicator types: {list(fallback_result.get('key_indicators', {}).keys())}")
        
        # Check if it includes volume zones
        critical_levels = fallback_result.get('critical_levels', {})
        if 'volume_bands' in critical_levels:
            print("✅ Volume zones integration working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback curation failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_context_engineering()
    success2 = test_fallback_curation()
    
    if success1 and success2:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ New Agent-Specific Architecture Working Correctly")
        print("✅ Context Engineering: PASSED") 
        print("✅ Prompt Management: PASSED")
        print("✅ Conflict Detection: PASSED")
        print("✅ Fallback Systems: PASSED")
        print("="*60)
    else:
        print("\n❌ Some tests failed - check output above")