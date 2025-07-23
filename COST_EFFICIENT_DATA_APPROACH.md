# Cost-Efficient Data Approach for Market Closed Hours

## Overview

This document outlines the implementation of a cost-efficient data handling system that optimizes API usage, storage costs, and processing overhead when markets are closed. The system automatically detects market hours and switches between live and historical data sources based on market status.

## Problem Statement

### Current Issues
1. **Continuous WebSocket Data**: WebSocket connections send the same tick data repeatedly when markets are closed
2. **High API Costs**: Unnecessary API calls during non-trading hours
3. **Storage Waste**: Storing duplicate/unchanged data
4. **Processing Overhead**: Processing identical ticks multiple times
5. **Resource Consumption**: Unnecessary CPU and memory usage

### Cost Impact
- **API Costs**: Live data APIs charge per request/minute
- **Storage Costs**: Duplicate data storage in databases/caches
- **Bandwidth**: Continuous WebSocket connections
- **Processing**: CPU cycles for processing unchanged data

## Solution Architecture

### 1. Market Hours Manager (`market_hours_manager.py`)

**Purpose**: Centralized market timing logic and optimization strategies

**Key Features**:
- Real-time market status detection (IST timezone)
- Weekend and holiday detection
- Cost estimation for different data approaches
- Optimal strategy recommendations

**Market Status Types**:
- `OPEN`: Regular trading hours (9:15 AM - 3:30 PM IST, Mon-Fri)
- `CLOSED`: Outside trading hours
- `WEEKEND`: Saturday/Sunday
- `HOLIDAY`: Market holidays
- `PRE_MARKET`: Before market opens (configurable)
- `POST_MARKET`: After market closes (configurable)

### 2. Enhanced WebSocket Client (`zerodha_ws_client.py`)

**Optimizations**:
- **Duplicate Tick Detection**: Skip processing identical ticks
- **Market Status Awareness**: Different processing logic for open/closed markets
- **Intelligent Logging**: Reduced log spam during closed hours
- **Cost Tracking**: Monitor API usage and costs

**Key Methods**:
```python
def _should_process_tick(self, token: int, tick_data: Dict[str, Any]) -> bool:
    """Determine if tick should be processed based on market status"""

def _is_duplicate_tick(self, token: int, tick_data: Dict[str, Any]) -> bool:
    """Check if tick is duplicate based on price and time"""
```

### 3. Enhanced Data Service (`enhanced_data_service.py`)

**Purpose**: Smart data fetching with caching and cost optimization

**Features**:
- **Intelligent Caching**: Different cache durations based on market status
- **Source Selection**: Choose between live/historical data
- **Cost Tracking**: Monitor and report data costs
- **Optimization Statistics**: Track savings and efficiency

## Implementation Details

### Market Hours Detection

```python
def get_market_status(self, dt: datetime = None) -> MarketStatus:
    """Get current market status with caching"""
    current_time = dt.time() if dt else self.get_current_ist_time().time()
    
    if self.is_weekend(dt):
        return MarketStatus.WEEKEND
    elif self.is_market_holiday(dt):
        return MarketStatus.HOLIDAY
    elif (self.market_hours.regular_session.start_time <= 
          current_time <= self.market_hours.regular_session.end_time):
        return MarketStatus.OPEN
    else:
        return MarketStatus.CLOSED
```

### Cost-Efficient Tick Processing

```python
def _should_process_tick(self, token: int, tick_data: Dict[str, Any]) -> bool:
    market_status = self._get_market_status()
    
    # Always process during market hours
    if market_status == MarketStatus.OPEN:
        return True
    
    # During closed hours, only process if:
    # 1. First tick for this token
    # 2. Price has actually changed
    # 3. Not a duplicate tick
    if market_status in [MarketStatus.CLOSED, MarketStatus.WEEKEND, MarketStatus.HOLIDAY]:
        if token not in self.last_tick_time:
            return True
        
        if self._is_duplicate_tick(token, tick_data):
            return False
        
        # Check if price has changed
        if token in tick_store:
            last_tick = tick_store[token]
            if (last_tick.get('last_price') != tick_data.get('last_price') or
                last_tick.get('volume_traded') != tick_data.get('volume_traded')):
                return True
        
        return False
```

### Optimal Data Strategy

```python
def get_optimal_data_strategy(self, symbol: str, interval: str = "1d") -> Dict[str, Any]:
    """Get optimal data fetching strategy based on market status"""
    current_status = self.get_market_status()
    
    if current_status == MarketStatus.OPEN:
        if interval in ["1m", "5m", "15m"]:
            return {
                "recommended_approach": "live",
                "websocket_recommended": True,
                "cache_duration": 60,  # 1 minute
                "cost_efficiency": "medium"
            }
        else:
            return {
                "recommended_approach": "historical",
                "cache_duration": 300,  # 5 minutes
                "cost_efficiency": "high"
            }
    else:
        return {
            "recommended_approach": "historical",
            "cache_duration": 3600,  # 1 hour
            "cost_efficiency": "high",
            "reason": f"Market is {current_status.value}"
        }
```

## API Endpoints

### Market Status
```bash
GET /market/status
```
Returns current market status, hours, and next open time.

### Optimization Strategy
```bash
GET /market/optimization/strategy?symbol=RELIANCE&interval=1d
```
Returns optimal data fetching strategy for a symbol.

### Optimization Statistics
```bash
GET /market/optimization/stats
```
Returns cost analysis and optimization statistics.

