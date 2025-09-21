"""
Volume-Based Support/Resistance Agent

Identifies volume-validated support and resistance levels using volume-at-price analysis.
"""

from .src.support_resistance_processor import SupportResistanceProcessor
from .src.support_resistance_charts import SupportResistanceChartGenerator

__all__ = [
    'SupportResistanceProcessor',
    'SupportResistanceChartGenerator'
]

__version__ = '1.0.0'