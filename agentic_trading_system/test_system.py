#!/usr/bin/env python3
"""
Test Script for Agentic Trading System
Tests individual components and integration
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import AnalysisData, AgentDecision, DecisionType, RiskLevel, AgentType
from config import TradingConfig
from portfolio_manager import PortfolioManager
from specialist_agents import TechnicalAnalysisAgent, SectorAnalysisAgent, RiskAssessmentAgent

class SystemTester:
    """Test the agentic trading system components"""
    
    def __init__(self):
        self.test_results = []
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Testing Agentic Trading System Components")
        print("=" * 50)
        
        # Test configuration
        self.test_configuration()
        
        # Test portfolio manager
        self.test_portfolio_manager()
        
        # Test specialist agents
        asyncio.run(self.test_specialist_agents())
        
        # Print results
        self.print_results()
    
    def test_configuration(self):
        """Test configuration loading"""
        print("\n⚙️ Testing Configuration...")
        
        try:
            # Test basic config
            assert TradingConfig.INITIAL_BUDGET == 100000, "Initial budget should be 100000"
            assert TradingConfig.MAX_POSITION_SIZE == 0.3, "Max position size should be 0.3"
            assert TradingConfig.BUY_CONFIDENCE_THRESHOLD == 70, "Buy threshold should be 70"
            
            # Test available stocks
            assert len(TradingConfig.DEFAULT_STOCKS) > 0, "Should have available stocks"
            assert "RELIANCE" in TradingConfig.DEFAULT_STOCKS, "RELIANCE should be in default stocks"
            
            print("✅ Configuration tests passed")
            self.test_results.append(("Configuration", True, ""))
            
        except Exception as e:
            print(f"❌ Configuration tests failed: {str(e)}")
            self.test_results.append(("Configuration", False, str(e)))
    
    def test_portfolio_manager(self):
        """Test portfolio manager functionality"""
        print("\n💰 Testing Portfolio Manager...")
        
        try:
            # Create portfolio manager
            portfolio = PortfolioManager(100000)
            
            # Test initial state
            state = portfolio.get_portfolio_state()
            assert state.available_cash == 100000, "Initial cash should be 100000"
            assert state.total_value == 100000, "Initial total value should be 100000"
            
            # Test buy validation
            can_buy, message = portfolio.can_buy("RELIANCE", 10, 1500)
            assert can_buy, f"Should be able to buy: {message}"
            
            # Test buy execution
            from models import TradeRequest, ActionType
            trade_request = TradeRequest(
                action=ActionType.BUY,
                symbol="RELIANCE",
                quantity=10,
                price=1500
            )
            
            success, message = portfolio.execute_buy(trade_request)
            assert success, f"Buy should succeed: {message}"
            
            # Test updated state
            state = portfolio.get_portfolio_state()
            assert state.available_cash < 100000, "Cash should be reduced after buy"
            assert len(state.holdings) > 0, "Should have holdings after buy"
            
            # Test sell validation
            can_sell, message = portfolio.can_sell("RELIANCE", 5)
            assert can_sell, f"Should be able to sell: {message}"
            
            print("✅ Portfolio Manager tests passed")
            self.test_results.append(("Portfolio Manager", True, ""))
            
        except Exception as e:
            print(f"❌ Portfolio Manager tests failed: {str(e)}")
            self.test_results.append(("Portfolio Manager", False, str(e)))
    
    async def test_specialist_agents(self):
        """Test specialist agents"""
        print("\n🤖 Testing Specialist Agents...")
        
        try:
            # Create test data
            test_data = AnalysisData(
                symbol="RELIANCE",
                exchange="NSE",
                timestamp="2025-01-30T10:00:00",
                current_price=1500.0,
                price_change=15.5,
                price_change_percentage=1.04,
                technical_indicators={
                    "rsi": 65.5,
                    "macd": {"macd": 12.5, "signal": 10.2, "histogram": 2.3},
                    "sma_20": 1480.0,
                    "ema_20": 1490.0
                },
                risk_level="Medium",
                recommendation="Buy",
                ai_analysis={
                    "trend": "Bullish",
                    "confidence_pct": 75.0,
                    "trading_strategy": "Momentum trading"
                },
                sector_context={
                    "sector": "Energy",
                    "sector_performance": 0.8,
                    "sector_rank": 3
                },
                multi_timeframe_analysis={
                    "1day": {"signal": "Buy", "confidence": 70},
                    "1hour": {"signal": "Hold", "confidence": 50}
                },
                ml_predictions={
                    "price_direction": "Up",
                    "confidence": 0.75,
                    "volatility": "Medium"
                },
                enhanced_metadata={
                    "mathematical_validation": True,
                    "code_execution_enabled": True
                }
            )
            
            portfolio_state = {
                "available_cash": 50000,
                "total_value": 100000,
                "holdings": {"RELIANCE": {"quantity": 20, "current_value": 30000}}
            }
            
            # Test Technical Analysis Agent
            technical_agent = TechnicalAnalysisAgent()
            technical_response = await technical_agent.analyze(test_data, portfolio_state)
            assert technical_response.agent_type == AgentType.TECHNICAL, "Should be technical agent"
            assert technical_response.decision.confidence > 0, "Should have confidence"
            
            # Test Sector Analysis Agent
            sector_agent = SectorAnalysisAgent()
            sector_response = await sector_agent.analyze(test_data, portfolio_state)
            assert sector_response.agent_type == AgentType.SECTOR, "Should be sector agent"
            assert sector_response.decision.confidence > 0, "Should have confidence"
            
            # Test Risk Assessment Agent
            risk_agent = RiskAssessmentAgent()
            risk_response = await risk_agent.analyze(test_data, portfolio_state)
            assert risk_response.agent_type == AgentType.RISK, "Should be risk agent"
            assert risk_response.decision.confidence > 0, "Should have confidence"
            
            print("✅ Specialist Agents tests passed")
            self.test_results.append(("Specialist Agents", True, ""))
            
        except Exception as e:
            print(f"❌ Specialist Agents tests failed: {str(e)}")
            self.test_results.append(("Specialist Agents", False, str(e)))
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success, error in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if not success and error:
                print(f"   Error: {error}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready to use.")
        else:
            print("⚠️ Some tests failed. Please check the errors above.")

def main():
    """Main test function"""
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

