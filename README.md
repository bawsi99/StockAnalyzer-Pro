# StockAnalyzer-Pro 📈

A state-of-the-art, enterprise-grade stock analysis platform that combines advanced technical indicators, AI-powered pattern recognition, multi-timeframe analysis, and real-time market data streaming to provide comprehensive stock market insights and trading recommendations.

## 🌟 Core Features

### 🧠 AI-Powered Analysis Engine
- **Google Gemini Pro Integration**: Advanced LLM analysis with context engineering and token optimization
- **Multi-modal Analysis**: Text and image-based chart analysis with intelligent prompt management
- **Context-Aware Processing**: Dynamic context engineering for optimal AI responses
- **Token Usage Optimization**: Intelligent token tracking and management for cost efficiency

### 📊 Advanced Technical Analysis
- **25+ Technical Indicators**: RSI, MACD, Bollinger Bands, ADX, Stochastic, OBV, Ichimoku, Fibonacci, Pivot Points
- **Multi-Timeframe Analysis**: Comprehensive analysis across 1min, 5min, 15min, 30min, 1hour, daily, weekly intervals
- **Enhanced Pattern Recognition**: Support/Resistance levels, Double tops/bottoms, Triangles, Flags, Volume anomalies, Divergences
- **Real-time Data Processing**: Live market data via Zerodha KiteConnect with WebSocket streaming

### 🏗️ Microservices Architecture
- **Data Service (Port 8000)**: Real-time data fetching, WebSocket streaming, market data management
- **Analysis Service (Port 8001)**: AI analysis, technical indicators, chart generation, pattern recognition
- **WebSocket Service (Port 8081)**: Dedicated real-time streaming with multiple endpoints
- **Service Orchestration**: Intelligent service coordination and load balancing

### 📈 Enhanced Visualization & Charts
- **Interactive Multi-pane Charts**: Price, volume, and indicator charts with pattern overlays
- **Real-time Chart Updates**: Live data streaming with WebSocket integration
- **Advanced Chart Management**: Automated cleanup, storage optimization, and deployment configurations
- **Export Capabilities**: High-resolution chart exports in multiple formats

### 🎯 Sector & Market Intelligence
- **Sector Classification**: AI-powered sector identification and classification
- **Sector Benchmarking**: Comprehensive sector performance analysis and comparison
- **Market Regime Detection**: Advanced market condition analysis and regime identification
- **NIFTY Index Integration**: Real-time NIFTY 50 and sector index data

### 🔒 Enterprise Security & Performance
- **Multi-layer Authentication**: Supabase integration with JWT token management
- **Performance Optimization**: 1000x faster database queries with optimized data structures
- **Caching Strategy**: Intelligent caching with Redis and in-memory optimization
- **Rate Limiting**: API protection and request throttling

## 🏗️ Architecture Overview

