"""
Specialist Agents for Agentic Trading System
Each agent specializes in a specific aspect of trading analysis
"""
import asyncio
from typing import Dict, Any, Optional, List
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from models import (
    AgentDecision, DecisionType, RiskLevel, AgentType, 
    AnalysisData, AgentResponse, ActionType
)
from config import TradingConfig, AgentPrompts

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all specialist agents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.llm = ChatOpenAI(
            model=TradingConfig.AGENT_MODEL,
            temperature=TradingConfig.AGENT_TEMPERATURE,
            max_tokens=TradingConfig.AGENT_MAX_TOKENS
        )
        self.parser = JsonOutputParser()
    
    async def analyze(self, data: AnalysisData, portfolio_state: Dict[str, Any]) -> AgentResponse:
        """Analyze data and return decision"""
        raise NotImplementedError
    
    def _extract_relevant_data(self, data: AnalysisData) -> Dict[str, Any]:
        """Extract relevant data for this agent type"""
        raise NotImplementedError
    
    def _create_prompt(self, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> str:
        """Create prompt for the agent"""
        raise NotImplementedError

class TechnicalAnalysisAgent(BaseAgent):
    """Agent specializing in technical analysis"""
    
    def __init__(self):
        super().__init__(AgentType.TECHNICAL)
    
    def _extract_relevant_data(self, data: AnalysisData) -> Dict[str, Any]:
        """Extract technical analysis data"""
        return {
            "technical_indicators": data.technical_indicators,
            "current_price": data.current_price,
            "price_change": data.price_change,
            "price_change_percentage": data.price_change_percentage,
            "risk_level": data.risk_level,
            "recommendation": data.recommendation
        }
    
    def _create_prompt(self, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> str:
        """Create technical analysis prompt"""
        return f"""
{AgentPrompts.TECHNICAL_AGENT_SYSTEM_PROMPT}

Current Analysis Data:
- Symbol: {data.get('symbol', 'N/A')}
- Current Price: {data.get('current_price', 0):.2f}
- Price Change: {data.get('price_change', 0):.2f} ({data.get('price_change_percentage', 0):.2f}%)
- Risk Level: {data.get('risk_level', 'Medium')}
- Recommendation: {data.get('recommendation', 'Hold')}

Technical Indicators:
{self._format_technical_indicators(data.get('technical_indicators', {}))}

Portfolio State:
- Available Cash: {portfolio_state.get('available_cash', 0):.2f}
- Total Value: {portfolio_state.get('total_value', 0):.2f}
- Current Holdings: {len(portfolio_state.get('holdings', {}))}

Please analyze the technical indicators and provide a trading recommendation.
"""
    
    def _format_technical_indicators(self, indicators: Dict[str, Any]) -> str:
        """Format technical indicators for prompt"""
        formatted = []
        for indicator, value in indicators.items():
            if isinstance(value, dict):
                formatted.append(f"- {indicator}: {value}")
            else:
                formatted.append(f"- {indicator}: {value}")
        return "\n".join(formatted)
    
    async def analyze(self, data: AnalysisData, portfolio_state: Dict[str, Any]) -> AgentResponse:
        """Analyze technical data and return decision"""
        try:
            relevant_data = self._extract_relevant_data(data)
            relevant_data['symbol'] = data.symbol
            
            prompt = self._create_prompt(relevant_data, portfolio_state)
            
            messages = [
                SystemMessage(content=AgentPrompts.TECHNICAL_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse the response
            decision = self._parse_technical_decision(response.content, relevant_data)
            
            return AgentResponse(
                agent_type=self.agent_type,
                decision=decision,
                data_processed=relevant_data,
                additional_analysis_needed=False
            )
            
        except Exception as e:
            logger.error(f"Technical analysis agent error: {str(e)}")
            return self._create_fallback_response()
    
    def _parse_technical_decision(self, response: str, data: Dict[str, Any]) -> AgentDecision:
        """Parse technical analysis decision from LLM response"""
        try:
            # Extract decision from response
            if "buy" in response.lower() and "strong" in response.lower():
                decision = DecisionType.STRONG_BUY
                confidence = 85
            elif "buy" in response.lower():
                decision = DecisionType.BUY
                confidence = 70
            elif "sell" in response.lower() and "strong" in response.lower():
                decision = DecisionType.STRONG_SELL
                confidence = 85
            elif "sell" in response.lower():
                decision = DecisionType.SELL
                confidence = 70
            else:
                decision = DecisionType.HOLD
                confidence = 50
            
            # Extract risk level
            risk_level = RiskLevel.MEDIUM
            if "high risk" in response.lower():
                risk_level = RiskLevel.HIGH
            elif "low risk" in response.lower():
                risk_level = RiskLevel.LOW
            
            return AgentDecision(
                agent_type=self.agent_type,
                decision=decision,
                confidence=confidence,
                reasoning=response,
                risk_assessment=risk_level,
                position_size=min(confidence / 100 * 30, 30)  # Max 30% position
            )
            
        except Exception as e:
            logger.error(f"Error parsing technical decision: {str(e)}")
            return self._create_fallback_decision()
    
    def _create_fallback_response(self) -> AgentResponse:
        """Create fallback response when analysis fails"""
        return AgentResponse(
            agent_type=self.agent_type,
            decision=self._create_fallback_decision(),
            data_processed={},
            additional_analysis_needed=True
        )
    
    def _create_fallback_decision(self) -> AgentDecision:
        """Create fallback decision"""
        return AgentDecision(
            agent_type=self.agent_type,
            decision=DecisionType.HOLD,
            confidence=30,
            reasoning="Unable to analyze technical indicators",
            risk_assessment=RiskLevel.MEDIUM,
            position_size=10
        )

class SectorAnalysisAgent(BaseAgent):
    """Agent specializing in sector analysis"""
    
    def __init__(self):
        super().__init__(AgentType.SECTOR)
    
    def _extract_relevant_data(self, data: AnalysisData) -> Dict[str, Any]:
        """Extract sector analysis data"""
        return {
            "sector_context": data.sector_context,
            "current_price": data.current_price,
            "symbol": data.symbol
        }
    
    def _create_prompt(self, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> str:
        """Create sector analysis prompt"""
        return f"""
{AgentPrompts.SECTOR_AGENT_SYSTEM_PROMPT}

Sector Analysis Data:
- Symbol: {data.get('symbol', 'N/A')}
- Current Price: {data.get('current_price', 0):.2f}

Sector Context:
{self._format_sector_context(data.get('sector_context', {}))}

Please analyze the sector context and provide sector-based trading recommendations.
"""
    
    def _format_sector_context(self, sector_context: Dict[str, Any]) -> str:
        """Format sector context for prompt"""
        formatted = []
        for key, value in sector_context.items():
            if isinstance(value, dict):
                formatted.append(f"- {key}: {value}")
            else:
                formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    async def analyze(self, data: AnalysisData, portfolio_state: Dict[str, Any]) -> AgentResponse:
        """Analyze sector data and return decision"""
        try:
            relevant_data = self._extract_relevant_data(data)
            
            prompt = self._create_prompt(relevant_data, portfolio_state)
            
            messages = [
                SystemMessage(content=AgentPrompts.SECTOR_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            decision = self._parse_sector_decision(response.content, relevant_data)
            
            return AgentResponse(
                agent_type=self.agent_type,
                decision=decision,
                data_processed=relevant_data,
                additional_analysis_needed=False
            )
            
        except Exception as e:
            logger.error(f"Sector analysis agent error: {str(e)}")
            return self._create_fallback_response()
    
    def _parse_sector_decision(self, response: str, data: Dict[str, Any]) -> AgentDecision:
        """Parse sector analysis decision"""
        try:
            if "outperform" in response.lower() or "positive" in response.lower():
                decision = DecisionType.BUY
                confidence = 75
            elif "underperform" in response.lower() or "negative" in response.lower():
                decision = DecisionType.SELL
                confidence = 75
            else:
                decision = DecisionType.HOLD
                confidence = 50
            
            return AgentDecision(
                agent_type=self.agent_type,
                decision=decision,
                confidence=confidence,
                reasoning=response,
                risk_assessment=RiskLevel.MEDIUM,
                position_size=min(confidence / 100 * 25, 25)  # Max 25% position
            )
            
        except Exception as e:
            logger.error(f"Error parsing sector decision: {str(e)}")
            return self._create_fallback_decision()
    
    def _create_fallback_response(self) -> AgentResponse:
        return AgentResponse(
            agent_type=self.agent_type,
            decision=self._create_fallback_decision(),
            data_processed={},
            additional_analysis_needed=True
        )
    
    def _create_fallback_decision(self) -> AgentDecision:
        return AgentDecision(
            agent_type=self.agent_type,
            decision=DecisionType.HOLD,
            confidence=30,
            reasoning="Unable to analyze sector context",
            risk_assessment=RiskLevel.MEDIUM,
            position_size=10
        )

class RiskAssessmentAgent(BaseAgent):
    """Agent specializing in risk assessment"""
    
    def __init__(self):
        super().__init__(AgentType.RISK)
    
    def _extract_relevant_data(self, data: AnalysisData) -> Dict[str, Any]:
        """Extract risk assessment data"""
        return {
            "risk_level": data.risk_level,
            "enhanced_metadata": data.enhanced_metadata,
            "current_price": data.current_price,
            "technical_indicators": data.technical_indicators,
            "ml_predictions": data.ml_predictions
        }
    
    def _create_prompt(self, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> str:
        """Create risk assessment prompt"""
        return f"""
{AgentPrompts.RISK_AGENT_SYSTEM_PROMPT}

Risk Assessment Data:
- Current Price: {data.get('current_price', 0):.2f}
- Risk Level: {data.get('risk_level', 'Medium')}
- Available Cash: {portfolio_state.get('available_cash', 0):.2f}
- Total Portfolio Value: {portfolio_state.get('total_value', 0):.2f}

Enhanced Metadata:
{self._format_enhanced_metadata(data.get('enhanced_metadata', {}))}

ML Predictions:
{self._format_ml_predictions(data.get('ml_predictions', {}))}

Please assess the risk and provide position sizing recommendations.
"""
    
    def _format_enhanced_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format enhanced metadata for prompt"""
        formatted = []
        for key, value in metadata.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    def _format_ml_predictions(self, predictions: Dict[str, Any]) -> str:
        """Format ML predictions for prompt"""
        formatted = []
        for key, value in predictions.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    async def analyze(self, data: AnalysisData, portfolio_state: Dict[str, Any]) -> AgentResponse:
        """Analyze risk and return decision"""
        try:
            relevant_data = self._extract_relevant_data(data)
            
            prompt = self._create_prompt(relevant_data, portfolio_state)
            
            messages = [
                SystemMessage(content=AgentPrompts.RISK_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            decision = self._parse_risk_decision(response.content, relevant_data)
            
            return AgentResponse(
                agent_type=self.agent_type,
                decision=decision,
                data_processed=relevant_data,
                additional_analysis_needed=False
            )
            
        except Exception as e:
            logger.error(f"Risk assessment agent error: {str(e)}")
            return self._create_fallback_response()
    
    def _parse_risk_decision(self, response: str, data: Dict[str, Any]) -> AgentDecision:
        """Parse risk assessment decision"""
        try:
            risk_level = RiskLevel.MEDIUM
            if "high risk" in response.lower():
                risk_level = RiskLevel.HIGH
            elif "low risk" in response.lower():
                risk_level = RiskLevel.LOW
            
            # Determine position size based on risk
            if risk_level == RiskLevel.LOW:
                position_size = 25
                confidence = 80
            elif risk_level == RiskLevel.MEDIUM:
                position_size = 15
                confidence = 60
            else:  # High risk
                position_size = 5
                confidence = 40
            
            return AgentDecision(
                agent_type=self.agent_type,
                decision=DecisionType.HOLD,  # Risk agent doesn't make buy/sell decisions
                confidence=confidence,
                reasoning=response,
                risk_assessment=risk_level,
                position_size=position_size
            )
            
        except Exception as e:
            logger.error(f"Error parsing risk decision: {str(e)}")
            return self._create_fallback_decision()
    
    def _create_fallback_response(self) -> AgentResponse:
        return AgentResponse(
            agent_type=self.agent_type,
            decision=self._create_fallback_decision(),
            data_processed={},
            additional_analysis_needed=True
        )
    
    def _create_fallback_decision(self) -> AgentDecision:
        return AgentDecision(
            agent_type=self.agent_type,
            decision=DecisionType.HOLD,
            confidence=30,
            reasoning="Unable to assess risk",
            risk_assessment=RiskLevel.MEDIUM,
            position_size=10
        )

class MLPredictionAgent(BaseAgent):
    """Agent specializing in ML predictions"""
    
    def __init__(self):
        super().__init__(AgentType.ML)
    
    def _extract_relevant_data(self, data: AnalysisData) -> Dict[str, Any]:
        """Extract ML prediction data"""
        return {
            "ml_predictions": data.ml_predictions,
            "multi_timeframe_analysis": data.multi_timeframe_analysis,
            "current_price": data.current_price
        }
    
    def _create_prompt(self, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> str:
        """Create ML prediction prompt"""
        return f"""
{AgentPrompts.ML_AGENT_SYSTEM_PROMPT}

ML Prediction Data:
- Current Price: {data.get('current_price', 0):.2f}

ML Predictions:
{self._format_ml_predictions(data.get('ml_predictions', {}))}

Multi-timeframe Analysis:
{self._format_mtf_analysis(data.get('multi_timeframe_analysis', {}))}

Please interpret the ML predictions and provide trading insights.
"""
    
    def _format_ml_predictions(self, predictions: Dict[str, Any]) -> str:
        """Format ML predictions for prompt"""
        formatted = []
        for key, value in predictions.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    def _format_mtf_analysis(self, mtf: Dict[str, Any]) -> str:
        """Format multi-timeframe analysis for prompt"""
        formatted = []
        for key, value in mtf.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    async def analyze(self, data: AnalysisData, portfolio_state: Dict[str, Any]) -> AgentResponse:
        """Analyze ML predictions and return decision"""
        try:
            relevant_data = self._extract_relevant_data(data)
            
            prompt = self._create_prompt(relevant_data, portfolio_state)
            
            messages = [
                SystemMessage(content=AgentPrompts.ML_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            decision = self._parse_ml_decision(response.content, relevant_data)
            
            return AgentResponse(
                agent_type=self.agent_type,
                decision=decision,
                data_processed=relevant_data,
                additional_analysis_needed=False
            )
            
        except Exception as e:
            logger.error(f"ML prediction agent error: {str(e)}")
            return self._create_fallback_response()
    
    def _parse_ml_decision(self, response: str, data: Dict[str, Any]) -> AgentDecision:
        """Parse ML prediction decision"""
        try:
            if "bullish" in response.lower() or "positive" in response.lower():
                decision = DecisionType.BUY
                confidence = 75
            elif "bearish" in response.lower() or "negative" in response.lower():
                decision = DecisionType.SELL
                confidence = 75
            else:
                decision = DecisionType.HOLD
                confidence = 50
            
            return AgentDecision(
                agent_type=self.agent_type,
                decision=decision,
                confidence=confidence,
                reasoning=response,
                risk_assessment=RiskLevel.MEDIUM,
                position_size=min(confidence / 100 * 20, 20)  # Max 20% position
            )
            
        except Exception as e:
            logger.error(f"Error parsing ML decision: {str(e)}")
            return self._create_fallback_decision()
    
    def _create_fallback_response(self) -> AgentResponse:
        return AgentResponse(
            agent_type=self.agent_type,
            decision=self._create_fallback_decision(),
            data_processed={},
            additional_analysis_needed=True
        )
    
    def _create_fallback_decision(self) -> AgentDecision:
        return AgentDecision(
            agent_type=self.agent_type,
            decision=DecisionType.HOLD,
            confidence=30,
            reasoning="Unable to interpret ML predictions",
            risk_assessment=RiskLevel.MEDIUM,
            position_size=10
        )

class PortfolioAgent(BaseAgent):
    """Agent specializing in portfolio management"""
    
    def __init__(self):
        super().__init__(AgentType.PORTFOLIO)
    
    def _extract_relevant_data(self, data: AnalysisData) -> Dict[str, Any]:
        """Extract portfolio management data"""
        return {
            "current_price": data.current_price,
            "symbol": data.symbol,
            "ai_analysis": data.ai_analysis
        }
    
    def _create_prompt(self, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> str:
        """Create portfolio management prompt"""
        return f"""
{AgentPrompts.PORTFOLIO_AGENT_SYSTEM_PROMPT}

Portfolio State:
- Available Cash: {portfolio_state.get('available_cash', 0):.2f}
- Total Portfolio Value: {portfolio_state.get('total_value', 0):.2f}
- Number of Holdings: {len(portfolio_state.get('holdings', {}))}
- Total PnL: {portfolio_state.get('total_pnl', 0):.2f}

Current Stock:
- Symbol: {data.get('symbol', 'N/A')}
- Current Price: {data.get('current_price', 0):.2f}

AI Analysis:
{self._format_ai_analysis(data.get('ai_analysis', {}))}

Please provide portfolio management recommendations.
"""
    
    def _format_ai_analysis(self, ai_analysis: Dict[str, Any]) -> str:
        """Format AI analysis for prompt"""
        formatted = []
        for key, value in ai_analysis.items():
            if isinstance(value, dict):
                formatted.append(f"- {key}: {value}")
            else:
                formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    async def analyze(self, data: AnalysisData, portfolio_state: Dict[str, Any]) -> AgentResponse:
        """Analyze portfolio and return decision"""
        try:
            relevant_data = self._extract_relevant_data(data)
            
            prompt = self._create_prompt(relevant_data, portfolio_state)
            
            messages = [
                SystemMessage(content=AgentPrompts.PORTFOLIO_AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            decision = self._parse_portfolio_decision(response.content, relevant_data, portfolio_state)
            
            return AgentResponse(
                agent_type=self.agent_type,
                decision=decision,
                data_processed=relevant_data,
                additional_analysis_needed=False
            )
            
        except Exception as e:
            logger.error(f"Portfolio agent error: {str(e)}")
            return self._create_fallback_response()
    
    def _parse_portfolio_decision(self, response: str, data: Dict[str, Any], portfolio_state: Dict[str, Any]) -> AgentDecision:
        """Parse portfolio management decision"""
        try:
            # Portfolio agent focuses on position sizing and risk management
            cash_percentage = (portfolio_state.get('available_cash', 0) / portfolio_state.get('total_value', 1)) * 100
            
            if cash_percentage > 80:
                # High cash position, can consider buying
                decision = DecisionType.BUY
                confidence = 60
            elif cash_percentage < 20:
                # Low cash position, be conservative
                decision = DecisionType.HOLD
                confidence = 70
            else:
                decision = DecisionType.HOLD
                confidence = 50
            
            return AgentDecision(
                agent_type=self.agent_type,
                decision=decision,
                confidence=confidence,
                reasoning=response,
                risk_assessment=RiskLevel.MEDIUM,
                position_size=min(confidence / 100 * 15, 15)  # Max 15% position
            )
            
        except Exception as e:
            logger.error(f"Error parsing portfolio decision: {str(e)}")
            return self._create_fallback_decision()
    
    def _create_fallback_response(self) -> AgentResponse:
        return AgentResponse(
            agent_type=self.agent_type,
            decision=self._create_fallback_decision(),
            data_processed={},
            additional_analysis_needed=True
        )
    
    def _create_fallback_decision(self) -> AgentDecision:
        return AgentDecision(
            agent_type=self.agent_type,
            decision=DecisionType.HOLD,
            confidence=30,
            reasoning="Unable to analyze portfolio",
            risk_assessment=RiskLevel.MEDIUM,
            position_size=10
        )

