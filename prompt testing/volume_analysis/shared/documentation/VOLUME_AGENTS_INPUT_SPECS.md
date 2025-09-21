# Volume Analysis Agents - Input Specifications

## 🎯 **Agent Input Requirements Overview**

Each specialized volume agent requires specific data inputs and chart visualizations to perform their focused analysis effectively.

---

## **1. Volume Confirmation Agent** 🔄

### **Data Inputs Required:**
- **Price-Volume Correlation Data**: Last 30-60 days
- **Recent Price Movements**: Daily OHLC data with corresponding volume
- **Volume Moving Averages**: 10, 20, 50-day volume averages
- **Trend Identification**: Price trend direction and strength

### **Chart Visualization:**
- **Primary**: Candlestick chart with volume bars
- **Overlays**: Volume moving average line
- **Highlights**: Volume spikes during price movements
- **Time Frame**: 30-90 days focus

### **Context Data Structure:**
```json
{
  "price_volume_correlation": {
    "correlation_coefficient": 0.695,
    "significance_level": "high",
    "trend_direction": "upward"
  },
  "recent_movements": [
    {"date": "2024-09-15", "price_change": 2.3, "volume_ratio": 1.8, "confirmation": true}
  ],
  "volume_averages": {
    "volume_10d_avg": 1500000,
    "volume_20d_avg": 1650000,
    "current_volume": 2214708
  }
}
```

---

## **2. Volume Anomaly Detection Agent** 📈

### **Data Inputs Required:**
- **Historical Volume Percentiles**: 90-day rolling percentiles
- **Volume Spike Detection**: Volumes >2x, >3x, >5x average
- **Anomaly Context**: Price context during volume spikes
- **Frequency Analysis**: Pattern of anomalies over time

### **Chart Visualization:**
- **Primary**: Volume histogram with percentile bands
- **Overlays**: Volume moving average and spike thresholds
- **Highlights**: Color-coded anomalies by significance
- **Time Frame**: 60-180 days for pattern recognition

### **Context Data Structure:**
```json
{
  "volume_statistics": {
    "volume_mean": 1500000,
    "volume_std": 750000,
    "percentile_90": 2250000,
    "percentile_95": 3000000,
    "percentile_99": 5000000
  },
  "detected_anomalies": [
    {
      "date": "2024-09-10",
      "volume": 4500000,
      "ratio_to_average": 3.0,
      "price_context": "breakout_up",
      "significance": "high"
    }
  ],
  "anomaly_frequency": {
    "last_30_days": 3,
    "last_90_days": 10,
    "pattern": "increasing"
  }
}
```

---

## **3. Institutional Activity Agent** 🏛️

### **Data Inputs Required:**
- **Volume Profile Data**: Volume-at-price distribution
- **Large Block Analysis**: Transactions >avg block size
- **Accumulation/Distribution Indicators**: Volume during consolidation
- **Time-based Volume Patterns**: Intraday vs closing volume

### **Chart Visualization:**
- **Primary**: Volume profile chart (horizontal volume bars)
- **Secondary**: Price chart with accumulation/distribution zones
- **Overlays**: Point of Control (POC) and Value Area
- **Time Frame**: 90-180 days for institutional pattern recognition

### **Context Data Structure:**
```json
{
  "volume_profile": {
    "point_of_control": 2450.0,
    "value_area_high": 2520.0,
    "value_area_low": 2380.0,
    "volume_nodes": [
      {"price": 2450.0, "volume": 15000000, "significance": "high"}
    ]
  },
  "institutional_indicators": {
    "quiet_accumulation_score": 75,
    "distribution_pressure": "low",
    "smart_money_sentiment": "bullish",
    "large_block_frequency": "above_average"
  },
  "activity_analysis": {
    "consolidation_volume": "elevated",
    "breakout_volume": "confirming",
    "institutional_phase": "accumulation"
  }
}
```

---

## **4. Volume-Based Support/Resistance Agent** 📊

### **Data Inputs Required:**
- **Volume-at-Price (VAP) Data**: Complete volume profile
- **Historical Support/Resistance**: Past price levels with volume
- **Level Testing Data**: How levels have held/broken
- **Current Position Analysis**: Price relative to volume levels

### **Chart Visualization:**
- **Primary**: Price chart with volume-based horizontal lines
- **Secondary**: Volume profile overlay showing high-volume zones
- **Highlights**: Level strength indicated by line thickness/color
- **Time Frame**: 180-365 days for level validation

### **Context Data Structure:**
```json
{
  "volume_levels": {
    "support_levels": [
      {
        "price": 2380.0,
        "volume_strength": 12000000,
        "tests": 3,
        "reliability": "high",
        "distance_from_current": -2.5
      }
    ],
    "resistance_levels": [
      {
        "price": 2620.0,
        "volume_strength": 8500000,
        "tests": 2,
        "reliability": "medium",
        "distance_from_current": 5.8
      }
    ]
  },
  "current_analysis": {
    "current_price": 2478.0,
    "nearest_support": 2380.0,
    "nearest_resistance": 2520.0,
    "position_type": "between_levels"
  },
  "level_quality": {
    "average_strength": "high",
    "recent_validation": true,
    "breakout_success_rate": 0.75
  }
}
```

---

## **5. Volume Trend Momentum Agent** 🚀

### **Data Inputs Required:**
- **Volume Trend Analysis**: Linear regression on volume data
- **Momentum Indicators**: Rate of change in volume trends
- **Comparative Data**: Volume vs historical averages
- **Cycle Analysis**: Volume expansion/contraction phases

### **Chart Visualization:**
- **Primary**: Volume trend line chart with regression channel
- **Secondary**: Volume momentum oscillator
- **Overlays**: Volume cycle phases and trend strength indicators
- **Time Frame**: 90-180 days for trend analysis

### **Context Data Structure:**
```json
{
  "trend_analysis": {
    "trend_direction": "increasing",
    "trend_slope": 0.125,
    "r_squared": 0.78,
    "trend_strength": "strong",
    "duration_days": 45
  },
  "momentum_indicators": {
    "current_momentum": "accelerating",
    "momentum_change": 15.5,
    "sustainability_score": 82,
    "exhaustion_risk": "low"
  },
  "cycle_analysis": {
    "current_phase": "expansion",
    "phase_maturity": "middle",
    "next_phase": "mature_expansion",
    "cycle_position": 0.6
  },
  "comparative_metrics": {
    "vs_historical_avg": 1.35,
    "vs_sector": 1.12,
    "percentile_rank": 78
  }
}
```

---

## 📋 **Implementation Summary**

### **Data Processing Pipeline:**
1. **Raw Data Collection**: OHLCV data for specified timeframes
2. **Agent-Specific Processing**: Calculate required metrics for each agent
3. **Chart Generation**: Create specialized visualizations per agent
4. **Context Formatting**: Structure data for each agent's prompt

### **Chart Generation Strategy:**
- **Confirmation Agent**: Standard price-volume chart
- **Anomaly Agent**: Volume spike detection chart  
- **Institutional Agent**: Volume profile chart
- **Support/Resistance Agent**: Price levels with volume validation
- **Momentum Agent**: Volume trend analysis chart

### **Testing Framework Requirements:**
- Separate test files for each agent
- Agent-specific data preparation functions
- Specialized chart generation methods
- Independent prompt formatting per agent

**Next Steps**: 
1. Create data processing functions for each agent
2. Implement specialized chart generation methods
3. Build agent-specific testing framework
4. Create integration layer for combining agent outputs

Each agent now has clear, focused requirements and can be developed independently while maintaining the overall volume analysis ecosystem.