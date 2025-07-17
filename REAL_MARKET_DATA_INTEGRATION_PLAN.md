# Real Market Data Integration Plan

## Overview
This plan outlines the strategy for integrating real market data from multiple sources to replace the current mock data and enhance LLM analysis with live, accurate market context.

## Current Data Sources

### ✅ Already Integrated
1. **Zerodha KiteConnect API**
   - Stock price data (OHLCV)
   - Real-time quotes
   - Historical data
   - Market status inference

### ❌ Currently Mock Data
1. **Market Context** (Nifty, Sensex, market breadth)
2. **Sector Performance** (sector indices, performance)
3. **News & Events** (company news, market events)
4. **Global Markets** (US, Asian, European markets)
5. **Volatility Data** (VIX, fear/greed index)

## Phase 2A: Market Context Integration

### 1. NSE/BSE Index Data Integration

**Data Sources:**
- **NSE India API** (free tier available)
- **Yahoo Finance API** (free, reliable)
- **Alpha Vantage** (free tier: 500 requests/day)

**Implementation Plan:**

```python
# New file: backend/data_sources/market_indices.py
class MarketIndicesProvider:
    def __init__(self):
        self.yahoo_client = YahooFinanceClient()
        self.nse_client = NSEClient()
        self.cache = {}
    
    def get_nifty_50_data(self) -> Dict[str, Any]:
        """Get Nifty 50 real-time data"""
        # Use Yahoo Finance API
        # Symbol: ^NSEI
        
    def get_sensex_data(self) -> Dict[str, Any]:
        """Get Sensex real-time data"""
        # Use Yahoo Finance API
        # Symbol: ^BSESN
        
    def get_market_breadth(self) -> Dict[str, Any]:
        """Get market breadth (advances/declines)"""
        # Use NSE India API for breadth data
```

### 2. Sector Performance Integration

**Data Sources:**
- **NSE Sector Indices** (NIFTY_BANK, NIFTY_IT, etc.)
- **Yahoo Finance** (sector ETFs)

**Implementation Plan:**

```python
# New file: backend/data_sources/sector_data.py
class SectorDataProvider:
    def __init__(self):
        self.sector_mapping = {
            'RELIANCE': 'NIFTY_ENERGY',
            'TCS': 'NIFTY_IT',
            'HDFCBANK': 'NIFTY_BANK',
            # ... more mappings
        }
    
    def get_sector_performance(self, symbol: str) -> Dict[str, Any]:
        """Get real sector performance for a stock"""
        sector_index = self.sector_mapping.get(symbol, 'NIFTY_50')
        return self._fetch_sector_data(sector_index)
```

## Phase 2B: News & Events Integration

### 1. News API Integration

**Data Sources:**
- **NewsAPI.org** (free tier: 100 requests/day)
- **Alpha Vantage News** (free tier)
- **Finnhub News** (free tier: 60 requests/minute)

**Implementation Plan:**

```python
# New file: backend/data_sources/news_provider.py
class NewsDataProvider:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.cache = {}
    
    def get_company_news(self, symbol: str, date_range: List[str]) -> List[Dict]:
        """Get real company news"""
        # Use NewsAPI with company name search
        # Cache results for 1 hour
        
    def get_market_news(self, date_range: List[str]) -> List[Dict]:
        """Get market-wide news"""
        # Use NewsAPI with market keywords
        
    def get_earnings_calendar(self, symbol: str) -> List[Dict]:
        """Get earnings calendar"""
        # Use Finnhub earnings calendar API
```

### 2. Economic Calendar Integration

**Data Sources:**
- **Trading Economics API** (free tier)
- **FRED API** (Federal Reserve Economic Data)

**Implementation Plan:**

```python
# New file: backend/data_sources/economic_calendar.py
class EconomicCalendarProvider:
    def __init__(self):
        self.trading_economics_key = os.getenv("TRADING_ECONOMICS_API_KEY")
    
    def get_market_events(self, date_range: List[str]) -> List[Dict]:
        """Get economic events and announcements"""
        # RBI meetings, GDP releases, etc.
```

## Phase 2C: Global Markets Integration

### 1. Global Indices Data

**Data Sources:**
- **Yahoo Finance** (free, reliable)
- **Alpha Vantage** (free tier)

**Implementation Plan:**

