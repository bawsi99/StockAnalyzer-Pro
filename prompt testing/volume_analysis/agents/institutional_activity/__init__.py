"""
Institutional Activity Agent

Detects smart money accumulation/distribution patterns through volume profile analysis.
"""

from .src.institutional_activity_processor import InstitutionalActivityProcessor
from .src.institutional_activity_charts import InstitutionalActivityChartGenerator

__all__ = [
    'InstitutionalActivityProcessor', 
    'InstitutionalActivityChartGenerator'
]

__version__ = '1.0.0'