# StockAnalyzer Pro - Warp Quick Reference 📈

A comprehensive guide for running and developing the StockAnalyzer Pro platform using Warp terminal.

## 🚀 Quick Start Commands

### Environment Setup
```bash
# Clone and setup project
git clone https://github.com/bawsi99/StockAnalyzer-Pro.git
cd StockAnalyzer-Pro

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Redis Setup (Required for caching)
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# Docker
docker run -d --name redis -p 6379:6379 redis:alpine

# Test Redis setup
cd backend
python test_redis_cache_manager.py
```

## 🔧 Service Management

### Start All Services (Recommended)
```bash
cd backend
python start_all_services.py
```

### Start Individual Services
```bash
# Terminal 1: Data Service (Port 8001, with WebSocket streaming)
cd backend
python start_data_service.py

# Terminal 2: Analysis Service (Port 8002)
cd backend
python start_analysis_service.py

# Terminal 3: Database Service (Port 8003)
cd backend
python start_database_service.py

# Terminal 4: Frontend Development Server
cd frontend
npm run dev
```

### Service Health Checks
```bash
# Check services
curl http://localhost:8001/health  # Data Service
curl http://localhost:8002/health  # Analysis Service
curl http://localhost:8003/health  # Database Service

# Check WebSocket (served by Data Service)
wscat -c ws://localhost:8001/ws/stream
```

## 📊 Analysis Commands

### Command Line Analysis
```bash
cd backend
python main.py --stock RELIANCE --period 365 --interval day
python main.py --stock TCS --period 30 --interval 1hour
python main.py --stock INFY --period 7 --interval 5min
```

### API Testing
```bash
# Basic stock analysis
curl -X POST "http://localhost:8002/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "RELIANCE",
    "exchange": "NSE",
    "period": 365,
    "interval": "day"
  }'

# Enhanced AI analysis
curl -X POST "http://localhost:8002/analyze/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "RELIANCE",
    "exchange": "NSE",
    "period": 365,
    "interval": "day",
    "include_sector_analysis": true,
    "include_mtf_analysis": true
  }'

# Multi-timeframe analysis
curl -X POST "http://localhost:8002/analyze/mtf" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "RELIANCE",
    "exchange": "NSE",
    "timeframes": ["1min", "5min", "15min", "1hour", "day"]
  }'
```

## 🗂️ Project Structure Navigation

### Backend Services
```bash
# Core analysis engine
cd backend
ls -la agent_capabilities.py      # Main orchestrator
ls -la technical_indicators.py    # 25+ indicators
ls -la enhanced_mtf_analysis.py   # Multi-timeframe engine
ls -la sector_benchmarking.py     # Sector analysis

# AI/ML components  
ls -la gemini/                     # AI integration
ls -la ml/                         # Machine learning
ls -la patterns/                   # Pattern recognition
ls -la quant_system/               # Quantitative tools
```

### Frontend Components
```bash
cd frontend/src
ls -la components/analysis/        # Analysis dashboards
ls -la components/charts/          # Chart components  
ls -la hooks/                      # React hooks
ls -la services/                   # API services
```

## 🧹 Maintenance Commands

### Cache Management
```bash
# Get Redis cache statistics
curl "http://localhost:8002/redis/cache/stats"

# Clear all cache
curl -X POST "http://localhost:8002/redis/cache/clear"

# Clear specific stock cache
curl -X DELETE "http://localhost:8002/redis/cache/stock/RELIANCE"

# Clear specific data type
curl -X POST "http://localhost:8002/redis/cache/clear?data_type=stock_data"
```

### Log Management
```bash
# View service logs
cd backend
tail -f logs/data_service.log
tail -f logs/analysis_service.log
tail -f logs/database_service.log

# Clear logs
rm -rf logs/*.log
```

### Database Operations
```bash
# Reset analysis datasets
rm -rf analysis_datasets/*

# Clear output directory  
rm -rf output/*

# Clear cache directory
rm -rf cache/*
```

## 🔍 Development & Debugging

### Environment Variables Check
```bash
# Check required environment variables
cd backend
python -c "
import os
required_vars = ['ZERODHA_API_KEY', 'ZERODHA_API_SECRET', 'GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
for var in required_vars:
    print(f'{var}: {\"✓\" if os.getenv(var) else \"✗ MISSING\"}')"
```

