#!/usr/bin/env python3
"""
Volume Analysis Package

Contains specialized agents for volume-based stock market analysis
"""

from support_resistance_processor import SupportResistanceProcessor
from support_resistance_agent import SupportResistanceAgent
from support_resistance_charts import SupportResistanceCharts

__version__ = "1.0.0"
__author__ = "StockAnalyzer Pro Team"

# Available agents
AVAILABLE_AGENTS = {
    'support_resistance': SupportResistanceAgent,
}

# Available processors
AVAILABLE_PROCESSORS = {
    'support_resistance': SupportResistanceProcessor,
}

# Available chart makers
AVAILABLE_CHARTS = {
    'support_resistance': SupportResistanceCharts,
}

def get_agent(agent_type: str):
    """Get an agent instance by type"""
    if agent_type in AVAILABLE_AGENTS:
        return AVAILABLE_AGENTS[agent_type]()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(AVAILABLE_AGENTS.keys())}")

def list_agents():
    """List all available agents"""
    return list(AVAILABLE_AGENTS.keys())

__all__ = [
    'SupportResistanceProcessor',
    'SupportResistanceAgent', 
    'SupportResistanceCharts',
    'get_agent',
    'list_agents',
    'AVAILABLE_AGENTS',
    'AVAILABLE_PROCESSORS',
    'AVAILABLE_CHARTS'
]