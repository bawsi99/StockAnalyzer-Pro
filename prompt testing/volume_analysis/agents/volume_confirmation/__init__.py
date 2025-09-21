"""
Volume Confirmation Agent

Validates price-volume relationships and trend confirmation analysis.
"""

from .src.volume_confirmation_processor import VolumeConfirmationProcessor
from .src.volume_confirmation_charts import VolumeConfirmationChartGenerator

__all__ = [
    'VolumeConfirmationProcessor',
    'VolumeConfirmationChartGenerator'
]

__version__ = '1.0.0'