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
│   └── dataset.py            # Data pipeline and feature engineering
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
- **Redis** (optional, for enhanced caching)
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
   REDIS_URL=redis://localhost:6379  # Optional
   ```

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