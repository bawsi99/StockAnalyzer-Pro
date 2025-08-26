# 🤖 Agentic Trading System

An AI-powered trading system that uses multiple specialist agents to make buy/sell/hold decisions based on comprehensive market analysis. The system integrates with your existing backend analysis service to provide intelligent trading recommendations.

## 🎯 Features

- **Multi-Agent Decision Making**: 5 specialist agents analyze different aspects of trading
- **Real-time Market Analysis**: Integrates with your existing backend analysis service
- **Portfolio Management**: Tracks holdings, budget, and PnL with 1 lakh rupee budget
- **Risk Management**: Automatic position sizing and stop-loss/take-profit levels
- **Multi-turn Conversations**: Interactive trading sessions with data intervals
- **Partial Position Management**: Support for selling 25%, 50%, 75%, or 100% of holdings
- **Automated Trading**: Background auto-trading with configurable iterations
- **REST API**: Full API for integration with frontend applications

## 🏗️ Architecture

### Specialist Agents

1. **Technical Analysis Agent**: Analyzes RSI, MACD, moving averages, support/resistance levels
2. **Sector Analysis Agent**: Evaluates sector performance, rotation, and correlation
3. **Risk Assessment Agent**: Assesses risk levels and provides position sizing recommendations
4. **ML Prediction Agent**: Interprets machine learning predictions and market regime
5. **Portfolio Agent**: Manages portfolio state, cash flow, and diversification

### Main Agent

- Orchestrates all specialist agents
- Makes final buy/sell/hold decisions
- Manages risk and position sizing
- Determines next data intervals

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd agentic_trading_system
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
# Backend Service URLs
BACKEND_ANALYSIS_URL=http://localhost:8001
BACKEND_DATA_URL=http://localhost:8000

# OpenAI API Key (for agent LLMs)
OPENAI_API_KEY=your_openai_api_key_here

# Agent Configuration
AGENT_MODEL=gpt-4
```

### 3. Start the API Server

```bash
python api.py
```

The server will start on `http://localhost:8002`

### 4. Create a Trading Session

```bash
curl -X POST "http://localhost:8002/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "initial_budget": 100000
  }'
```

### 5. Process Market Data

```bash
curl -X POST "http://localhost:8002/sessions/{session_id}/process-interval" \
  -H "Content-Type: application/json" \
  -d '{
    "interval": "1day"
  }'
```

## 📊 API Endpoints

### Session Management

- `POST /sessions/create` - Create new trading session
- `GET /sessions` - List all sessions
- `GET /sessions/{session_id}` - Get session state
- `GET /sessions/{session_id}/history` - Get session history
- `DELETE /sessions/{session_id}` - Close session

### Trading Operations

- `POST /sessions/{session_id}/process-interval` - Process data for specific interval
- `POST /sessions/{session_id}/next-interval` - Get next data interval
- `POST /sessions/{session_id}/analyze-again` - Trigger new analysis
- `POST /sessions/{session_id}/manual-action` - Execute manual trade
- `POST /sessions/{session_id}/auto-trade` - Start automated trading

### System Information

- `GET /health` - Health check
- `GET /config` - System configuration
- `GET /available-stocks` - List available stocks

## 🎮 Usage Examples

### Interactive Trading Session

```python
import asyncio
import aiohttp

async def trading_session_example():
    async with aiohttp.ClientSession() as session:
        # 1. Create session
        async with session.post("http://localhost:8002/sessions/create", 
                               json={"symbol": "RELIANCE", "initial_budget": 100000}) as resp:
            session_data = await resp.json()
            session_id = session_data["session_id"]
        
        # 2. Process initial analysis
        async with session.post(f"http://localhost:8002/sessions/{session_id}/process-interval",
                               json={"interval": "1day"}) as resp:
            decision = await resp.json()
            print(f"Decision: {decision['decision']['action']}")
            print(f"Confidence: {decision['decision']['confidence']}%")
        
        # 3. Get next interval
        async with session.post(f"http://localhost:8002/sessions/{session_id}/next-interval") as resp:
            next_decision = await resp.json()
            print(f"Next decision: {next_decision['decision']['action']}")
        
        # 4. Manual buy action
        async with session.post(f"http://localhost:8002/sessions/{session_id}/manual-action",
                               json={"action": "BUY", "percentage": 25}) as resp:
            trade_result = await resp.json()
            print(f"Trade result: {trade_result}")

# Run the example
asyncio.run(trading_session_example())
```

