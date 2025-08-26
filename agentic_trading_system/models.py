"""
Data models for Agentic Trading System
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """Available trading actions"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    ANALYZE = "ANALYZE"
    GET_DATA = "GET_DATA"

class DecisionType(str, Enum):
    """Decision types from agents"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class RiskLevel(str, Enum):
    """Risk levels"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"

class AgentType(str, Enum):
    """Types of specialist agents"""
    TECHNICAL = "technical"
    SECTOR = "sector"
    RISK = "risk"
    ML = "ml"
    PORTFOLIO = "portfolio"
    MAIN = "main"

class TradeRequest(BaseModel):
    """Request for trading action"""
    action: ActionType
    symbol: str
    quantity: Optional[int] = None
    percentage: Optional[float] = None  # Percentage of budget or holdings
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: Optional[str] = None
    confidence: Optional[float] = None

class AgentDecision(BaseModel):
    """Decision from a specialist agent"""
    agent_type: AgentType
    decision: DecisionType
    confidence: float = Field(ge=0, le=100)
    reasoning: str
    recommendations: List[str] = Field(default_factory=list)
    risk_assessment: Optional[RiskLevel] = None
    position_size: Optional[float] = None  # Percentage of budget

class PortfolioState(BaseModel):
    """Current portfolio state"""
    total_budget: float
    available_cash: float
    total_value: float
    holdings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    total_pnl: float = 0.0
    total_pnl_percentage: float = 0.0

class Holding(BaseModel):
    """Individual stock holding"""
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_percentage: float
    percentage_of_portfolio: float

class AnalysisData(BaseModel):
    """Analysis data from backend"""
    symbol: str
    exchange: str
    timestamp: str
    current_price: float
    price_change: float
    price_change_percentage: float
    
    # Technical Analysis
    technical_indicators: Dict[str, Any]
    risk_level: str
    recommendation: str
    
    # AI Analysis
    ai_analysis: Dict[str, Any]
    
    # Sector Analysis
    sector_context: Dict[str, Any]
    
    # Multi-timeframe Analysis
    multi_timeframe_analysis: Dict[str, Any]
    
    # ML Predictions
    ml_predictions: Dict[str, Any]
    
    # Enhanced Metadata
    enhanced_metadata: Dict[str, Any]

class TradingSession(BaseModel):
    """Trading session state"""
    session_id: str
    start_time: datetime
    current_time: datetime
    symbol: str
    portfolio: PortfolioState
    analysis_history: List[AnalysisData] = Field(default_factory=list)
    decision_history: List[AgentDecision] = Field(default_factory=list)
    trade_history: List[TradeRequest] = Field(default_factory=list)
    current_interval: str = "1day"
    session_active: bool = True

class AgentResponse(BaseModel):
    """Response from an agent"""
    agent_type: AgentType
    decision: AgentDecision
    data_processed: Dict[str, Any]
    next_action: Optional[ActionType] = None
    additional_analysis_needed: bool = False

class MainAgentDecision(BaseModel):
    """Final decision from main agent"""
    final_action: ActionType
    symbol: str
    quantity: Optional[int] = None
    percentage: Optional[float] = None
    price: Optional[float] = None
    confidence: float
    reasoning: str
    agent_decisions: List[AgentDecision]
    risk_assessment: RiskLevel
    position_size: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    next_interval: Optional[str] = None

class BackendAnalysisResponse(BaseModel):
    """Response structure from backend analysis"""
    success: bool
    stock_symbol: str
    exchange: str
    analysis_period: str
    interval: str
    timestamp: str
    message: str
    results: Dict[str, Any]

class DataInterval(BaseModel):
    """Data interval configuration"""
    interval: str
    duration_minutes: int
    description: str

class TradingConfig(BaseModel):
    """Trading configuration"""
    initial_budget: float
    max_position_size: float
    min_position_size: float
    buy_confidence_threshold: float
    sell_confidence_threshold: float
    stop_loss_percentage: float
    take_profit_percentage: float

