"""
Agentic Trading System
AI-powered trading system with multi-agent decision making
"""

__version__ = "1.0.0"
__author__ = "StockAnalyzer Pro Team"
__description__ = "An AI-powered trading system that uses multiple specialist agents to make buy/sell/hold decisions based on comprehensive market analysis"

from .main_agent import MainAgent
from .trading_session import TradingSessionManager
from .portfolio_manager import PortfolioManager
from .backend_client import BackendClient
from .specialist_agents import (
    TechnicalAnalysisAgent,
    SectorAnalysisAgent,
    RiskAssessmentAgent,
    MLPredictionAgent,
    PortfolioAgent
)

__all__ = [
    "MainAgent",
    "TradingSessionManager", 
    "PortfolioManager",
    "BackendClient",
    "TechnicalAnalysisAgent",
    "SectorAnalysisAgent",
    "RiskAssessmentAgent",
    "MLPredictionAgent",
    "PortfolioAgent"
]

