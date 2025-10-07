#!/usr/bin/env python3
"""
Test script to verify volume_confirmation agent migration to backend/llm

This script tests that:
1. The volume confirmation agent loads properly
2. It uses the new LLM agent instead of legacy GeminiClient
3. The integration with the volume orchestrator works correctly
4. Data processing flows work end-to-end
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Test the volume confirmation processor directly
def test_volume_confirmation_processor():
    """Test the data processing component"""
    print("🔬 Testing Volume Confirmation Processor")
    print("-" * 50)
    
    try:
        from backend.agents.volume.volume_confirmation.processor import VolumeConfirmationProcessor
        
        # Create test data
        dates = pd.date_range(start='2024-09-01', end='2024-10-07', freq='D')
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'open': 100 + np.random.randn(len(dates)) * 2,
            'high': 102 + np.random.randn(len(dates)) * 2,
            'low': 98 + np.random.randn(len(dates)) * 2,
            'close': 100 + np.random.randn(len(dates)) * 2,
            'volume': np.abs(np.random.lognormal(12, 0.5, len(dates)))
        }, index=dates)
        
        # Ensure OHLC relationships are valid
        test_data['high'] = np.maximum(test_data[['open', 'close']].max(axis=1), test_data['high'])
        test_data['low'] = np.minimum(test_data[['open', 'close']].min(axis=1), test_data['low'])
        
        processor = VolumeConfirmationProcessor()
        result = processor.process_volume_confirmation_data(test_data)
        
        if 'error' in result:
            print(f"❌ Processor failed: {result['error']}")
            return False
            
        print("✅ Processor works correctly")
        print(f"   Data period: {result.get('data_period', 'unknown')}")
        print(f"   Overall assessment: {result.get('overall_assessment', {}).get('confirmation_status', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Processor test failed: {e}")
        return False

# Test the LLM agent directly
async def test_volume_confirmation_llm_agent():
    """Test the new LLM agent component"""
    print("\n🤖 Testing Volume Confirmation LLM Agent")
    print("-" * 50)
    
    try:
        from backend.agents.volume.volume_confirmation.llm_agent import create_volume_confirmation_llm_agent
        
        # Create mock LLM client
        class MockLLMClient:
            def get_provider_info(self):
                return "mock:gemini-2.5-flash"
            async def generate(self, prompt, images=None, **kwargs):
                return '{"volume_confirmation_status": "confirmed", "confirmation_strength": "medium", "confidence_score": 78, "key_insight": "Volume supports recent price movements"}'
            async def generate_text(self, prompt, **kwargs):
                return '{"volume_confirmation_status": "confirmed", "confirmation_strength": "medium", "confidence_score": 78, "key_insight": "Volume supports recent price movements"}'
        
        # Create agent
        agent = create_volume_confirmation_llm_agent(MockLLMClient())
        print(f"✅ LLM agent created using: {agent.get_provider_info()}")
        
        # Test context building and prompt formatting
        sample_analysis = {
            'overall_assessment': {
                'confirmation_status': 'volume_confirms_price',
                'confirmation_strength': 'medium',
                'confidence_score': 75
            },
            'price_volume_correlation': {
                'correlation_coefficient': 0.65,
                'correlation_strength': 'medium'
            },
            'recent_movements': [
                {
                    'date': '2024-10-07',
                    'price_change_pct': 2.5,
                    'volume_response': 'confirming',
                    'volume_ratio': 1.6
                }
            ]
        }
        
        # Test with chart
        mock_chart = b'mock_chart_data'
        response = await agent.analyze_with_chart(sample_analysis, "TESTSTOCK", mock_chart)
        print("✅ Chart analysis completed")
        print(f"   Response length: {len(response)} chars")
        
        # Test without chart
        text_response = await agent.analyze_without_chart(sample_analysis, "TESTSTOCK")
        print("✅ Text analysis completed")
        print(f"   Response length: {len(text_response)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test the volume orchestrator integration
async def test_volume_orchestrator_integration():
    """Test that the orchestrator uses the new LLM agent correctly"""
    print("\n🎭 Testing Volume Orchestrator Integration")
    print("-" * 50)
    
    try:
        from backend.agents.volume.volume_agents import VolumeAgentsOrchestrator
        
        # Create orchestrator (this should initialize the new LLM agent)
        orchestrator = VolumeAgentsOrchestrator()
        
        # Check that the volume_confirmation agent is set up with the new LLM agent
        has_llm_agents = hasattr(orchestrator, 'llm_agents')
        has_volume_confirmation = False
        
        if has_llm_agents:
            has_volume_confirmation = 'volume_confirmation' in orchestrator.llm_agents
            
        print(f"✅ Orchestrator initialized")
        print(f"   Has LLM agents: {has_llm_agents}")
        print(f"   Has volume_confirmation LLM agent: {has_volume_confirmation}")
        
        # Check the agent configuration
        if 'volume_confirmation' in orchestrator.agent_config:
            config = orchestrator.agent_config['volume_confirmation']
            print(f"   Agent enabled: {config['enabled']}")
            print(f"   Agent weight: {config['weight']}")
        
        # Check legacy client setup
        if hasattr(orchestrator, 'agent_clients') and orchestrator.agent_clients:
            has_legacy_volume_confirmation = 'volume_confirmation' in orchestrator.agent_clients
            print(f"   Legacy Gemini client for volume_confirmation: {has_legacy_volume_confirmation}")
            print(f"   Active legacy agents: {list(orchestrator.agent_clients.keys())}")
        
        return has_volume_confirmation
        
    except Exception as e:
        print(f"❌ Orchestrator integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test end-to-end workflow
async def test_end_to_end_workflow():
    """Test the complete workflow with mock data"""
    print("\n🔄 Testing End-to-End Workflow")
    print("-" * 50)
    
    try:
        from backend.agents.volume.volume_confirmation import (
            VolumeConfirmationProcessor, 
            VolumeConfirmationCharts,
            create_volume_confirmation_llm_agent
        )
        
        # 1. Create test data
        dates = pd.date_range(start='2024-09-01', end='2024-10-07', freq='D')
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'high': 102 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'low': 98 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'volume': np.abs(np.random.lognormal(12, 0.6, len(dates)))
        }, index=dates)
        
        # Ensure OHLC relationships
        test_data['high'] = np.maximum(test_data[['open', 'close']].max(axis=1), test_data['high'])
        test_data['low'] = np.minimum(test_data[['open', 'close']].min(axis=1), test_data['low'])
        
        print("✅ Test data created")
        
        # 2. Process data
        processor = VolumeConfirmationProcessor()
        analysis_data = processor.process_volume_confirmation_data(test_data)
        
        if 'error' in analysis_data:
            print(f"❌ Data processing failed: {analysis_data['error']}")
            return False
            
        print("✅ Data processing completed")
        
        # 3. Generate chart (mock)
        print("✅ Chart generation (mocked)")
        mock_chart = b'mock_chart_bytes_data_for_testing'
        
        # 4. Run LLM analysis
        class MockLLMClient:
            def get_provider_info(self):
                return "mock:gemini-2.5-flash"
            async def generate(self, prompt, images=None, **kwargs):
                return '''{"volume_confirmation_status": "confirmed", "confirmation_strength": "strong", "price_volume_correlation": 0.72, "trend_volume_support": "strong", "confidence_score": 85, "key_insight": "Recent price movements show strong volume confirmation with above-average trading activity supporting the upward trend"}'''
        
        llm_agent = create_volume_confirmation_llm_agent(MockLLMClient())
        llm_response = await llm_agent.analyze_with_chart(analysis_data, "TESTSTOCK", mock_chart)
        
        print("✅ LLM analysis completed")
        print(f"   Response preview: {llm_response[:100]}...")
        
        # 5. Verify the complete workflow worked
        workflow_success = (
            isinstance(analysis_data, dict) and 
            'overall_assessment' in analysis_data and
            isinstance(llm_response, str) and
            len(llm_response) > 50
        )
        
        print(f"✅ End-to-end workflow: {'SUCCESS' if workflow_success else 'FAILED'}")
        return workflow_success
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all migration tests"""
    print("🚀 Volume Confirmation Agent Migration Test")
    print("=" * 60)
    print("Testing migration from backend/gemini to backend/llm")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Processor
    results['processor'] = test_volume_confirmation_processor()
    
    # Test 2: LLM Agent
    results['llm_agent'] = await test_volume_confirmation_llm_agent()
    
    # Test 3: Orchestrator Integration
    results['orchestrator'] = await test_volume_orchestrator_integration()
    
    # Test 4: End-to-End Workflow
    results['end_to_end'] = await test_end_to_end_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 MIGRATION TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
    
    print("-" * 60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Migration successful!")
        return True
    else:
        print("⚠️  Some tests failed - Migration needs attention")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)