### Automated Trading

```python
# Start automated trading for 10 iterations
curl -X POST "http://localhost:8002/sessions/{session_id}/auto-trade" \
  -H "Content-Type: application/json" \
  -d '{"max_iterations": 10}'
```

## 🔧 Configuration

### Trading Parameters

- **Initial Budget**: 1,00,000 rupees (configurable)
- **Max Position Size**: 30% of portfolio
- **Min Position Size**: 5% of portfolio
- **Buy Confidence Threshold**: 70%
- **Sell Confidence Threshold**: 60%
- **Stop Loss**: 5% (configurable by risk level)
- **Take Profit**: 15% (configurable by risk level)

### Available Stocks

- RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK
- HINDUNILVR, ITC, SBIN, BHARTIARTL, KOTAKBANK

### Data Intervals

- 1min, 5min, 15min, 30min, 1hour, 1day

## 🧠 Agent Decision Process

1. **Data Collection**: Get analysis from backend service
2. **Agent Analysis**: Each specialist agent analyzes relevant data
3. **Consensus Building**: Main agent aggregates agent recommendations
4. **Decision Making**: Final buy/sell/hold decision with confidence
5. **Position Sizing**: Calculate optimal position size based on risk
6. **Risk Management**: Set stop-loss and take-profit levels
7. **Interval Planning**: Determine next data interval

## 📈 Decision Logic

### Buy Conditions
- Multiple agents recommend BUY
- Weighted confidence ≥ 70%
- Sufficient available cash
- Position size within limits

### Sell Conditions
- Multiple agents recommend SELL
- Weighted confidence ≥ 60%
- Existing holdings available
- Risk management triggers

### Hold Conditions
- Mixed agent recommendations
- Low confidence levels
- Market uncertainty
- Portfolio rebalancing needed

## 🔒 Risk Management

- **Position Sizing**: Based on confidence and risk level
- **Stop Loss**: 5% default (adjusts by risk level)
- **Take Profit**: 15% default (adjusts by risk level)
- **Portfolio Limits**: Max 30% per position
- **Cash Management**: Maintains minimum cash reserves

## 🚨 Error Handling

- Backend service failures
- Agent analysis errors
- Network connectivity issues
- Invalid trading parameters
- Insufficient funds/holdings

## 🔄 Integration with Backend

The system integrates with your existing backend analysis service:

- **Analysis Service** (Port 8001): Enhanced analysis with code execution
- **Data Service** (Port 8000): Historical data and technical indicators
- **Real-time Updates**: WebSocket support for live data

## 📝 Logging

Comprehensive logging for:
- Agent decisions and reasoning
- Trade executions
- Portfolio changes
- Error conditions
- Performance metrics

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8002/health
```

### Configuration Check
```bash
curl http://localhost:8002/config
```

### Session Creation Test
```bash
curl -X POST "http://localhost:8002/sessions/create" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE"}'
```

## 🔮 Future Enhancements

- **Advanced ML Models**: Integration with your ML prediction system
- **Real-time Data**: WebSocket streaming for live market data
- **Backtesting**: Historical performance analysis
- **Portfolio Optimization**: Advanced portfolio management
- **Risk Analytics**: Sophisticated risk assessment
- **Market Sentiment**: News and social media analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the logs for error details
2. Verify backend services are running
3. Ensure environment variables are set correctly
4. Check API documentation at `http://localhost:8002/docs`

---

**Note**: This is a simulation system for testing and educational purposes. It does not execute real trades and should not be used for actual trading without proper validation and risk assessment.

