#!/usr/bin/env python3
"""
Test script to verify data extraction from backend response
"""

import requests
import json

def test_backend_response():
    """Test the backend response and verify data extraction"""
    
    # Test the enhanced analysis endpoint
    response = requests.post('http://localhost:8001/analyze/enhanced', 
                           json={'stock': 'RELIANCE', 'exchange': 'NSE', 'period': 30, 'interval': 'day'})
    
    if response.status_code != 200:
        print(f"❌ Backend request failed: {response.status_code}")
        return False
    
    data = response.json()
    
    print("✅ Backend response received successfully")
    print(f"📊 Response structure:")
    print(f"   - Success: {data.get('success')}")
    print(f"   - Stock Symbol: {data.get('stock_symbol')}")
    print(f"   - Exchange: {data.get('exchange')}")
    print(f"   - Analysis Period: {data.get('analysis_period')}")
    
    results = data.get('results', {})
    
    # Test consensus data extraction
    consensus = results.get('consensus', {})
    print(f"\n📈 Consensus Data:")
    print(f"   - Overall Signal: {consensus.get('overall_signal', 'Not found')}")
    print(f"   - Signal Strength: {consensus.get('signal_strength', 'Not found')}")
    print(f"   - Confidence: {consensus.get('confidence', 'Not found')}")
    print(f"   - Bullish %: {consensus.get('bullish_percentage', 'Not found')}")
    print(f"   - Bearish %: {consensus.get('bearish_percentage', 'Not found')}")
    print(f"   - Neutral %: {consensus.get('neutral_percentage', 'Not found')}")
    
    # Test AI analysis data extraction
    ai_analysis = results.get('ai_analysis', {})
    print(f"\n🤖 AI Analysis Data:")
    print(f"   - Meta confidence: {ai_analysis.get('meta', {}).get('overall_confidence', 'Not found')}")
    print(f"   - Meta trend: {ai_analysis.get('meta', {}).get('trend', 'Not found')}")
    
    # Test technical indicators data extraction
    technical_indicators = results.get('technical_indicators', {})
    print(f"\n📊 Technical Indicators:")
    print(f"   - RSI: {technical_indicators.get('rsi', {}).get('rsi_14', 'Not found')}")
    print(f"   - MACD Line: {technical_indicators.get('macd', {}).get('macd_line', 'Not found')}")
    print(f"   - SMA 20: {technical_indicators.get('moving_averages', {}).get('sma_20', 'Not found')}")
    
    # Test summary data extraction
    summary = results.get('summary', {})
    print(f"\n📋 Summary Data:")
    print(f"   - Overall Signal: {summary.get('overall_signal', 'Not found')}")
    print(f"   - Confidence: {summary.get('confidence', 'Not found')}")
    print(f"   - Risk Level: {summary.get('risk_level', 'Not found')}")
    
    # Test price data extraction
    print(f"\n💰 Price Data:")
    print(f"   - Current Price: {results.get('current_price', 'Not found')}")
    print(f"   - Price Change: {results.get('price_change', 'Not found')}")
    print(f"   - Price Change %: {results.get('price_change_percentage', 'Not found')}")
    
    # Verify that all required fields are present
    required_fields = [
        'consensus', 'ai_analysis', 'technical_indicators', 'summary',
        'current_price', 'price_change', 'price_change_percentage'
    ]
    
    missing_fields = []
    for field in required_fields:
        if not results.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n❌ Missing required fields: {missing_fields}")
        return False
    else:
        print(f"\n✅ All required fields are present")
        return True

def test_frontend_compatibility():
    """Test if the data structure is compatible with frontend expectations"""
    
    response = requests.post('http://localhost:8001/analyze/enhanced', 
                           json={'stock': 'RELIANCE', 'exchange': 'NSE', 'period': 30, 'interval': 'day'})
    
    if response.status_code != 200:
        print(f"❌ Backend request failed: {response.status_code}")
        return False
    
    data = response.json()
    results = data.get('results', {})
    
    # Test consensus structure compatibility
    consensus = results.get('consensus', {})
    required_consensus_fields = [
        'overall_signal', 'signal_strength', 'bullish_percentage', 
        'bearish_percentage', 'neutral_percentage', 'confidence'
    ]
    
    missing_consensus_fields = []
    for field in required_consensus_fields:
        if field not in consensus:
            missing_consensus_fields.append(field)
    
    if missing_consensus_fields:
        print(f"❌ Missing consensus fields: {missing_consensus_fields}")
        return False
    
    # Test AI analysis structure compatibility
    ai_analysis = results.get('ai_analysis', {})
    if 'meta' not in ai_analysis:
        print("❌ Missing AI analysis meta field")
        return False
    
    # Test technical indicators structure compatibility
    technical_indicators = results.get('technical_indicators', {})
    required_indicator_fields = ['rsi', 'macd', 'moving_averages']
    
    missing_indicator_fields = []
    for field in required_indicator_fields:
        if field not in technical_indicators:
            missing_indicator_fields.append(field)
    
    if missing_indicator_fields:
        print(f"❌ Missing technical indicator fields: {missing_indicator_fields}")
        return False
    
    print("✅ Data structure is compatible with frontend expectations")
    return True

if __name__ == "__main__":
    print("🧪 Testing Backend Response and Data Extraction")
    print("=" * 50)
    
    # Test backend response
    backend_success = test_backend_response()
    
    print("\n" + "=" * 50)
    
    # Test frontend compatibility
    frontend_success = test_frontend_compatibility()
    
    print("\n" + "=" * 50)
    
    if backend_success and frontend_success:
        print("🎉 All tests passed! Data extraction is working correctly.")
        print("\n📝 Summary:")
        print("   ✅ Backend is sending properly structured data")
        print("   ✅ Consensus data is populated correctly")
        print("   ✅ AI analysis data is available")
        print("   ✅ Technical indicators are present")
        print("   ✅ Data structure matches frontend expectations")
        print("\n🚀 The frontend should now be able to display the analysis data!")
    else:
        print("❌ Some tests failed. Please check the issues above.") 