### Testing Commands
```bash
# Test Redis connectivity
cd backend  
python -c "import redis; r = redis.Redis(); print('Redis:', r.ping())"

# Test API connectivity
python -c "
import requests
try:
    r = requests.get('http://localhost:8001/health', timeout=5)
    print('Data Service:', r.status_code)
except: print('Data Service: OFFLINE')
"

# Test WebSocket connection
python -c "
import asyncio
import websockets
async def test():
    try:
        async with websockets.connect('ws://localhost:8001/ws/stream') as ws:
            print('WebSocket: Connected')
    except: print('WebSocket: OFFLINE')
asyncio.run(test())
"
```

### Performance Monitoring
```bash
# Monitor service processes
ps aux | grep python | grep -E "(data_service|analysis_service|database_service)"

# Check port usage
lsof -i :8001  # Data Service (with WebSocket)
lsof -i :8002  # Analysis Service  
lsof -i :8003  # Database Service
lsof -i :5173  # Frontend Dev Server

# Monitor Redis memory usage
redis-cli info memory
```

## 🐛 Troubleshooting

### Common Issues & Solutions
```bash
# Port already in use
lsof -ti:8001 | xargs kill -9  # Kill process on port 8001 (Data/WebSocket)
lsof -ti:8002 | xargs kill -9  # Kill process on port 8002 (Analysis)
lsof -ti:8003 | xargs kill -9  # Kill process on port 8003 (Database)

# Redis connection issues
redis-cli ping                  # Test Redis connectivity
brew services restart redis    # Restart Redis (macOS)
sudo systemctl restart redis-server  # Restart Redis (Linux)

# Python environment issues
cd backend
deactivate                     # Exit current environment
rm -rf .venv                   # Remove environment
python -m venv .venv           # Create new environment
source .venv/bin/activate      # Activate environment
pip install -r requirements.txt  # Reinstall dependencies

# Node modules issues
cd frontend
rm -rf node_modules package-lock.json
npm install                    # Reinstall dependencies
```

### Service Recovery
```bash
# Restart all services
cd backend
pkill -f "python.*service"     # Kill all service processes
sleep 2
python start_all_services.py   # Restart all services

# Check service status
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:8002/health | jq .
curl -s http://localhost:8003/health | jq .
```

## 📱 Access Points

- **Frontend**: http://localhost:5173
- **Data Service**: http://localhost:8001
- **Analysis Service**: http://localhost:8002
- **Database Service**: http://localhost:8003
- **WebSocket**: ws://localhost:8001
- **API Documentation**: http://localhost:8002/docs

## 🛠️ Useful Aliases

Add these to your shell profile for quick access:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias sap-start="cd '/Users/aaryanmanawat/Aaryan/StockAnalyzer Pro/version3.0/3.0/backend' && python start_all_services.py"
alias sap-frontend="cd '/Users/aaryanmanawat/Aaryan/StockAnalyzer Pro/version3.0/3.0/frontend' && npm run dev"
alias sap-analyze="cd '/Users/aaryanmanawat/Aaryan/StockAnalyzer Pro/version3.0/3.0/backend' && python main.py"
alias sap-health="curl -s http://localhost:8001/health && curl -s http://localhost:8002/health && curl -s http://localhost:8003/health"
alias sap-logs="cd '/Users/aaryanmanawat/Aaryan/StockAnalyzer Pro/version3.0/3.0/backend' && tail -f logs/*.log"
alias sap-redis="redis-cli"
alias sap-cache-clear="curl -X POST 'http://localhost:8002/redis/cache/clear'"

# Reload shell to use aliases
source ~/.zshrc  # or source ~/.bashrc
```

## 🔧 Environment Configuration

### Required Environment Variables (.env)
```bash
# Zerodha API Configuration
ZERODHA_API_KEY=your_zerodha_api_key
ZERODHA_API_SECRET=your_zerodha_api_secret

# Google Gemini AI Configuration  
GEMINI_API_KEY=your_gemini_api_key

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_ENABLE_COMPRESSION=true
REDIS_CACHE_ENABLE_LOCAL_FALLBACK=true
REDIS_CACHE_LOCAL_SIZE=1000
REDIS_CACHE_CLEANUP_INTERVAL_MINUTES=60

# Production Settings
ENVIRONMENT=development
CHART_MAX_AGE_HOURS=24
CHART_MAX_SIZE_MB=100
CHART_CLEANUP_INTERVAL_MINUTES=30
```

---

**Quick Help**: Run `sap-health` to check all services (Data:8001, Analysis:8002, Database:8003), `sap-start` to start the backend, and `sap-frontend` to start the development server.

**Tip**: Use Warp's AI command suggestions by typing natural language descriptions of what you want to do!