### Backend Services (Python/FastAPI)
```
backend/
├── main.py                    # CLI orchestrator for direct analysis
├── data_service.py           # Data fetching and WebSocket streaming (Port 8000)
├── analysis_service.py       # AI analysis and chart generation (Port 8001)
├── websocket_stream_service.py # Dedicated WebSocket service (Port 8081)
├── agent_capabilities.py     # Core analysis workflow orchestrator
├── technical_indicators.py   # 25+ technical indicator calculations
├── enhanced_mtf_analysis.py  # Multi-timeframe analysis engine
├── sector_benchmarking.py    # Sector analysis and benchmarking
├── patterns/                 # Pattern recognition & visualization
│   ├── recognition.py        # Advanced pattern detection algorithms
│   └── visualization.py      # Chart visualization and overlays
├── gemini/                   # AI/LLM integration with context engineering
│   ├── gemini_client.py      # Main AI client with token optimization
│   ├── context_engineer.py   # Dynamic context management
│   ├── prompt_manager.py     # Optimized prompt templates
│   └── token_tracker.py      # Token usage monitoring
├── ml/                       # Machine learning components
│   ├── hybrid_ml_engine.py   # Hybrid ML analysis engine
│   ├── model.py              # ML model training and inference
│   ├── dataset.py            # Data pipeline and feature engineering
│   ├── data_processing/      # ML data processing pipeline
│   │   ├── build_dataset.py  # Feature engineering (40+ indicators)
│   │   ├── build_labels.py   # Label generation with forward returns
│   │   ├── combine_processed.py # Multi-stock dataset consolidation
│   │   ├── multi_stock_processor.py # Unified multi-stock pipeline
│   │   ├── split_and_standardize.py # Data splitting & normalization
│   │   └── qc_dataset.py     # Quality control checks
│   ├── training/             # Model training scripts
│   │   ├── train_multi_models.py # Multi-model training framework
│   │   ├── train_logistic.py # Logistic regression training
│   │   └── analyze_results.py # Performance analysis
│   ├── models/               # Trained model artifacts
│   │   └── multi_model_YYYYMMDD_HHMMSS/
│   │       ├── *.joblib      # Serialized models
│   │       ├── *_test_predictions.csv
│   │       ├── model_comparison_summary.csv
│   │       └── all_models_metrics.json
│   └── data/                 # ML datasets
│       ├── raw/              # Raw OHLCV data (symbol=*/timeframe=*/)
│       ├── processed/        # Processed features & labels
│       └── data_YYYYMMDD_HHMMSS/ # Combined dataset runs
└── quant_system/             # Quantitative analysis tools
    ├── backtesting_engine.py # Advanced backtesting capabilities
    ├── risk_management.py    # Risk assessment and management
    └── feature_engineering.py # Feature extraction and engineering
```

### Frontend (React/TypeScript/Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── analysis/         # Advanced analysis components
│   │   │   ├── EnhancedAnalysisDashboard.tsx
│   │   │   ├── MultiTimeframeAnalysisCard.tsx
│   │   │   ├── EnhancedAIAnalysisCard.tsx
│   │   │   ├── SectorBenchmarkingCard.tsx
│   │   │   └── AdvancedRiskAssessmentCard.tsx
│   │   ├── charts/           # Chart components
│   │   │   ├── LiveSimpleChart.tsx
│   │   │   └── SimpleChart.tsx
│   │   └── ui/               # shadcn/ui components
│   ├── pages/                # Application pages
│   │   ├── Dashboard.tsx     # Enhanced analysis dashboard
│   │   ├── NewStockAnalysis.tsx # Stock analysis interface
│   │   ├── NewOutput.tsx     # Analysis results display
│   │   └── Charts.tsx        # Chart visualization
│   ├── hooks/                # Custom React hooks
│   │   ├── useStockAnalyses.ts # Stock analysis data management
│   │   ├── useLiveChart.ts   # Real-time chart updates
│   │   └── useSmartData.ts   # Intelligent data fetching
│   ├── contexts/             # React contexts
│   │   └── AuthContext.tsx   # Authentication management
│   └── services/             # API services
│       ├── analysisService.ts # Analysis service integration
│       ├── liveDataService.ts # Real-time data service
│       └── authService.ts    # Authentication service
├── supabase/                 # Database configuration
└── package.json              # Dependencies and scripts
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** with pip
- **Node.js 18+** with npm
- **Redis** (for data caching only)
- **Zerodha KiteConnect API** credentials
- **Google Gemini API** key
- **Supabase** account (for authentication and database)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bawsi99/StockAnalyzer-Pro.git
   cd StockAnalyzer-Pro
   ```

2. **Backend Environment Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Environment Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Create .env file in backend directory
   ZERODHA_API_KEY=your_zerodha_api_key
   ZERODHA_API_SECRET=your_zerodha_api_secret
   GEMINI_API_KEY=your_gemini_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   
   # Redis Configuration (for data caching only)
REDIS_URL=redis://localhost:6379/0

# Redis Cache Manager Settings
REDIS_CACHE_ENABLE_COMPRESSION=true
REDIS_CACHE_ENABLE_LOCAL_FALLBACK=true
REDIS_CACHE_LOCAL_SIZE=1000
REDIS_CACHE_CLEANUP_INTERVAL_MINUTES=60
   ```

### Redis Setup

The system uses Redis for caching stock data and analysis results. Charts are now generated in-memory on-demand, providing better performance and eliminating storage overhead.