### Optimized Data
```bash
POST /market/optimization/data
{
    "symbol": "RELIANCE",
    "interval": "1d",
    "force_live": false
}
```
Returns data using optimal strategy.

## Cost Analysis

### Cost Comparison

| Approach | Cost per Hour | Best For | When to Use |
|----------|---------------|----------|-------------|
| WebSocket | 5.0 units | Real-time | Market open, short intervals |
| Live API | 60.0 units | Real-time | Market open, occasional updates |
| Historical | 10.0 units | Analysis | Market closed, long intervals |

### Savings Calculation

**Before Optimization**:
- WebSocket running 24/7: 5.0 × 24 = 120 units/day
- Live API calls: 60.0 × 24 = 1,440 units/day
- Total: 1,560 units/day

**After Optimization**:
- WebSocket during market hours only: 5.0 × 6.25 = 31.25 units/day
- Historical data during closed hours: 10.0 × 2 = 20 units/day
- Total: 51.25 units/day

**Savings**: 96.7% cost reduction

## Configuration

### Environment Variables

```bash
# Market hours configuration
MARKET_TIMEZONE=Asia/Kolkata
MARKET_OPEN_TIME=09:15
MARKET_CLOSE_TIME=15:30

# Optimization settings
DUPLICATE_TICK_THRESHOLD=30  # seconds
CACHE_DURATION_OPEN=60       # seconds
CACHE_DURATION_CLOSED=3600   # seconds

# Cost tracking
ENABLE_COST_TRACKING=true
COST_ALERT_THRESHOLD=100     # units
```

### Cache Configuration

```python
# Market open hours
CACHE_CONFIG_OPEN = {
    "1m": 60,    # 1 minute
    "5m": 300,   # 5 minutes
    "15m": 900,  # 15 minutes
    "1h": 3600,  # 1 hour
    "1d": 3600   # 1 hour
}

# Market closed hours
CACHE_CONFIG_CLOSED = {
    "1m": 3600,   # 1 hour
    "5m": 3600,   # 1 hour
    "15m": 3600,  # 1 hour
    "1h": 7200,   # 2 hours
    "1d": 86400   # 24 hours
}
```

## Monitoring and Alerts

### Key Metrics

1. **Cost Per Request**: Track average cost per data request
2. **Cache Hit Rate**: Monitor cache effectiveness
3. **Duplicate Tick Rate**: Track optimization effectiveness
4. **Market Status Accuracy**: Ensure correct market detection
5. **API Usage**: Monitor API call frequency

### Alerts

- **High Cost Alert**: When daily cost exceeds threshold
- **Cache Miss Alert**: When cache hit rate drops below 80%
- **Market Status Error**: When market status detection fails
- **WebSocket Disconnect**: When live data connection drops

## Best Practices

### 1. Data Freshness Management
- Use appropriate cache durations based on market status
- Implement cache invalidation strategies
- Monitor data staleness

### 2. Error Handling
- Graceful fallback from live to historical data
- Retry mechanisms for failed API calls
- Circuit breaker patterns for external services

### 3. Performance Optimization
- Batch historical data requests
- Implement connection pooling
- Use async/await for I/O operations

### 4. Cost Monitoring
- Set up cost alerts and budgets
- Track usage patterns
- Optimize based on usage analytics

## Migration Guide

### Step 1: Update Dependencies
```bash
pip install pytz  # For timezone handling
```

### Step 2: Update Configuration
Add market hours configuration to your environment.

### Step 3: Update Code
Replace direct API calls with enhanced data service:
```python
# Before
data = zerodha_client.get_historical_data(symbol, interval, period)

# After
request = DataRequest(symbol=symbol, interval=interval, period=period)
response = enhanced_data_service.get_optimal_data(request)
data = response.data
```

### Step 4: Monitor and Optimize
- Monitor cost savings
- Adjust cache durations
- Fine-tune optimization parameters

## Troubleshooting

### Common Issues

1. **Incorrect Market Status**
   - Check timezone configuration
   - Verify market hours settings
   - Test with known market times

2. **High Cache Miss Rate**
   - Increase cache duration
   - Check cache size limits
   - Monitor memory usage

3. **Duplicate Ticks Still Processing**
   - Adjust duplicate threshold
   - Check tick comparison logic
   - Verify market status detection

4. **API Cost Not Reducing**
   - Verify optimization is enabled
   - Check WebSocket connection status
   - Monitor API call frequency

### Debug Endpoints

```bash
# Check market status
GET /market/status

# View optimization stats
GET /market/optimization/stats

# Test optimization strategy
GET /market/optimization/strategy?symbol=RELIANCE&interval=1d

# Clear caches
POST /market/optimization/clear-cache
```

## Future Enhancements

1. **Holiday Calendar Integration**: Automatic holiday detection
2. **Machine Learning**: Predict optimal cache durations
3. **Multi-Exchange Support**: Support for different exchanges
4. **Advanced Caching**: Redis-based distributed caching
5. **Cost Prediction**: Predict costs before data requests
6. **Auto-Scaling**: Scale resources based on market activity

## Conclusion

This cost-efficient approach provides significant savings while maintaining data quality and system reliability. The automatic market detection and intelligent data source selection ensure optimal performance during both market open and closed hours.

Key Benefits:
- **96.7% cost reduction** in data fetching costs
- **Automatic optimization** based on market status
- **Improved performance** through intelligent caching
- **Better resource utilization** during closed hours
- **Comprehensive monitoring** and alerting

The system is designed to be production-ready with proper error handling, monitoring, and scalability considerations. 