#!/usr/bin/env python3
"""
Test the enhanced text extraction in debug_logger
"""

import os
import sys
import asyncio

# Add backend to path
sys.path.insert(0, 'backend')

from gemini.gemini_core import GeminiCore

async def test_sector_extraction():
    """Test sector synthesis to see if enhanced extraction works."""
    
    # Get API key from environment
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return
    
    print(f"🔑 Using API key ending with: ...{api_key[-6:]}")
    
    # Create core client
    core = GeminiCore(api_key=api_key)
    
    # Test prompt similar to what the sector agent would use
    test_prompt = """
[Source: SectorContext]
Timeframes: Relative performance and beta = 12m; Rotation = 3m

Sector Metrics:
- Sector Outperformance (12m): 5.2%
- Market Outperformance (12m): 3.1%
- Sector Beta (12m): 1.15

Additional Context (if available):
- Sector: Financial Services
- Market Beta (12m): 0.98
- Rotation Stage (3m): Leading
- Rotation Momentum (3m): 2.8%

Generate 4 concise, actionable sector analysis bullets (each ~15-25 words):
• Focus on relative performance vs sector/market with specific timeframes
• Include beta/volatility insights and position sizing implications  
• Address rotation stage and momentum for timing context
• Highlight key sector tailwinds, headwinds, or catalysts

Format: Use bullet points (•) and keep each point focused and specific.
"""
    
    print("\n📤 Testing enhanced text extraction...")
    print("=" * 60)
    
    try:
        # Call with code execution enabled (this is where the issue occurs)
        text_response, code_results, execution_results = await core.call_llm_with_code_execution(
            test_prompt, return_full_response=False
        )
        
        print(f"\n📥 ENHANCED EXTRACTION RESULTS:")
        print(f"   Text response length: {len(text_response) if text_response else 0}")
        print(f"   Code results: {len(code_results)}")
        print(f"   Execution results: {len(execution_results)}")
        
        if text_response:
            print(f"\n✅ SUCCESS! Text extracted:")
            print("-" * 40)
            print(text_response)
            print("-" * 40)
        else:
            print(f"\n❌ Still no text response after enhancement")
            
            # Get full response to debug further
            response, code_results, execution_results = await core.call_llm_with_code_execution(
                test_prompt, return_full_response=True
            )
            
            print(f"\n🔍 RAW RESPONSE DEBUG INFO:")
            print(f"Response type: {type(response).__name__}")
            print(f"Response has __dict__: {hasattr(response, '__dict__')}")
            
            # Show available attributes
            if hasattr(response, '__dict__'):
                attrs = [attr for attr in dir(response) if not attr.startswith('_')]
                print(f"Available attributes: {attrs}")
                
                # Try to access some common ones manually
                for attr in ['text', 'content', 'message', 'candidates']:
                    if hasattr(response, attr):
                        try:
                            value = getattr(response, attr)
                            print(f"  {attr}: {type(value).__name__} = {str(value)[:100]}")
                        except Exception as e:
                            print(f"  {attr}: Error accessing - {e}")
            
            print(f"\nResponse as string: {str(response)[:300]}")
    
    except Exception as e:
        print(f"\n❌ ERROR during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sector_extraction())