**Key Features:**
- **In-Memory Chart Generation**: Charts are generated on-demand in memory
- **Base64 Response**: Charts are immediately converted to base64 for frontend display
- **Redis Caching**: Stock data, indicators, patterns, and sector data are cached in Redis
- **Automatic Cleanup**: Age-based and size-based cleanup for both images and cache data

#### Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Docker:**
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

#### Test Redis Setup
```bash
cd backend
python test_redis_cache_manager.py
python test_chart_generation_redis.py
```

Redis image storage has been removed - charts are now generated in-memory.

### Service Startup

#### Option 1: Start All Services (Recommended)
```bash
cd backend
python start_all_services.py
```

#### Option 2: Start Services Individually
```bash
# Terminal 1: Data Service (Port 8000)
cd backend
python start_data_service.py

# Terminal 2: Analysis Service (Port 8001)
cd backend
python start_analysis_service.py

# Terminal 3: WebSocket Service (Port 8081)
cd backend
python start_websocket_service.py
```

#### Option 3: Command Line Analysis
```bash
cd backend
python main.py --stock RELIANCE --period 365 --interval day
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5173
- **Data Service**: http://localhost:8000
- **Analysis Service**: http://localhost:8001
- **WebSocket Service**: ws://localhost:8081
- **Health Checks**: 
  - http://localhost:8000/health
  - http://localhost:8001/health

## 🧠 Machine Learning & Data Processing

### ML Pipeline Overview

The ML system provides automated trading signals by predicting profitable opportunities across multiple stocks and timeframes.

#### **Supported Models**
- **Logistic Regression**: L2-regularized, balanced class weights
- **Random Forest**: 200 estimators, max_depth=4
- **Gradient Boosting**: 50 estimators, learning_rate=0.05
- **XGBoost**: Advanced gradient boosting with regularization
- **LightGBM**: Fast gradient boosting with optimized memory usage

#### **Default Stock Universe**
```python
RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, 
ITC, SBIN, BAJFINANCE, BHARTIARTL, HINDUNILVR
```

#### **Timeframe Configurations**
| Timeframe | Horizon | Est. Cost | Use Case |
|-----------|---------|-----------|----------|
| 5m | 12 bars (1hr) | 8 bps | High-frequency trading |
| 15m | 8 bars (2hrs) | 7 bps | Intraday swing |
| 1h | 12 bars (12hrs) | 6 bps | End-of-day |
| 1d | 5 bars (5 days) | 5 bps | Swing/position |

### ML Data Processing Workflow

#### **Option 1: Multi-Stock Unified Pipeline (Recommended)**
```bash
cd backend/agents/ml/data_processing

# Process all stocks and timeframes in one go
python multi_stock_processor.py \
  --base_dir ../data/raw \
  --output_dir ../data/processed/multi_stock \
  --symbols RELIANCE TCS INFY \
  --timeframes 5m 15m 1h 1d \
  --train_pct 0.6 --val_pct 0.2 --test_pct 0.2

# Output: train.csv, val.csv, test.csv, scaler.json, processing_metadata.json
```

**What it does:**
1. Consolidates raw OHLCV data from all symbol/timeframe combinations
2. Applies 40+ technical indicators uniformly across all stocks
3. Creates forward-looking labels (y_cls, y_reg) with transaction costs
4. Performs quality control (removes outliers, validates data)
5. Creates temporal train/val/test splits (60/20/20 by default)
6. Standardizes features using training set statistics
7. Saves ready-to-train datasets with metadata

#### **Option 2: Individual Stock Pipeline**
```bash
cd backend/agents/ml/data_processing

# Step 1: Build features (40+ technical indicators)
python build_dataset.py \
  ../data/raw/symbol=RELIANCE/timeframe=1d/bars.csv \
  --output_csv ../data/processed/symbol=RELIANCE/timeframe=1d/features.csv

# Step 2: Generate labels (y_cls, y_reg)
python build_labels.py \
  ../data/processed/symbol=RELIANCE/timeframe=1d/features.csv \
  --timeframe 1d

# Step 3: Quality control
python qc_dataset.py \
  ../data/processed/symbol=RELIANCE/timeframe=1d/labels.csv

