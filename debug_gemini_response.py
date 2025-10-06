#!/usr/bin/env python3
"""
Debug Gemini Response Structure
Helps identify how to extract text from Gemini API responses when standard methods fail.
"""

import os
import sys
import json
from typing import Any

# Add backend to path
sys.path.insert(0, 'backend')

from gemini.gemini_core import GeminiCore

def inspect_response_structure(response: Any, depth: int = 0, max_depth: int = 4):
    """Recursively inspect the response structure to find text content."""
    indent = "  " * depth
    
    if depth > max_depth:
        print(f"{indent}[MAX DEPTH REACHED]")
        return
    
    print(f"{indent}{type(response).__name__}")
    
    # If it's a simple type, show the value
    if isinstance(response, (str, int, float, bool, type(None))):
        if isinstance(response, str) and len(response) > 100:
            print(f"{indent}  → {repr(response[:100])}...")
        else:
            print(f"{indent}  → {repr(response)}")
        return
    
    # For complex objects, inspect attributes
    if hasattr(response, '__dict__'):
        for attr_name in dir(response):
            if attr_name.startswith('_'):
                continue
            try:
                attr_value = getattr(response, attr_name)
                if callable(attr_value):
                    continue
                print(f"{indent}  .{attr_name}:")
                inspect_response_structure(attr_value, depth + 1, max_depth)
            except Exception as e:
                print(f"{indent}  .{attr_name}: [ERROR: {e}]")
    
    # For lists/tuples
    elif isinstance(response, (list, tuple)):
        print(f"{indent}  [{len(response)} items]")
        for i, item in enumerate(response[:3]):  # Show first 3 items
            print(f"{indent}    [{i}]:")
            inspect_response_structure(item, depth + 1, max_depth)
        if len(response) > 3:
            print(f"{indent}    ... and {len(response) - 3} more items")
    
    # For dictionaries
    elif isinstance(response, dict):
        print(f"{indent}  {{{len(response)} keys}}")
        for key, value in list(response.items())[:5]:  # Show first 5 keys
            print(f"{indent}    '{key}':")
            inspect_response_structure(value, depth + 1, max_depth)
        if len(response) > 5:
            print(f"{indent}    ... and {len(response) - 5} more keys")

def extract_all_text_fields(obj: Any, path: str = "") -> list:
    """Find all text fields in the response object."""
    text_fields = []
    
    if isinstance(obj, str) and len(obj.strip()) > 0:
        text_fields.append((path, obj))
    elif hasattr(obj, '__dict__'):
        for attr_name in dir(obj):
            if attr_name.startswith('_'):
                continue
            try:
                attr_value = getattr(obj, attr_name)
                if callable(attr_value):
                    continue
                text_fields.extend(extract_all_text_fields(attr_value, f"{path}.{attr_name}"))
            except Exception:
                pass
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            text_fields.extend(extract_all_text_fields(item, f"{path}[{i}]"))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            text_fields.extend(extract_all_text_fields(value, f"{path}['{key}']"))
    
    return text_fields

async def test_gemini_response():
    """Test Gemini API response and inspect structure."""
    
    # Get API key from environment
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return
    
    print(f"🔑 Using API key ending with: ...{api_key[-6:]}")
    
    # Create core client
    core = GeminiCore(api_key=api_key)
    
    # Test prompt
    test_prompt = """
    Analyze this simple data and provide a JSON response:
    
    Stock: RELIANCE
    Price: 2500
    Volume: High
    
    Please respond with:
    ```json
    {
        "symbol": "RELIANCE",
        "analysis": "Brief analysis here",
        "trend": "bullish/bearish/neutral"
    }
    ```
    """
    
    print("\n📤 Sending test prompt to Gemini...")
    print("=" * 50)
    
    try:
        # Call with code execution enabled
        text_response, code_results, execution_results = await core.call_llm_with_code_execution(
            test_prompt, return_full_response=False
        )
        
        print(f"\n📥 RESULTS:")
        print(f"   Text response length: {len(text_response) if text_response else 0}")
        print(f"   Code results: {len(code_results)}")
        print(f"   Execution results: {len(execution_results)}")
        
        if text_response:
            print(f"\n✅ TEXT RESPONSE FOUND:")
            print("-" * 30)
            print(text_response[:500])
            if len(text_response) > 500:
                print("... [truncated]")
        else:
            print(f"\n❌ NO TEXT RESPONSE - Let's inspect the raw response...")
            
            # Get the full response object
            response, code_results, execution_results = await core.call_llm_with_code_execution(
                test_prompt, return_full_response=True
            )
            
            print(f"\n🔍 RAW RESPONSE STRUCTURE:")
            print("=" * 50)
            inspect_response_structure(response)
            
            print(f"\n🔍 ALL TEXT FIELDS FOUND:")
            print("=" * 50)
            text_fields = extract_all_text_fields(response)
            for path, text in text_fields:
                if len(text.strip()) > 10:  # Only show substantial text
                    print(f"  {path}: {repr(text[:100])}")
                    if len(text) > 100:
                        print(f"    ... [total length: {len(text)}]")
        
        if code_results:
            print(f"\n💻 CODE RESULTS:")
            print("-" * 30)
            for i, code in enumerate(code_results):
                print(f"  [{i}]: {code[:200]}")
                if len(code) > 200:
                    print("    ... [truncated]")
        
        if execution_results:
            print(f"\n⚡ EXECUTION RESULTS:")
            print("-" * 30)
            for i, result in enumerate(execution_results):
                print(f"  [{i}]: {str(result)[:200]}")
                if len(str(result)) > 200:
                    print("    ... [truncated]")
    
    except Exception as e:
        print(f"\n❌ ERROR during API call: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_gemini_response())