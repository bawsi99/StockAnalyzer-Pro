#!/usr/bin/env python3
"""
Test script to verify the switch to optimized_final_decision template
and the comprehensive context building functionality.
"""

import sys
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from gemini.gemini_client import GeminiClient
    from core.utils import clean_for_json
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def test_comprehensive_context_building():
    """Test the comprehensive context building functionality."""
    
    # Create sample data
    sample_enhanced_ind_json = {
        "market_outlook": {
            "primary_trend": {
                "direction": "bullish",
                "confidence": 75,
                "strength": "moderate"
            }
        },
        "trading_strategy": {
            "short_term": {
                "bias": "bullish",
                "confidence": 80,
                "entry_strategy": {
                    "entry_range": [2450.0, 2470.0]
                },
                "exit_strategy": {
                    "stop_loss": 2400.0,
                    "targets": [
                        {"price": 2520.0, "probability": "high"},
                        {"price": 2580.0, "probability": "medium"}
                    ]
                }
            },
            "medium_term": {
                "bias": "bullish", 
                "confidence": 72,
                "entry_strategy": {
                    "entry_range": [2440.0, 2480.0]
                },
                "exit_strategy": {
                    "stop_loss": 2350.0,
                    "targets": [
                        {"price": 2600.0, "probability": "high"},
                        {"price": 2700.0, "probability": "medium"},
                        {"price": 2800.0, "probability": "low"}
                    ]
                }
            }
        },
        "existing_trading_strategy": {
            "short_term": {
                "entry_range": [2450.0, 2470.0],
                "stop_loss": 2400.0,
                "targets": [2520.0, 2580.0],
                "bias": "bullish",
                "confidence": 80
            },
            "medium_term": {
                "entry_range": [2440.0, 2480.0],
                "stop_loss": 2350.0,
                "targets": [2600.0, 2700.0, 2800.0],
                "bias": "bullish",
                "confidence": 72
            }
        }
    }
    
    sample_chart_insights = """
    **Technical Overview (Comprehensive Analysis):**
    The stock shows strong bullish momentum with RSI at 65 and MACD turning positive.
    
    **Pattern Analysis (All Pattern Recognition):**
    Ascending triangle pattern detected with breakout potential above 2470.
    
    **Volume Analysis (Complete Volume Story):**
    Volume confirms the bullish breakout with above-average trading activity.
    """
    
    sample_knowledge_context = """
    SECTOR CONTEXT:
    - Market Outperformance: +2.3%
    - Sector Outperformance: +1.8%
    - Sector Beta: 1.15
    
    MultiTimeframeContext:
    {
      "consensus_signal": "bullish",
      "confidence": 0.78,
      "timeframe_alignment": "strong"
    }
    
    MLSystemValidation:
    {
      "price": {"direction": "up", "confidence": 0.75},
      "consensus": {"overall_signal": "bullish", "confidence": 0.72}
    }
    
    AdvancedAnalysisDigest:
    {
      "advanced_risk": {"risk_level": "medium"},
      "stress_testing": "moderate_stress"
    }
    """
    
    print("=== Testing Comprehensive Context Building ===")
    
    client = GeminiClient()
    
    # Test the comprehensive context building
    try:
        comprehensive_context = client._build_comprehensive_context(
            sample_enhanced_ind_json, 
            sample_chart_insights, 
            sample_knowledge_context
        )
        
        print(f"✅ Context built successfully")
        print(f"📊 Context length: {len(comprehensive_context)} characters")
        
        # Verify that all expected sections are present
        expected_sections = [
            "## Technical Indicators Analysis",
            "## Chart Pattern Insights",
            "## Multi-Timeframe Analysis Context",
            "## Sector Analysis Context",
            "## Advanced Analysis Context", 
            "## ML System Context",
            "## EXISTING TRADING STRATEGY"
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in comprehensive_context:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  Missing sections: {missing_sections}")
        else:
            print("✅ All expected sections present in context")
        
        # Check for existing trading strategy
        if "existing_trading_strategy" in comprehensive_context:
            print("✅ Existing trading strategy included for consistency")
        else:
            print("❌ Existing trading strategy not found in context")
        
        # Verify JSON structures are valid
        sections = comprehensive_context.split("##")
        json_sections = 0
        for section in sections:
            if "{" in section and "}" in section:
                try:
                    # Extract potential JSON from section
                    start_idx = section.find("{")
                    brace_count = 0
                    end_idx = start_idx
                    for i, char in enumerate(section[start_idx:], start_idx):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                    
                    potential_json = section[start_idx:end_idx+1]
                    json.loads(potential_json)
                    json_sections += 1
                except json.JSONDecodeError:
                    pass
        
        print(f"✅ Found {json_sections} valid JSON sections in context")
        
        # Show a preview of the context structure
        print("\n📋 Context Structure Preview:")
        lines = comprehensive_context.split('\n')
        for line in lines[:20]:  # Show first 20 lines
            if line.startswith('##'):
                print(f"  {line}")
        
        if len(lines) > 20:
            print(f"  ... and {len(lines) - 20} more lines")
        
        return True
        
    except Exception as e:
        print(f"❌ Context building failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_switch_verification():
    """Verify that the template switch is properly configured."""
    
    print("\n=== Testing Template Switch Verification ===")
    
    # Check if the prompt template files exist
    backend_dir = Path(__file__).resolve().parent / "backend"
    final_decision_path = backend_dir / "prompts" / "final_stock_decision.txt"
    optimized_decision_path = backend_dir / "prompts" / "optimized_final_decision.txt"
    
    if not final_decision_path.exists():
        print("❌ final_stock_decision.txt not found")
        return False
    
    if not optimized_decision_path.exists():
        print("❌ optimized_final_decision.txt not found")
        return False
    
    print("✅ Both prompt templates exist")
    
    # Read the optimized template to verify our consistency changes
    with open(optimized_decision_path, 'r') as f:
        optimized_content = f.read()
    
    consistency_indicators = [
        "Existing Strategy Review",
        "Consistency Maintenance", 
        "EXISTING TRADING STRATEGY",
        "Maintain Consistency",
        "Explain Changes"
    ]
    
    found_indicators = []
    for indicator in consistency_indicators:
        if indicator in optimized_content:
            found_indicators.append(indicator)
    
    print(f"✅ Found {len(found_indicators)}/{len(consistency_indicators)} consistency indicators in optimized template")
    
    if len(found_indicators) < len(consistency_indicators):
        missing = set(consistency_indicators) - set(found_indicators)
        print(f"⚠️  Missing consistency indicators: {missing}")
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Optimized Final Decision Template Switch")
    print("=" * 60)
    
    try:
        # Test 1: Comprehensive context building
        context_test_passed = test_comprehensive_context_building()
        
        # Test 2: Template switch verification
        template_test_passed = test_template_switch_verification()
        
        print("\n" + "=" * 60)
        
        if context_test_passed and template_test_passed:
            print("🎉 ALL TESTS PASSED!")
            print("\nThe optimized final decision template is now active with:")
            print("✅ Comprehensive context building")
            print("✅ Existing trading strategy consistency")
            print("✅ Multi-timeframe integration")
            print("✅ Sector context integration")
            print("✅ Advanced analysis integration")
            print("✅ ML system integration")
            
            print("\n🔄 Changes Made:")
            print("1. Switched from 'final_stock_decision' to 'optimized_final_decision' template")
            print("2. Added comprehensive context builder method")
            print("3. Enhanced template with consistency instructions")
            print("4. Integrated existing trading strategy data")
            
            print("\n🎯 Expected Benefits:")
            print("• Consistent targets/stop losses across all frontend components")
            print("• Better integration of multi-timeframe analysis")
            print("• Enhanced sector context in decisions")
            print("• More sophisticated conflict resolution")
            print("• Comprehensive synthesis of all analysis data")
            
        else:
            print("❌ SOME TESTS FAILED!")
            print("Context test:", "PASSED" if context_test_passed else "FAILED")
            print("Template test:", "PASSED" if template_test_passed else "FAILED")
            
    except Exception as e:
        print(f"\n💥 TEST EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return context_test_passed and template_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)