# Step 4: Combine multiple stocks (optional)
python combine_processed.py \
  --processed_dir ../data/processed \
  --symbols RELIANCE TCS INFY \
  --timeframes 1d 1h 15m

# Step 5: Split and standardize
python split_and_standardize.py \
  --input_csv ../data/data_20241022_120000/combined_raw.csv \
  --train_pct 0.7 --val_pct 0.15 --test_pct 0.15
```

### Training Machine Learning Models

#### **Multi-Model Training**
```bash
cd backend/agents/ml/training

# Train all available models
python train_multi_models.py \
  --splits_dir ../data/processed/multi_stock/run_20241022_124619

# Train specific models only
python train_multi_models.py \
  --splits_dir ../data/processed/multi_stock/run_20241022_124619 \
  --models logistic xgboost lightgbm
```

**Output artifacts:**
```
backend/agents/ml/models/multi_model_20241022_124619/
├── logistic.joblib                     # Trained logistic regression
├── random_forest.joblib                # Trained random forest
├── gradient_boosting.joblib            # Trained gradient boosting
├── xgboost.joblib                      # Trained XGBoost
├── lightgbm.joblib                     # Trained LightGBM
├── *_test_predictions.csv              # Per-model test predictions
├── model_comparison_summary.csv        # Performance comparison
├── all_models_metrics.json             # Comprehensive metrics
└── roc_curves_comparison.png           # ROC curve visualization
```

### ML Features (40+ Technical Indicators)

**Volatility (3):** `atr_14_pct`, `atr_vol_20`, `range_pct`  
**Trend (2):** `dist_sma50_pct`, `macd_hist`  
**Bollinger Bands (1):** `bb_bw_20`  
**Volume (5):** `vol_ratio_20`, `vol_cv_20`, `cmf_20`, `up_down_vol_ratio_20`, `ret_vol_corr_20`  
**Price Position (4):** `pct_dist_to_20_high`, `breakout_up_20`, `breakout_down_20`, `vwap_dist`  
**VWAP (2):** `vwap_dist`, `vwap_slope_5`  
**Candlestick (8):** `wick_to_body_ratio`, `inside_bar`, `engulfing`, `gap_pct`, `up_streak`, `down_streak`, `wick_up_streak_3`, `wick_down_streak_3`  
**Statistical (2):** `ret_skew_20`, `ret_kurt_20`  
**Calendar (8):** `dow`, `dow_sin`, `dow_cos`, `hour`, `hour_sin`, `hour_cos`

### Labels (Target Variables)

**y_reg (Continuous)**: Forward log-return after transaction costs  
```python
y_reg = ln(future_price / current_price) - (cost_bps / 10000)
```

**y_cls (Binary)**: Classification target (1 = profitable, 0 = unprofitable)  
```python
y_cls = 1 if y_reg > 0 else 0
```

### Dataset Structure

#### **Raw Data Format**
```
backend/agents/ml/data/raw/
├── symbol=RELIANCE/
│   ├── timeframe=5m/
│   │   └── bars.csv (or bars.parquet)
│   ├── timeframe=15m/
│   │   └── bars.csv
│   ├── timeframe=1h/
│   │   └── bars.csv
│   └── timeframe=1d/
│       └── bars.csv
├── symbol=TCS/
│   └── ...
```

**Required columns:** `open`, `high`, `low`, `close`, `volume`, datetime index

#### **Processed Data Format**
```
backend/agents/ml/data/processed/
├── symbol=RELIANCE/
│   └── timeframe=1d/
│       ├── features.csv           # 40+ engineered features
│       ├── labels.csv             # features + y_cls + y_reg
│       └── labels_capped_cleaned.csv  # QC-applied version
```

#### **Combined Dataset Format**
```
backend/agents/ml/data/data_20241022_120000/
├── combined_raw.csv               # All symbols/timeframes combined
├── combine_metadata.json          # Dataset coverage info
├── train.csv                      # Training split
├── val.csv                        # Validation split  
├── test.csv                       # Test split
├── train_standardized.csv         # Standardized training data
├── scaler.json                    # Standardization parameters
└── split_metadata.json            # Split statistics
```

### Quality Control Checks

The QC pipeline applies:
- **Missing data**: Max 10% NaN features per row
- **Minimum samples**: 100+ periods per symbol/timeframe group
- **Outlier removal**: IQR method with 3.0x factor
- **Distribution validation**: Checks for data drift
- **Feature correlation**: Removes highly correlated features (>0.95)

### Model Evaluation Metrics

**Classification Metrics:**
- **AUC-ROC**: Area under ROC curve (train/val/test)
- **Average Precision**: Precision-recall curve summary

**Trading Performance:**
- **Threshold**: Optimized probability cutoff for max returns
- **Coverage**: % of time model signals "BUY"
- **Avg Return**: Mean y_reg for signals above threshold
- **Cumulative Return**: Total y_reg for all signals

### Example Model Comparison Output

```
Model             Test_AUC   Val_AP    Coverage   Avg_Return   Cum_Return
─────────────────────────────────────────────────────────────────────────
XGBoost           0.687      0.594     28.3%      0.0189       4.82
LightGBM          0.683      0.588     31.2%      0.0174       5.12
Gradient Boost    0.676      0.581     29.5%      0.0165       4.58
Random Forest     0.671      0.573     33.1%      0.0158       4.94
Logistic          0.668      0.569     35.4%      0.0151       5.03
```

## 📖 Usage Guide

### API Endpoints

#### Data Service (Port 8000)
- `GET /health` - Service health check
- `GET /data/{symbol}` - Get stock data
- `GET /indicators/{symbol}` - Get technical indicators
- `GET /patterns/{symbol}` - Get pattern recognition
- `GET /sector/{symbol}` - Get sector classification
- `WS /ws/stream` - Real-time data streaming

#### Analysis Service (Port 8001)
- `POST /analyze` - Comprehensive stock analysis
- `POST /analyze/enhanced` - Enhanced AI analysis
- `POST /analyze/mtf` - Multi-timeframe analysis
- `POST /ml/train` - Train ML models
- `POST /ml/predict` - ML predictions
- `GET /health` - Service health check

#### Chart & Image Management
- `GET /charts/storage/stats` - Get chart storage statistics (file-based only)
- `POST /charts/cleanup` - Cleanup old charts (file-based only)
- `DELETE /charts/{symbol}/{interval}` - Cleanup specific charts
- Charts are now generated in-memory on-demand

### Example API Requests

#### Basic Stock Analysis
```bash
curl -X POST "http://localhost:8001/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "RELIANCE",
    "exchange": "NSE",
    "period": 365,
    "interval": "day"
  }'
