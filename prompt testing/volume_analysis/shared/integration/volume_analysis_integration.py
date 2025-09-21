#!/usr/bin/env python3
"""
Volume Analysis Integration Module

This module integrates both the Volume Confirmation Agent and Volume Anomaly Detection Agent
to provide comprehensive volume analysis combining trend confirmation and anomaly detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import our volume analysis modules
from volume_confirmation_processor import VolumeConfirmationProcessor
from volume_confirmation_charts import VolumeConfirmationChartGenerator
from volume_anomaly_processor import VolumeAnomalyProcessor
from volume_anomaly_charts import VolumeAnomalyChartGenerator

class VolumeAnalysisIntegration:
    """
    Integrated Volume Analysis combining Volume Confirmation and Anomaly Detection
    
    Provides comprehensive volume analysis that combines:
    1. Volume confirmation of price trends
    2. Volume anomaly detection and classification
    3. Integrated analysis and recommendations
    """
    
    def __init__(self):
        # Initialize both processors and chart generators
        self.confirmation_processor = VolumeConfirmationProcessor()
        self.confirmation_charts = VolumeConfirmationChartGenerator()
        self.anomaly_processor = VolumeAnomalyProcessor()
        self.anomaly_charts = VolumeAnomalyChartGenerator()
        
        print("🔧 Volume Analysis Integration initialized")
        print("   ✅ Volume Confirmation Agent ready")
        print("   ✅ Volume Anomaly Detection Agent ready")
    
    def analyze_comprehensive_volume(self, data: pd.DataFrame, 
                                   stock_symbol: str = "STOCK") -> Dict[str, Any]:
        """
        Perform comprehensive volume analysis combining both agents
        
        Args:
            data: DataFrame with OHLCV data
            stock_symbol: Stock symbol for analysis
            
        Returns:
            Comprehensive analysis results from both agents
        """
        try:
            print(f"\n🔍 Starting comprehensive volume analysis for {stock_symbol}")
            print("=" * 70)
            
            # Run Volume Confirmation Analysis
            print("📈 Running Volume Confirmation Analysis...")
            confirmation_data = self.confirmation_processor.process_volume_confirmation_data(data)
            
            if 'error' in confirmation_data:
                print(f"❌ Volume Confirmation failed: {confirmation_data['error']}")
                confirmation_success = False
            else:
                confirmation_success = True
                trend_analysis = confirmation_data.get('trend_analysis', {})
                volume_signals = confirmation_data.get('volume_signals', {})
                print(f"   ✅ Trend direction: {trend_analysis.get('primary_trend', 'unknown')}")
                print(f"   ✅ Volume confirmation: {volume_signals.get('volume_trend_alignment', 'unknown')}")
            
            # Run Volume Anomaly Detection
            print("🚨 Running Volume Anomaly Detection...")
            anomaly_data = self.anomaly_processor.process_volume_anomaly_data(data)
            
            if 'error' in anomaly_data:
                print(f"❌ Volume Anomaly Detection failed: {anomaly_data['error']}")
                anomaly_success = False
            else:
                anomaly_success = True
                anomalies = anomaly_data.get('significant_anomalies', [])
                current_status = anomaly_data.get('current_volume_status', {})
                print(f"   ✅ Anomalies detected: {len(anomalies)}")
                print(f"   ✅ Current volume status: {current_status.get('current_status', 'unknown')}")
            
            # Create integrated analysis
            integrated_analysis = self._create_integrated_analysis(
                confirmation_data, anomaly_data, confirmation_success, anomaly_success
            )
            
            # Combine results
            comprehensive_results = {
                'symbol': stock_symbol,
                'analysis_timestamp': pd.Timestamp.now().isoformat(),
                'confirmation_analysis': confirmation_data if confirmation_success else {'error': 'analysis_failed'},
                'anomaly_analysis': anomaly_data if anomaly_success else {'error': 'analysis_failed'},
                'integrated_analysis': integrated_analysis,
                'success': {
                    'confirmation': confirmation_success,
                    'anomaly': anomaly_success,
                    'overall': confirmation_success and anomaly_success
                }
            }
            
            print(f"\n✅ Comprehensive volume analysis completed")
            print(f"   Overall Score: {integrated_analysis.get('overall_score', 0)}/100")
            print(f"   Trading Signal: {integrated_analysis.get('trading_signal', 'unknown').upper()}")
            
            return comprehensive_results
            
        except Exception as e:
            error_msg = f"Comprehensive volume analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'error': error_msg,
                'symbol': stock_symbol,
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }
    
    def generate_comprehensive_charts(self, data: pd.DataFrame, 
                                    comprehensive_results: Dict[str, Any],
                                    stock_symbol: str = "STOCK",
                                    save_confirmation_path: Optional[str] = None,
                                    save_anomaly_path: Optional[str] = None) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Generate both confirmation and anomaly charts
        
        Args:
            data: DataFrame with OHLCV data
            comprehensive_results: Results from analyze_comprehensive_volume
            stock_symbol: Stock symbol for charts
            save_confirmation_path: Path to save confirmation chart
            save_anomaly_path: Path to save anomaly chart
            
        Returns:
            Tuple of (confirmation_chart_bytes, anomaly_chart_bytes)
        """
        try:
            print(f"\n🎨 Generating comprehensive charts for {stock_symbol}")
            print("=" * 60)
            
            confirmation_chart = None
            anomaly_chart = None
            
            # Generate Volume Confirmation chart
            if comprehensive_results.get('success', {}).get('confirmation', False):
                print("📊 Generating Volume Confirmation chart...")
                confirmation_data = comprehensive_results['confirmation_analysis']
                confirmation_chart = self.confirmation_charts.generate_volume_confirmation_chart(
                    data, confirmation_data, stock_symbol, save_confirmation_path
                )
                
                if confirmation_chart:
                    print(f"   ✅ Confirmation chart: {len(confirmation_chart)} bytes")
                else:
                    print("   ❌ Confirmation chart generation failed")
            else:
                print("   ⚠️ Skipping confirmation chart - analysis failed")
            
            # Generate Volume Anomaly chart
            if comprehensive_results.get('success', {}).get('anomaly', False):
                print("🚨 Generating Volume Anomaly chart...")
                anomaly_data = comprehensive_results['anomaly_analysis']
                anomaly_chart = self.anomaly_charts.generate_volume_anomaly_chart(
                    data, anomaly_data, stock_symbol, save_anomaly_path
                )
                
                if anomaly_chart:
                    print(f"   ✅ Anomaly chart: {len(anomaly_chart)} bytes")
                else:
                    print("   ❌ Anomaly chart generation failed")
            else:
                print("   ⚠️ Skipping anomaly chart - analysis failed")
            
            return confirmation_chart, anomaly_chart
            
        except Exception as e:
            print(f"❌ Chart generation failed: {e}")
            return None, None
    
    def _create_integrated_analysis(self, confirmation_data: Dict[str, Any], 
                                  anomaly_data: Dict[str, Any],
                                  confirmation_success: bool, 
                                  anomaly_success: bool) -> Dict[str, Any]:
        """Create integrated analysis combining both agents' results"""
        try:
            integrated = {
                'analysis_quality': self._assess_integrated_quality(confirmation_success, anomaly_success),
                'overall_score': 0,
                'trading_signal': 'unknown',
                'signal_strength': 'unknown',
                'key_insights': [],
                'risk_assessment': {},
                'recommendations': []
            }
            
            # Extract key data from both analyses
            confirmation_insights = []
            anomaly_insights = []
            signal_components = []
            risk_factors = []
            
            # Process confirmation analysis
            if confirmation_success and 'error' not in confirmation_data:
                trend_analysis = confirmation_data.get('trend_analysis', {})
                volume_signals = confirmation_data.get('volume_signals', {})
                
                # Confirmation insights
                primary_trend = trend_analysis.get('primary_trend', 'unknown')
                volume_alignment = volume_signals.get('volume_trend_alignment', 'unknown')
                
                confirmation_insights.append(f"Primary trend: {primary_trend}")
                confirmation_insights.append(f"Volume-trend alignment: {volume_alignment}")
                
                # Signal components from confirmation
                if volume_alignment in ['strong_confirmation', 'moderate_confirmation']:
                    signal_components.append('positive_confirmation')
                elif volume_alignment in ['divergence', 'weak_confirmation']:
                    signal_components.append('negative_confirmation')
                    risk_factors.append('volume_price_divergence')
            
            # Process anomaly analysis
            if anomaly_success and 'error' not in anomaly_data:
                anomalies = anomaly_data.get('significant_anomalies', [])
                current_status = anomaly_data.get('current_volume_status', {})
                anomaly_patterns = anomaly_data.get('anomaly_patterns', {})
                
                # Anomaly insights
                anomaly_count = len(anomalies)
                high_anomalies = len([a for a in anomalies if a.get('significance') == 'high'])
                current_vol_status = current_status.get('current_status', 'unknown')
                
                anomaly_insights.append(f"Volume anomalies detected: {anomaly_count}")
                anomaly_insights.append(f"High significance anomalies: {high_anomalies}")
                anomaly_insights.append(f"Current volume status: {current_vol_status}")
                
                # Signal components from anomalies
                if high_anomalies > 0:
                    signal_components.append('high_anomaly_activity')
                    risk_factors.append('unusual_volume_activity')
                
                if current_vol_status in ['extremely_high', 'very_high']:
                    signal_components.append('elevated_volume')
                elif current_vol_status in ['extremely_low', 'very_low']:
                    signal_components.append('suppressed_volume')
                    risk_factors.append('low_liquidity')
                
                # Pattern-based insights
                anomaly_frequency = anomaly_patterns.get('anomaly_frequency', 'unknown')
                if anomaly_frequency == 'high':
                    risk_factors.append('high_volatility_pattern')
            
            # Combine insights
            integrated['key_insights'] = confirmation_insights + anomaly_insights
            
            # Determine overall trading signal
            integrated['trading_signal'], integrated['signal_strength'] = self._determine_integrated_signal(
                signal_components, confirmation_success, anomaly_success
            )
            
            # Assess integrated risk
            integrated['risk_assessment'] = {
                'risk_level': self._assess_integrated_risk(risk_factors),
                'risk_factors': risk_factors,
                'risk_score': min(len(risk_factors) * 20, 100)
            }
            
            # Calculate overall score
            integrated['overall_score'] = self._calculate_integrated_score(
                confirmation_success, anomaly_success, signal_components, risk_factors
            )
            
            # Generate recommendations
            integrated['recommendations'] = self._generate_integrated_recommendations(
                integrated['trading_signal'], integrated['risk_assessment'], 
                signal_components, risk_factors
            )
            
            return integrated
            
        except Exception as e:
            return {
                'error': f"Integrated analysis failed: {str(e)}",
                'overall_score': 0,
                'trading_signal': 'unknown'
            }
    
    def _assess_integrated_quality(self, confirmation_success: bool, anomaly_success: bool) -> str:
        """Assess the quality of integrated analysis"""
        if confirmation_success and anomaly_success:
            return 'excellent'
        elif confirmation_success or anomaly_success:
            return 'partial'
        else:
            return 'failed'
    
    def _determine_integrated_signal(self, signal_components: List[str], 
                                   confirmation_success: bool, 
                                   anomaly_success: bool) -> Tuple[str, str]:
        """Determine integrated trading signal"""
        if not confirmation_success and not anomaly_success:
            return 'unknown', 'weak'
        
        # Count signal strength indicators
        bullish_signals = len([s for s in signal_components if s in ['positive_confirmation', 'elevated_volume']])
        bearish_signals = len([s for s in signal_components if s in ['negative_confirmation', 'suppressed_volume']])
        neutral_signals = len([s for s in signal_components if s in ['high_anomaly_activity']])
        
        # Determine signal
        if bullish_signals > bearish_signals + neutral_signals:
            signal = 'bullish'
        elif bearish_signals > bullish_signals + neutral_signals:
            signal = 'bearish'
        else:
            signal = 'neutral'
        
        # Determine strength
        total_signals = len(signal_components)
        if total_signals >= 3:
            strength = 'strong'
        elif total_signals >= 2:
            strength = 'moderate'
        elif total_signals >= 1:
            strength = 'weak'
        else:
            strength = 'very_weak'
        
        return signal, strength
    
    def _assess_integrated_risk(self, risk_factors: List[str]) -> str:
        """Assess integrated risk level"""
        if len(risk_factors) >= 3:
            return 'high'
        elif len(risk_factors) >= 2:
            return 'medium'
        elif len(risk_factors) >= 1:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_integrated_score(self, confirmation_success: bool, anomaly_success: bool,
                                  signal_components: List[str], risk_factors: List[str]) -> int:
        """Calculate overall integrated analysis score"""
        score = 0
        
        # Base score for successful analyses
        if confirmation_success:
            score += 30
        if anomaly_success:
            score += 30
        
        # Signal clarity bonus
        score += min(len(signal_components) * 8, 25)
        
        # Risk penalty
        score -= min(len(risk_factors) * 5, 20)
        
        # Integration quality bonus
        if confirmation_success and anomaly_success:
            score += 15
        
        return max(0, min(score, 100))
    
    def _generate_integrated_recommendations(self, trading_signal: str, 
                                           risk_assessment: Dict[str, Any],
                                           signal_components: List[str], 
                                           risk_factors: List[str]) -> List[str]:
        """Generate integrated trading recommendations"""
        recommendations = []
        
        # Signal-based recommendations
        if trading_signal == 'bullish':
            recommendations.append("Consider bullish positions with volume confirmation")
        elif trading_signal == 'bearish':
            recommendations.append("Consider bearish positions or reduce exposure")
        else:
            recommendations.append("Maintain neutral stance until clearer signals emerge")
        
        # Risk-based recommendations
        risk_level = risk_assessment.get('risk_level', 'unknown')
        if risk_level == 'high':
            recommendations.append("Exercise increased caution due to high risk factors")
            recommendations.append("Consider smaller position sizes")
        elif risk_level == 'medium':
            recommendations.append("Monitor risk factors closely")
        
        # Specific factor recommendations
        if 'volume_price_divergence' in risk_factors:
            recommendations.append("Watch for potential trend reversal due to volume divergence")
        if 'unusual_volume_activity' in risk_factors:
            recommendations.append("Monitor news and events causing volume spikes")
        if 'low_liquidity' in risk_factors:
            recommendations.append("Be cautious of wider bid-ask spreads")
        
        return recommendations