```python
# New file: backend/data_sources/global_markets.py
class GlobalMarketsProvider:
    def __init__(self):
        self.indices = {
            'US': ['^GSPC', '^IXIC', '^DJI'],  # S&P 500, NASDAQ, Dow
            'ASIA': ['^N225', '^HSI', '^KS11'],  # Nikkei, Hang Seng, KOSPI
            'EUROPE': ['^FTSE', '^GDAXI', '^FCHI']  # FTSE, DAX, CAC
        }
    
    def get_global_markets_data(self) -> Dict[str, Any]:
        """Get real global market data"""
        # Fetch all major indices
        # Calculate trends and correlations
```

### 2. Currency & Commodity Data

**Data Sources:**
- **Yahoo Finance** (currency pairs)
- **Alpha Vantage** (commodities)

**Implementation Plan:**

```python
# New file: backend/data_sources/currency_commodity.py
class CurrencyCommodityProvider:
    def __init__(self):
        self.currency_pairs = ['USDINR=X', 'EURUSD=X', 'GBPUSD=X']
        self.commodities = ['GC=F', 'CL=F', 'SI=F']  # Gold, Oil, Silver
    
    def get_currency_data(self) -> Dict[str, Any]:
        """Get currency exchange rates"""
        
    def get_commodity_data(self) -> Dict[str, Any]:
        """Get commodity prices"""
```

## Phase 2D: Volatility & Sentiment Integration

### 1. VIX Data Integration

**Data Sources:**
- **NSE India** (India VIX)
- **Yahoo Finance** (^VIX for US VIX)

**Implementation Plan:**

```python
# New file: backend/data_sources/volatility_data.py
class VolatilityDataProvider:
    def __init__(self):
        self.vix_symbols = {
            'INDIA': '^INDIAVIX',
            'US': '^VIX'
        }
    
    def get_vix_data(self) -> Dict[str, Any]:
        """Get real VIX data"""
        # Current VIX, 30-day average, trend
        
    def get_fear_greed_index(self) -> Dict[str, Any]:
        """Calculate fear/greed index from market data"""
        # Use multiple indicators to calculate sentiment
```

### 2. Options Data Integration

**Data Sources:**
- **Zerodha KiteConnect** (options chain)
- **NSE India** (options data)

**Implementation Plan:**

```python
# New file: backend/data_sources/options_data.py
class OptionsDataProvider:
    def __init__(self):
        self.kite_client = None  # Will be initialized with Zerodha client
    
    def get_put_call_ratio(self, symbol: str) -> float:
        """Calculate put-call ratio"""
        # Fetch options chain and calculate ratio
        
    def get_options_flow(self, symbol: str) -> Dict[str, Any]:
        """Get options flow analysis"""
        # Analyze options activity for sentiment
```

## Phase 2E: Enhanced Market Context Provider

### 1. Unified Market Context Provider

**Implementation Plan:**

```python
# Updated file: backend/market_context.py
class EnhancedMarketContextProvider:
    def __init__(self):
        self.indices_provider = MarketIndicesProvider()
        self.sector_provider = SectorDataProvider()
        self.news_provider = NewsDataProvider()
        self.global_provider = GlobalMarketsProvider()
        self.volatility_provider = VolatilityDataProvider()
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)  # 15-minute cache
    
    def get_market_context(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """Get comprehensive real market context"""
        cache_key = f"market_context_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            context = {
                "timestamp": datetime.now().isoformat(),
                "market_overview": self._get_real_market_overview(),
                "sector_performance": self._get_real_sector_performance(symbol),
                "market_sentiment": self._get_real_market_sentiment(),
                "volatility_index": self._get_real_volatility_data(),
                "global_markets": self._get_real_global_markets_context()
            }
            
            self.cache[cache_key] = context
            return context
            
        except Exception as e:
            logger.error(f"Error getting real market context: {e}")
            # Fallback to calculated data
            return self._get_fallback_market_context()
    
    def _get_real_market_overview(self) -> Dict[str, Any]:
        """Get real market overview data"""
        nifty_data = self.indices_provider.get_nifty_50_data()
        sensex_data = self.indices_provider.get_sensex_data()
        breadth_data = self.indices_provider.get_market_breadth()
        
        return {
            "nifty_50": nifty_data,
            "sensex": sensex_data,
            "market_breadth": breadth_data,
            "data_source": "real_time"
        }
```

