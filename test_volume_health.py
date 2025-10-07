#!/usr/bin/env python3
"""
Volume Agents Health Diagnostic Script

This script tests the health check fixes for the volume agents system.
"""

import sys
import os

# Add the backend path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_volume_health():
    """Test the volume agents health system"""
    print("🔧 Testing Volume Agents Health System")
    print("=" * 50)
    
    try:
        # Try importing the volume agents system
        from agents.volume.volume_agents import VolumeAgentIntegrationManager
        print("✅ Successfully imported VolumeAgentIntegrationManager")
        
        # Create manager instance
        manager = VolumeAgentIntegrationManager()
        print("✅ Successfully created VolumeAgentIntegrationManager instance")
        
        # Test health check
        health_status = manager.get_agent_health_status()
        print("✅ Health check completed successfully!")
        
        print("\n📊 Agent Health Status:")
        for agent_name, status in health_status.items():
            health_indicator = "✅" if status["healthy"] else "❌"
            print(f"   {health_indicator} {agent_name}: {status['status']} (healthy: {status['healthy']})")
            
            # Show diagnostics
            diagnostics = status.get('diagnostics', {})
            print(f"      - Initialized: {diagnostics.get('initialized', False)}")
            print(f"      - LLM Capability: {diagnostics.get('llm_capability', False)}")
            print(f"      - Agent Type: {diagnostics.get('agent_type', 'Unknown')}")
        
        # Test system health summary
        system_health = manager.get_system_health_summary()
        print(f"\n📈 System Health Summary:")
        print(f"   Health Percentage: {system_health['health_percentage']:.1f}%")
        print(f"   Healthy Agents: {system_health['healthy_agents']}/{system_health['total_agents']}")
        print(f"   System Status: {system_health['system_status']}")
        print(f"   Recommendation: {system_health['recommendation']}")
        
        # Test should_use_volume_agents
        should_use, reason = manager.should_use_volume_agents()
        use_indicator = "✅" if should_use else "❌"
        print(f"\n🎯 Should Use Volume Agents: {use_indicator} {should_use}")
        print(f"   Reason: {reason}")
        
        print("\n🎉 All health check tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during health check test: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_fallback_info():
    """Show information about fallback mechanisms"""
    print("\n📋 Volume Agents Fallback Mechanisms:")
    print("=" * 50)
    
    fallbacks = [
        {
            "name": "Degraded Analysis Result",
            "trigger": "All agents fail or system <40% healthy",
            "provides": "Minimal volume summary with error status",
            "confidence": "0%",
            "features": ["Error reporting", "System status", "Risk assessment"]
        },
        {
            "name": "Partial Success Handling", 
            "trigger": "Some agents succeed, others fail",
            "provides": "Results from successful agents only",
            "confidence": "Weighted by successful agents",
            "features": ["Consensus from successful agents", "Conflict detection", "Partial warnings"]
        },
        {
            "name": "Basic Volume Analysis",
            "trigger": "Volume agents system unavailable",
            "provides": "Traditional volume metrics",
            "confidence": "30%",
            "features": ["Volume ratios", "Moving averages", "Basic signals", "Percentile analysis"]
        }
    ]
    
    for i, fallback in enumerate(fallbacks, 1):
        print(f"\n{i}. {fallback['name']}")
        print(f"   📌 Trigger: {fallback['trigger']}")
        print(f"   📊 Provides: {fallback['provides']}")
        print(f"   🎯 Confidence: {fallback['confidence']}")
        print(f"   ⚡ Features: {', '.join(fallback['features'])}")

if __name__ == "__main__":
    print("🚀 Volume Agents Health Diagnostic")
    print("=" * 60)
    
    # Test health system
    success = test_volume_health()
    
    # Show fallback information
    show_fallback_info()
    
    if success:
        print("\n✅ DIAGNOSIS: Volume agents health system is working correctly!")
        print("   The AttributeError should be resolved.")
    else:
        print("\n❌ DIAGNOSIS: Issues still exist in the volume agents system.")
        print("   Further investigation may be needed.")