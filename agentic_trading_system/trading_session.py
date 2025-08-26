"""
Trading Session Manager for Agentic Trading System
Manages multi-turn conversations and data intervals
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict

from models import (
    TradingSession, MainAgentDecision, ActionType, 
    AnalysisData, AgentDecision, DataInterval
)
from main_agent import MainAgent
from config import TradingConfig

logger = logging.getLogger(__name__)

@dataclass
class SessionState:
    """Current session state"""
    session_id: str
    symbol: str
    start_time: datetime
    current_time: datetime
    current_interval: str
    portfolio_state: Dict[str, Any]
    analysis_history: List[AnalysisData]
    decision_history: List[AgentDecision]
    trade_history: List[Dict[str, Any]]
    session_active: bool = True
    last_decision: Optional[MainAgentDecision] = None
    next_interval_time: Optional[datetime] = None

class TradingSessionManager:
    """Manages trading sessions with multi-turn conversations"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.agents: Dict[str, MainAgent] = {}
        
    async def create_session(self, symbol: str, initial_budget: float = None) -> Dict[str, Any]:
        """Create a new trading session"""
        session_id = f"session_{symbol}_{int(datetime.now().timestamp())}"
        
        # Create main agent
        agent = MainAgent()
        await agent.start_trading_session(symbol, initial_budget)
        
        # Create session state
        session_state = SessionState(
            session_id=session_id,
            symbol=symbol,
            start_time=datetime.now(),
            current_time=datetime.now(),
            current_interval="1day",
            portfolio_state=agent.get_portfolio_summary(),
            analysis_history=[],
            decision_history=[],
            trade_history=[],
            session_active=True
        )
        
        # Store session and agent
        self.sessions[session_id] = session_state
        self.agents[session_id] = agent
        
        logger.info(f"Created trading session {session_id} for {symbol}")
        
        return {
            "session_id": session_id,
            "symbol": symbol,
            "budget": agent.portfolio_manager.initial_budget,
            "start_time": session_state.start_time.isoformat(),
            "status": "active"
        }
    
    async def process_data_interval(self, session_id: str, interval: str = None) -> Dict[str, Any]:
        """Process data for a specific interval"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        agent = self.agents[session_id]
        
        if not session_state.session_active:
            return {"error": "Session is not active"}
        
        # Use provided interval or current interval
        interval = interval or session_state.current_interval
        
        try:
            # Process market data
            decision = await agent.process_market_data(session_state.symbol, interval)
            
            # Update session state
            session_state.current_time = datetime.now()
            session_state.current_interval = interval
            session_state.last_decision = decision
            session_state.analysis_history.extend(agent.analysis_history)
            session_state.decision_history.extend(agent.decision_history)
            session_state.portfolio_state = agent.get_portfolio_summary()
            
            # Calculate next interval time
            next_interval = self._calculate_next_interval(decision.next_interval)
            session_state.next_interval_time = datetime.now() + timedelta(minutes=next_interval)
            
            # Execute decision if confidence is high enough
            execution_result = None
            if decision.confidence >= TradingConfig.BUY_CONFIDENCE_THRESHOLD:
                execution_result = await agent.execute_decision(decision)
                if execution_result.get("success"):
                    session_state.trade_history.append(execution_result)
            
            return {
                "session_id": session_id,
                "symbol": session_state.symbol,
                "interval": interval,
                "decision": {
                    "action": decision.final_action.value,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "position_size": decision.position_size,
                    "risk_level": decision.risk_assessment.value,
                    "stop_loss": decision.stop_loss,
                    "take_profit": decision.take_profit,
                    "next_interval": decision.next_interval
                },
                "agent_decisions": [
                    {
                        "agent_type": d.agent_type.value,
                        "decision": d.decision.value,
                        "confidence": d.confidence,
                        "reasoning": d.reasoning,
                        "position_size": d.position_size
                    }
                    for d in decision.agent_decisions
                ],
                "execution_result": execution_result,
                "portfolio_state": session_state.portfolio_state,
                "next_interval_time": session_state.next_interval_time.isoformat() if session_state.next_interval_time else None
            }
            
        except Exception as e:
            logger.error(f"Error processing data interval for session {session_id}: {str(e)}")
            return {"error": f"Failed to process data interval: {str(e)}"}
    
    async def get_next_data_interval(self, session_id: str) -> Dict[str, Any]:
        """Get the next data interval based on last decision"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        
        if not session_state.last_decision:
            return {"error": "No previous decision available"}
        
        next_interval = session_state.last_decision.next_interval
        
        return await self.process_data_interval(session_id, next_interval)
    
    async def analyze_again(self, session_id: str) -> Dict[str, Any]:
        """Trigger new analysis for the current symbol"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        
        return await self.process_data_interval(session_id, session_state.current_interval)
    
    async def execute_manual_action(self, session_id: str, action: str, 
                                  quantity: Optional[int] = None, 
                                  percentage: Optional[float] = None) -> Dict[str, Any]:
        """Execute manual trading action"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        agent = self.agents[session_id]
        
        try:
            if action.upper() == "BUY":
                # Create buy decision
                decision = MainAgentDecision(
                    final_action=ActionType.BUY,
                    symbol=session_state.symbol,
                    quantity=quantity,
                    percentage=percentage,
                    confidence=100,  # Manual action
                    reasoning="Manual buy action",
                    agent_decisions=[],
                    risk_assessment=session_state.last_decision.risk_assessment if session_state.last_decision else None,
                    position_size=percentage or 10,
                    stop_loss=None,
                    take_profit=None,
                    next_interval="1hour"
                )
                
                execution_result = await agent.execute_decision(decision)
                
            elif action.upper() == "SELL":
                # Create sell decision
                decision = MainAgentDecision(
                    final_action=ActionType.SELL,
                    symbol=session_state.symbol,
                    quantity=quantity,
                    percentage=percentage,
                    confidence=100,  # Manual action
                    reasoning="Manual sell action",
                    agent_decisions=[],
                    risk_assessment=session_state.last_decision.risk_assessment if session_state.last_decision else None,
                    position_size=percentage or 10,
                    stop_loss=None,
                    take_profit=None,
                    next_interval="1hour"
                )
                
                execution_result = await agent.execute_decision(decision)
                
            else:
                return {"error": f"Invalid action: {action}"}
            
            # Update session state
            session_state.portfolio_state = agent.get_portfolio_summary()
            if execution_result.get("success"):
                session_state.trade_history.append(execution_result)
            
            return {
                "action": action,
                "execution_result": execution_result,
                "portfolio_state": session_state.portfolio_state
            }
            
        except Exception as e:
            logger.error(f"Error executing manual action: {str(e)}")
            return {"error": f"Failed to execute action: {str(e)}"}
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current session state"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "symbol": session_state.symbol,
            "start_time": session_state.start_time.isoformat(),
            "current_time": session_state.current_time.isoformat(),
            "current_interval": session_state.current_interval,
            "session_active": session_state.session_active,
            "portfolio_state": session_state.portfolio_state,
            "analysis_count": len(session_state.analysis_history),
            "decision_count": len(session_state.decision_history),
            "trade_count": len(session_state.trade_history),
            "last_decision": {
                "action": session_state.last_decision.final_action.value,
                "confidence": session_state.last_decision.confidence,
                "reasoning": session_state.last_decision.reasoning
            } if session_state.last_decision else None,
            "next_interval_time": session_state.next_interval_time.isoformat() if session_state.next_interval_time else None
        }
    
    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get session history"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "symbol": session_state.symbol,
            "start_time": session_state.start_time.isoformat(),
            "current_time": session_state.current_time.isoformat(),
            "portfolio_state": session_state.portfolio_state,
            "trade_history": session_state.trade_history,
            "analysis_history": [
                {
                    "timestamp": analysis.timestamp,
                    "current_price": analysis.current_price,
                    "price_change_percentage": analysis.price_change_percentage,
                    "risk_level": analysis.risk_level,
                    "recommendation": analysis.recommendation
                }
                for analysis in session_state.analysis_history[-10:]  # Last 10 analyses
            ],
            "decision_history": [
                {
                    "agent_type": decision.agent_type.value,
                    "decision": decision.decision.value,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning[:100] + "..." if len(decision.reasoning) > 100 else decision.reasoning
                }
                for decision in session_state.decision_history[-20:]  # Last 20 decisions
            ]
        }
    
    def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a trading session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        session_state.session_active = False
        
        # Get final portfolio summary
        agent = self.agents[session_id]
        final_portfolio = agent.get_portfolio_summary()
        
        return {
            "session_id": session_id,
            "status": "closed",
            "final_portfolio": final_portfolio,
            "session_duration": (datetime.now() - session_state.start_time).total_seconds() / 3600,  # hours
            "total_trades": len(session_state.trade_history),
            "total_pnl": final_portfolio.get("total_pnl", 0),
            "total_pnl_percentage": final_portfolio.get("total_pnl_percentage", 0)
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        sessions = []
        for session_id, session_state in self.sessions.items():
            sessions.append({
                "session_id": session_id,
                "symbol": session_state.symbol,
                "start_time": session_state.start_time.isoformat(),
                "session_active": session_state.session_active,
                "portfolio_value": session_state.portfolio_state.get("total_value", 0),
                "total_pnl": session_state.portfolio_state.get("total_pnl", 0)
            })
        return sessions
    
    def _calculate_next_interval(self, interval: str) -> int:
        """Calculate next interval in minutes"""
        interval_map = {
            "1min": 1,
            "5min": 5,
            "15min": 15,
            "30min": 30,
            "1hour": 60,
            "1day": 1440
        }
        return interval_map.get(interval, 60)  # Default to 1 hour
    
    async def auto_trade_session(self, session_id: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Run automated trading session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session_state = self.sessions[session_id]
        results = []
        
        for i in range(max_iterations):
            try:
                # Process next data interval
                result = await self.get_next_data_interval(session_id)
                
                if "error" in result:
                    results.append({"iteration": i + 1, "error": result["error"]})
                    break
                
                results.append({
                    "iteration": i + 1,
                    "decision": result["decision"],
                    "execution_result": result.get("execution_result"),
                    "portfolio_state": result["portfolio_state"]
                })
                
                # Wait for next interval
                if session_state.next_interval_time:
                    wait_time = (session_state.next_interval_time - datetime.now()).total_seconds()
                    if wait_time > 0:
                        await asyncio.sleep(min(wait_time, 60))  # Max 1 minute wait
                
            except Exception as e:
                results.append({"iteration": i + 1, "error": str(e)})
                break
        
        return {
            "session_id": session_id,
            "auto_trade_completed": True,
            "iterations": len(results),
            "results": results,
            "final_portfolio": session_state.portfolio_state
        }