### 2. Data Quality & Fallback Strategy

**Implementation Plan:**

```python
# New file: backend/data_sources/data_quality.py
class DataQualityManager:
    def __init__(self):
        self.quality_thresholds = {
            'price_data': 0.95,  # 95% data completeness
            'news_data': 0.80,   # 80% data completeness
            'market_data': 0.90  # 90% data completeness
        }
    
    def validate_data_quality(self, data: Dict[str, Any], data_type: str) -> bool:
        """Validate data quality and completeness"""
        
    def get_fallback_data(self, data_type: str) -> Dict[str, Any]:
        """Get fallback data when real data is unavailable"""
        
    def log_data_quality_metrics(self, data: Dict[str, Any], source: str):
        """Log data quality metrics for monitoring"""
```

## Phase 2F: Configuration & Environment Setup

### 1. Environment Variables

**Required API Keys:**

```bash
# Market Data APIs
NEWS_API_KEY=your_news_api_key
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
TRADING_ECONOMICS_API_KEY=your_trading_economics_key

# Existing Zerodha keys
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret
```

### 2. Rate Limiting & Caching Strategy

**Implementation Plan:**

```python
# New file: backend/data_sources/rate_limiter.py
class APIRateLimiter:
    def __init__(self):
        self.limits = {
            'news_api': {'requests': 100, 'period': 86400},  # 100/day
            'alpha_vantage': {'requests': 500, 'period': 86400},  # 500/day
            'finnhub': {'requests': 60, 'period': 60}  # 60/minute
        }
        self.request_logs = {}
    
    def can_make_request(self, api_name: str) -> bool:
        """Check if we can make a request to the API"""
        
    def log_request(self, api_name: str):
        """Log a request to track rate limits"""
```

## Implementation Timeline

### Week 1-2: Market Indices Integration
- Implement MarketIndicesProvider
- Integrate Yahoo Finance API
- Add NSE India API integration
- Update market context provider

### Week 3-4: News & Events Integration
- Implement NewsDataProvider
- Integrate NewsAPI.org
- Add earnings calendar integration
- Implement economic calendar

### Week 5-6: Global Markets Integration
- Implement GlobalMarketsProvider
- Add currency and commodity data
- Integrate multiple global indices
- Calculate global correlations

### Week 7-8: Volatility & Sentiment Integration
- Implement VolatilityDataProvider
- Add VIX data integration
- Implement options data analysis
- Calculate fear/greed index

### Week 9-10: Testing & Optimization
- Implement data quality validation
- Add comprehensive error handling
- Optimize caching strategies
- Performance testing

## Benefits of Real Market Data Integration

### 1. Enhanced LLM Analysis
- **Real-time market context** for better decision making
- **Accurate sector performance** data
- **Live news correlation** with price movements
- **Global market impact** analysis

### 2. Improved Accuracy
- **Real VIX data** for volatility assessment
- **Actual market breadth** for trend confirmation
- **Live options flow** for sentiment analysis
- **Current economic events** for context

### 3. Better Risk Assessment
- **Real-time correlation** analysis
- **Live market sentiment** indicators
- **Current volatility regime** detection
- **Global market stress** indicators

### 4. Enhanced User Experience
- **Live market updates** during analysis
- **Real-time news alerts** for significant events
- **Current market status** indicators
- **Live global market** context

## Cost Considerations

### Free Tier Limits
- **NewsAPI**: 100 requests/day
- **Alpha Vantage**: 500 requests/day
- **Finnhub**: 60 requests/minute
- **Yahoo Finance**: No limits (unofficial API)

### Paid Options
- **NewsAPI Pro**: $449/month for 1000 requests/day
- **Alpha Vantage Premium**: $49.99/month for 1200 requests/minute
- **Finnhub Pro**: $9.99/month for 1000 requests/minute

### Optimization Strategies
- **Intelligent caching** (15-minute cache for market data)
- **Batch requests** for multiple symbols
- **Fallback mechanisms** when APIs are unavailable
- **Data quality monitoring** to ensure reliability

This comprehensive plan will transform the system from using mock data to real-time market data, significantly enhancing the LLM analysis capabilities and providing more accurate, actionable insights. 