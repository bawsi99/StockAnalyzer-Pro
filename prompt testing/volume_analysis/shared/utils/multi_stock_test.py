#!/usr/bin/env python3
"""
Multi-Stock Volume Analysis Prompt Testing Framework

Tests the optimized_volume_analysis prompt across multiple stocks from different sectors
to validate volume analysis consistency and quality.

This framework focuses specifically on:
- Volume anomaly detection and significance
- Price-volume correlation analysis
- Volume trend confirmation/divergence
- Volume-based support/resistance levels
- Institutional activity pattern recognition
- Volume signal reliability and risk assessment

Usage: python multi_stock_test.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..')
backend_full_path = os.path.join(backend_path, 'backend')
sys.path.insert(0, backend_full_path)
sys.path.insert(0, backend_path)

# Import optional dependencies
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    print("⚠️  scipy not available - using numpy alternatives for statistical analysis")
    HAS_SCIPY = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    print("⚠️  openpyxl not available - Excel export will be disabled")
    HAS_OPENPYXL = False

# Import backend modules
try:
    from gemini.gemini_client import GeminiClient
    from gemini.prompt_manager import PromptManager
    from gemini.context_engineer import ContextEngineer, AnalysisType
    from zerodha.client import ZerodhaDataClient
    
    # Try to import volume profile functions
    try:
        from ml.indicators.volume_profile import calculate_volume_profile, identify_significant_levels, calculate_vwap
        HAS_VOLUME_PROFILE = True
    except ImportError:
        print("⚠️  Volume profile functions not available - using simplified calculations")
        HAS_VOLUME_PROFILE = False
        
except ImportError as e:
    print(f"❌ Backend Import Error: {e}")
    print("Make sure you're running this from the correct directory (3.0/)")
    print("Current working directory:", os.getcwd())
    print("Backend path:", backend_path)
    sys.exit(1)

# Fallback functions for missing dependencies
def numpy_linregress(x, y):
    """Simple linear regression using numpy when scipy is not available"""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    
    # Calculate slope and intercept
    n = len(x)
    if n < 2:
        return 0, 0, 0, 0, 0
    
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Calculate slope
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    
    if denominator == 0:
        slope = 0
    else:
        slope = numerator / denominator
    
    intercept = y_mean - slope * x_mean
    
    # Calculate correlation coefficient
    x_std = np.std(x)
    y_std = np.std(y)
    
    if x_std == 0 or y_std == 0:
        r_value = 0
    else:
        r_value = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
        if np.isnan(r_value):
            r_value = 0
    
    # Simple p-value and std_err approximation
    p_value = 0.05  # Default assumption
    std_err = 0.1   # Default assumption
    
    return slope, intercept, r_value, p_value, std_err

def simple_volume_profile(data: pd.DataFrame, bins: int = 20) -> Dict[float, float]:
    """Simplified volume profile calculation when ml.indicators is not available"""
    if len(data) < 10:
        return {}
    
    try:
        # Calculate typical price
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        
        # Create price bins
        price_min = data['low'].min()
        price_max = data['high'].max()
        
        if price_max <= price_min:
            return {}
        
        bin_edges = np.linspace(price_min, price_max, bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Assign volume to price bins
        volume_profile = {}
        for center in bin_centers:
            volume_profile[center] = 0.0
        
        for i, tp in enumerate(typical_price):
            # Find the closest bin
            closest_bin = min(bin_centers, key=lambda x: abs(x - tp))
            volume_profile[closest_bin] += data['volume'].iloc[i]
        
        return volume_profile
        
    except Exception:
        return {}

def simple_identify_levels(volume_profile: Dict[float, float], current_price: float) -> Tuple[List[float], List[float]]:
    """Simplified level identification when ml.indicators is not available"""
    if not volume_profile:
        return [], []
    
    try:
        # Sort by volume to find high-volume price levels
        sorted_levels = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 30% of levels
        top_count = max(1, int(len(sorted_levels) * 0.3))
        significant_levels = [price for price, volume in sorted_levels[:top_count]]
        
        # Separate into support and resistance
        support_levels = [p for p in significant_levels if p < current_price]
        resistance_levels = [p for p in significant_levels if p > current_price]
        
        # Sort support (descending) and resistance (ascending)
        support_levels.sort(reverse=True)
        resistance_levels.sort()
        
        return support_levels[:3], resistance_levels[:3]
        
    except Exception:
        return [], []

def simple_vwap(data: pd.DataFrame) -> pd.Series:
    """Simplified VWAP calculation when ml.indicators is not available"""
    try:
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        vwap = (typical_price * data['volume']).cumsum() / data['volume'].cumsum()
        return vwap.ffill().bfill()
    except Exception:
        return pd.Series([data['close'].iloc[-1]] * len(data), index=data.index)

class StockTestConfig:
    """Configuration for individual stock tests with volume characteristics"""
    def __init__(self, symbol: str, name: str, sector: str, expected_behavior: str, volume_characteristics: str = "normal"):
        self.symbol = symbol
        self.name = name
        self.sector = sector
        self.expected_behavior = expected_behavior
        self.volume_characteristics = volume_characteristics

class VolumeIndicatorCalculator:
    """Calculate comprehensive volume indicators for volume analysis testing"""
    
    @staticmethod
    def calculate_volume_anomalies(data: pd.DataFrame, threshold_sigma: float = 2.0) -> Dict[str, Any]:
        """Detect volume anomalies and unusual spikes"""
        if len(data) < 20:
            return {"unusual_spikes": [], "volume_patterns": [], "anomaly_frequency": "low"}
        
        # Calculate volume moving average and standard deviation
        data['volume_ma_20'] = data['volume'].rolling(window=20).mean()
        data['volume_std_20'] = data['volume'].rolling(window=20).std()
        
        # Detect anomalies
        anomalies = []
        for i in range(20, len(data)):
            vol_ma = data['volume_ma_20'].iloc[i-1]  # Use previous day's average
            vol_std = data['volume_std_20'].iloc[i-1]
            current_vol = data['volume'].iloc[i]
            current_price = data['close'].iloc[i]
            prev_price = data['close'].iloc[i-1]
            
            if vol_ma > 0 and vol_std > 0:
                volume_ratio = current_vol / vol_ma
                z_score = (current_vol - vol_ma) / vol_std
                
                if z_score > threshold_sigma:
                    # Determine price context
                    price_change_pct = ((current_price - prev_price) / prev_price) * 100
                    if abs(price_change_pct) > 3:
                        price_context = "breakout" if price_change_pct > 0 else "breakdown"
                    else:
                        price_context = "consolidation"
                    
                    significance = "high" if z_score > 3 else "medium" if z_score > 2.5 else "low"
                    
                    anomalies.append({
                        "date": data.index[i].strftime('%Y-%m-%d'),
                        "volume_ratio": round(volume_ratio, 2),
                        "z_score": round(z_score, 2),
                        "significance": significance,
                        "price_context": price_context,
                        "price_change_pct": round(price_change_pct, 2)
                    })
        
        # Identify volume patterns
        patterns = []
        recent_anomalies = [a for a in anomalies if len(anomalies) - anomalies.index(a) <= 10]
        
        if len(recent_anomalies) >= 3:
            patterns.append("frequent_spikes")
        
        # Check for volume trend patterns
        recent_volume_ratio = data['volume'].tail(5).mean() / data['volume_ma_20'].tail(5).mean()
        if recent_volume_ratio > 1.2:
            patterns.append("elevated_baseline")
        elif recent_volume_ratio < 0.8:
            patterns.append("declining_interest")
        
        # Determine anomaly frequency
        anomaly_frequency = "high" if len(anomalies) / len(data) > 0.1 else "medium" if len(anomalies) / len(data) > 0.05 else "low"
        
        return {
            "unusual_spikes": anomalies[-10:],  # Last 10 anomalies
            "volume_patterns": patterns,
            "anomaly_frequency": anomaly_frequency
        }
    
    @staticmethod
    def calculate_price_volume_correlation(data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate price-volume correlation metrics"""
        if len(data) < 20:
            return {"correlation_strength": 0.0, "correlation_direction": "neutral", 
                   "correlation_significance": "low", "correlation_trend": "stable"}
        
        # Calculate price and volume changes
        price_changes = data['close'].pct_change().dropna()
        volume_changes = data['volume'].pct_change().dropna()
        
        # Align series
        min_length = min(len(price_changes), len(volume_changes))
        if min_length < 10:
            return {"correlation_strength": 0.0, "correlation_direction": "neutral", 
                   "correlation_significance": "low", "correlation_trend": "stable"}
        
        price_changes = price_changes.iloc[-min_length:]
        volume_changes = volume_changes.iloc[-min_length:]
        
        # Calculate correlation
        correlation_20 = price_changes.tail(20).corr(volume_changes.tail(20)) if min_length >= 20 else 0.0
        correlation_50 = price_changes.tail(50).corr(volume_changes.tail(50)) if min_length >= 50 else correlation_20
        
        # Handle NaN correlations
        if pd.isna(correlation_20):
            correlation_20 = 0.0
        if pd.isna(correlation_50):
            correlation_50 = correlation_20
        
        # Determine correlation characteristics
        abs_corr = abs(correlation_20)
        
        correlation_strength = abs_corr
        correlation_direction = "positive" if correlation_20 > 0.1 else "negative" if correlation_20 < -0.1 else "neutral"
        correlation_significance = "high" if abs_corr > 0.5 else "medium" if abs_corr > 0.3 else "low"
        
        # Check correlation trend
        correlation_trend = "increasing" if correlation_50 < correlation_20 else "decreasing" if correlation_50 > correlation_20 else "stable"
        
        return {
            "correlation_strength": round(correlation_20, 3),
            "correlation_direction": correlation_direction,
            "correlation_significance": correlation_significance,
            "correlation_trend": correlation_trend,
            "correlation_50d": round(correlation_50, 3)
        }
    
    @staticmethod
    def analyze_volume_trends(data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume trends and momentum"""
        if len(data) < 20:
            return {"overall_volume_trend": "stable", "volume_confirmation": "neutral", 
                   "volume_momentum": "weak", "volume_consistency": "low"}
        
        # Calculate volume moving averages
        volume_ma_5 = data['volume'].rolling(window=5).mean()
        volume_ma_20 = data['volume'].rolling(window=20).mean()
        volume_ma_50 = data['volume'].rolling(window=50).mean() if len(data) >= 50 else volume_ma_20
        
        # Determine overall trend
        current_vol = data['volume'].tail(5).mean()
        ma_20_vol = volume_ma_20.iloc[-1]
        ma_50_vol = volume_ma_50.iloc[-1]
        
        if current_vol > ma_20_vol * 1.1 and ma_20_vol > ma_50_vol * 1.05:
            overall_trend = "increasing"
        elif current_vol < ma_20_vol * 0.9 and ma_20_vol < ma_50_vol * 0.95:
            overall_trend = "decreasing"
        else:
            overall_trend = "stable"
        
        # Price trend vs volume confirmation
        price_trend = "up" if data['close'].iloc[-1] > data['close'].iloc[-5] else "down"
        volume_trend = "up" if current_vol > ma_20_vol else "down"
        
        if (price_trend == "up" and volume_trend == "up") or (price_trend == "down" and volume_trend == "up"):
            volume_confirmation = "confirmed"
        elif (price_trend == "up" and volume_trend == "down") or (price_trend == "down" and volume_trend == "down"):
            volume_confirmation = "diverging"
        else:
            volume_confirmation = "neutral"
        
        # Volume momentum
        recent_acceleration = (current_vol / ma_20_vol) if ma_20_vol > 0 else 1.0
        volume_momentum = "strong" if recent_acceleration > 1.5 else "medium" if recent_acceleration > 1.2 else "weak"
        
        # Volume consistency
        volume_cv = data['volume'].tail(20).std() / data['volume'].tail(20).mean() if data['volume'].tail(20).mean() > 0 else 1.0
        volume_consistency = "high" if volume_cv < 0.5 else "medium" if volume_cv < 1.0 else "low"
        
        return {
            "overall_volume_trend": overall_trend,
            "volume_confirmation": volume_confirmation,
            "volume_momentum": volume_momentum,
            "volume_consistency": volume_consistency,
            "current_vs_ma20": round(recent_acceleration, 2)
        }
    
    @staticmethod
    def detect_volume_divergences(data: pd.DataFrame) -> Dict[str, Any]:
        """Detect volume-price divergences"""
        if len(data) < 20:
            return {"divergence_detected": False, "divergence_type": "none", 
                   "divergence_strength": "weak", "divergence_significance": "low"}
        
        # Calculate price and volume trends
        price_series = data['close'].tail(20)
        volume_series = data['volume'].tail(20)
        
        # Price trend (linear regression slope)
        x = np.arange(len(price_series))
        if HAS_SCIPY:
            price_slope, _, price_r_value, _, _ = stats.linregress(x, price_series)
            volume_slope, _, volume_r_value, _, _ = stats.linregress(x, volume_series)
        else:
            price_slope, _, price_r_value, _, _ = numpy_linregress(x, price_series)
            volume_slope, _, volume_r_value, _, _ = numpy_linregress(x, volume_series)
        
        # Detect divergence
        price_trend = "up" if price_slope > 0 else "down"
        volume_trend = "up" if volume_slope > 0 else "down"
        
        # Classic divergences
        if price_trend == "up" and volume_trend == "down":
            divergence_type = "bearish"
            divergence_detected = True
        elif price_trend == "down" and volume_trend == "up":
            divergence_type = "bullish"  # Less common but possible
            divergence_detected = True
        else:
            divergence_type = "none"
            divergence_detected = False
        
        # Divergence strength based on R-squared values
        avg_r_squared = (abs(price_r_value) + abs(volume_r_value)) / 2
        divergence_strength = "strong" if avg_r_squared > 0.6 else "medium" if avg_r_squared > 0.4 else "weak"
        
        # Significance based on slope magnitudes
        price_slope_abs = abs(price_slope / price_series.mean()) if price_series.mean() > 0 else 0
        volume_slope_abs = abs(volume_slope / volume_series.mean()) if volume_series.mean() > 0 else 0
        
        avg_slope_significance = (price_slope_abs + volume_slope_abs) / 2
        divergence_significance = "high" if avg_slope_significance > 0.02 else "medium" if avg_slope_significance > 0.01 else "low"
        
        return {
            "divergence_detected": divergence_detected,
            "divergence_type": divergence_type,
            "divergence_strength": divergence_strength,
            "divergence_significance": divergence_significance,
            "price_trend": price_trend,
            "volume_trend": volume_trend
        }
    
    @staticmethod
    def calculate_volume_based_levels(data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume-based support and resistance levels"""
        if len(data) < 50:
            return {"support_levels": [], "resistance_levels": [], 
                   "level_strength": "weak", "volume_confirmation": "neutral"}
        
        try:
            # Use volume profile to identify significant levels
            current_price = data['close'].iloc[-1]
            
            if HAS_VOLUME_PROFILE:
                volume_profile = calculate_volume_profile(data, bins=20)
                if volume_profile:
                    support_levels, resistance_levels = identify_significant_levels(
                        volume_profile, current_price, threshold_sigma=1.0
                    )
                else:
                    volume_profile = simple_volume_profile(data, bins=20)
                    support_levels, resistance_levels = simple_identify_levels(volume_profile, current_price)
            else:
                volume_profile = simple_volume_profile(data, bins=20)
                support_levels, resistance_levels = simple_identify_levels(volume_profile, current_price)
            
            # Limit to top 3 levels of each type
            support_levels = support_levels[:3]
            resistance_levels = resistance_levels[:3]
            
            # Determine level strength based on volume concentration
            if volume_profile:
                volumes = list(volume_profile.values())
                if volumes and len(volumes) > 1:
                    volume_concentration = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
                    level_strength = "strong" if volume_concentration > 0.5 else "medium" if volume_concentration > 0.3 else "weak"
                else:
                    level_strength = "weak"
            else:
                level_strength = "weak"
            
            # Volume confirmation of current price relative to levels
            if support_levels and current_price > support_levels[0]:
                volume_confirmation = "confirmed"
            elif resistance_levels and current_price < resistance_levels[0]:
                volume_confirmation = "confirmed"
            else:
                volume_confirmation = "neutral"
        
        except Exception as e:
            print(f"Warning: Volume profile calculation failed: {e}")
            support_levels, resistance_levels = [], []
            level_strength = "weak"
            volume_confirmation = "neutral"
        
        return {
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "level_strength": level_strength,
            "volume_confirmation": volume_confirmation
        }
    
    @staticmethod
    def analyze_institutional_activity(data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze institutional activity patterns"""
        if len(data) < 20:
            return {"activity_level": "low", "activity_pattern": "neutral", 
                   "institutional_sentiment": "neutral", "activity_significance": "low"}
        
        # Large volume days (institutional activity indicators)
        volume_ma = data['volume'].rolling(window=20).mean()
        volume_std = data['volume'].rolling(window=20).std()
        
        # Identify large volume days (2+ standard deviations above mean)
        large_volume_days = data[data['volume'] > (volume_ma + 2 * volume_std)]
        
        # Activity level based on frequency of large volume days
        activity_ratio = len(large_volume_days) / len(data) if len(data) > 0 else 0
        activity_level = "high" if activity_ratio > 0.1 else "medium" if activity_ratio > 0.05 else "low"
        
        # Analyze price movement on large volume days
        if len(large_volume_days) > 0:
            avg_price_change = large_volume_days['close'].pct_change().mean()
            
            # Determine if accumulation or distribution
            if avg_price_change > 0.01:  # 1% average gain on high volume
                activity_pattern = "accumulation"
                institutional_sentiment = "bullish"
            elif avg_price_change < -0.01:  # 1% average loss on high volume
                activity_pattern = "distribution"
                institutional_sentiment = "bearish"
            else:
                activity_pattern = "neutral"
                institutional_sentiment = "neutral"
        else:
            activity_pattern = "neutral"
            institutional_sentiment = "neutral"
        
        # Activity significance based on volume magnitude and consistency
        if len(large_volume_days) >= 3:
            avg_volume_multiple = (large_volume_days['volume'] / volume_ma).mean()
            activity_significance = "high" if avg_volume_multiple > 3 else "medium" if avg_volume_multiple > 2 else "low"
        else:
            activity_significance = "low"
        
        return {
            "activity_level": activity_level,
            "activity_pattern": activity_pattern,
            "institutional_sentiment": institutional_sentiment,
            "activity_significance": activity_significance,
            "large_volume_days": len(large_volume_days)
        }
    
    @classmethod
    def calculate_comprehensive_volume_indicators(cls, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all volume indicators needed for the volume analysis prompt"""
        if len(data) < 10:
            return {"error": "Insufficient data for volume analysis", "min_required": 10, "available": len(data)}
        
        # Ensure data has required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return {"error": f"Missing required columns: {missing_columns}"}
        
        # Calculate all volume analysis components
        volume_anomalies = cls.calculate_volume_anomalies(data)
        price_volume_correlation = cls.calculate_price_volume_correlation(data)
        volume_trends = cls.analyze_volume_trends(data)
        volume_divergences = cls.detect_volume_divergences(data)
        volume_based_levels = cls.calculate_volume_based_levels(data)
        institutional_activity = cls.analyze_institutional_activity(data)
        
        # Basic volume metrics
        current_volume = data['volume'].iloc[-1]
        volume_ma_20 = data['volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = current_volume / volume_ma_20 if volume_ma_20 > 0 else 1.0
        
        # VWAP calculation
        try:
            if HAS_VOLUME_PROFILE:
                vwap_series = calculate_vwap(data)
                current_vwap = vwap_series.iloc[-1] if not vwap_series.empty else data['close'].iloc[-1]
            else:
                vwap_series = simple_vwap(data)
                current_vwap = vwap_series.iloc[-1] if not vwap_series.empty else data['close'].iloc[-1]
        except Exception:
            current_vwap = data['close'].iloc[-1]
        
        # Recent price and volume data for context
        recent_data = {
            "recent_prices": data['close'].tail(10).tolist(),
            "recent_volumes": data['volume'].tail(10).tolist(),
            "recent_dates": [d.strftime('%Y-%m-%d') for d in data.index[-10:]]
        }
        
        return {
            # Core volume metrics
            "current_volume": int(current_volume),
            "volume_ma_20": int(volume_ma_20) if volume_ma_20 > 0 else 0,
            "volume_ratio": round(volume_ratio, 2),
            "current_price": round(data['close'].iloc[-1], 2),
            "current_vwap": round(current_vwap, 2),
            
            # Analysis components
            "volume_anomalies": volume_anomalies,
            "price_volume_correlation": price_volume_correlation,
            "volume_trends": volume_trends,
            "volume_divergences": volume_divergences,
            "volume_based_levels": volume_based_levels,
            "institutional_activity": institutional_activity,
            
            # Context data
            "recent_data": recent_data,
            "analysis_period": f"{len(data)} days",
            "data_quality": "good" if current_volume > 0 else "poor"
        }

class MultiStockVolumeTester:
    """Test volume analysis prompt across multiple stocks"""
    
    def __init__(self):
        # Initialize Zerodha client
        try:
            self.zerodha_client = ZerodhaDataClient()
            print("✅ Zerodha client initialized")
        except Exception as e:
            print(f"❌ Cannot initialize Zerodha client: {e}")
            sys.exit(1)
        
        # Initialize other components
        self.calculator = VolumeIndicatorCalculator()
        self.prompt_manager = PromptManager()
        self.context_engineer = ContextEngineer()
        
        # Initialize Gemini client if API key is available
        self.gemini_client = None
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                self.gemini_client = GeminiClient(api_key=api_key)
                print("✅ Gemini API client initialized")
            else:
                print("⚠️  GEMINI_API_KEY not found - will show prompts only")
        except Exception as e:
            print(f"⚠️  Could not initialize Gemini client: {e}")
        
        # Define test stocks with volume characteristics
        self.test_stocks = [
            StockTestConfig("RELIANCE", "Reliance Industries", "Energy/Petrochemicals", "large_cap_stable", "high_liquidity"),
            StockTestConfig("TCS", "Tata Consultancy Services", "IT Services", "large_cap_growth", "consistent_volume"),
            StockTestConfig("HDFCBANK", "HDFC Bank", "Banking", "large_cap_stable", "high_liquidity"),
            StockTestConfig("ICICIBANK", "ICICI Bank", "Banking", "large_cap_volatile", "volatile_volume"),
            StockTestConfig("ITC", "ITC Limited", "FMCG/Tobacco", "large_cap_defensive", "steady_volume"),
            # Additional stocks with different volume patterns
            StockTestConfig("INFY", "Infosys", "IT Services", "large_cap_stable", "consistent_volume"),
            StockTestConfig("BHARTIARTL", "Bharti Airtel", "Telecommunications", "large_cap_cyclical", "moderate_volume"),
            StockTestConfig("HINDUNILVR", "Hindustan Unilever", "FMCG", "large_cap_defensive", "low_volume"),
        ]
        
        self.results = []
    
    async def run_multi_stock_volume_tests(self):
        """Run volume analysis tests across all configured stocks"""
        print(f"🔊 Starting Multi-Stock Volume Analysis Testing")
        print(f"Testing {len(self.test_stocks)} stocks with 365 days of data")
        print("Focus: Volume anomalies, correlations, trends, and institutional activity")
        print("=" * 80)
        
        # Authenticate with Zerodha first
        print("🔗 Authenticating with Zerodha...")
        if not self.zerodha_client.authenticate():
            print("❌ Zerodha authentication failed")
            return False
        
        print("✅ Zerodha authentication successful")
        
        # Create results directory with organized structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f"volume_analysis_test_results_{timestamp}"
        os.makedirs(results_dir, exist_ok=True)
        
        # Create subdirectories for different types of files
        charts_dir = os.path.join(results_dir, "charts")
        prompts_dir = os.path.join(results_dir, "prompts")
        responses_dir = os.path.join(results_dir, "responses")
        reports_dir = os.path.join(results_dir, "reports")
        
        os.makedirs(charts_dir, exist_ok=True)
        os.makedirs(prompts_dir, exist_ok=True)
        os.makedirs(responses_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)
        
        print(f"📁 Results will be saved to: {results_dir}")
        print(f"   📊 Charts: {charts_dir}")
        print(f"   📝 Prompts: {prompts_dir}")
        print(f"   💬 Responses: {responses_dir}")
        print(f"   📋 Reports: {reports_dir}")
        
        # Create async tasks for all stocks
        async def test_single_stock(stock_config, stock_index):
            """Test volume analysis for a single stock"""
            print(f"\n📊 Testing Volume Analysis {stock_index}/{len(self.test_stocks)}: {stock_config.symbol}")
            print(f"   Company: {stock_config.name}")
            print(f"   Sector: {stock_config.sector}")
            print(f"   Volume Characteristics: {stock_config.volume_characteristics}")
            print("-" * 60)
            
            try:
                # Get stock data
                print(f"📈 Fetching 365 days of data for {stock_config.symbol}...")
                
                # Use async version if available
                if hasattr(self.zerodha_client, 'get_historical_data_async'):
                    stock_data = await self.zerodha_client.get_historical_data_async(
                        symbol=stock_config.symbol,
                        exchange="NSE",
                        interval="day",
                        period=365
                    )
                else:
                    # Fallback to sync version in executor
                    loop = asyncio.get_event_loop()
                    stock_data = await loop.run_in_executor(
                        None,
                        self.zerodha_client.get_historical_data,
                        stock_config.symbol,
                        "NSE",
                        "day",
                        None,
                        None,
                        365
                    )
                
                if stock_data is None or stock_data.empty:
                    print(f"❌ No data available for {stock_config.symbol}")
                    return self._create_error_result(stock_config, 'No data available', 0)
                
                # Ensure we have the right columns
                required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                
                # Handle date index/column
                if 'date' not in stock_data.columns and stock_data.index.name == 'date':
                    stock_data = stock_data.reset_index()
                elif 'date' not in stock_data.columns:
                    stock_data['date'] = stock_data.index
                    stock_data = stock_data.reset_index(drop=True)
                
                # Check for missing columns
                missing_columns = [col for col in required_columns if col not in stock_data.columns]
                if missing_columns:
                    print(f"❌ Missing required columns for {stock_config.symbol}: {missing_columns}")
                    return self._create_error_result(stock_config, f'Missing columns: {missing_columns}', 0)
                
                # Set date as index for calculations
                stock_data = stock_data.set_index('date').sort_index()
                
                print(f"✅ Retrieved {len(stock_data)} days of data")
                print(f"   Date range: {stock_data.index.min()} to {stock_data.index.max()}")
                print(f"   Price range: ₹{stock_data['close'].min():.2f} to ₹{stock_data['close'].max():.2f}")
                print(f"   Volume range: {stock_data['volume'].min():,} to {stock_data['volume'].max():,}")
                
                # Calculate volume indicators
                print("📊 Calculating volume analysis indicators...")
                volume_indicators = self.calculator.calculate_comprehensive_volume_indicators(stock_data)
                
                if 'error' in volume_indicators:
                    print(f"❌ Volume calculation error: {volume_indicators['error']}")
                    return self._create_error_result(stock_config, volume_indicators['error'], 0)
                
                # Generate volume analysis chart
                print("📊 Generating volume analysis chart...")
                volume_chart = self._generate_volume_analysis_chart(stock_data, volume_indicators, stock_config, charts_dir)
                
                if volume_chart is None:
                    print("⚠️  Volume chart generation failed - proceeding without chart")
                
                # Test the volume analysis prompt (with chart if available)
                test_dirs = {
                    'base': results_dir,
                    'charts': charts_dir,
                    'prompts': prompts_dir,
                    'responses': responses_dir,
                    'reports': reports_dir
                }
                result = await self._test_volume_analysis_prompt(stock_config, volume_indicators, test_dirs, volume_chart)
                
                print(f"✅ Volume analysis test completed for {stock_config.symbol}")
                print(f"   Success: {result['success']}")
                print(f"   Quality Score: {result['quality_score']:.1f}/100")
                print(f"   Response Time: {result['execution_time']:.1f}s")
                
                return result
                
            except Exception as e:
                print(f"❌ Error testing {stock_config.symbol}: {e}")
                import traceback
                traceback.print_exc()
                return self._create_error_result(stock_config, str(e), 0)
        
        # Run all stock tests with controlled concurrency
        semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent tests for volume analysis
        
        async def test_with_semaphore(stock_config, index):
            async with semaphore:
                return await test_single_stock(stock_config, index)
        
        # Create tasks for all stocks
        tasks = [
            test_with_semaphore(stock_config, i + 1)
            for i, stock_config in enumerate(self.test_stocks)
        ]
        
        # Wait for all tasks to complete
        print(f"\n🔄 Running {len(tasks)} volume analysis tests concurrently (max 2 at a time)...")
        results = await asyncio.gather(*tasks)
        self.results.extend(results)
        
        # Generate comprehensive report
        self._generate_volume_analysis_report(reports_dir, results)
        
        print(f"\n✅ Multi-stock volume analysis testing completed!")
        print(f"📁 Results saved to: {results_dir}/")
        
        return True
    
    def _create_error_result(self, stock_config: StockTestConfig, error: str, execution_time: float) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            'stock_config': stock_config,
            'success': False,
            'error': error,
            'execution_time': execution_time,
            'quality_score': 0,
            'data_quality': 'error'
        }
    
    def _format_volume_analysis_context(self, curated_indicators: Dict[str, Any], 
                                      stock_config: StockTestConfig, 
                                      volume_indicators: Dict[str, Any]) -> str:
        """Format comprehensive volume analysis context for the LLM prompt"""
        
        # Extract key components
        technical_context = curated_indicators.get("technical_context", {})
        volume_metrics = curated_indicators.get("volume_metrics", {})
        
        # Build comprehensive context string
        context_parts = []
        
        # Header
        context_parts.append(f"## Volume Analysis Context:")
        context_parts.append(f"**Stock**: {stock_config.symbol} ({stock_config.name})")
        context_parts.append(f"**Sector**: {stock_config.sector}")
        context_parts.append(f"**Volume Characteristics**: {stock_config.volume_characteristics}")
        context_parts.append(f"**Analysis Focus**: {curated_indicators.get('analysis_focus', 'volume_analysis')}")
        context_parts.append("")
        
        # Technical Context
        context_parts.append("## Technical Context:")
        if technical_context:
            context_parts.append(f"- **Current Price**: ₹{technical_context.get('current_price', 0):.2f}")
            context_parts.append(f"- **Current VWAP**: ₹{technical_context.get('current_vwap', 0):.2f}")
            context_parts.append(f"- **Analysis Period**: {technical_context.get('analysis_period', 'N/A')}")
            context_parts.append(f"- **Data Quality**: {technical_context.get('data_quality', 'N/A')}")
        else:
            context_parts.append("- No technical context available")
        context_parts.append("")
        
        # Volume Metrics
        context_parts.append("## Volume Metrics:")
        if volume_metrics:
            context_parts.append(f"- **Current Volume**: {volume_metrics.get('current_volume', 0):,}")
            context_parts.append(f"- **20-Day Volume MA**: {volume_metrics.get('volume_ma_20', 0):,}")
            context_parts.append(f"- **Volume Ratio**: {volume_metrics.get('volume_ratio', 1.0):.2f}x")
            
            # Volume Anomalies
            anomalies = volume_metrics.get('volume_anomalies', {})
            if anomalies:
                context_parts.append(f"- **Volume Anomalies**: {len(anomalies.get('unusual_spikes', []))} recent spikes")
                context_parts.append(f"- **Anomaly Frequency**: {anomalies.get('anomaly_frequency', 'unknown')}")
                context_parts.append(f"- **Volume Patterns**: {', '.join(anomalies.get('volume_patterns', []))}")
            
            # Price-Volume Correlation
            correlation = volume_metrics.get('price_volume_correlation', {})
            if correlation:
                context_parts.append(f"- **Price-Volume Correlation**: {correlation.get('correlation_strength', 0):.3f} ({correlation.get('correlation_direction', 'neutral')})")
                context_parts.append(f"- **Correlation Significance**: {correlation.get('correlation_significance', 'unknown')}")
                context_parts.append(f"- **Correlation Trend**: {correlation.get('correlation_trend', 'unknown')}")
            
            # Volume Trends
            trends = volume_metrics.get('volume_trends', {})
            if trends:
                context_parts.append(f"- **Overall Volume Trend**: {trends.get('overall_volume_trend', 'unknown')}")
                context_parts.append(f"- **Volume Confirmation**: {trends.get('volume_confirmation', 'unknown')}")
                context_parts.append(f"- **Volume Momentum**: {trends.get('volume_momentum', 'unknown')}")
                context_parts.append(f"- **Volume Consistency**: {trends.get('volume_consistency', 'unknown')}")
            
            # Volume Divergences
            divergences = volume_metrics.get('volume_divergences', {})
            if divergences:
                detected = divergences.get('divergence_detected', False)
                context_parts.append(f"- **Volume Divergence**: {'Detected' if detected else 'None detected'}")
                if detected:
                    context_parts.append(f"- **Divergence Type**: {divergences.get('divergence_type', 'unknown')}")
                    context_parts.append(f"- **Divergence Strength**: {divergences.get('divergence_strength', 'unknown')}")
            
            # Volume-Based Levels
            levels = volume_metrics.get('volume_based_levels', {})
            if levels:
                support_levels = levels.get('support_levels', [])
                resistance_levels = levels.get('resistance_levels', [])
                context_parts.append(f"- **Volume-Based Support**: {len(support_levels)} levels identified")
                context_parts.append(f"- **Volume-Based Resistance**: {len(resistance_levels)} levels identified")
                context_parts.append(f"- **Level Strength**: {levels.get('level_strength', 'unknown')}")
            
            # Institutional Activity
            institutional = volume_metrics.get('institutional_activity', {})
            if institutional:
                context_parts.append(f"- **Institutional Activity**: {institutional.get('activity_level', 'unknown')} level")
                context_parts.append(f"- **Activity Pattern**: {institutional.get('activity_pattern', 'unknown')}")
                context_parts.append(f"- **Institutional Sentiment**: {institutional.get('institutional_sentiment', 'unknown')}")
        else:
            context_parts.append("- No volume metrics available")
        context_parts.append("")
        
        # Recent Data Context
        recent_data = volume_metrics.get('recent_data', {})
        if recent_data:
            recent_prices = recent_data.get('recent_prices', [])
            recent_volumes = recent_data.get('recent_volumes', [])
            recent_dates = recent_data.get('recent_dates', [])
            
            if recent_prices and len(recent_prices) >= 5:
                context_parts.append("## Recent Market Activity:")
                context_parts.append(f"- **Recent Price Range**: ₹{min(recent_prices[-5:]):.2f} - ₹{max(recent_prices[-5:]):.2f}")
                context_parts.append(f"- **Recent Volume Range**: {min(recent_volumes[-5:]):,} - {max(recent_volumes[-5:]):,}")
                
                # Price and volume trends
                if len(recent_prices) >= 3:
                    recent_price_trend = "increasing" if recent_prices[-1] > recent_prices[-3] else "decreasing"
                    recent_volume_trend = "increasing" if recent_volumes[-1] > recent_volumes[-3] else "decreasing"
                    context_parts.append(f"- **Recent Price Trend**: {recent_price_trend}")
                    context_parts.append(f"- **Recent Volume Trend**: {recent_volume_trend}")
                context_parts.append("")
        
        # Analysis Questions
        questions = curated_indicators.get("specific_questions", [])
        if questions:
            context_parts.append("## Specific Analysis Questions:")
            for question in questions:
                context_parts.append(f"- {question}")
            context_parts.append("")
        
        # Analysis Instructions
        context_parts.append("## Analysis Instructions:")
        context_parts.append("1. Analyze volume patterns in relation to price movements")
        context_parts.append("2. Identify volume confirmation or divergence signals")
        context_parts.append("3. Determine volume-based support/resistance levels")
        context_parts.append("4. Assess institutional activity and sentiment")
        context_parts.append("5. Evaluate overall volume trend implications")
        context_parts.append("6. Provide risk assessment for volume-based signals")
        
        return "\n".join(context_parts)
    def _generate_volume_analysis_chart(self, data: pd.DataFrame, 
                                       volume_indicators: Dict[str, Any], 
                                       stock_config: StockTestConfig,
                                       charts_dir: str) -> Optional[bytes]:
        """Generate comprehensive volume analysis chart for the LLM"""
        try:
            # Set matplotlib backend to Agg for headless operation
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from matplotlib.patches import Rectangle
            import io
            
            # Set up the figure with multiple subplots for comprehensive volume analysis
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(4, 2, height_ratios=[2, 1, 1, 1], hspace=0.3, wspace=0.2)
            
            # Color scheme
            colors = {
                'price': '#2E86AB',
                'volume': '#A23B72',
                'volume_ma': '#F18F01', 
                'anomaly': '#C73E1D',
                'support': '#4CAF50',
                'resistance': '#F44336',
                'vwap': '#9C27B0'
            }
            
            # 1. Main Price and Volume Chart (top section)
            ax1 = fig.add_subplot(gs[0, :])
            
            # Plot price
            ax1.plot(data.index, data['close'], color=colors['price'], linewidth=2, label='Price', alpha=0.8)
            
            # Add VWAP if available
            current_vwap = volume_indicators.get('current_vwap')
            if current_vwap and current_vwap > 0:
                ax1.axhline(y=current_vwap, color=colors['vwap'], linestyle='--', 
                           linewidth=1.5, alpha=0.7, label=f'VWAP (₹{current_vwap:.2f})')
            
            # Add volume-based support/resistance levels
            levels = volume_indicators.get('volume_based_levels', {})
            support_levels = levels.get('support_levels', [])
            resistance_levels = levels.get('resistance_levels', [])
            
            for i, level in enumerate(support_levels[:3]):
                ax1.axhline(y=level, color=colors['support'], linestyle='-', alpha=0.6, 
                           linewidth=1, label='Support' if i == 0 else '')
            
            for i, level in enumerate(resistance_levels[:3]):
                ax1.axhline(y=level, color=colors['resistance'], linestyle='-', alpha=0.6, 
                           linewidth=1, label='Resistance' if i == 0 else '')
            
            # Highlight volume anomalies on price chart
            anomalies = volume_indicators.get('volume_anomalies', {}).get('unusual_spikes', [])
            for anomaly in anomalies[-10:]:  # Show last 10 anomalies
                try:
                    anomaly_date = pd.to_datetime(anomaly['date'])
                    if anomaly_date in data.index:
                        price_at_anomaly = data.loc[anomaly_date, 'close']
                        significance = anomaly.get('significance', 'low')
                        marker_size = 150 if significance == 'high' else 100 if significance == 'medium' else 60
                        ax1.scatter(anomaly_date, price_at_anomaly, color=colors['anomaly'], 
                                   s=marker_size, alpha=0.8, marker='^', edgecolors='white', linewidth=1,
                                   label='Volume Spike' if anomaly == anomalies[0] else '')
                except:
                    continue
            
            ax1.set_title(f'{stock_config.symbol} - Comprehensive Volume Analysis\n' + 
                         f'{stock_config.name} ({stock_config.volume_characteristics})', fontsize=14, pad=20)
            ax1.set_ylabel('Price (₹)', fontsize=12)
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(True, alpha=0.3)
            
            # 2. Volume with Moving Average (second row)
            ax2 = fig.add_subplot(gs[1, :])
            
            # Calculate volume moving average for display
            volume_ma_20 = data['volume'].rolling(window=20).mean()
            
            # Plot volume bars
            volume_colors = [colors['anomaly'] if pd.to_datetime(date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)[:10]) in 
                            [pd.to_datetime(a['date']) for a in anomalies] else colors['volume'] 
                            for date in data.index]
            
            ax2.bar(data.index, data['volume'], color=volume_colors, alpha=0.7, width=0.8)
            ax2.plot(data.index, volume_ma_20, color=colors['volume_ma'], linewidth=2, 
                    label=f'Volume MA(20): {volume_indicators.get("volume_ma_20", 0):,}')
            
            # Add current volume ratio text
            volume_ratio = volume_indicators.get('volume_ratio', 1.0)
            ax2.text(0.02, 0.98, f'Current Volume Ratio: {volume_ratio:.2f}x', 
                    transform=ax2.transAxes, fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.legend(loc='upper right', fontsize=10)
            ax2.grid(True, alpha=0.3)
            
            # 3. Price-Volume Correlation Analysis (third row, left)
            ax3 = fig.add_subplot(gs[2, 0])
            
            correlation_data = volume_indicators.get('price_volume_correlation', {})
            corr_strength = correlation_data.get('correlation_strength', 0)
            corr_direction = correlation_data.get('correlation_direction', 'neutral')
            corr_significance = correlation_data.get('correlation_significance', 'low')
            
            # Create correlation visualization
            if len(data) >= 20:
                price_changes = data['close'].pct_change().dropna()
                volume_changes = data['volume'].pct_change().dropna()
                
                min_len = min(len(price_changes), len(volume_changes))
                if min_len >= 10:
                    recent_price = price_changes.tail(min_len)
                    recent_volume = volume_changes.tail(min_len)
                    
                    ax3.scatter(recent_price, recent_volume, alpha=0.6, color=colors['volume'])
                    
                    # Add trend line if correlation is significant
                    if abs(corr_strength) > 0.3:
                        z = np.polyfit(recent_price, recent_volume, 1)
                        p = np.poly1d(z)
                        ax3.plot(recent_price, p(recent_price), color=colors['anomaly'], linestyle='--', alpha=0.8)
            
            ax3.set_title(f'Price-Volume Correlation\nStrength: {corr_strength:.3f} ({corr_direction})', fontsize=11)
            ax3.set_xlabel('Price Change %', fontsize=10)
            ax3.set_ylabel('Volume Change %', fontsize=10)
            ax3.grid(True, alpha=0.3)
            
            # 4. Volume Trends and Institutional Activity (third row, right)
            ax4 = fig.add_subplot(gs[2, 1])
            
            volume_trends = volume_indicators.get('volume_trends', {})
            institutional = volume_indicators.get('institutional_activity', {})
            
            # Create text-based summary
            trend_text = f"Volume Trend: {volume_trends.get('overall_volume_trend', 'unknown')}"
            momentum_text = f"Momentum: {volume_trends.get('volume_momentum', 'unknown')}"
            confirmation_text = f"Confirmation: {volume_trends.get('volume_confirmation', 'unknown')}"
            institutional_text = f"Institutional: {institutional.get('activity_level', 'unknown')} ({institutional.get('activity_pattern', 'unknown')})"
            
            ax4.text(0.05, 0.85, trend_text, transform=ax4.transAxes, fontsize=11, fontweight='bold')
            ax4.text(0.05, 0.70, momentum_text, transform=ax4.transAxes, fontsize=10)
            ax4.text(0.05, 0.55, confirmation_text, transform=ax4.transAxes, fontsize=10)
            ax4.text(0.05, 0.40, institutional_text, transform=ax4.transAxes, fontsize=10)
            
            # Add divergence info if detected
            divergences = volume_indicators.get('volume_divergences', {})
            if divergences.get('divergence_detected', False):
                div_text = f"⚠️ Divergence: {divergences.get('divergence_type', 'unknown')}"
                ax4.text(0.05, 0.25, div_text, transform=ax4.transAxes, fontsize=10, 
                        color=colors['anomaly'], fontweight='bold')
            
            ax4.set_title('Volume Analysis Summary', fontsize=11)
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
            ax4.axis('off')
            
            # 5. Recent Volume Activity (bottom section)
            ax5 = fig.add_subplot(gs[3, :])
            
            # Show recent 30 days volume with anomalies highlighted
            recent_data = data.tail(30)
            recent_volume_ma = recent_data['volume'].rolling(window=5).mean()
            
            bars = ax5.bar(recent_data.index, recent_data['volume'], 
                          color=[colors['anomaly'] if pd.to_datetime(date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)[:10]) in 
                                [pd.to_datetime(a['date']) for a in anomalies] else colors['volume'] 
                                for date in recent_data.index], alpha=0.7)
            
            ax5.plot(recent_data.index, recent_volume_ma, color=colors['volume_ma'], 
                    linewidth=2, label='Volume MA(5)')
            
            ax5.set_title('Recent 30-Day Volume Activity (Anomalies in Red)', fontsize=11)
            ax5.set_ylabel('Volume', fontsize=10)
            ax5.legend(loc='upper right', fontsize=9)
            ax5.grid(True, alpha=0.3)
            
            # Format x-axis dates
            ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax5.xaxis.set_major_locator(mdates.WeekdayLocator())
            plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
            
            # Add overall analysis summary as text
            summary_text = (f"Analysis Period: {volume_indicators.get('analysis_period', 'unknown')} | "
                          f"Data Quality: {volume_indicators.get('data_quality', 'unknown')} | "
                          f"Anomalies: {len(anomalies)} detected | "
                          f"Correlation: {corr_strength:.3f} ({corr_significance})")
            
            fig.suptitle(summary_text, fontsize=10, y=0.02, alpha=0.7)
            
            # Convert to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            chart_bytes = buf.getvalue()
            buf.close()
            
            # Save chart to organized charts directory
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                chart_filename = f"volume_chart_{stock_config.symbol}_{timestamp}.png"
                chart_file_path = os.path.join(charts_dir, chart_filename)
                
                with open(chart_file_path, 'wb') as f:
                    f.write(chart_bytes)
                print(f"✓ Generated volume analysis chart: {len(chart_bytes)} bytes")
                print(f"  💾 Saved to: charts/{chart_filename}")
            except Exception as save_error:
                print(f"✓ Generated volume analysis chart: {len(chart_bytes)} bytes (could not save file: {save_error})")
            
            plt.close(fig)
            return chart_bytes
            
        except Exception as e:
            print(f"❌ Volume chart generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _test_volume_analysis_prompt(self, stock_config: StockTestConfig, 
                                         volume_indicators: Dict[str, Any], 
                                         test_dirs: Dict[str, str], 
                                         volume_chart: Optional[bytes] = None) -> Dict[str, Any]:
        """Test the volume analysis prompt for a single stock"""
        start_time = time.time()
        
        try:
            # Structure the volume indicators in a format that the context engineer expects
            # and also include the comprehensive volume analysis data
            structured_indicators = {
                # Add the comprehensive volume data directly
                "volume_analysis": volume_indicators,
                
                # Add basic price/volume arrays for context engineer compatibility
                "close": volume_indicators.get("recent_data", {}).get("recent_prices", []),
                "volume": volume_indicators.get("recent_data", {}).get("recent_volumes", []),
                "current_volume": volume_indicators.get("current_volume", 0),
                "volume_ratio": volume_indicators.get("volume_ratio", 1.0),
                "current_price": volume_indicators.get("current_price", 0),
            }
            
            # Apply context engineering for volume analysis
            curated_indicators = self.context_engineer.curate_indicators(
                structured_indicators, 
                AnalysisType.VOLUME_ANALYSIS
            )
            
            # If the context engineer returns empty data, use our comprehensive structure directly
            if not curated_indicators.get("volume_metrics") or not curated_indicators.get("technical_context"):
                # Create our own comprehensive volume context
                curated_indicators = {
                    "analysis_focus": "comprehensive_volume_analysis",
                    "technical_context": {
                        "current_price": volume_indicators.get("current_price", 0),
                        "current_vwap": volume_indicators.get("current_vwap", 0),
                        "analysis_period": volume_indicators.get("analysis_period", "unknown"),
                        "data_quality": volume_indicators.get("data_quality", "unknown")
                    },
                    "volume_metrics": {
                        "current_volume": volume_indicators.get("current_volume", 0),
                        "volume_ma_20": volume_indicators.get("volume_ma_20", 0),
                        "volume_ratio": volume_indicators.get("volume_ratio", 1.0),
                        "volume_anomalies": volume_indicators.get("volume_anomalies", {}),
                        "price_volume_correlation": volume_indicators.get("price_volume_correlation", {}),
                        "volume_trends": volume_indicators.get("volume_trends", {}),
                        "volume_divergences": volume_indicators.get("volume_divergences", {}),
                        "volume_based_levels": volume_indicators.get("volume_based_levels", {}),
                        "institutional_activity": volume_indicators.get("institutional_activity", {}),
                        "recent_data": volume_indicators.get("recent_data", {})
                    },
                    "specific_questions": [
                        "Are volume spikes confirming price movements?",
                        "Is there volume divergence indicating trend weakness?",
                        "What are the key volume-based support/resistance levels?",
                        "What does institutional activity suggest?",
                        "How reliable are the volume-based signals?"
                    ]
                }
            
            # Create detailed volume analysis context
            context = self._format_volume_analysis_context(
                curated_indicators, 
                stock_config, 
                volume_indicators
            )
            
            # Format the volume analysis prompt
            prompt = self.prompt_manager.format_prompt(
                "optimized_volume_analysis",
                context=context
            )
            prompt += self.prompt_manager.SOLVING_LINE
            
            # Save detailed prompt analysis to organized prompts directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            prompt_filename = f"volume_prompt_{stock_config.symbol}_{timestamp}.txt"
            prompt_file = os.path.join(test_dirs['prompts'], prompt_filename)
            with open(prompt_file, 'w') as f:
                f.write("VOLUME ANALYSIS PROMPT FOR LLM\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Stock Symbol: {stock_config.symbol}\n")
                f.write(f"Company: {stock_config.name}\n")
                f.write(f"Sector: {stock_config.sector}\n")
                f.write(f"Volume Characteristics: {stock_config.volume_characteristics}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Prompt Length: {len(prompt)} characters\n")
                f.write(f"Context Length: {len(context)} characters\n\n")
                
                f.write("KEY VOLUME ANALYSIS INDICATORS:\n")
                f.write("-" * 40 + "\n")
                volume_summary = {
                    "current_volume": volume_indicators.get('current_volume', 0),
                    "volume_ratio": volume_indicators.get('volume_ratio', 1.0),
                    "volume_anomalies": len(volume_indicators.get('volume_anomalies', {}).get('unusual_spikes', [])),
                    "price_volume_correlation": volume_indicators.get('price_volume_correlation', {}).get('correlation_strength', 0),
                    "volume_trend": volume_indicators.get('volume_trends', {}).get('overall_volume_trend', 'stable'),
                    "institutional_activity": volume_indicators.get('institutional_activity', {}).get('activity_level', 'low'),
                    "volume_confirmation": volume_indicators.get('volume_trends', {}).get('volume_confirmation', 'neutral'),
                    "divergence_detected": volume_indicators.get('volume_divergences', {}).get('divergence_detected', False)
                }
                f.write(json.dumps(volume_summary, indent=2, default=str))
                f.write("\n\nFINAL VOLUME ANALYSIS PROMPT:\n")
                f.write("-" * 40 + "\n")
                f.write(prompt)
            
            # Make API call if available
            llm_response = ""
            response = ""  # Initialize response variable
            code_results = None
            execution_results = None
            response_filename = None  # Initialize response filename
            
            if self.gemini_client:
                try:
                    print(f"🚀 Making volume analysis API call for {stock_config.symbol}...")
                    
                    if volume_chart:
                        # Use the proper volume analysis method with chart image
                        print(f"   Using volume chart: {len(volume_chart)} bytes")
                        llm_response = await self.gemini_client.analyze_volume_analysis(volume_chart, structured_indicators)
                        response = llm_response  # Set response for file writing compatibility
                    else:
                        # Fallback to text-only analysis (less optimal)
                        print("   No volume chart available - using text-only analysis")
                        response, code_results, execution_results = await self.gemini_client.core.call_llm_with_code_execution(prompt)
                        llm_response = response
                    
                    # Save response to organized responses directory
                    response_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    response_filename = f"volume_response_{stock_config.symbol}_{response_timestamp}.txt"
                    response_file = os.path.join(test_dirs['responses'], response_filename)
                    with open(response_file, 'w') as f:
                        f.write("VOLUME ANALYSIS LLM RESPONSE\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(f"Stock Symbol: {stock_config.symbol}\n")
                        f.write(f"Company: {stock_config.name}\n")
                        f.write(f"Sector: {stock_config.sector}\n")
                        f.write(f"Response Time: {datetime.now().isoformat()}\n")
                        f.write(f"Response Length: {len(response) if response else 0} characters\n")
                        if code_results:
                            f.write(f"Code Executions: {len(code_results)}\n")
                        if execution_results:
                            f.write(f"Calculation Results: {len(execution_results)}\n")
                        f.write("\nCOMPLETE VOLUME ANALYSIS RESPONSE:\n")
                        f.write("-" * 40 + "\n")
                        f.write(response or "No response received")
                        
                        # Parse JSON response if possible
                        try:
                            json_response = json.loads(response)
                            f.write("\n\nPARSED JSON RESPONSE:\n")
                            f.write("-" * 40 + "\n")
                            f.write(json.dumps(json_response, indent=2))
                        except:
                            f.write("\n\n(Response is not valid JSON)")
                    
                except Exception as e:
                    print(f"❌ API call failed for {stock_config.symbol}: {e}")
                    llm_response = f"API_ERROR: {str(e)}"
            
            execution_time = time.time() - start_time
            
            # Evaluate volume analysis quality
            quality_metrics = self._evaluate_volume_analysis_quality(stock_config, volume_indicators, llm_response)
            
            # Track generated files
            generated_files = {
                'prompt_file': prompt_filename,
                'chart_file': f"volume_chart_{stock_config.symbol}_{timestamp}.png" if volume_chart else None,
                'response_file': response_filename if llm_response and not llm_response.startswith("API_ERROR") else None
            }
            
            return {
                'stock_config': stock_config,
                'success': True,
                'execution_time': execution_time,
                'quality_score': quality_metrics['overall_score'],
                'data_quality': quality_metrics['data_quality'],
                'response_length': len(llm_response) if llm_response else 0,
                'volume_metrics': {
                    'volume_ratio': volume_indicators.get('volume_ratio', 1.0),
                    'anomalies_count': len(volume_indicators.get('volume_anomalies', {}).get('unusual_spikes', [])),
                    'correlation_strength': volume_indicators.get('price_volume_correlation', {}).get('correlation_strength', 0),
                    'institutional_activity': volume_indicators.get('institutional_activity', {}).get('activity_level', 'low'),
                    'divergence_detected': volume_indicators.get('volume_divergences', {}).get('divergence_detected', False)
                },
                'quality_metrics': quality_metrics,
                'has_llm_response': bool(llm_response and not llm_response.startswith("API_ERROR")),
                'generated_files': generated_files
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_error_result(stock_config, str(e), execution_time)
    
    def _evaluate_volume_analysis_quality(self, stock_config: StockTestConfig, 
                                        volume_indicators: Dict[str, Any], 
                                        llm_response: str) -> Dict[str, Any]:
        """Evaluate the quality of volume analysis"""
        metrics = {
            'data_quality': 'unknown',
            'volume_data_completeness': 0,
            'analysis_depth': 0,
            'response_quality': 0,
            'volume_insight_quality': 0,
            'overall_score': 0
        }
        
        # Evaluate volume data completeness
        volume_components = ['volume_anomalies', 'price_volume_correlation', 'volume_trends', 'institutional_activity']
        available_components = sum(1 for comp in volume_components if comp in volume_indicators and volume_indicators[comp])
        metrics['volume_data_completeness'] = (available_components / len(volume_components)) * 100
        
        # Check data quality
        current_volume = volume_indicators.get('current_volume', 0)
        volume_ratio = volume_indicators.get('volume_ratio', 0)
        
        if current_volume > 0 and volume_ratio > 0:
            metrics['data_quality'] = 'excellent'
        else:
            metrics['data_quality'] = 'poor'
        
        # Evaluate analysis depth based on detected patterns
        depth_score = 0
        
        # Volume anomalies detected
        anomalies = volume_indicators.get('volume_anomalies', {}).get('unusual_spikes', [])
        if len(anomalies) > 0:
            depth_score += 25
        
        # Strong correlation detected
        correlation = volume_indicators.get('price_volume_correlation', {}).get('correlation_strength', 0)
        if abs(correlation) > 0.3:
            depth_score += 25
        
        # Institutional activity detected
        institutional = volume_indicators.get('institutional_activity', {}).get('activity_level', 'low')
        if institutional in ['medium', 'high']:
            depth_score += 25
        
        # Volume divergence detected
        divergence = volume_indicators.get('volume_divergences', {}).get('divergence_detected', False)
        if divergence:
            depth_score += 25
        
        metrics['analysis_depth'] = depth_score
        
        # Evaluate response quality if available
        if llm_response and not llm_response.startswith("API_ERROR"):
            response_score = 0
            
            # Check response length
            if len(llm_response) > 1500:
                response_score += 30
            elif len(llm_response) > 800:
                response_score += 20
            elif len(llm_response) > 400:
                response_score += 10
            
            # Check for volume-specific terms
            volume_terms = ['volume', 'anomal', 'spike', 'correlation', 'institutional', 'divergence', 'accumulation', 'distribution']
            term_count = sum(1 for term in volume_terms if term.lower() in llm_response.lower())
            response_score += min(term_count * 5, 35)
            
            # Check for JSON structure
            try:
                json_data = json.loads(llm_response)
                expected_keys = ['volume_anomalies', 'price_volume_correlation', 'volume_trends', 'institutional_activity']
                key_count = sum(1 for key in expected_keys if key in json_data)
                response_score += min(key_count * 8, 35)
            except:
                pass
            
            metrics['response_quality'] = min(response_score, 100)
        
        # Volume insight quality based on characteristics match
        insight_score = 60  # Base score
        
        # Bonus for matching expected volume characteristics
        expected_char = stock_config.volume_characteristics
        if expected_char == "high_liquidity" and volume_ratio > 1.0:
            insight_score += 20
        elif expected_char == "volatile_volume" and len(anomalies) > 0:
            insight_score += 20
        elif expected_char == "steady_volume" and abs(correlation) < 0.3:
            insight_score += 15
        
        metrics['volume_insight_quality'] = min(insight_score, 100)
        
        # Calculate overall score
        metrics['overall_score'] = (
            metrics['volume_data_completeness'] * 0.25 +
            metrics['analysis_depth'] * 0.25 +
            metrics['response_quality'] * 0.25 +
            metrics['volume_insight_quality'] * 0.25
        )
        
        return metrics
    
    def _generate_volume_analysis_report(self, reports_dir: str, results: List[Dict[str, Any]]):
        """Generate comprehensive volume analysis report"""
        # Use passed results and prepare summary data
        self.results = results  # Store for compatibility
        summary_data = []
        successful_tests = [r for r in results if r['success']]
        
        for result in results:
            summary_data.append({
                'Symbol': result['stock_config'].symbol,
                'Company': result['stock_config'].name,
                'Sector': result['stock_config'].sector,
                'Volume Characteristics': result['stock_config'].volume_characteristics,
                'Success': result['success'],
                'Quality Score': result['quality_score'],
                'Execution Time (s)': result['execution_time'],
                'Data Quality': result.get('data_quality', 'unknown'),
                'Has LLM Response': result.get('has_llm_response', False),
                'Volume Ratio': result.get('volume_metrics', {}).get('volume_ratio', 'N/A'),
                'Anomalies Count': result.get('volume_metrics', {}).get('anomalies_count', 'N/A'),
                'Correlation Strength': result.get('volume_metrics', {}).get('correlation_strength', 'N/A'),
                'Institutional Activity': result.get('volume_metrics', {}).get('institutional_activity', 'N/A'),
                'Divergence Detected': result.get('volume_metrics', {}).get('divergence_detected', 'N/A')
            })
        
        # Save to Excel (if openpyxl is available)
        summary_df = pd.DataFrame(summary_data)
        if HAS_OPENPYXL:
            excel_path = os.path.join(reports_dir, "volume_analysis_summary.xlsx")
            summary_df.to_excel(excel_path, index=False)
        else:
            # Save to CSV as fallback
            csv_path = os.path.join(reports_dir, "volume_analysis_summary.csv")
            summary_df.to_csv(csv_path, index=False)
            excel_path = csv_path
        
        # Generate detailed text report
        report_path = os.path.join(reports_dir, "volume_analysis_comprehensive_report.txt")
        with open(report_path, 'w') as f:
            f.write("MULTI-STOCK VOLUME ANALYSIS TESTING REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Stocks Tested: {len(self.results)}\n")
            f.write(f"Successful Tests: {len(successful_tests)}\n")
            f.write(f"Success Rate: {len(successful_tests)/len(self.results)*100:.1f}%\n\n")
            
            # Overall statistics
            if successful_tests:
                avg_quality = sum(r['quality_score'] for r in successful_tests) / len(successful_tests)
                avg_execution = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
                
                f.write("VOLUME ANALYSIS STATISTICS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Average Quality Score: {avg_quality:.1f}/100\n")
                f.write(f"Average Execution Time: {avg_execution:.1f}s\n")
                
                # Volume-specific metrics
                avg_volume_ratio = np.mean([r.get('volume_metrics', {}).get('volume_ratio', 0) for r in successful_tests if r.get('volume_metrics', {}).get('volume_ratio', 0) != 'N/A'])
                anomaly_detection_rate = sum(1 for r in successful_tests if r.get('volume_metrics', {}).get('anomalies_count', 0) > 0) / len(successful_tests) * 100
                
                f.write(f"Average Volume Ratio: {avg_volume_ratio:.2f}\n")
                f.write(f"Anomaly Detection Rate: {anomaly_detection_rate:.1f}%\n\n")
            
            # Volume characteristics analysis
            f.write("VOLUME CHARACTERISTICS ANALYSIS\n")
            f.write("-" * 40 + "\n")
            volume_chars = {}
            for result in successful_tests:
                char = result['stock_config'].volume_characteristics
                if char not in volume_chars:
                    volume_chars[char] = []
                volume_chars[char].append(result)
            
            for char, char_results in volume_chars.items():
                char_avg_quality = sum(r['quality_score'] for r in char_results) / len(char_results)
                f.write(f"\n{char.replace('_', ' ').title()}:\n")
                f.write(f"  Stocks: {len(char_results)}\n")
                f.write(f"  Average Quality: {char_avg_quality:.1f}/100\n")
                f.write(f"  Companies: {', '.join(r['stock_config'].symbol for r in char_results)}\n")
            
            # Individual stock details
            f.write("\n\nINDIVIDUAL STOCK VOLUME ANALYSIS\n")
            f.write("-" * 40 + "\n")
            for result in self.results:
                f.write(f"\n{result['stock_config'].symbol} ({result['stock_config'].name}):\n")
                f.write(f"  Sector: {result['stock_config'].sector}\n")
                f.write(f"  Volume Profile: {result['stock_config'].volume_characteristics}\n")
                f.write(f"  Success: {'✅' if result['success'] else '❌'}\n")
                if result['success']:
                    f.write(f"  Quality Score: {result['quality_score']:.1f}/100\n")
                    f.write(f"  Execution Time: {result['execution_time']:.1f}s\n")
                    f.write(f"  Data Quality: {result.get('data_quality', 'unknown')}\n")
                    if 'volume_metrics' in result:
                        vm = result['volume_metrics']
                        f.write(f"  Volume Ratio: {vm.get('volume_ratio', 'N/A')}\n")
                        f.write(f"  Anomalies: {vm.get('anomalies_count', 'N/A')}\n")
                        f.write(f"  Correlation: {vm.get('correlation_strength', 'N/A'):.3f}\n")
                        f.write(f"  Institutional Activity: {vm.get('institutional_activity', 'N/A')}\n")
                else:
                    f.write(f"  Error: {result.get('error', 'Unknown error')}\n")
        
        print(f"📊 Volume analysis report saved to: {report_path}")
        if HAS_OPENPYXL:
            print(f"📈 Summary data saved to Excel: {excel_path}")
        else:
            print(f"📈 Summary data saved to CSV: {excel_path}")

async def main():
    """Main function to run volume analysis testing"""
    print("🔍 Multi-Stock Volume Analysis Prompt Testing Framework")
    print("Testing optimized_volume_analysis prompt across multiple stocks for comprehensive volume analysis")
    
    tester = MultiStockVolumeTester()
    success = await tester.run_multi_stock_volume_tests()
    
    if success:
        print("\n🎉 Volume analysis testing completed successfully!")
    else:
        print("\n❌ Volume analysis testing failed")

if __name__ == "__main__":
    asyncio.run(main())
