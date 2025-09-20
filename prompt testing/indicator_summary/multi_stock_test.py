#!/usr/bin/env python3
"""
Multi-Stock Prompt Testing Framework

Tests the optimized_indicators_summary prompt across multiple stocks from different sectors
to validate consistency and quality of analysis.

Usage: python multi_stock_test.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import openpyxl
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.gemini.gemini_client import GeminiClient
    from backend.gemini.prompt_manager import PromptManager
    from backend.gemini.context_engineer import ContextEngineer, AnalysisType
    from backend.zerodha.client import ZerodhaDataClient
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

class StockTestConfig:
    """Configuration for individual stock tests"""
    def __init__(self, symbol: str, name: str, sector: str, expected_behavior: str):
        self.symbol = symbol
        self.name = name
        self.sector = sector
        self.expected_behavior = expected_behavior

class TechnicalIndicatorCalculator:
    """Calculate comprehensive technical indicators from real stock data"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD Indicator"""
        exp1 = data.ewm(span=fast).mean()
        exp2 = data.ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return {
            'upper': upper,
            'middle': sma,
            'lower': lower
        }
    
    @classmethod
    def calculate_all_indicators(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators needed for the prompt"""
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # Moving Averages
        sma_20 = cls.calculate_sma(close, 20)
        sma_50 = cls.calculate_sma(close, 50)
        sma_200 = cls.calculate_sma(close, 200)
        ema_12 = cls.calculate_ema(close, 12)
        ema_26 = cls.calculate_ema(close, 26)
        
        # RSI
        rsi = cls.calculate_rsi(close)
        
        # MACD
        macd_data = cls.calculate_macd(close)
        
        # Bollinger Bands
        bb_data = cls.calculate_bollinger_bands(close)
        
        # Volume indicators
        volume_sma = cls.calculate_sma(volume, 20)
        
        # Get latest values (remove NaN)
        def get_latest_valid(series):
            valid_values = series.dropna()
            return float(valid_values.iloc[-1]) if not valid_values.empty else None
        
        def get_recent_values(series, count=5):
            valid_values = series.dropna()
            return valid_values.tail(count).tolist() if not valid_values.empty else []
        
        # Current price info
        current_price = get_latest_valid(close)
        
        # Build comprehensive indicators dictionary matching the expected format
        indicators = {
            # Price data
            'close': get_recent_values(close, 20),
            'high': get_recent_values(high, 20),
            'low': get_recent_values(low, 20),
            'volume': get_recent_values(volume, 20),
            
            # Moving averages structure
            'moving_averages': {
                'sma_20': get_latest_valid(sma_20),
                'sma_50': get_latest_valid(sma_50),
                'sma_200': get_latest_valid(sma_200),
                'ema_20': get_latest_valid(cls.calculate_ema(close, 20)),
                'ema_50': get_latest_valid(cls.calculate_ema(close, 50)),
                'price_to_sma_200': (current_price / get_latest_valid(sma_200) - 1) * 100 if get_latest_valid(sma_200) else None,
                'sma_20_to_sma_50': (get_latest_valid(sma_20) / get_latest_valid(sma_50) - 1) * 100 if get_latest_valid(sma_50) else None,
                'golden_cross': get_latest_valid(sma_20) > get_latest_valid(sma_50) if get_latest_valid(sma_20) and get_latest_valid(sma_50) else False,
                'death_cross': get_latest_valid(sma_20) < get_latest_valid(sma_50) if get_latest_valid(sma_20) and get_latest_valid(sma_50) else False
            },
            
            # RSI structure
            'rsi': {
                'rsi_14': get_latest_valid(rsi),
                'trend': 'bullish' if get_latest_valid(rsi) and get_latest_valid(rsi) > 50 else 'bearish',
                'status': 'overbought' if get_latest_valid(rsi) and get_latest_valid(rsi) > 70 else 'oversold' if get_latest_valid(rsi) and get_latest_valid(rsi) < 30 else 'neutral'
            },
            
            # MACD structure
            'macd': {
                'macd_line': get_latest_valid(macd_data['macd']),
                'signal_line': get_latest_valid(macd_data['signal']),
                'histogram': get_latest_valid(macd_data['histogram']),
                'trend': 'bullish' if get_latest_valid(macd_data['histogram']) and get_latest_valid(macd_data['histogram']) > 0 else 'bearish'
            },
            
            # Volume structure
            'volume': {
                'volume_ratio': get_latest_valid(volume) / get_latest_valid(volume_sma) if get_latest_valid(volume_sma) else None,
                'volume_trend': 'increasing' if len(get_recent_values(volume, 5)) >= 2 and get_recent_values(volume, 5)[-1] > get_recent_values(volume, 5)[-2] else 'decreasing',
                'obv': None,  # On Balance Volume would need more complex calculation
                'volume_sma': get_latest_valid(volume_sma)
            },
            
            # Bollinger Bands
            'bollinger_bands': {
                'upper': get_latest_valid(bb_data['upper']),
                'middle': get_latest_valid(bb_data['middle']),
                'lower': get_latest_valid(bb_data['lower']),
                'position': 'upper' if current_price and get_latest_valid(bb_data['upper']) and current_price > get_latest_valid(bb_data['upper']) else 'lower' if current_price and get_latest_valid(bb_data['lower']) and current_price < get_latest_valid(bb_data['lower']) else 'middle'
            }
        }
        
        return indicators

class MultiStockTester:
    """Test prompt across multiple stocks"""
    
    def __init__(self):
        # Initialize Zerodha client
        try:
            self.zerodha_client = ZerodhaDataClient()
            print("✅ Zerodha client initialized")
        except Exception as e:
            print(f"❌ Cannot initialize Zerodha client: {e}")
            sys.exit(1)
        
        # Initialize other components
        self.calculator = TechnicalIndicatorCalculator()
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
        
        # Define test stocks from different sectors (starting with 5 key stocks)
        self.test_stocks = [
            StockTestConfig("RELIANCE", "Reliance Industries", "Energy/Petrochemicals", "large_cap_stable"),
            StockTestConfig("TCS", "Tata Consultancy Services", "IT Services", "large_cap_growth"),
            StockTestConfig("HDFCBANK", "HDFC Bank", "Banking", "large_cap_stable"),
            StockTestConfig("ICICIBANK", "ICICI Bank", "Banking", "large_cap_volatile"),
            StockTestConfig("ITC", "ITC Limited", "FMCG/Tobacco", "large_cap_defensive")
            # Note: Add more stocks here later for comprehensive testing:
            # StockTestConfig("INFY", "Infosys", "IT Services", "large_cap_stable"),
            # StockTestConfig("BHARTIARTL", "Bharti Airtel", "Telecommunications", "large_cap_cyclical"),
            # StockTestConfig("HINDUNILVR", "Hindustan Unilever", "FMCG", "large_cap_defensive"),
            # StockTestConfig("MARUTI", "Maruti Suzuki", "Automotive", "large_cap_cyclical"),
            # StockTestConfig("BAJFINANCE", "Bajaj Finance", "NBFC", "large_cap_growth")
        ]
        
        self.results = []
    
    async def run_multi_stock_tests(self):
        """Run tests across all configured stocks"""
        print(f"🚀 Starting Multi-Stock Prompt Testing")
        print(f"Testing {len(self.test_stocks)} stocks with 365 days of data")
        print("=" * 80)
        
        # Authenticate with Zerodha first
        print("🔗 Authenticating with Zerodha...")
        if not self.zerodha_client.authenticate():
            print("❌ Zerodha authentication failed")
            return False
        
        print("✅ Zerodha authentication successful")
        
        # Create results directory
        results_dir = "multi_stock_test_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Create async tasks for all stocks to run them concurrently
        async def test_single_stock(stock_config, stock_index):
            """Test a single stock asynchronously"""
            print(f"\n📊 Testing Stock {stock_index}/{len(self.test_stocks)}: {stock_config.symbol}")
            print(f"   Company: {stock_config.name}")
            print(f"   Sector: {stock_config.sector}")
            print("-" * 60)
            
            try:
                # Get stock data
                print(f"📈 Fetching 365 days of data for {stock_config.symbol}...")
                
                # Use async version of get_historical_data if available
                if hasattr(self.zerodha_client, 'get_historical_data_async'):
                    stock_data = await self.zerodha_client.get_historical_data_async(
                        symbol=stock_config.symbol,
                        exchange="NSE",
                        interval="day",
                        period=365
                    )
                else:
                    # Fallback to sync version in executor
                    import asyncio
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
                    return {
                        'stock_config': stock_config,
                        'success': False,
                        'error': 'No data available',
                        'execution_time': 0,
                        'quality_score': 0,
                        'data_quality': 'no_data'
                    }
                
                # Ensure we have the right columns
                required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                
                # If date is the index, reset it
                if 'date' not in stock_data.columns and stock_data.index.name == 'date':
                    stock_data = stock_data.reset_index()
                elif 'date' not in stock_data.columns:
                    stock_data['date'] = stock_data.index
                    stock_data = stock_data.reset_index(drop=True)
                
                # Check for missing columns
                missing_columns = [col for col in required_columns if col not in stock_data.columns]
                if missing_columns:
                    print(f"❌ Missing required columns for {stock_config.symbol}: {missing_columns}")
                    return {
                        'stock_config': stock_config,
                        'success': False,
                        'error': f'Missing columns: {missing_columns}',
                        'execution_time': 0,
                        'quality_score': 0,
                        'data_quality': 'missing_columns'
                    }
                
                # Sort by date to ensure proper order
                stock_data = stock_data.sort_values('date').reset_index(drop=True)
                
                print(f"✅ Retrieved {len(stock_data)} days of data")
                print(f"   Date range: {stock_data['date'].min()} to {stock_data['date'].max()}")
                print(f"   Price range: ₹{stock_data['close'].min():.2f} to ₹{stock_data['close'].max():.2f}")
                
                # Calculate technical indicators using the sophisticated system
                print("📊 Calculating technical indicators...")
                from ml.indicators.technical_indicators import TechnicalIndicators
                
                # Set date as index for technical indicators calculation
                stock_data_for_indicators = stock_data.set_index('date')
                
                # Use the sophisticated technical indicators system
                indicators = TechnicalIndicators.calculate_all_indicators_optimized(
                    stock_data_for_indicators, 
                    stock_config.symbol
                )
                
                # Test the prompt
                result = await self._test_stock_prompt(stock_config, indicators, results_dir)
                
                print(f"✅ Test completed for {stock_config.symbol}")
                print(f"   Success: {result['success']}")
                print(f"   Quality Score: {result['quality_score']:.1f}/100")
                print(f"   Response Time: {result['execution_time']:.1f}s")
                
                return result
                
            except Exception as e:
                print(f"❌ Error testing {stock_config.symbol}: {e}")
                import traceback
                traceback.print_exc()
                
                # Return error result
                return {
                    'stock_config': stock_config,
                    'success': False,
                    'error': str(e),
                    'execution_time': 0,
                    'quality_score': 0,
                    'data_quality': 'failed'
                }
        
        # Run all stock tests concurrently with a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent tests
        
        async def test_with_semaphore(stock_config, index):
            async with semaphore:
                return await test_single_stock(stock_config, index)
        
        # Create tasks for all stocks
        tasks = [
            test_with_semaphore(stock_config, i + 1)
            for i, stock_config in enumerate(self.test_stocks)
        ]
        
        # Wait for all tasks to complete
        print(f"\n🔄 Running {len(tasks)} stock tests concurrently (max 3 at a time)...")
        results = await asyncio.gather(*tasks)
        self.results.extend(results)
        
        # Generate comprehensive report
        self._generate_multi_stock_report(results_dir)
        
        print(f"\n✅ Multi-stock testing completed!")
        print(f"📁 Results saved to: {results_dir}/")
        
        return True
    
    async def _test_stock_prompt(self, stock_config: StockTestConfig, indicators: Dict[str, Any], results_dir: str) -> Dict[str, Any]:
        """Test the prompt for a single stock"""
        start_time = time.time()
        
        # Helper function for safe dictionary access
        def safe_get(data, *keys):
            """Safely get nested dictionary values"""
            try:
                result = data
                for key in keys:
                    result = result[key]
                return result
            except (KeyError, TypeError, AttributeError):
                return None
        
        try:
            # Apply context engineering
            curated_indicators = self.context_engineer.curate_indicators(
                indicators, 
                AnalysisType.INDICATOR_SUMMARY
            )
            
            # Structure context
            context = self.context_engineer.structure_context(
                curated_indicators,
                AnalysisType.INDICATOR_SUMMARY,
                stock_config.symbol,
                "1yr, daily",
                f"Company: {stock_config.name}, Sector: {stock_config.sector}"
            )
            
            # Format the final prompt
            prompt = self.prompt_manager.format_prompt(
                "optimized_indicators_summary",
                context=context
            )
            prompt += self.prompt_manager.SOLVING_LINE
            
            # Save prompt details with timestamp format like single test
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            prompt_file = os.path.join(results_dir, f"prompt_analysis_{stock_config.symbol}_{timestamp}.txt")
            with open(prompt_file, 'w') as f:
                f.write("PROMPT ANALYSIS FOR LLM\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Stock Symbol: {stock_config.symbol}\n")
                f.write(f"Company: {stock_config.name}\n")
                f.write(f"Sector: {stock_config.sector}\n")
                f.write(f"Expected Behavior: {stock_config.expected_behavior}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Prompt Length: {len(prompt)} characters\n")
                f.write(f"Context Length: {len(context)} characters\n\n")
                f.write("KEY TECHNICAL INDICATORS SUMMARY:\n")
                f.write("-" * 40 + "\n")
                # Only include essential indicator values (no redundant data)
                # Handle sophisticated indicator structure
                
                # Get actual current price from indicators or data
                # First try to get from common current price locations
                current_price = (
                    safe_get(indicators, 'current_price') or  # Direct current price
                    safe_get(indicators, 'daily_metrics', 'current_price') or  # Enhanced volume analysis
                    safe_get(indicators, 'enhanced_volume', 'comprehensive_analysis', 'daily_metrics', 'current_price') or  # Deep nested
                    safe_get(indicators, 'moving_averages', 'sma_20')  # Fallback to SMA20 only if no actual price
                ) or 0
                
                key_indicators = {
                    "current_price": current_price,
                    "rsi_14": safe_get(indicators, 'rsi', 'rsi_14'),
                    "rsi_status": safe_get(indicators, 'rsi', 'status'),
                    "macd_signal": "bullish" if safe_get(indicators, 'macd', 'histogram') and safe_get(indicators, 'macd', 'histogram') > 0 else "bearish",
                    "sma_20": safe_get(indicators, 'moving_averages', 'sma_20'),
                    "sma_50": safe_get(indicators, 'moving_averages', 'sma_50'),
                    "sma_200": safe_get(indicators, 'moving_averages', 'sma_200'),
                    "price_vs_sma200_pct": safe_get(indicators, 'moving_averages', 'price_to_sma_200'),
                    "volume_ratio": safe_get(indicators, 'volume', 'volume_ratio'),
                    "death_cross": safe_get(indicators, 'moving_averages', 'death_cross'),
                    "golden_cross": safe_get(indicators, 'moving_averages', 'golden_cross'),
                    # Add enhanced levels info for debugging
                    "enhanced_levels_available": 'enhanced_levels' in indicators,
                    "support_levels_count": len(safe_get(indicators, 'enhanced_levels', 'dynamic_support') or []),
                    "resistance_levels_count": len(safe_get(indicators, 'enhanced_levels', 'dynamic_resistance') or [])
                }
                f.write(json.dumps(key_indicators, indent=2, default=str))
                f.write("\n\n")
                f.write("FINAL PROMPT SENT TO LLM:\n")
                f.write("-" * 40 + "\n")
                f.write(prompt)
            
            # Make API call if available
            llm_response = ""
            if self.gemini_client:
                try:
                    print(f"🚀 Making API call for {stock_config.symbol}...")
                    response, code_results, execution_results = await self.gemini_client.core.call_llm_with_code_execution(prompt)
                    llm_response = response
                    
                    # Save response with timestamp format like single test
                    response_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    response_file = os.path.join(results_dir, f"response_analysis_{stock_config.symbol}_{response_timestamp}.txt")
                    with open(response_file, 'w') as f:
                        f.write("LLM ANALYSIS RESULTS\n")
                        f.write("=" * 80 + "\n\n")
                        f.write(f"Stock Symbol: {stock_config.symbol}\n")
                        f.write(f"Company: {stock_config.name}\n")
                        f.write(f"Sector: {stock_config.sector}\n")
                        f.write(f"Response Time: {datetime.now().isoformat()}\n")
                        f.write(f"Response Length: {len(response) if response else 0} characters\n")
                        if code_results:
                            f.write(f"Mathematical Calculations: {len(code_results)} code snippets executed\n")
                        if execution_results:
                            f.write(f"Calculation Results: {len(execution_results)} computational outputs\n")
                        f.write("\n")
                        
                        
                        # Full response (for completeness but without code dumps)
                        f.write("COMPLETE LLM RESPONSE:\n")
                        f.write("-" * 40 + "\n")
                        f.write(response or "No response received")
                        f.write("\n")
                    
                except Exception as e:
                    print(f"❌ API call failed for {stock_config.symbol}: {e}")
                    llm_response = f"API_ERROR: {str(e)}"
            
            execution_time = time.time() - start_time
            
            # Evaluate quality
            quality_metrics = self._evaluate_stock_analysis(stock_config, indicators, llm_response)
            
            return {
                'stock_config': stock_config,
                'success': True,
                'execution_time': execution_time,
                'quality_score': quality_metrics['overall_score'],
                'data_quality': quality_metrics['data_quality'],
                'response_length': len(llm_response) if llm_response else 0,
                'technical_indicators': {
                    'rsi': safe_get(indicators, 'rsi', 'rsi_14'),
                    'rsi_status': safe_get(indicators, 'rsi', 'status'),
                    'sma_20': safe_get(indicators, 'moving_averages', 'sma_20'),
                    'sma_200': safe_get(indicators, 'moving_averages', 'sma_200'),
                    'price_to_sma_200': safe_get(indicators, 'moving_averages', 'price_to_sma_200'),
                    'macd_trend': "bullish" if safe_get(indicators, 'macd', 'histogram') and safe_get(indicators, 'macd', 'histogram') > 0 else "bearish",
                    'volume_ratio': safe_get(indicators, 'volume', 'volume_ratio')
                },
                'quality_metrics': quality_metrics,
                'has_llm_response': bool(llm_response and not llm_response.startswith("API_ERROR"))
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'stock_config': stock_config,
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'quality_score': 0,
                'data_quality': 'error'
            }
    
    def _evaluate_stock_analysis(self, stock_config: StockTestConfig, indicators: Dict[str, Any], llm_response: str) -> Dict[str, Any]:
        """Evaluate the quality of analysis for a stock"""
        metrics = {
            'data_quality': 'unknown',
            'indicator_completeness': 0,
            'response_quality': 0,
            'sector_appropriateness': 0,
            'overall_score': 0
        }
        
        # Evaluate data quality
        required_indicators = ['rsi', 'macd', 'moving_averages', 'volume']
        available_indicators = 0
        for indicator in required_indicators:
            if indicator in indicators and indicators[indicator]:
                available_indicators += 1
        
        metrics['indicator_completeness'] = (available_indicators / len(required_indicators)) * 100
        
        # Check if we have SMA200 (key for long-term analysis)
        has_sma_200 = indicators['moving_averages']['sma_200'] is not None
        if has_sma_200:
            metrics['data_quality'] = 'excellent'
            metrics['indicator_completeness'] += 20
        else:
            metrics['data_quality'] = 'good'
        
        # Evaluate response quality if available
        if llm_response and not llm_response.startswith("API_ERROR"):
            if len(llm_response) > 1000:  # Substantial response
                metrics['response_quality'] = 80
            elif len(llm_response) > 500:  # Moderate response
                metrics['response_quality'] = 60
            else:
                metrics['response_quality'] = 40
            
            # Check for JSON format
            if 'market_outlook' in llm_response and 'trading_strategy' in llm_response:
                metrics['response_quality'] += 20
        
        # Sector appropriateness (basic check)
        metrics['sector_appropriateness'] = 70  # Default good score
        
        # Calculate overall score
        metrics['overall_score'] = min(100, (
            metrics['indicator_completeness'] * 0.4 +
            metrics['response_quality'] * 0.4 +
            metrics['sector_appropriateness'] * 0.2
        ))
        
        return metrics
    
    def _generate_multi_stock_report(self, results_dir: str):
        """Generate comprehensive multi-stock analysis report"""
        # Prepare summary data
        summary_data = []
        successful_tests = [r for r in self.results if r['success']]
        
        for result in self.results:
            summary_data.append({
                'Symbol': result['stock_config'].symbol,
                'Company': result['stock_config'].name,
                'Sector': result['stock_config'].sector,
                'Success': result['success'],
                'Quality Score': result['quality_score'],
                'Execution Time (s)': result['execution_time'],
                'Data Quality': result.get('data_quality', 'unknown'),
                'Has LLM Response': result.get('has_llm_response', False),
                'RSI': result.get('technical_indicators', {}).get('rsi', 'N/A'),
                'RSI Status': result.get('technical_indicators', {}).get('rsi_status', 'N/A'),
                'SMA200': result.get('technical_indicators', {}).get('sma_200', 'N/A'),
                'Price vs SMA200 (%)': result.get('technical_indicators', {}).get('price_to_sma_200', 'N/A')
            })
        
        # Save to Excel
        summary_df = pd.DataFrame(summary_data)
        excel_path = os.path.join(results_dir, "multi_stock_summary.xlsx")
        summary_df.to_excel(excel_path, index=False)
        
        # Generate detailed text report
        report_path = os.path.join(results_dir, "multi_stock_comprehensive_report.txt")
        with open(report_path, 'w') as f:
            f.write("MULTI-STOCK PROMPT TESTING REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Stocks Tested: {len(self.results)}\n")
            f.write(f"Successful Tests: {len(successful_tests)}\n")
            f.write(f"Success Rate: {len(successful_tests)/len(self.results)*100:.1f}%\n\n")
            
            # Overall statistics
            if successful_tests:
                avg_quality = sum(r['quality_score'] for r in successful_tests) / len(successful_tests)
                avg_execution = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
                
                f.write("OVERALL STATISTICS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Average Quality Score: {avg_quality:.1f}/100\n")
                f.write(f"Average Execution Time: {avg_execution:.1f}s\n\n")
            
            # Sector-wise analysis
            f.write("SECTOR-WISE ANALYSIS\n")
            f.write("-" * 40 + "\n")
            sectors = {}
            for result in successful_tests:
                sector = result['stock_config'].sector
                if sector not in sectors:
                    sectors[sector] = []
                sectors[sector].append(result)
            
            for sector, sector_results in sectors.items():
                sector_avg_quality = sum(r['quality_score'] for r in sector_results) / len(sector_results)
                f.write(f"\n{sector}:\n")
                f.write(f"  Stocks Tested: {len(sector_results)}\n")
                f.write(f"  Average Quality: {sector_avg_quality:.1f}/100\n")
                f.write(f"  Companies: {', '.join(r['stock_config'].symbol for r in sector_results)}\n")
            
            # Individual stock details
            f.write("\n\nINDIVIDUAL STOCK ANALYSIS\n")
            f.write("-" * 40 + "\n")
            for result in self.results:
                f.write(f"\n{result['stock_config'].symbol} ({result['stock_config'].name}):\n")
                f.write(f"  Sector: {result['stock_config'].sector}\n")
                f.write(f"  Success: {'✅' if result['success'] else '❌'}\n")
                if result['success']:
                    f.write(f"  Quality Score: {result['quality_score']:.1f}/100\n")
                    f.write(f"  Execution Time: {result['execution_time']:.1f}s\n")
                    f.write(f"  Data Quality: {result.get('data_quality', 'unknown')}\n")
                    if 'technical_indicators' in result:
                        ti = result['technical_indicators']
                        f.write(f"  RSI: {ti.get('rsi', 'N/A'):.1f} ({ti.get('rsi_status', 'N/A')})\n")
                        f.write(f"  SMA200 Available: {'Yes' if ti.get('sma_200') else 'No'}\n")
                        if ti.get('price_to_sma_200'):
                            f.write(f"  Price vs SMA200: {ti['price_to_sma_200']:+.1f}%\n")
                else:
                    f.write(f"  Error: {result.get('error', 'Unknown error')}\n")
        
        print(f"📊 Multi-stock report saved to: {report_path}")
        print(f"📈 Summary data saved to: {excel_path}")

async def main():
    """Main function"""
    print("🔍 Multi-Stock Prompt Testing Framework")
    print("Testing optimized_indicators_summary across multiple stocks from different sectors")
    
    tester = MultiStockTester()
    success = await tester.run_multi_stock_tests()
    
    if success:
        print("\n🎉 Multi-stock testing completed successfully!")
    else:
        print("\n❌ Multi-stock testing failed")

if __name__ == "__main__":
    asyncio.run(main())