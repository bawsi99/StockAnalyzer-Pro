"""
Volume Trend Momentum Agent

Assesses volume trend sustainability and momentum for trend continuation analysis.
"""

from .src.volume_trend_momentum_processor import VolumeTrendMomentumProcessor
from .src.volume_trend_momentum_charts import VolumeTrendMomentumChartGenerator

__all__ = [
    'VolumeTrendMomentumProcessor',
    'VolumeTrendMomentumChartGenerator'
]

__version__ = '1.0.0'