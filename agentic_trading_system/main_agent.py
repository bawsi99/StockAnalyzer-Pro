"""
Main Agent for Agentic Trading System
Orchestrates specialist agents and makes final trading decisions
"""
import asyncio
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from models import (
    MainAgentDecision, AgentDecision, DecisionType, RiskLevel, 
    ActionType, TradeRequest, AnalysisData, AgentType
)
from config import TradingConfig, AgentPrompts
from specialist_agents import (
    TechnicalAnalysisAgent, SectorAnalysisAgent, RiskAssessmentAgent,
    MLPredictionAgent, PortfolioAgent
)
from backend_client import BackendClient
from portfolio_manager import PortfolioManager

logger = logging.getLogger(__name__)

class MainAgent:
    """Main agent that orchestrates specialist agents and makes final decisions"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=TradingConfig.AGENT_MODEL,
            temperature=TradingConfig.AGENT_TEMPERATURE,
            max_tokens=TradingConfig.AGENT_MAX_TOKENS
        )
        
        # Initialize specialist agents
        self.technical_agent = TechnicalAnalysisAgent()
        self.sector_agent = SectorAnalysisAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.ml_agent = MLPredictionAgent()
        self.portfolio_agent = PortfolioAgent()
        
        # Initialize portfolio manager
        self.portfolio_manager = PortfolioManager()
        
        # Session state
        self.current_symbol = None
        self.current_interval = "1day"
        self.analysis_history = []
        self.decision_history = []
        
    async def start_trading_session(self, symbol: str, initial_budget: float = None) -> Dict[str, Any]:
        """Start a new trading session"""
        self.current_symbol = symbol
        if initial_budget:
            self.portfolio_manager = PortfolioManager(initial_budget)
        
        logger.info(f"Started trading session for {symbol} with budget: {self.portfolio_manager.initial_budget}")
        
        return {
            "session_started": True,
            "symbol": symbol,
            "budget": self.portfolio_manager.initial_budget,
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_market_data(self, symbol: str = None, interval: str = None) -> MainAgentDecision:
        """
        Process market data and make trading decisions
        
        Args:
            symbol: Stock symbol (uses current if not provided)
            interval: Time interval (uses current if not provided)
        
        Returns:
            MainAgentDecision with final trading decision
        """
        symbol = symbol or self.current_symbol
        interval = interval or self.current_interval
        
        if not symbol:
            raise ValueError("No symbol specified for analysis")
        
        logger.info(f"Processing market data for {symbol} at {interval} interval")
        
        # Get analysis from backend
        async with BackendClient() as backend_client:
            analysis_data = await backend_client.get_analysis(symbol, interval=interval)
            
            if not analysis_data:
                logger.error(f"Failed to get analysis for {symbol}")
                return self._create_error_decision(symbol, "Failed to get analysis from backend")
        
        # Update portfolio with current price
        self.portfolio_manager.update_holding_price(symbol, analysis_data.current_price)
        
        # Get current portfolio state
        portfolio_state = self.portfolio_manager.get_portfolio_state()
        
        # Run specialist agents in parallel
        agent_tasks = [
            self.technical_agent.analyze(analysis_data, portfolio_state.dict()),
            self.sector_agent.analyze(analysis_data, portfolio_state.dict()),
            self.risk_agent.analyze(analysis_data, portfolio_state.dict()),
            self.ml_agent.analyze(analysis_data, portfolio_state.dict()),
            self.portfolio_agent.analyze(analysis_data, portfolio_state.dict())
        ]
        
        agent_responses = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Process agent responses
        agent_decisions = []
        for i, response in enumerate(agent_responses):
            if isinstance(response, Exception):
                logger.error(f"Agent {i} failed: {str(response)}")
                continue
            agent_decisions.append(response.decision)
        
        # Make final decision
        final_decision = await self._make_final_decision(
            analysis_data, agent_decisions, portfolio_state
        )
        
        # Store in history
        self.analysis_history.append(analysis_data)
        self.decision_history.extend(agent_decisions)
        
        return final_decision
    
    async def _make_final_decision(
        self, 
        analysis_data: AnalysisData, 
        agent_decisions: List[AgentDecision], 
        portfolio_state: Dict[str, Any]
    ) -> MainAgentDecision:
        """Make final trading decision based on agent recommendations"""
        
        # Calculate consensus
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        total_confidence = 0
        weighted_confidence = 0
        
        for decision in agent_decisions:
            if decision.decision in [DecisionType.STRONG_BUY, DecisionType.BUY]:
                buy_votes += 1
                weighted_confidence += decision.confidence * 1.2  # Weight buy signals higher
            elif decision.decision in [DecisionType.STRONG_SELL, DecisionType.SELL]:
                sell_votes += 1
                weighted_confidence += decision.confidence * 1.1  # Weight sell signals higher
            else:
                hold_votes += 1
                weighted_confidence += decision.confidence
            
            total_confidence += decision.confidence
        
        avg_confidence = total_confidence / len(agent_decisions) if agent_decisions else 0
        weighted_avg_confidence = weighted_confidence / len(agent_decisions) if agent_decisions else 0
        
        # Determine final action
        if buy_votes > sell_votes and buy_votes > hold_votes:
            if weighted_avg_confidence >= TradingConfig.BUY_CONFIDENCE_THRESHOLD:
                final_action = ActionType.BUY
            else:
                final_action = ActionType.HOLD
        elif sell_votes > buy_votes and sell_votes > hold_votes:
            if weighted_avg_confidence >= TradingConfig.SELL_CONFIDENCE_THRESHOLD:
                final_action = ActionType.SELL
            else:
                final_action = ActionType.HOLD
        else:
            final_action = ActionType.HOLD
        
        # Calculate position size
        position_size = self._calculate_position_size(agent_decisions, portfolio_state)
        
        # Determine risk level
        risk_level = self._determine_risk_level(agent_decisions)
        
        # Create reasoning
        reasoning = self._create_reasoning(agent_decisions, final_action, weighted_avg_confidence)
        
        # Calculate stop loss and take profit
        stop_loss, take_profit = self._calculate_risk_levels(analysis_data.current_price, risk_level)
        
        # Determine next interval
        next_interval = self._determine_next_interval(final_action, weighted_avg_confidence)
        
        return MainAgentDecision(
            final_action=final_action,
            symbol=analysis_data.symbol,
            confidence=weighted_avg_confidence,
            reasoning=reasoning,
            agent_decisions=agent_decisions,
            risk_assessment=risk_level,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            next_interval=next_interval
        )
    
    def _calculate_position_size(self, agent_decisions: List[AgentDecision], portfolio_state: Dict[str, Any]) -> float:
        """Calculate recommended position size"""
        if not agent_decisions:
            return 10.0  # Default 10%
        
        # Average position size recommendations from agents
        total_position_size = sum(d.position_size or 10 for d in agent_decisions)
        avg_position_size = total_position_size / len(agent_decisions)
        
        # Adjust based on available cash
        available_cash = portfolio_state.get('available_cash', 0)
        total_value = portfolio_state.get('total_value', 1)
        cash_percentage = (available_cash / total_value) * 100
        
        if cash_percentage < 20:
            # Low cash, reduce position size
            avg_position_size *= 0.5
        elif cash_percentage > 80:
            # High cash, can increase position size
            avg_position_size *= 1.2
        
        # Ensure within limits
        avg_position_size = max(avg_position_size, TradingConfig.MIN_POSITION_SIZE * 100)
        avg_position_size = min(avg_position_size, TradingConfig.MAX_POSITION_SIZE * 100)
        
        return avg_position_size
    
    def _determine_risk_level(self, agent_decisions: List[AgentDecision]) -> RiskLevel:
        """Determine overall risk level from agent decisions"""
        if not agent_decisions:
            return RiskLevel.MEDIUM
        
        risk_scores = {
            RiskLevel.VERY_LOW: 1,
            RiskLevel.LOW: 2,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 4,
            RiskLevel.VERY_HIGH: 5
        }
        
        total_risk_score = 0
        for decision in agent_decisions:
            if decision.risk_assessment:
                total_risk_score += risk_scores.get(decision.risk_assessment, 3)
            else:
                total_risk_score += 3  # Default to medium
        
        avg_risk_score = total_risk_score / len(agent_decisions)
        
        if avg_risk_score <= 1.5:
            return RiskLevel.VERY_LOW
        elif avg_risk_score <= 2.5:
            return RiskLevel.LOW
        elif avg_risk_score <= 3.5:
            return RiskLevel.MEDIUM
        elif avg_risk_score <= 4.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _create_reasoning(self, agent_decisions: List[AgentDecision], final_action: ActionType, confidence: float) -> str:
        """Create reasoning for the final decision"""
        reasoning_parts = [f"Final decision: {final_action.value} with {confidence:.1f}% confidence"]
        
        # Add agent insights
        for decision in agent_decisions:
            reasoning_parts.append(f"{decision.agent_type.value}: {decision.decision.value} ({decision.confidence:.1f}%)")
        
        return "\n".join(reasoning_parts)
    
    def _calculate_risk_levels(self, current_price: float, risk_level: RiskLevel) -> tuple[Optional[float], Optional[float]]:
        """Calculate stop loss and take profit levels"""
        if risk_level == RiskLevel.VERY_LOW:
            stop_loss_pct = TradingConfig.STOP_LOSS_PERCENTAGE * 0.5
            take_profit_pct = TradingConfig.TAKE_PROFIT_PERCENTAGE * 1.5
        elif risk_level == RiskLevel.LOW:
            stop_loss_pct = TradingConfig.STOP_LOSS_PERCENTAGE * 0.75
            take_profit_pct = TradingConfig.TAKE_PROFIT_PERCENTAGE * 1.25
        elif risk_level == RiskLevel.MEDIUM:
            stop_loss_pct = TradingConfig.STOP_LOSS_PERCENTAGE
            take_profit_pct = TradingConfig.TAKE_PROFIT_PERCENTAGE
        elif risk_level == RiskLevel.HIGH:
            stop_loss_pct = TradingConfig.STOP_LOSS_PERCENTAGE * 1.25
            take_profit_pct = TradingConfig.TAKE_PROFIT_PERCENTAGE * 0.75
        else:  # Very High
            stop_loss_pct = TradingConfig.STOP_LOSS_PERCENTAGE * 1.5
            take_profit_pct = TradingConfig.TAKE_PROFIT_PERCENTAGE * 0.5
        
        stop_loss = current_price * (1 - stop_loss_pct)
        take_profit = current_price * (1 + take_profit_pct)
        
        return stop_loss, take_profit
    
    def _determine_next_interval(self, final_action: ActionType, confidence: float) -> str:
        """Determine next data interval based on action and confidence"""
        if final_action == ActionType.BUY and confidence > 80:
            return "1hour"  # Monitor closely after strong buy
        elif final_action == ActionType.SELL and confidence > 80:
            return "1hour"  # Monitor closely after strong sell
        elif confidence > 70:
            return "5min"  # High confidence, check frequently
        elif confidence > 50:
            return "15min"  # Medium confidence, moderate frequency
        else:
            return "1hour"  # Low confidence, less frequent checks
    
    def _create_error_decision(self, symbol: str, error_message: str) -> MainAgentDecision:
        """Create error decision when analysis fails"""
        return MainAgentDecision(
            final_action=ActionType.HOLD,
            symbol=symbol,
            confidence=0,
            reasoning=f"Error: {error_message}",
            agent_decisions=[],
            risk_assessment=RiskLevel.HIGH,
            position_size=0,
            stop_loss=None,
            take_profit=None,
            next_interval="1hour"
        )
    
    async def execute_decision(self, decision: MainAgentDecision) -> Dict[str, Any]:
        """Execute the trading decision"""
        if decision.final_action == ActionType.BUY:
            return await self._execute_buy(decision)
        elif decision.final_action == ActionType.SELL:
            return await self._execute_sell(decision)
        else:
            return {"action": "HOLD", "message": "No action taken"}
    
    async def _execute_buy(self, decision: MainAgentDecision) -> Dict[str, Any]:
        """Execute buy decision"""
        try:
            # Get current price
            async with BackendClient() as backend_client:
                analysis_data = await backend_client.get_analysis(decision.symbol)
                if not analysis_data:
                    return {"error": "Failed to get current price"}
            
            current_price = analysis_data.current_price
            
            # Create trade request
            trade_request = TradeRequest(
                action=ActionType.BUY,
                symbol=decision.symbol,
                percentage=decision.position_size,
                price=current_price,
                stop_loss=decision.stop_loss,
                take_profit=decision.take_profit,
                reason=decision.reasoning,
                confidence=decision.confidence
            )
            
            # Execute trade
            success, message = self.portfolio_manager.execute_buy(trade_request)
            
            return {
                "action": "BUY",
                "success": success,
                "message": message,
                "symbol": decision.symbol,
                "quantity": trade_request.quantity,
                "price": current_price,
                "total_cost": trade_request.quantity * current_price if trade_request.quantity else 0
            }
            
        except Exception as e:
            logger.error(f"Error executing buy: {str(e)}")
            return {"error": f"Failed to execute buy: {str(e)}"}
    
    async def _execute_sell(self, decision: MainAgentDecision) -> Dict[str, Any]:
        """Execute sell decision"""
        try:
            # Get current price
            async with BackendClient() as backend_client:
                analysis_data = await backend_client.get_analysis(decision.symbol)
                if not analysis_data:
                    return {"error": "Failed to get current price"}
            
            current_price = analysis_data.current_price
            
            # Create trade request
            trade_request = TradeRequest(
                action=ActionType.SELL,
                symbol=decision.symbol,
                percentage=decision.position_size,
                price=current_price,
                stop_loss=decision.stop_loss,
                take_profit=decision.take_profit,
                reason=decision.reasoning,
                confidence=decision.confidence
            )
            
            # Execute trade
            success, message = self.portfolio_manager.execute_sell(trade_request)
            
            return {
                "action": "SELL",
                "success": success,
                "message": message,
                "symbol": decision.symbol,
                "quantity": trade_request.quantity,
                "price": current_price,
                "total_proceeds": trade_request.quantity * current_price if trade_request.quantity else 0
            }
            
        except Exception as e:
            logger.error(f"Error executing sell: {str(e)}")
            return {"error": f"Failed to execute sell: {str(e)}"}
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        return self.portfolio_manager.get_portfolio_summary()
    
    def get_session_history(self) -> Dict[str, Any]:
        """Get trading session history"""
        return {
            "symbol": self.current_symbol,
            "interval": self.current_interval,
            "analysis_count": len(self.analysis_history),
            "decision_count": len(self.decision_history),
            "portfolio_summary": self.get_portfolio_summary()
        }

