#!/usr/bin/env python3
"""
Example Usage Script for Agentic Trading System
Demonstrates how to use the trading system with interactive sessions
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any

class TradingSystemExample:
    """Example usage of the agentic trading system"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session_id = None
    
    async def run_complete_example(self):
        """Run a complete example trading session"""
        print("🤖 Starting Agentic Trading System Example")
        print("=" * 50)
        
        try:
            # 1. Check system health
            await self.check_health()
            
            # 2. Get system configuration
            await self.get_config()
            
            # 3. Create trading session
            await self.create_session("RELIANCE", 100000)
            
            # 4. Process initial analysis
            await self.process_initial_analysis()
            
            # 5. Get next data interval
            await self.get_next_interval()
            
            # 6. Execute manual buy
            await self.execute_manual_buy()
            
            # 7. Analyze again
            await self.analyze_again()
            
            # 8. Execute manual sell
            await self.execute_manual_sell()
            
            # 9. Get session history
            await self.get_session_history()
            
            # 10. Close session
            await self.close_session()
            
            print("\n✅ Example completed successfully!")
            
        except Exception as e:
            print(f"❌ Error in example: {str(e)}")
    
    async def check_health(self):
        """Check system health"""
        print("\n🏥 Checking system health...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ System Status: {health_data['status']}")
                    print(f"   Backend Services: {health_data['backend_services']}")
                    print(f"   Active Sessions: {health_data['active_sessions']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
    
    async def get_config(self):
        """Get system configuration"""
        print("\n⚙️ Getting system configuration...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/config") as response:
                if response.status == 200:
                    config = await response.json()
                    print(f"✅ Initial Budget: ₹{config['initial_budget']:,}")
                    print(f"   Max Position Size: {config['max_position_size'] * 100}%")
                    print(f"   Buy Threshold: {config['buy_confidence_threshold']}%")
                    print(f"   Available Stocks: {len(config['available_stocks'])}")
                else:
                    print(f"❌ Config check failed: {response.status}")
    
    async def create_session(self, symbol: str, budget: float):
        """Create a new trading session"""
        print(f"\n🚀 Creating trading session for {symbol}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/sessions/create",
                json={"symbol": symbol, "initial_budget": budget}
            ) as response:
                if response.status == 200:
                    session_data = await response.json()
                    self.session_id = session_data["session_id"]
                    print(f"✅ Session created: {self.session_id}")
                    print(f"   Symbol: {session_data['symbol']}")
                    print(f"   Budget: ₹{session_data['budget']:,}")
                else:
                    print(f"❌ Session creation failed: {response.status}")
    
    async def process_initial_analysis(self):
        """Process initial market analysis"""
        print(f"\n📊 Processing initial analysis...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/sessions/{self.session_id}/process-interval",
                json={"interval": "1day"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    decision = result["decision"]
                    print(f"✅ Analysis completed:")
                    print(f"   Action: {decision['action']}")
                    print(f"   Confidence: {decision['confidence']:.1f}%")
                    print(f"   Position Size: {decision['position_size']:.1f}%")
                    print(f"   Risk Level: {decision['risk_level']}")
                    print(f"   Reasoning: {decision['reasoning'][:100]}...")
                    
                    # Show agent decisions
                    print(f"\n   Agent Decisions:")
                    for agent_decision in result["agent_decisions"]:
                        print(f"     {agent_decision['agent_type']}: {agent_decision['decision']} ({agent_decision['confidence']:.1f}%)")
                    
                    # Show portfolio state
                    portfolio = result["portfolio_state"]
                    print(f"\n   Portfolio State:")
                    print(f"     Total Value: ₹{portfolio['total_value']:,.2f}")
                    print(f"     Available Cash: ₹{portfolio['available_cash']:,.2f}")
                    print(f"     Total PnL: ₹{portfolio['total_pnl']:,.2f}")
                    
                else:
                    print(f"❌ Analysis failed: {response.status}")
    
    async def get_next_interval(self):
        """Get next data interval"""
        print(f"\n⏰ Getting next data interval...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/sessions/{self.session_id}/next-interval"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    decision = result["decision"]
                    print(f"✅ Next interval analysis:")
                    print(f"   Action: {decision['action']}")
                    print(f"   Confidence: {decision['confidence']:.1f}%")
                    print(f"   Next Interval: {decision['next_interval']}")
                else:
                    print(f"❌ Next interval failed: {response.status}")
    
    async def execute_manual_buy(self):
        """Execute manual buy action"""
        print(f"\n💰 Executing manual buy...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/sessions/{self.session_id}/manual-action",
                json={"action": "BUY", "percentage": 25}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    execution = result["execution_result"]
                    print(f"✅ Manual buy executed:")
                    print(f"   Success: {execution['success']}")
                    print(f"   Message: {execution['message']}")
                    if execution.get("quantity"):
                        print(f"   Quantity: {execution['quantity']}")
                        print(f"   Price: ₹{execution['price']:.2f}")
                        print(f"   Total Cost: ₹{execution['total_cost']:,.2f}")
                else:
                    print(f"❌ Manual buy failed: {response.status}")
    
    async def analyze_again(self):
        """Analyze again"""
        print(f"\n🔄 Analyzing again...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/sessions/{self.session_id}/analyze-again"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    decision = result["decision"]
                    print(f"✅ Re-analysis completed:")
                    print(f"   Action: {decision['action']}")
                    print(f"   Confidence: {decision['confidence']:.1f}%")
                    print(f"   Position Size: {decision['position_size']:.1f}%")
                else:
                    print(f"❌ Re-analysis failed: {response.status}")
    
    async def execute_manual_sell(self):
        """Execute manual sell action"""
        print(f"\n💸 Executing manual sell...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/sessions/{self.session_id}/manual-action",
                json={"action": "SELL", "percentage": 50}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    execution = result["execution_result"]
                    print(f"✅ Manual sell executed:")
                    print(f"   Success: {execution['success']}")
                    print(f"   Message: {execution['message']}")
                    if execution.get("quantity"):
                        print(f"   Quantity: {execution['quantity']}")
                        print(f"   Price: ₹{execution['price']:.2f}")
                        print(f"   Total Proceeds: ₹{execution['total_proceeds']:,.2f}")
                else:
                    print(f"❌ Manual sell failed: {response.status}")
    
    async def get_session_history(self):
        """Get session history"""
        print(f"\n📜 Getting session history...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/sessions/{self.session_id}/history"
            ) as response:
                if response.status == 200:
                    history = await response.json()
                    print(f"✅ Session history:")
                    print(f"   Analysis Count: {len(history['analysis_history'])}")
                    print(f"   Decision Count: {len(history['decision_history'])}")
                    print(f"   Trade Count: {len(history['trade_history'])}")
                    
                    # Show recent trades
                    if history['trade_history']:
                        print(f"\n   Recent Trades:")
                        for trade in history['trade_history'][-3:]:  # Last 3 trades
                            print(f"     {trade['action']}: {trade.get('quantity', 'N/A')} shares at ₹{trade.get('price', 0):.2f}")
                else:
                    print(f"❌ History retrieval failed: {response.status}")
    
    async def close_session(self):
        """Close the trading session"""
        print(f"\n🔚 Closing trading session...")
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/sessions/{self.session_id}"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Session closed:")
                    print(f"   Duration: {result['session_duration']:.2f} hours")
                    print(f"   Total Trades: {result['total_trades']}")
                    print(f"   Total PnL: ₹{result['total_pnl']:,.2f}")
                    print(f"   PnL Percentage: {result['total_pnl_percentage']:.2f}%")
                else:
                    print(f"❌ Session closure failed: {response.status}")

async def run_auto_trade_example():
    """Run automated trading example"""
    print("\n🤖 Running Automated Trading Example")
    print("=" * 50)
    
    example = TradingSystemExample()
    
    try:
        # Create session
        await example.create_session("TCS", 50000)
        
        # Start auto-trade
        print(f"\n🚀 Starting automated trading...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{example.base_url}/sessions/{example.session_id}/auto-trade",
                json={"max_iterations": 5}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Auto-trade started: {result['message']}")
                    print(f"   Max Iterations: {result['max_iterations']}")
                    
                    # Wait a bit for auto-trade to progress
                    print("   Waiting for auto-trade to progress...")
                    await asyncio.sleep(10)
                    
                    # Check session state
                    async with session.get(f"{example.base_url}/sessions/{example.session_id}") as resp:
                        if resp.status == 200:
                            state = await resp.json()
                            print(f"   Current State: {state['trade_count']} trades executed")
                    
                else:
                    print(f"❌ Auto-trade failed: {response.status}")
        
        # Close session
        await example.close_session()
        
    except Exception as e:
        print(f"❌ Error in auto-trade example: {str(e)}")

async def main():
    """Main function to run examples"""
    print("🤖 Agentic Trading System Examples")
    print("=" * 50)
    
    # Run complete example
    await TradingSystemExample().run_complete_example()
    
    print("\n" + "=" * 50)
    
    # Run auto-trade example
    await run_auto_trade_example()

if __name__ == "__main__":
    asyncio.run(main())

