#!/usr/bin/env python3
"""
Validation script for market regime detection
Tests the new comprehensive regime detection system
"""
import pandas as pd
import numpy as np
import logging
import sys
import json
import os
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RegimeDetectionValidator")

# Import the regime detection function
try:
    from backend.signals.regimes import detect_market_regime
    logger.info("Successfully imported detect_market_regime")
except ImportError as e:
    logger.error(f"Failed to import detect_market_regime: {e}")
    sys.exit(1)

def create_test_data():
    """Create synthetic price data for testing"""
    # Create date range
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    # Create different price patterns
    
    # 1. Uptrend
    uptrend = np.linspace(100, 150, 100) + np.random.normal(0, 2, 100)
    
    # 2. Downtrend
    downtrend = np.linspace(150, 100, 100) + np.random.normal(0, 2, 100)
    
    # 3. Sideways/ranging
    sideways = np.ones(100) * 100 + np.random.normal(0, 3, 100)
    
    # 4. High volatility
    high_vol = np.linspace(100, 130, 100) + np.random.normal(0, 8, 100)
    
    # 5. Low volatility
    low_vol = np.linspace(100, 110, 100) + np.random.normal(0, 1, 100)
    
    # Create DataFrames
    datasets = {}
    
    for name, prices in [
        ("uptrend", uptrend),
        ("downtrend", downtrend),
        ("sideways", sideways),
        ("high_volatility", high_vol),
        ("low_volatility", low_vol)
    ]:
        # Create OHLC data
        high = prices + np.random.uniform(1, 3, 100)
        low = prices - np.random.uniform(1, 3, 100)
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': high,
            'low': low,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        })
        df.set_index('date', inplace=True)
        datasets[name] = df
    
    return datasets

def test_regime_detection():
    """Test the regime detection function with different market conditions"""
    logger.info("Starting regime detection validation tests")
    
    # Create test datasets
    datasets = create_test_data()
    
    results = {}
    
    # Test each dataset
    for name, data in datasets.items():
        logger.info(f"Testing regime detection on {name} dataset")
        
        try:
            # Call the regime detection function
            regime = detect_market_regime(data, {})
            logger.info(f"Regime detection result for {name}: {regime}")
            results[name] = regime
        except Exception as e:
            logger.error(f"Error detecting regime for {name}: {e}")
            results[name] = {"error": str(e)}
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"regime_detection_validation_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Validation results saved to {output_file}")
    
    return results

def validate_frontend_integration():
    """Test the integration with frontend response builder"""
    logger.info("Testing frontend integration")
    
    try:
        from backend.frontend_response_builder import FrontendResponseBuilder
        from backend.signals.scoring import compute_signals_summary
        
        # Create test data
        data = create_test_data()["uptrend"]
        
        # Create dummy indicators
        indicators = {
            "day": {
                "adx": {"adx": 30},
                "atr": {"atr_percent": 2.5},
                "bollinger_bands": {"bandwidth": 0.12}
            }
        }
        
        # Test compute_signals_summary directly
        logger.info("Testing compute_signals_summary function")
        try:
            summary = compute_signals_summary(indicators, data)
            logger.info(f"Signals summary result: {summary.regime}")
        except Exception as e:
            logger.error(f"Error in compute_signals_summary: {e}")
        
        # Test frontend response builder
        logger.info("Testing frontend response builder")
        try:
            response = FrontendResponseBuilder.build_frontend_response(
                symbol="TEST", 
                exchange="TEST", 
                data=data,
                indicators=indicators, 
                ai_analysis={}, 
                indicator_summary="", 
                chart_insights="",
                chart_paths={}, 
                sector_context={}, 
                mtf_context={}, 
                advanced_analysis={},
                ml_predictions=None,
                period=1,
                interval="day"
            )
            
            logger.info(f"Frontend response signals: {response.get('signals', {}).get('regime', 'Not found')}")
        except Exception as e:
            logger.error(f"Error in frontend response builder: {e}")
    
    except ImportError as e:
        logger.error(f"Import error in frontend integration test: {e}")

if __name__ == "__main__":
    logger.info("=== Market Regime Detection Validation ===")
    
    # Run tests
    test_results = test_regime_detection()
    
    # Validate frontend integration
    validate_frontend_integration()
    
    logger.info("Validation complete")