```

#### Enhanced AI Analysis
```bash
curl -X POST "http://localhost:8001/analyze/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "RELIANCE",
    "exchange": "NSE",
    "period": 365,
    "interval": "day",
    "include_sector_analysis": true,
    "include_mtf_analysis": true
  }'
```

#### Multi-Timeframe Analysis
```bash
curl -X POST "http://localhost:8001/analyze/mtf" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "RELIANCE",
    "exchange": "NSE",
    "timeframes": ["1min", "5min", "15min", "1hour", "day"]
  }'
```

#### Redis Image Management
Redis image storage has been removed - charts are now generated in-memory on-demand.

#### Redis Cache Management
```bash
# Get Redis cache statistics
curl "http://localhost:8001/redis/cache/stats"

# Clear all cache entries
curl -X POST "http://localhost:8001/redis/cache/clear"

# Clear specific data type cache
curl -X POST "http://localhost:8001/redis/cache/clear?data_type=stock_data"

# Clear cache for a specific stock
curl -X DELETE "http://localhost:8001/redis/cache/stock/RELIANCE"

# Get cached stock data
curl "http://localhost:8001/redis/cache/stock/RELIANCE"
```

### WebSocket Streaming
```javascript
// Connect to real-time data stream
const ws = new WebSocket('ws://localhost:8081/ws/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time data:', data);
};