def test_comprehensive_volume_analysis():
    """Test the comprehensive volume analysis integration"""
    print("🔧 Testing Comprehensive Volume Analysis Integration")
    print("=" * 70)
    
    # Create realistic test data
    dates = pd.date_range(start='2024-07-01', end='2024-10-20', freq='D')
    np.random.seed(42)
    
    base_price = 2400
    base_volume = 1800000
    
    # Generate trending price data with some reversals
    price_changes = np.random.normal(0.002, 0.015, len(dates))  # Slight uptrend
    # Add some trend reversals
    reversal_points = [30, 70]
    for point in reversal_points:
        if point < len(price_changes):
            price_changes[point:point+10] *= -1.5  # Reverse trend briefly
    
    prices = base_price * np.cumprod(1 + price_changes)
    
    # Generate volume data with trend alignment and some anomalies
    volumes = np.random.lognormal(np.log(base_volume), 0.5, len(dates))
    
    # Add volume spikes during trend changes
    spike_indices = [30, 35, 70, 75, 95]
    for idx in spike_indices:
        if idx < len(volumes):
            volumes[idx] *= np.random.uniform(3.0, 6.0)
    
    # Create realistic OHLCV data
    test_data = pd.DataFrame({
        'open': prices + np.random.normal(0, 2, len(dates)),
        'high': prices + np.abs(np.random.normal(8, 4, len(dates))),
        'low': prices - np.abs(np.random.normal(8, 4, len(dates))),
        'close': prices,
        'volume': volumes.astype(int)
    }, index=dates)
    
    # Ensure realistic OHLC relationships
    test_data['high'] = np.maximum(test_data[['open', 'close']].max(axis=1), test_data['high'])
    test_data['low'] = np.minimum(test_data[['open', 'close']].min(axis=1), test_data['low'])
    
    print(f"✅ Created test data: {len(test_data)} days")
    print(f"   Price range: ${test_data['close'].min():.2f} - ${test_data['close'].max():.2f}")
    print(f"   Volume range: {test_data['volume'].min():,} - {test_data['volume'].max():,}")
    
    # Run comprehensive analysis
    integrator = VolumeAnalysisIntegration()
    results = integrator.analyze_comprehensive_volume(test_data, "TEST_STOCK")
    
    if 'error' in results:
        print(f"❌ Analysis failed: {results['error']}")
        return False
    
    # Display results summary
    print(f"\n📊 Comprehensive Analysis Results:")
    print(f"   Success - Confirmation: {results['success']['confirmation']}")
    print(f"   Success - Anomaly: {results['success']['anomaly']}")
    print(f"   Success - Overall: {results['success']['overall']}")
    
    integrated = results.get('integrated_analysis', {})
    print(f"\\n🎯 Integrated Analysis:")
    print(f"   Overall Score: {integrated.get('overall_score', 0)}/100")
    print(f"   Trading Signal: {integrated.get('trading_signal', 'unknown').upper()}")
    print(f"   Signal Strength: {integrated.get('signal_strength', 'unknown').upper()}")
    print(f"   Risk Level: {integrated.get('risk_assessment', {}).get('risk_level', 'unknown').upper()}")
    
    # Generate charts
    confirmation_chart, anomaly_chart = integrator.generate_comprehensive_charts(
        test_data, results, "TEST_STOCK",
        "test_comprehensive_confirmation.png",
        "test_comprehensive_anomaly.png"
    )
    
    chart_success = 0
    if confirmation_chart:
        chart_success += 1
        print(f"✅ Confirmation chart generated: {len(confirmation_chart)} bytes")
    if anomaly_chart:
        chart_success += 1
        print(f"✅ Anomaly chart generated: {len(anomaly_chart)} bytes")
    
    print(f"\\n🎨 Chart Generation Summary: {chart_success}/2 charts successful")
    
    # Display key insights
    insights = integrated.get('key_insights', [])
    if insights:
        print(f"\\n💡 Key Insights:")
        for i, insight in enumerate(insights[:5], 1):
            print(f"   {i}. {insight}")
    
    # Display recommendations
    recommendations = integrated.get('recommendations', [])
    if recommendations:
        print(f"\\n🎯 Trading Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    return results['success']['overall']

if __name__ == "__main__":
    test_comprehensive_volume_analysis()