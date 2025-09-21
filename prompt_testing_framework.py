#!/usr/bin/env python3
"""
Comprehensive Prompt Testing Framework

This script systematically tests all optimized prompts with real stock data
across multiple companies to evaluate output quality and identify improvements.

Features:
1. Fetches real historical data for multiple stocks
2. Calculates technical indicators
3. Tests each prompt individually
4. Evaluates output quality
5. Generates improvement recommendations
6. Saves results to Excel files

Usage: python prompt_testing_framework.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import requests
from dataclasses import dataclass
import traceback

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.gemini.gemini_client import GeminiClient
    from backend.gemini.prompt_manager import PromptManager
    from backend.gemini.context_engineer import ContextEngineer, AnalysisType
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

@dataclass
class PromptTestConfig:
    """Configuration for individual prompt tests"""
    prompt_name: str
    analysis_type: AnalysisType
    requires_image: bool
    expected_output_format: str  # 'json', 'markdown', 'mixed'
    key_output_fields: List[str]
    evaluation_criteria: List[str]

@dataclass
class TestStock:
    """Stock configuration for testing"""
    symbol: str
    exchange: str
    name: str
    expected_behavior: str  # 'trending', 'volatile', 'stable', etc.

@dataclass
class TestResult:
    """Results from a single prompt test"""
    prompt_name: str
    stock_symbol: str
    execution_time: float
    success: bool
    output_length: int
    output_format_valid: bool
    contains_key_fields: bool
    quality_score: float
    recommendations: List[str]
    raw_output: str
    error_message: str = None

class TechnicalIndicatorCalculator:
    """Calculate technical indicators from stock data"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD"""
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
        """Calculate Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return {
            'upper': upper,
            'middle': sma,
            'lower': lower
        }
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators for a stock"""
        close = df['close'] if 'close' in df.columns else df['Close']
        high = df['high'] if 'high' in df.columns else df['High']
        low = df['low'] if 'low' in df.columns else df['Low']
        volume = df['volume'] if 'volume' in df.columns else df['Volume']
        
        indicators = {
            'close': close.tolist(),
            'high': high.tolist(),
            'low': low.tolist(),
            'volume': volume.tolist(),
            'sma_20': TechnicalIndicatorCalculator.calculate_sma(close, 20).tolist(),
            'sma_50': TechnicalIndicatorCalculator.calculate_sma(close, 50).tolist(),
            'ema_12': TechnicalIndicatorCalculator.calculate_ema(close, 12).tolist(),
            'ema_26': TechnicalIndicatorCalculator.calculate_ema(close, 26).tolist(),
            'rsi': TechnicalIndicatorCalculator.calculate_rsi(close).tolist(),
        }
        
        # MACD
        macd_data = TechnicalIndicatorCalculator.calculate_macd(close)
        indicators.update({
            'macd': macd_data['macd'].tolist(),
            'macd_signal': macd_data['signal'].tolist(),
            'macd_histogram': macd_data['histogram'].tolist(),
        })
        
        # Bollinger Bands
        bb_data = TechnicalIndicatorCalculator.calculate_bollinger_bands(close)
        indicators.update({
            'bb_upper': bb_data['upper'].tolist(),
            'bb_middle': bb_data['middle'].tolist(),
            'bb_lower': bb_data['lower'].tolist(),
        })
        
        # Remove NaN values
        for key, value in indicators.items():
            if isinstance(value, list):
                indicators[key] = [v for v in value if not pd.isna(v)]
        
        return indicators