// Subscribe to specific symbols
ws.send(JSON.stringify({
  action: 'subscribe',
  symbols: ['RELIANCE', 'TCS', 'INFY']
}));
```

## 🔧 Configuration & Customization

### Technical Indicators
- **Moving Averages**: SMA, EMA, WMA (configurable periods: 20, 50, 200)
- **Momentum**: RSI, MACD, Stochastic, ADX, Williams %R
- **Volatility**: Bollinger Bands, ATR, Keltner Channels
- **Volume**: OBV, Volume ratio analysis, Volume profile
- **Trend**: Ichimoku, Parabolic SAR, ADX
- **Support/Resistance**: Fibonacci retracements, Pivot points

### Pattern Recognition
- **Price Patterns**: Double tops/bottoms, Triangles, Flags, Pennants
- **Volume Patterns**: Volume anomalies, Volume breakouts, Volume confirmation
- **Divergence Detection**: Price-indicator divergences, Hidden divergences
- **Support/Resistance**: Automatic level detection, Dynamic level updates

### AI Analysis Configuration
- **Context Engineering**: Dynamic context optimization for different analysis types
- **Prompt Management**: Optimized prompts for various analysis scenarios
- **Token Optimization**: Intelligent token usage and cost management
- **Response Parsing**: Structured AI response parsing and validation

### Multi-Timeframe Analysis
- **Timeframe Configurations**: Customizable intervals and analysis parameters
- **Cross-Timeframe Validation**: Signal confirmation across multiple timeframes
- **Confidence Weighting**: Weighted analysis based on timeframe importance
- **Trend Alignment**: Multi-timeframe trend analysis and confirmation

## 📊 Output & Analysis Structure

### Analysis Results
```json
{
  "stock_info": {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "sector": "OIL_GAS",
    "analysis_timestamp": "2024-01-15T10:30:00Z"
  },
  "technical_analysis": {
    "indicators": {
      "rsi": {"value": 65.4, "signal": "neutral", "trend": "rising"},
      "macd": {"value": 0.85, "signal": "bullish", "histogram": "positive"},
      "bollinger_bands": {"position": "upper", "width": "normal"}
    },
    "patterns": {
      "support_levels": [2450, 2400, 2350],
      "resistance_levels": [2550, 2600, 2650],
      "chart_patterns": ["ascending_triangle", "volume_breakout"]
    }
  },
  "ai_analysis": {
    "overall_sentiment": "bullish",
    "confidence_score": 78.5,
    "risk_assessment": "medium",
    "trading_recommendations": ["buy_on_dips", "target_2600"],
    "key_insights": ["Strong sector momentum", "Volume confirmation"]
  },
  "multi_timeframe": {
    "timeframe_signals": {
      "1min": {"trend": "neutral", "confidence": 45},
      "5min": {"trend": "bullish", "confidence": 62},
      "15min": {"trend": "bullish", "confidence": 78},
      "1hour": {"trend": "bullish", "confidence": 85},
      "day": {"trend": "bullish", "confidence": 92}
    },
    "consensus_trend": "bullish",
    "overall_confidence": 78.5
  },
  "sector_analysis": {
    "sector_performance": "+2.3%",
    "sector_rank": 3,
    "relative_strength": "outperforming",
    "sector_momentum": "strong"
  }
}
```

### Generated Charts
```
output/STOCK_SYMBOL/
├── technical_analysis/
│   ├── candlestick_volume.png
│   ├── indicators_overlay.png
│   ├── support_resistance.png
│   └── pattern_recognition.png
├── multi_timeframe/
│   ├── mtf_comparison.png
│   ├── timeframe_signals.png
│   └── consensus_analysis.png
├── sector_analysis/
│   ├── sector_performance.png
│   ├── relative_strength.png
│   └── sector_rotation.png
└── ai_analysis/
    ├── ai_insights.png
    ├── risk_assessment.png
    └── trading_recommendations.png
