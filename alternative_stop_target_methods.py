#!/usr/bin/env python3
"""
Alternative Methods for Stop Loss and Target Calculation

This module demonstrates various professional approaches to calculating
stop losses and profit targets beyond the current hybrid system.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from scipy import stats
import math

logger = logging.getLogger(__name__)

@dataclass
class MarketContext:
    """Market context for adaptive stop/target calculation."""
    volatility: float
    trend_strength: float
    volume_profile: str  # "high", "medium", "low"
    market_regime: str   # "trending", "ranging", "volatile"
    sector_momentum: float

class VolatilityBasedMethods:
    """Volatility-based stop loss and target methods."""
    
    def __init__(self):
        self.lookback_periods = [10, 20, 50]
    
    def atr_stops_targets(self, data: pd.DataFrame, atr_multiplier_stop: float = 2.0, 
                         atr_multiplier_target: float = 3.0) -> Dict[str, float]:
        """
        ATR (Average True Range) based stops and targets.
        Most popular professional method.
        
        Used by: Most professional traders, hedge funds
        Pros: Adapts to market volatility, robust
        Cons: Can be whipsawed in choppy markets
        """
        if len(data) < 14:
            return {"error": "Insufficient data"}
        
        # Calculate True Range
        high_low = data['high'] - data['low']
        high_close_prev = np.abs(data['high'] - data['close'].shift(1))
        low_close_prev = np.abs(data['low'] - data['close'].shift(1))
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(14).mean().iloc[-1]
        
        current_price = data['close'].iloc[-1]
        
        return {
            "method": "ATR_based",
            "stop_loss": current_price - (atr * atr_multiplier_stop),
            "target_1": current_price + (atr * atr_multiplier_target),
            "target_2": current_price + (atr * atr_multiplier_target * 1.5),
            "atr_value": atr,
            "stop_distance_pct": (atr * atr_multiplier_stop) / current_price * 100,
            "pros": ["Adapts to volatility", "Widely used", "Robust"],
            "cons": ["Can be whipsawed", "Lag in volatile markets"]
        }
    
    def bollinger_band_stops(self, data: pd.DataFrame, std_multiplier: float = 2.0) -> Dict[str, float]:
        """
        Bollinger Band based stops and targets.
        
        Used by: Mean reversion traders, volatility traders
        Pros: Great for ranging markets, adapts to volatility
        Cons: Poor in strong trends
        """
        if len(data) < 20:
            return {"error": "Insufficient data"}
        
        sma_20 = data['close'].rolling(20).mean()
        std_20 = data['close'].rolling(20).std()
        
        upper_band = sma_20 + (std_20 * std_multiplier)
        lower_band = sma_20 - (std_20 * std_multiplier)
        
        current_price = data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_sma = sma_20.iloc[-1]
        
        # Determine position relative to bands
        if current_price > current_sma:
            # Long bias
            stop_loss = current_lower
            target = current_upper
        else:
            # Short bias or neutral
            stop_loss = current_upper
            target = current_lower
        
        return {
            "method": "Bollinger_bands",
            "stop_loss": stop_loss,
            "target_1": target,
            "middle_line": current_sma,
            "band_width": (current_upper - current_lower) / current_sma * 100,
            "pros": ["Great for mean reversion", "Clear levels"],
            "cons": ["Poor in trending markets", "False signals"]
        }
    
    def keltner_channel_method(self, data: pd.DataFrame, multiplier: float = 2.0) -> Dict[str, float]:
        """
        Keltner Channel based method.
        
        Used by: Trend followers, breakout traders
        Pros: Less noisy than Bollinger, good trend signals
        Cons: Can miss quick reversals
        """
        if len(data) < 20:
            return {"error": "Insufficient data"}
        
        # Calculate EMA and ATR
        ema_20 = data['close'].ewm(span=20).mean()
        high_low = data['high'] - data['low']
        high_close_prev = np.abs(data['high'] - data['close'].shift(1))
        low_close_prev = np.abs(data['low'] - data['close'].shift(1))
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(10).mean()
        
        upper_channel = ema_20 + (atr * multiplier)
        lower_channel = ema_20 - (atr * multiplier)
        
        current_price = data['close'].iloc[-1]
        current_upper = upper_channel.iloc[-1]
        current_lower = lower_channel.iloc[-1]
        
        return {
            "method": "Keltner_channels",
            "stop_loss": current_lower,
            "target_1": current_upper,
            "ema_20": ema_20.iloc[-1],
            "channel_width": (current_upper - current_lower) / current_price * 100,
            "pros": ["Less noisy", "Good for trends"],
            "cons": ["Can miss reversals", "Lag in fast markets"]
        }

class StructuralLevelMethods:
    """Methods based on market structure and price levels."""
    
    def support_resistance_method(self, data: pd.DataFrame, lookback: int = 50) -> Dict[str, any]:
        """
        Support and Resistance based stops and targets.
        
        Used by: Technical analysts, swing traders
        Pros: Based on market psychology, clear levels
        Cons: Subjective, can be broken easily
        """
        if len(data) < lookback:
            return {"error": "Insufficient data"}
        
        recent_data = data.tail(lookback)
        
        # Find support levels (local lows)
        support_levels = []
        for i in range(2, len(recent_data) - 2):
            if (recent_data['low'].iloc[i] < recent_data['low'].iloc[i-1] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i-2] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+1] and
                recent_data['low'].iloc[i] < recent_data['low'].iloc[i+2]):
                support_levels.append(recent_data['low'].iloc[i])
        
        # Find resistance levels (local highs)
        resistance_levels = []
        for i in range(2, len(recent_data) - 2):
            if (recent_data['high'].iloc[i] > recent_data['high'].iloc[i-1] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i-2] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+1] and
                recent_data['high'].iloc[i] > recent_data['high'].iloc[i+2]):
                resistance_levels.append(recent_data['high'].iloc[i])
        
        current_price = data['close'].iloc[-1]
        
        # Find nearest support and resistance
        support_levels_below = [s for s in support_levels if s < current_price]
        resistance_levels_above = [r for r in resistance_levels if r > current_price]
        
        nearest_support = max(support_levels_below) if support_levels_below else current_price * 0.95
        nearest_resistance = min(resistance_levels_above) if resistance_levels_above else current_price * 1.05
        
        return {
            "method": "Support_resistance",
            "stop_loss": nearest_support * 0.99,  # Slightly below support
            "target_1": nearest_resistance,
            "target_2": nearest_resistance * 1.02,  # Slightly above resistance
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "support_count": len(support_levels_below),
            "resistance_count": len(resistance_levels_above),
            "pros": ["Market psychology based", "Clear levels"],
            "cons": ["Subjective identification", "Can be broken"]
        }
    
    def fibonacci_retracement_method(self, data: pd.DataFrame, lookback: int = 100) -> Dict[str, float]:
        """
        Fibonacci retracement based method.
        
        Used by: Technical analysts, harmonic pattern traders
        Pros: Mathematical precision, widely watched
        Cons: Self-fulfilling prophecy, many levels to choose from
        """
        if len(data) < lookback:
            return {"error": "Insufficient data"}
        
        recent_data = data.tail(lookback)
        
        # Find swing high and low
        swing_high = recent_data['high'].max()
        swing_low = recent_data['low'].min()
        
        # Calculate Fibonacci levels
        diff = swing_high - swing_low
        fib_levels = {
            0.0: swing_high,
            0.236: swing_high - (diff * 0.236),
            0.382: swing_high - (diff * 0.382),
            0.5: swing_high - (diff * 0.5),
            0.618: swing_high - (diff * 0.618),
            0.786: swing_high - (diff * 0.786),
            1.0: swing_low
        }
        
        current_price = data['close'].iloc[-1]
        
        # Determine trend and appropriate levels
        if current_price > (swing_high + swing_low) / 2:
            # Uptrend - use retracements as support
            stop_loss = fib_levels[0.618]  # 61.8% retracement
            target_1 = swing_high * 1.272  # 127.2% extension
            target_2 = swing_high * 1.618  # 161.8% extension
        else:
            # Downtrend - use retracements as resistance
            stop_loss = fib_levels[0.382]  # 38.2% retracement
            target_1 = swing_low * 0.728   # 72.8% of low
            target_2 = swing_low * 0.382   # 38.2% of low
        
        return {
            "method": "Fibonacci_retracement",
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "fib_levels": fib_levels,
            "pros": ["Mathematical precision", "Widely watched"],
            "cons": ["Many levels", "Self-fulfilling prophecy"]
        }

class StatisticalMethods:
    """Statistical and probability-based methods."""
    
    def percentile_method(self, data: pd.DataFrame, lookback: int = 252) -> Dict[str, float]:
        """
        Percentile-based stops and targets.
        
        Used by: Quantitative traders, statistical arbitrage
        Pros: Data-driven, removes emotion
        Cons: Assumes normal distribution, backward-looking
        """
        if len(data) < lookback:
            return {"error": "Insufficient data"}
        
        returns = data['close'].pct_change().dropna().tail(lookback)
        
        # Calculate percentiles for returns
        p5 = np.percentile(returns, 5)    # 5th percentile (stop loss level)
        p95 = np.percentile(returns, 95)  # 95th percentile (target level)
        p10 = np.percentile(returns, 10)  # Conservative stop
        p90 = np.percentile(returns, 90)  # Conservative target
        
        current_price = data['close'].iloc[-1]
        
        return {
            "method": "Percentile_based",
            "conservative_stop": current_price * (1 + p10),
            "aggressive_stop": current_price * (1 + p5),
            "conservative_target": current_price * (1 + p90),
            "aggressive_target": current_price * (1 + p95),
            "p5_return": p5 * 100,
            "p95_return": p95 * 100,
            "pros": ["Data-driven", "Removes emotion"],
            "cons": ["Assumes normality", "Backward-looking"]
        }
    
    def z_score_method(self, data: pd.DataFrame, lookback: int = 20) -> Dict[str, float]:
        """
        Z-score based mean reversion method.
        
        Used by: Mean reversion traders, pairs traders
        Pros: Statistical significance, good for ranging markets
        Cons: Poor in trending markets, assumes mean reversion
        """
        if len(data) < lookback:
            return {"error": "Insufficient data"}
        
        prices = data['close'].tail(lookback)
        mean_price = prices.mean()
        std_price = prices.std()
        current_price = data['close'].iloc[-1]
        
        z_score = (current_price - mean_price) / std_price
        
        # Define thresholds
        overbought_threshold = 2.0
        oversold_threshold = -2.0
        target_threshold = 0.0  # Mean reversion to average
        
        if z_score > overbought_threshold:
            # Price is overbought - expect mean reversion down
            stop_loss = current_price * 1.02  # 2% above current
            target = mean_price
        elif z_score < oversold_threshold:
            # Price is oversold - expect mean reversion up
            stop_loss = current_price * 0.98  # 2% below current
            target = mean_price
        else:
            # Neutral zone
            stop_loss = current_price * (0.98 if z_score > 0 else 1.02)
            target = mean_price
        
        return {
            "method": "Z_score_mean_reversion",
            "stop_loss": stop_loss,
            "target_1": target,
            "current_z_score": z_score,
            "mean_price": mean_price,
            "std_price": std_price,
            "interpretation": "overbought" if z_score > 2 else "oversold" if z_score < -2 else "neutral",
            "pros": ["Statistical significance", "Good for ranging"],
            "cons": ["Poor in trends", "Assumes mean reversion"]
        }

class AdaptiveMethods:
    """Adaptive methods that change based on market conditions."""
    
    def regime_adaptive_method(self, data: pd.DataFrame, context: MarketContext) -> Dict[str, any]:
        """
        Adaptive method that changes based on market regime.
        
        Used by: Sophisticated hedge funds, adaptive algorithms
        Pros: Adapts to market conditions, robust
        Cons: Complex implementation, requires market regime detection
        """
        current_price = data['close'].iloc[-1]
        
        if context.market_regime == "trending":
            # In trending markets, use wider stops and targets
            if context.trend_strength > 0.7:
                stop_multiplier = 3.0
                target_multiplier = 5.0
            else:
                stop_multiplier = 2.5
                target_multiplier = 4.0
                
        elif context.market_regime == "ranging":
            # In ranging markets, use tighter stops and targets
            stop_multiplier = 1.5
            target_multiplier = 2.0
            
        else:  # volatile
            # In volatile markets, use very wide stops
            stop_multiplier = 4.0
            target_multiplier = 3.0
        
        # Calculate ATR for base volatility
        high_low = data['high'] - data['low']
        high_close_prev = np.abs(data['high'] - data['close'].shift(1))
        low_close_prev = np.abs(data['low'] - data['close'].shift(1))
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(14).mean().iloc[-1]
        
        # Adjust for volume
        volume_adjustment = 1.0
        if context.volume_profile == "high":
            volume_adjustment = 0.8  # Tighter stops with high volume
        elif context.volume_profile == "low":
            volume_adjustment = 1.2  # Wider stops with low volume
        
        final_stop_distance = atr * stop_multiplier * volume_adjustment
        final_target_distance = atr * target_multiplier * volume_adjustment
        
        return {
            "method": "Regime_adaptive",
            "stop_loss": current_price - final_stop_distance,
            "target_1": current_price + final_target_distance,
            "target_2": current_price + (final_target_distance * 1.5),
            "market_regime": context.market_regime,
            "trend_strength": context.trend_strength,
            "volume_profile": context.volume_profile,
            "stop_multiplier_used": stop_multiplier,
            "volume_adjustment": volume_adjustment,
            "pros": ["Adapts to conditions", "Robust across regimes"],
            "cons": ["Complex implementation", "Requires regime detection"]
        }
    
    def machine_learning_method(self, data: pd.DataFrame, features: Dict[str, float]) -> Dict[str, any]:
        """
        Machine learning based stop and target prediction.
        
        Used by: Quantitative hedge funds, algo trading firms
        Pros: Data-driven, can find complex patterns
        Cons: Black box, requires lots of data, overfitting risk
        """
        # Simplified ML approach using feature scoring
        current_price = data['close'].iloc[-1]
        
        # Feature engineering
        volatility_score = features.get('volatility', 0.02) * 100
        momentum_score = features.get('momentum', 0.0) * 100
        trend_score = features.get('trend_strength', 0.5) * 100
        
        # Simple linear model (in reality, this would be a trained ML model)
        risk_score = (volatility_score * 0.4 + abs(momentum_score) * 0.3 + (100 - trend_score) * 0.3) / 100
        
        # Adaptive stop loss based on risk score
        base_stop_pct = 0.02  # 2%
        adaptive_stop_pct = base_stop_pct * (1 + risk_score)
        
        # Adaptive target based on momentum and trend
        base_target_pct = 0.04  # 4%
        adaptive_target_pct = base_target_pct * (1 + abs(momentum_score) / 100) * (trend_score / 100)
        
        return {
            "method": "Machine_learning_based",
            "stop_loss": current_price * (1 - adaptive_stop_pct),
            "target_1": current_price * (1 + adaptive_target_pct),
            "target_2": current_price * (1 + adaptive_target_pct * 1.5),
            "risk_score": risk_score,
            "adaptive_stop_pct": adaptive_stop_pct * 100,
            "adaptive_target_pct": adaptive_target_pct * 100,
            "features_used": features,
            "pros": ["Data-driven", "Complex pattern detection"],
            "cons": ["Black box", "Overfitting risk", "Requires lots of data"]
        }

class MethodComparison:
    """Compare different methods and provide recommendations."""
    
    @staticmethod
    def compare_methods(data: pd.DataFrame, context: MarketContext = None) -> Dict[str, any]:
        """Compare all methods and provide analysis."""
        if context is None:
            context = MarketContext(
                volatility=data['close'].pct_change().std() * np.sqrt(252),
                trend_strength=0.6,
                volume_profile="medium",
                market_regime="trending",
                sector_momentum=0.5
            )
        
        methods = {
            "volatility": VolatilityBasedMethods(),
            "structural": StructuralLevelMethods(), 
            "statistical": StatisticalMethods(),
            "adaptive": AdaptiveMethods()
        }
        
        results = {}
        
        try:
            # Volatility methods
            vol_methods = methods["volatility"]
            results["atr"] = vol_methods.atr_stops_targets(data)
            results["bollinger"] = vol_methods.bollinger_band_stops(data)
            results["keltner"] = vol_methods.keltner_channel_method(data)
            
            # Structural methods
            struct_methods = methods["structural"]
            results["support_resistance"] = struct_methods.support_resistance_method(data)
            results["fibonacci"] = struct_methods.fibonacci_retracement_method(data)
            
            # Statistical methods
            stat_methods = methods["statistical"]
            results["percentile"] = stat_methods.percentile_method(data)
            results["z_score"] = stat_methods.z_score_method(data)
            
            # Adaptive methods
            adaptive_methods = methods["adaptive"]
            results["regime_adaptive"] = adaptive_methods.regime_adaptive_method(data, context)
            
            # ML method with dummy features
            ml_features = {
                "volatility": context.volatility,
                "momentum": 0.05,  # 5% momentum
                "trend_strength": context.trend_strength
            }
            results["machine_learning"] = adaptive_methods.machine_learning_method(data, ml_features)
            
        except Exception as e:
            logger.error(f"Error in method comparison: {e}")
        
        return {
            "methods": results,
            "market_context": {
                "volatility": context.volatility,
                "trend_strength": context.trend_strength,
                "market_regime": context.market_regime,
                "recommendations": MethodComparison._get_recommendations(context)
            }
        }
    
    @staticmethod
    def _get_recommendations(context: MarketContext) -> Dict[str, str]:
        """Provide method recommendations based on market context."""
        recommendations = {}
        
        if context.market_regime == "trending":
            if context.trend_strength > 0.7:
                recommendations["best_method"] = "ATR-based with wider multipliers"
                recommendations["avoid"] = "Mean reversion methods (Z-score, Bollinger)"
            else:
                recommendations["best_method"] = "Support/Resistance with ATR confirmation"
                recommendations["avoid"] = "Tight statistical methods"
                
        elif context.market_regime == "ranging":
            recommendations["best_method"] = "Bollinger Bands or Z-score mean reversion"
            recommendations["avoid"] = "Trend-following methods with wide stops"
            
        else:  # volatile
            recommendations["best_method"] = "Percentile-based with wide stops"
            recommendations["avoid"] = "Fixed percentage methods"
        
        if context.volatility > 0.3:
            recommendations["volatility_note"] = "Use wider stops due to high volatility"
        elif context.volatility < 0.15:
            recommendations["volatility_note"] = "Can use tighter stops in low volatility"
        
        return recommendations

# Example usage and testing
def demonstrate_methods():
    """Demonstrate different methods with sample data."""
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Generate realistic price data
    returns = np.random.normal(0.001, 0.02, 100)  # Daily returns
    prices = [100]  # Starting price
    
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    # Create sample data with OHLCV
    data = pd.DataFrame({
        'date': dates,
        'open': prices[:-1],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices[:-1]],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices[:-1]],
        'close': prices[1:],
        'volume': np.random.randint(1000000, 5000000, 100)
    })
    
    # Create market context
    context = MarketContext(
        volatility=0.25,
        trend_strength=0.7,
        volume_profile="high",
        market_regime="trending",
        sector_momentum=0.6
    )
    
    # Compare all methods
    comparison = MethodComparison.compare_methods(data, context)
    
    return comparison

if __name__ == "__main__":
    print("🎯 Alternative Stop Loss and Target Calculation Methods")
    print("=" * 70)
    
    # Run demonstration
    results = demonstrate_methods()
    
    print("\n📊 Method Comparison Results:")
    for method_name, result in results["methods"].items():
        if "error" not in result:
            print(f"\n{method_name.upper()}:")
            print(f"  Stop Loss: ${result.get('stop_loss', 'N/A'):.2f}")
            print(f"  Target 1:  ${result.get('target_1', 'N/A'):.2f}")
            if 'pros' in result:
                print(f"  Pros: {', '.join(result['pros'])}")
            if 'cons' in result:
                print(f"  Cons: {', '.join(result['cons'])}")
    
    print(f"\n🎯 Recommendations for {results['market_context']['market_regime']} market:")
    recs = results['market_context']['recommendations']
    for key, value in recs.items():
        print(f"  {key}: {value}")