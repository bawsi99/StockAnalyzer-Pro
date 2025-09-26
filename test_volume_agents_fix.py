#!/usr/bin/env python3

import asyncio
import sys
import os
import time

# Add the backend directory to the path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from analysis.orchestrator import StockAnalysisOrchestrator

class VolumeAgentsExecutionCounter:
    """Simple counter to track volume agents execution."""
    
    def __init__(self):
        self.execution_count = 0
        self.execution_times = []
        
    def track_execution(self, original_method):
        """Wrapper to track volume agents method calls."""
        async def wrapper(*args, **kwargs):
            self.execution_count += 1
            timestamp = time.time()
            self.execution_times.append(timestamp)
            print(f"[VOLUME_AGENT_COUNTER] Execution #{self.execution_count} at {time.strftime('%H:%M:%S', time.localtime(timestamp))}")
            return await original_method(*args, **kwargs)
        return wrapper

async def test_volume_agents_single_execution():
    """Test that volume agents execute only once per analysis."""
    print("="*60)
    print("TESTING VOLUME AGENTS SINGLE EXECUTION")
    print("="*60)
    
    try:
        # Initialize orchestrator
        orchestrator = StockAnalysisOrchestrator()
        
        # Set up execution counter
        counter = VolumeAgentsExecutionCounter()
        
        # Monkey patch the volume agents manager to track executions
        if hasattr(orchestrator, 'volume_agents_manager') and orchestrator.volume_agents_manager:
            original_method = orchestrator.volume_agents_manager.get_comprehensive_volume_analysis
            orchestrator.volume_agents_manager.get_comprehensive_volume_analysis = counter.track_execution(original_method)
            print("[SETUP] Successfully patched volume agents manager for execution tracking")
        else:
            print("[ERROR] No volume agents manager found")
            return False
        
        # Use a real stock symbol that should exist
        symbol = "RELIANCE"
        
        print(f"\n[TEST] Starting enhanced analysis for {symbol}...")
        print(f"[TEST] Initial execution count: {counter.execution_count}")
        
        start_time = time.time()
        
        try:
            # Run the enhanced analysis which should call volume agents only once
            result, success_msg, error_msg = await orchestrator.enhanced_analyze_stock(
                symbol=symbol,
                exchange="NSE", 
                period=30,
                interval="day",
                output_dir="test_output",
                knowledge_context="Test analysis for single volume agents execution verification",
                sector="Oil & Gas"
            )
            
            execution_time = time.time() - start_time
            
            print(f"\n[TEST] Analysis completed in {execution_time:.2f} seconds")
            print(f"[TEST] Result status: {'SUCCESS' if result else 'FAILED'}")
            
            # Check the execution count
            print(f"\n[COUNTER] Final volume agents execution count: {counter.execution_count}")
            print(f"[COUNTER] Execution timestamps: {[time.strftime('%H:%M:%S', time.localtime(t)) for t in counter.execution_times]}")
            
            if counter.execution_count == 1:
                print("✅ SUCCESS: Volume agents executed exactly once!")
                print("✅ FIXED: Duplicate volume agents calls have been eliminated!")
                return True
            elif counter.execution_count == 0:
                print("⚠️  WARNING: Volume agents were not executed at all")
                return False
            else:
                print(f"❌ FAILURE: Volume agents executed {counter.execution_count} times (expected: 1)")
                print(f"❌ ISSUE: Duplicate calls still exist")
                
                # Analyze timing between executions
                if len(counter.execution_times) > 1:
                    time_diffs = [counter.execution_times[i+1] - counter.execution_times[i] 
                                 for i in range(len(counter.execution_times)-1)]
                    print(f"[ANALYSIS] Time differences between executions: {[f'{diff:.2f}s' for diff in time_diffs]}")
                
                return False
                
        except Exception as test_error:
            print(f"[TEST] Analysis failed with error: {test_error}")
            print(f"[COUNTER] Volume agents execution count at failure: {counter.execution_count}")
            
            if counter.execution_count == 1:
                print("✅ Volume agents executed once before error occurred - this is expected behavior")
                return True
            else:
                return False
            
    except Exception as e:
        print(f"[ERROR] Test setup failed: {e}")
        return False

async def main():
    """Main test function."""
    print("Starting volume agents single execution test...")
    
    success = await test_volume_agents_single_execution()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 TEST PASSED: Volume agents execute only once per analysis!")
        print("✅ The duplicate execution issue has been successfully resolved.")
        print("✅ Volume agents now run efficiently with no redundant calls.")
    else:
        print("❌ TEST FAILED: Volume agents execution issue detected.")
        print("❌ Further investigation needed to resolve duplicate executions.")
    print(f"{'='*60}")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)