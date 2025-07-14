# StockAnalyzer-Pro 📈

A comprehensive stock analysis platform that combines technical indicators, pattern recognition, and AI-powered insights to provide detailed stock market analysis and trading recommendations.

## 🌟 Features

### 📊 Technical Analysis
- **20+ Technical Indicators**: RSI, MACD, Bollinger Bands, ADX, Stochastic, OBV, and more
- **Pattern Recognition**: Support/Resistance levels, Double tops/bottoms, Triangles, Flags, Volume anomalies
- **Consensus Analysis**: Multi-indicator consensus signals with strength assessment
- **Real-time Data**: Live market data integration via Zerodha KiteConnect API

### 🤖 AI-Powered Insights
- **Google Gemini Integration**: Advanced LLM analysis of technical charts and indicators
- **Multi-modal Analysis**: Text and image-based chart analysis
- **Trading Recommendations**: AI-generated buy/sell signals with risk assessment
- **Target Price Analysis**: AI-predicted support and resistance levels

### 📈 Visualization
- **Interactive Charts**: Candlestick charts with volume analysis
- **Pattern Overlays**: Visual identification of technical patterns
- **Multi-pane Analysis**: Price, volume, and indicator charts
- **Export Capabilities**: High-resolution chart exports

### 🎯 User Experience
- **Modern UI**: React-based frontend with shadcn/ui components
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live data refresh and analysis
- **Historical Analysis**: Customizable time periods and intervals

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
backend/
├── main.py                 # Main orchestrator
├── api.py                  # FastAPI endpoints
├── agent_capabilities.py   # Core analysis workflow
├── technical_indicators.py # Technical indicator calculations
├── zerodha_client.py      # Market data integration
├── gemini/                # AI/LLM integration
├── patterns/              # Pattern recognition & visualization
├── prompts/               # LLM prompt templates
└── rag_documents/         # Knowledge base for RAG
```

### Frontend (React/TypeScript)
```
frontend/
├── src/
│   ├── components/        # UI components
│   ├── pages/            # Application pages
│   ├── hooks/            # Custom React hooks
│   ├── contexts/         # React contexts
│   └── utils/            # Utility functions
├── public/               # Static assets
└── supabase/             # Database configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Zerodha KiteConnect API credentials
- Google Gemini API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bawsi99/StockAnalyzer-Pro.git
   cd StockAnalyzer-Pro
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file in backend directory
   ZERODHA_API_KEY=your_zerodha_api_key
   ZERODHA_API_SECRET=your_zerodha_api_secret
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Run the backend server**
   ```bash
   python main.py --stock RELIANCE  # Command line analysis
   # OR
   uvicorn api:app --reload --host 0.0.0.0 --port 8000  # API server
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## 📖 Usage

### Command Line Analysis
```bash
# Basic analysis
python main.py --stock RELIANCE

# Advanced analysis with custom parameters
python main.py --stock RELIANCE --exchange NSE --period 365 --interval 60minute
```

### API Endpoints
- `POST /analyze` - Analyze a stock symbol
- `GET /health` - Health check endpoint

### Example API Request
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol": "RELIANCE", "exchange": "NSE", "period": 365}'
```

## 🔧 Configuration

### Technical Indicators
- **Moving Averages**: SMA, EMA, WMA (20, 50, 200 periods)
- **Momentum**: RSI, MACD, Stochastic, ADX
- **Volatility**: Bollinger Bands, ATR
- **Volume**: OBV, Volume ratio analysis

### Pattern Recognition
- **Support/Resistance**: Automatic level detection
- **Chart Patterns**: Double tops/bottoms, triangles, flags
- **Volume Analysis**: Anomaly detection and correlation

### AI Analysis
- **Chart Analysis**: Image-based pattern recognition
- **Indicator Summary**: Technical indicator consensus
- **Risk Assessment**: AI-powered risk evaluation
- **Target Prediction**: Support/resistance level prediction

## 🛠️ Development

### Adding New Indicators
1. Add calculation logic in `technical_indicators.py`
2. Register in the indicator registry
3. Update visualization in `patterns/visualization.py`

### Adding New Patterns
1. Implement detection logic in `patterns/recognition.py`
2. Add visualization in `PatternVisualizer`
3. Update the main analysis workflow

### Extending AI Analysis
1. Modify prompts in `prompts/` directory
2. Update `GeminiClient` for new analysis types
3. Extend the response parsing logic

## 📊 Output Structure

Each analysis generates:
```
output/STOCK_SYMBOL/
├── comparison_chart.png
├── divergence.png
├── double_tops_bottoms.png
├── support_resistance.png
├── triangles_flags.png
├── volume_anomalies.png
├── candlestick_volume.png
├── price_volume_correlation.png
└── results.json
```

## 🔒 Security

- API keys are stored in environment variables
- Zerodha authentication uses secure token management
- Input validation on all API endpoints
- Rate limiting for API requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Zerodha**: For providing market data APIs
- **Google Gemini**: For AI-powered analysis capabilities
- **FastAPI**: For the robust backend framework
- **React & shadcn/ui**: For the modern frontend components

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the [Wiki](https://github.com/bawsi99/StockAnalyzer-Pro/wiki) for detailed documentation
- Review the backend and frontend README files for specific component details

---

**Disclaimer**: This tool is for educational and research purposes only. Trading decisions should be based on comprehensive analysis and professional advice. Past performance does not guarantee future results. 