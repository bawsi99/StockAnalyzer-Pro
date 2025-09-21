"""
Volume Anomaly Detection Agent

Identifies and classifies significant volume spikes and anomalous patterns.
"""

from .src.volume_anomaly_processor import VolumeAnomalyProcessor
from .src.volume_anomaly_charts import VolumeAnomalyChartGenerator

__all__ = [
    'VolumeAnomalyProcessor',
    'VolumeAnomalyChartGenerator'
]

__version__ = '1.0.0'