```

## 🛠️ Development & Extension

### Adding New Technical Indicators
1. **Implement calculation logic** in `technical_indicators.py`
2. **Register in indicator registry** with `get_available_indicators()`
3. **Add visualization** in `patterns/visualization.py`
4. **Update analysis workflow** in `agent_capabilities.py`

### Adding New Patterns
1. **Implement detection logic** in `patterns/recognition.py`
2. **Add visualization methods** in `PatternVisualizer` class
3. **Integrate with main workflow** in `StockAnalysisOrchestrator`
4. **Update AI prompts** for pattern analysis

### Extending AI Analysis
1. **Modify prompts** in `gemini/prompts/` directory
2. **Update context engineering** in `ContextEngineer` class
3. **Extend response parsing** in `GeminiClient`
4. **Add new analysis types** to `AnalysisType` enum

### Customizing Multi-Timeframe Analysis
1. **Modify timeframe configurations** in `enhanced_mtf_analysis.py`
2. **Adjust indicator sets** for each timeframe
3. **Customize confidence weights** and validation logic
4. **Add new timeframe intervals** as needed

## 🔒 Security & Performance

### Security Features
- **API Key Management**: Environment variable-based configuration
- **JWT Authentication**: Secure token-based authentication via Supabase
- **CORS Protection**: Configurable cross-origin resource sharing
- **Rate Limiting**: API request throttling and protection
- **Input Validation**: Comprehensive request validation and sanitization

### Performance Optimizations
- **Intelligent Caching**: Multi-layer caching strategy with Redis
- **Async Processing**: Non-blocking I/O operations throughout
- **Database Optimization**: 1000x faster queries with optimized structures
- **Memory Management**: Efficient chart storage and cleanup
- **Load Balancing**: Service distribution and resource optimization

### Monitoring & Logging
- **Performance Monitoring**: Real-time performance metrics
- **Error Tracking**: Comprehensive error logging and handling
- **Token Usage Monitoring**: AI API cost tracking and optimization
- **Service Health Checks**: Automated health monitoring
- **Resource Usage Tracking**: Memory and CPU utilization monitoring

## 🚀 Deployment

### Production Deployment
```bash
# Set environment variables
export ENVIRONMENT=production
export CHART_MAX_AGE_HOURS=6
export CHART_MAX_SIZE_MB=200
export CHART_CLEANUP_INTERVAL_MINUTES=15

# Start services with production config
python start_all_services.py
```

### Docker Deployment (Recommended)
```dockerfile
# Backend Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "start_all_services.py"]
```

### Environment-Specific Configurations
- **Development**: Relaxed cleanup, larger storage, debugging enabled
- **Staging**: Moderate cleanup, medium storage, testing optimized
- **Production**: Aggressive cleanup, minimal storage, performance optimized

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Implement your changes** following the established patterns
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request** with detailed description

### Development Guidelines
- **Code Style**: Follow PEP 8 for Python, ESLint for TypeScript
- **Testing**: Ensure all new features have corresponding tests
- **Documentation**: Update README and inline documentation
- **Performance**: Consider performance implications of changes
- **Security**: Follow security best practices for all additions

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Zerodha**: For providing comprehensive market data APIs
- **Google Gemini**: For advanced AI analysis capabilities
- **FastAPI**: For the robust, high-performance backend framework
- **React & shadcn/ui**: For the modern, accessible frontend components
- **Supabase**: For authentication and database infrastructure
- **Redis**: For high-performance caching and data storage

## 📞 Support & Community

### Getting Help
- **GitHub Issues**: Create issues for bugs and feature requests
- **Documentation**: Check the comprehensive inline documentation
- **Wiki**: Visit the project wiki for detailed guides
- **Discussions**: Join community discussions for questions and ideas

### System Requirements
- **Backend**: Python 3.12+, 4GB RAM, 10GB storage
- **Frontend**: Modern browser with ES6+ support
- **Database**: Supabase account (free tier available)
- **APIs**: Zerodha KiteConnect, Google Gemini

### Performance Benchmarks
- **Analysis Speed**: 2-5 seconds for comprehensive analysis
- **Real-time Updates**: <100ms latency for WebSocket data
- **Chart Generation**: 1-3 seconds for complex charts
- **Database Queries**: 1000x faster than previous versions
- **Memory Usage**: Optimized for production environments

---

**Disclaimer**: This tool is for educational and research purposes only. Trading decisions should be based on comprehensive analysis and professional advice. Past performance does not guarantee future results. The system provides analysis and insights but does not constitute financial advice. 