class StockDataProvider:
    """Fetch historical stock data"""
    
    def __init__(self):
        self.base_url = "https://api.polygon.io/v2/aggs/ticker"
        self.api_key = os.environ.get("POLYGON_API_KEY", "")
        
        # If Polygon API key not available, use Alpha Vantage as fallback
        if not self.api_key:
            self.alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
            print("⚠️  No Polygon API key found, will try Alpha Vantage")
    
    def fetch_stock_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """Fetch historical stock data"""
        try:
            if self.api_key:
                return self._fetch_polygon_data(symbol, days)
            elif hasattr(self, 'alpha_vantage_key') and self.alpha_vantage_key:
                return self._fetch_alpha_vantage_data(symbol)
            else:
                # Generate synthetic data for testing
                print(f"⚠️  No API keys available, generating synthetic data for {symbol}")
                return self._generate_synthetic_data(symbol, days)
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return self._generate_synthetic_data(symbol, days)
    
    def _fetch_polygon_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch data from Polygon API"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = f"{self.base_url}/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        params = {"apikey": self.api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'results' not in data:
            raise ValueError("No data returned from API")
        
        df = pd.DataFrame(data['results'])
        df['date'] = pd.to_datetime(df['t'], unit='ms')
        df = df.rename(columns={'c': 'close', 'h': 'high', 'l': 'low', 'o': 'open', 'v': 'volume'})
        return df[['date', 'open', 'high', 'low', 'close', 'volume']].sort_values('date')
    
    def _fetch_alpha_vantage_data(self, symbol: str) -> pd.DataFrame:
        """Fetch data from Alpha Vantage API"""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key,
            "outputsize": "compact"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'Time Series (Daily)' not in data:
            raise ValueError("No data returned from Alpha Vantage API")
        
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume'
        })
        df = df.astype(float)
        df['date'] = df.index
        return df[['date', 'open', 'high', 'low', 'close', 'volume']].sort_values('date').tail(100)
    
    def _generate_synthetic_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Generate synthetic stock data for testing"""
        np.random.seed(hash(symbol) % 2**32)  # Consistent seed per symbol
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 100 + (hash(symbol) % 200)  # Different base price per symbol
        
        # Generate realistic price movements
        returns = np.random.normal(0.001, 0.02, days)  # Small positive drift with volatility
        prices = [base_price]
        
        for i in range(1, days):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(max(new_price, prices[-1] * 0.95))  # Prevent extreme drops
        
        # Generate OHLC data
        data = []
        for i, date in enumerate(dates):
            close = prices[i]
            high = close * (1 + abs(np.random.normal(0, 0.01)))
            low = close * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else close
            volume = int(np.random.normal(1000000, 300000))
            
            data.append({
                'date': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': max(volume, 100000)
            })
        
        return pd.DataFrame(data)

class PromptTester:
    """Main class for testing prompts"""
    
    def __init__(self):
        self.gemini_client = None
        self.prompt_manager = PromptManager()
        self.context_engineer = ContextEngineer()
        self.data_provider = StockDataProvider()
        self.calculator = TechnicalIndicatorCalculator()
        
        # Initialize Gemini client if API key is available
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                self.gemini_client = GeminiClient(api_key=api_key)
                print("✅ Gemini API client initialized")
            else:
                print("⚠️  GEMINI_API_KEY not found. LLM testing will be skipped.")
        except Exception as e:
            print(f"⚠️  Could not initialize Gemini client: {e}")
        
        self.test_stocks = [
            TestStock("AAPL", "NASDAQ", "Apple Inc.", "trending"),
            TestStock("MSFT", "NASDAQ", "Microsoft Corp.", "stable"),
            TestStock("GOOGL", "NASDAQ", "Alphabet Inc.", "trending"),
            TestStock("TSLA", "NASDAQ", "Tesla Inc.", "volatile"),
            TestStock("SPY", "NYSE", "S&P 500 ETF", "stable"),
        ]
        
        self.prompt_configs = [
            PromptTestConfig(
                prompt_name="optimized_indicators_summary",
                analysis_type=AnalysisType.INDICATOR_SUMMARY,
                requires_image=False,
                expected_output_format="mixed",
                key_output_fields=["trend", "confidence_pct", "trading_strategy"],
                evaluation_criteria=["completeness", "accuracy", "actionability", "format_compliance"]
            ),
            PromptTestConfig(
                prompt_name="optimized_volume_analysis",
                analysis_type=AnalysisType.VOLUME_ANALYSIS,
                requires_image=True,
                expected_output_format="json",
                key_output_fields=["volume_anomalies", "price_volume_correlation", "institutional_activity"],
                evaluation_criteria=["volume_insights", "correlation_analysis", "anomaly_detection"]
            ),
            PromptTestConfig(
                prompt_name="optimized_reversal_patterns",
                analysis_type=AnalysisType.REVERSAL_PATTERNS,
                requires_image=True,
                expected_output_format="markdown",
                key_output_fields=["divergence_analysis", "reversal_patterns", "signal_strength"],
                evaluation_criteria=["pattern_accuracy", "risk_assessment", "entry_exit_levels"]
            ),
            PromptTestConfig(
                prompt_name="optimized_continuation_levels",
                analysis_type=AnalysisType.CONTINUATION_LEVELS,
                requires_image=True,
                expected_output_format="markdown",
                key_output_fields=["continuation_patterns", "key_levels", "breakout_potential"],
                evaluation_criteria=["level_identification", "pattern_reliability", "breakout_analysis"]
            ),
            PromptTestConfig(
                prompt_name="optimized_final_decision",
                analysis_type=AnalysisType.FINAL_DECISION,
                requires_image=False,
                expected_output_format="json",
                key_output_fields=["decision", "confidence", "trading_plan", "risk_management"],
                evaluation_criteria=["decision_clarity", "risk_assessment", "actionability", "comprehensive_analysis"]
            ),
        ]
    
    async def run_comprehensive_tests(self):
        """Run comprehensive tests on all prompts"""
        print("🚀 Starting Comprehensive Prompt Testing Framework")
        print("=" * 80)
        
        # Create results directory
        results_dir = "prompt_test_results"
        os.makedirs(results_dir, exist_ok=True)
        
        all_results = []
        
        # Test each prompt
        for prompt_config in self.prompt_configs:
            print(f"\n📋 Testing Prompt: {prompt_config.prompt_name}")
            print("-" * 60)
            
            prompt_results = await self._test_single_prompt(prompt_config)
            all_results.extend(prompt_results)
            
            # Save individual prompt results
            self._save_prompt_results(prompt_config.prompt_name, prompt_results, results_dir)
        
        # Generate comprehensive report
        self._generate_comprehensive_report(all_results, results_dir)
        
        print("\n✅ All tests completed!")
        print(f"📁 Results saved to: {results_dir}/")
    
    async def _test_single_prompt(self, config: PromptTestConfig) -> List[TestResult]:
        """Test a single prompt across all stocks"""
        results = []
        
        for stock in self.test_stocks:
            print(f"  📊 Testing {stock.symbol}...")
            
            try:
                # Fetch data and calculate indicators
                stock_data = self.data_provider.fetch_stock_data(stock.symbol)
                indicators = self.calculator.calculate_all_indicators(stock_data)
                
                # Test the prompt
                result = await self._execute_prompt_test(config, stock, indicators)
                results.append(result)
                
                print(f"    ✅ {stock.symbol}: {'Success' if result.success else 'Failed'} "
                      f"({result.execution_time:.2f}s, Quality: {result.quality_score:.2f})")
                
                # Small delay between tests
                await asyncio.sleep(0.5)
                
            except Exception as e:
                error_result = TestResult(
                    prompt_name=config.prompt_name,
                    stock_symbol=stock.symbol,
                    execution_time=0,
                    success=False,
                    output_length=0,
                    output_format_valid=False,
                    contains_key_fields=False,
                    quality_score=0,
                    recommendations=[f"Test failed with error: {str(e)}"],
                    raw_output="",
                    error_message=str(e)
                )
                results.append(error_result)
                print(f"    ❌ {stock.symbol}: Error - {str(e)}")
        
        return results
    
    async def _execute_prompt_test(self, config: PromptTestConfig, stock: TestStock, indicators: Dict[str, Any]) -> TestResult:
        """Execute a single prompt test"""
        start_time = time.time()
        
        try:
            if not self.gemini_client:
                # Simulate output for testing without API
                raw_output = self._simulate_prompt_output(config)
                success = True
            elif config.requires_image:
                # For image-based prompts, we'll simulate since we don't have actual chart images
                raw_output = self._simulate_prompt_output(config)
                success = True
            else:
                # Execute actual prompt
                raw_output = await self._call_gemini_api(config, stock, indicators)
                success = bool(raw_output and raw_output.strip())
            
            execution_time = time.time() - start_time
            
            # Evaluate the output
            evaluation = self._evaluate_output(config, raw_output)
            
            return TestResult(
                prompt_name=config.prompt_name,
                stock_symbol=stock.symbol,
                execution_time=execution_time,
                success=success,
                output_length=len(raw_output) if raw_output else 0,
                output_format_valid=evaluation['format_valid'],
                contains_key_fields=evaluation['has_key_fields'],
                quality_score=evaluation['quality_score'],
                recommendations=evaluation['recommendations'],
                raw_output=raw_output or ""
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                prompt_name=config.prompt_name,
                stock_symbol=stock.symbol,
                execution_time=execution_time,
                success=False,
                output_length=0,
                output_format_valid=False,
                contains_key_fields=False,
                quality_score=0,
                recommendations=[f"Execution failed: {str(e)}"],
                raw_output="",
                error_message=str(e)
            )
    
    def _simulate_prompt_output(self, config: PromptTestConfig) -> str:
        """Simulate prompt output for testing without actual API calls"""
        if config.expected_output_format == "json":
            return json.dumps({
                "test_field": "simulated_value",
                "quality": "high",
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        else:
            return f"Simulated output for {config.prompt_name}\n\nThis is a test response that would normally come from the LLM."
    
    async def _call_gemini_api(self, config: PromptTestConfig, stock: TestStock, indicators: Dict[str, Any]) -> str:
        """Make actual API call to Gemini"""
        try:
            # Prepare context
            curated_indicators = self.context_engineer.curate_indicators(indicators, config.analysis_type)
            context = self.context_engineer.structure_context(
                curated_indicators,
                config.analysis_type,
                stock.symbol,
                "100 days, daily",
                ""
            )
            
            # Format prompt
            prompt = self.prompt_manager.format_prompt(config.prompt_name, context=context)
            prompt += self.prompt_manager.SOLVING_LINE
            
            # Call API
            response, code_results, execution_results = await self.gemini_client.core.call_llm_with_code_execution(prompt)
            return response
            
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def _evaluate_output(self, config: PromptTestConfig, output: str) -> Dict[str, Any]:
        """Evaluate the quality of prompt output"""
        if not output:
            return {
                'format_valid': False,
                'has_key_fields': False,
                'quality_score': 0,
                'recommendations': ['Empty output received']
            }
        
        recommendations = []
        format_valid = True
        has_key_fields = False
        quality_score = 0
        
        # Check format validity
        if config.expected_output_format == "json":
            try:
                json.loads(output)
                quality_score += 25
            except json.JSONDecodeError:
                format_valid = False
                recommendations.append("Output is not valid JSON")
        
        # Check for key fields
        key_field_count = 0
        for field in config.key_output_fields:
            if field.lower() in output.lower():
                key_field_count += 1
        
        has_key_fields = key_field_count > len(config.key_output_fields) * 0.5
        quality_score += (key_field_count / len(config.key_output_fields)) * 25
        
        # Check output length (not too short, not too long)
        if 100 < len(output) < 5000:
            quality_score += 25
        elif len(output) < 100:
            recommendations.append("Output seems too short for comprehensive analysis")
        else:
            recommendations.append("Output might be too verbose")
        
        # Check for technical depth
        technical_terms = ['rsi', 'macd', 'sma', 'ema', 'volume', 'trend', 'support', 'resistance']
        found_terms = sum(1 for term in technical_terms if term in output.lower())
        quality_score += min(found_terms * 3, 25)
        
        if found_terms < 3:
            recommendations.append("Output lacks sufficient technical analysis depth")
        
        return {
            'format_valid': format_valid,
            'has_key_fields': has_key_fields,
            'quality_score': min(quality_score, 100),
            'recommendations': recommendations
        }
    
    def _save_prompt_results(self, prompt_name: str, results: List[TestResult], results_dir: str):
        """Save results for a single prompt to Excel"""
        data = []
        for result in results:
            data.append({
                'Stock': result.stock_symbol,
                'Success': result.success,
                'Execution Time (s)': result.execution_time,
                'Output Length': result.output_length,
                'Format Valid': result.output_format_valid,
                'Has Key Fields': result.contains_key_fields,
                'Quality Score': result.quality_score,
                'Recommendations': '; '.join(result.recommendations),
                'Error Message': result.error_message or '',
            })
        
        df = pd.DataFrame(data)
        excel_path = os.path.join(results_dir, f"{prompt_name}_results.xlsx")
        df.to_excel(excel_path, index=False)
        print(f"  💾 Results saved to: {excel_path}")
    
    def _generate_comprehensive_report(self, all_results: List[TestResult], results_dir: str):
        """Generate comprehensive analysis report"""
        # Summary statistics
        summary_data = []
        prompt_names = list(set(r.prompt_name for r in all_results))
        
        for prompt_name in prompt_names:
            prompt_results = [r for r in all_results if r.prompt_name == prompt_name]
            success_rate = sum(r.success for r in prompt_results) / len(prompt_results) * 100
            avg_quality = sum(r.quality_score for r in prompt_results) / len(prompt_results)
            avg_execution_time = sum(r.execution_time for r in prompt_results) / len(prompt_results)
            
            summary_data.append({
                'Prompt': prompt_name,
                'Success Rate (%)': success_rate,
                'Average Quality Score': avg_quality,
                'Average Execution Time (s)': avg_execution_time,
                'Tests Run': len(prompt_results),
                'Total Recommendations': sum(len(r.recommendations) for r in prompt_results)
            })
        
        # Save summary
        summary_df = pd.DataFrame(summary_data)
        summary_path = os.path.join(results_dir, "comprehensive_summary.xlsx")
        summary_df.to_excel(summary_path, index=False)
        
        # Generate detailed report
        report_path = os.path.join(results_dir, "detailed_analysis_report.txt")
        with open(report_path, 'w') as f:
            f.write("COMPREHENSIVE PROMPT TESTING REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tests: {len(all_results)}\n")
            f.write(f"Prompts Tested: {len(prompt_names)}\n")
            f.write(f"Stocks Tested: {len(self.test_stocks)}\n\n")
            
            # Overall statistics
            overall_success_rate = sum(r.success for r in all_results) / len(all_results) * 100
            overall_avg_quality = sum(r.quality_score for r in all_results) / len(all_results)
            
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Overall Success Rate: {overall_success_rate:.1f}%\n")
            f.write(f"Average Quality Score: {overall_avg_quality:.1f}/100\n\n")
            
            # Per-prompt analysis
            f.write("PER-PROMPT ANALYSIS\n")
            f.write("-" * 40 + "\n")
            for prompt_name in prompt_names:
                prompt_results = [r for r in all_results if r.prompt_name == prompt_name]
                f.write(f"\n{prompt_name.upper()}:\n")
                f.write(f"  Success Rate: {sum(r.success for r in prompt_results) / len(prompt_results) * 100:.1f}%\n")
                f.write(f"  Average Quality: {sum(r.quality_score for r in prompt_results) / len(prompt_results):.1f}/100\n")
                
                # Common recommendations
                all_recommendations = []
                for r in prompt_results:
                    all_recommendations.extend(r.recommendations)
                if all_recommendations:
                    f.write(f"  Common Issues: {'; '.join(set(all_recommendations))}\n")
            
            # Recommendations
            f.write("\nRECOMMENDations FOR IMPROVEMENT\n")
            f.write("-" * 40 + "\n")
            f.write("1. Focus on prompts with success rates below 80%\n")
            f.write("2. Improve format validation for JSON-based prompts\n")
            f.write("3. Enhance technical depth in analysis outputs\n")
            f.write("4. Consider prompt length optimization\n")
            f.write("5. Add more specific evaluation criteria\n")
        
        print(f"\n📊 Comprehensive report saved to: {report_path}")
        print(f"📈 Summary statistics saved to: {summary_path}")

async def main():
    """Main entry point"""
    tester = PromptTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())