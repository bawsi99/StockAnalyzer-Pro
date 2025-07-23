# Live Chart Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing live chart rendering with real-time updates using Zerodha WebSocket API. The implementation follows the [Zerodha WebSocket documentation](https://kite.trade/docs/connect/v3/websocket/) and provides a complete solution for live chart updates.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │  Zerodha API    │
│   (React)       │◄──►│   (FastAPI)      │◄──►│  (WebSocket)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Chart Library │    │  Candle Aggregator│    │  Binary Parser  │
│   (Lightweight  │    │  (Real-time)     │    │  (Zerodha)      │
│    Charts)      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Setup

### 1. Automated Setup
```bash
cd backend/
python setup_live_charts.py
```

### 2. Manual Setup

#### Environment Setup
1. **Create `.env` file in backend directory:**
   ```bash
   cd backend/
   touch .env
   ```

2. **Add Zerodha credentials:**
   ```bash
   # Zerodha API Configuration
   ZERODHA_API_KEY=your_zerodha_api_key
   ZERODHA_ACCESS_TOKEN=your_zerodha_access_token
   
   # JWT Authentication
   JWT_SECRET=your-super-secret-jwt-key
   REQUIRE_AUTH=true
   API_KEYS=test-api-key-1,test-api-key-2
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Implementation Details

### ✅ Completed Features

#### 1. **Environment Variable Loading**
- ✅ Added `dotenv.load_dotenv()` to both `zerodha_ws_client.py` and `api.py`
- ✅ Graceful handling of missing dependencies
- ✅ Proper error messages for missing credentials

#### 2. **Binary Data Parser**
- ✅ Implemented `parse_binary_message()` method following Zerodha's documentation
- ✅ Implemented `parse_quote_packet()` method for 44-byte quote packets
- ✅ Proper paise-to-rupees conversion (÷100)
- ✅ Type hints and error handling

#### 3. **Enhanced WebSocket Client**
- ✅ Updated `on_ticks()` to handle binary data
- ✅ Added 403 authentication error detection
- ✅ Implemented reconnection logic with token resubscription
- ✅ Configured 'quote' mode for OHLCV data
- ✅ Proper cleanup and resource management

#### 4. **Backend Configuration**
- ✅ Updated startup event to set WebSocket mode
- ✅ Enhanced error handling and logging
- ✅ Proper token subscription and mode configuration
- ✅ Clean imports and dependency management

#### 5. **Frontend Improvements**
- ✅ Enhanced WebSocket data handler with validation
- ✅ Proper timestamp conversion (Unix to ISO)
- ✅ Data type conversion and error handling
- ✅ Connection status management
- ✅ TypeScript type definitions

#### 6. **Testing and Validation**
- ✅ Created `test_websocket_connection.py` for debugging
- ✅ Created `setup_live_charts.py` for validation
- ✅ Comprehensive error handling and logging

### 🔧 Key Technical Improvements

#### **Type Safety**
- Added comprehensive TypeScript types for frontend
- Added Python type hints for backend
- Proper interface definitions for WebSocket messages

#### **Error Handling**
- Graceful handling of missing dependencies
- Proper authentication error detection (403)
- Automatic reconnection with token resubscription
- Comprehensive logging and debugging

#### **Performance Optimization**
- Efficient binary parsing with struct module
- Data point limiting for frontend performance
- Connection pooling and resource management
- Optional Redis caching support

#### **Code Organization**
- Clean imports and dependency management
- Proper separation of concerns
- Comprehensive documentation
- Modular architecture

## Testing

### 1. Setup Validation
```bash
cd backend/
python setup_live_charts.py
```

### 2. WebSocket Connection Test
```bash
cd backend/
python test_websocket_connection.py
```

### 3. Full System Test
1. Start backend server:
   ```bash
   cd backend/
   python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start frontend development server:
   ```bash
   cd frontend/
   npm run dev
   ```

3. Navigate to the charts page and test live updates

## Data Flow

### 1. Zerodha WebSocket → Backend
```
Binary Data (44 bytes) → parse_binary_message() → parse_quote_packet() → Tick Object
```

### 2. Backend → Frontend
```
Tick Object → Candle Aggregator → candle_forward_hook() → WebSocket → Frontend
```

### 3. Frontend → Chart
```
WebSocket Data → Data Validation → Timestamp Conversion → Chart Update
```

## Key Features

### ✅ Binary Data Parsing
- Handles Zerodha's binary packet format correctly
- Converts paise to rupees (÷100)
- Supports quote mode (44 bytes) for OHLCV data
- Proper error handling and validation

### ✅ Real-time Candle Aggregation
- Aggregates ticks into candles for multiple timeframes
- Triggers callbacks on new candle formation
- Maintains historical candle data
- Efficient memory management

### ✅ Error Handling
- Authentication error detection (403)
- Automatic reconnection with token resubscription
- Graceful degradation when WebSocket fails
- Comprehensive logging and debugging

### ✅ Frontend Integration
- Real-time chart updates
- Data validation and type conversion
- Connection status management
- Performance optimization with data limiting
- TypeScript type safety

### ✅ Development Tools
- Automated setup and validation
- Comprehensive testing scripts
- Clear error messages and debugging
- Documentation and examples

## Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Check `.env` file exists in backend directory
   - Verify `ZERODHA_API_KEY` and `ZERODHA_ACCESS_TOKEN` are set
   - Ensure access token is valid (expires daily)
   - Run `python setup_live_charts.py` to validate

2. **No Data Received**
   - Check if market is open (9:15 AM - 3:30 PM IST)
   - Verify WebSocket connection status
   - Check browser console for errors
   - Run `python test_websocket_connection.py`

3. **Chart Not Updating**
   - Verify WebSocket subscription
   - Check data format in browser console
   - Ensure chart library is properly configured
   - Check for TypeScript errors

### Debug Commands

```bash
# Validate setup
python setup_live_charts.py

# Test WebSocket connection
python test_websocket_connection.py

# Check environment variables
echo $ZERODHA_API_KEY
echo $ZERODHA_ACCESS_TOKEN

# Monitor WebSocket logs
tail -f backend/logs/websocket.log
```

## Performance Considerations

1. **Data Limiting**: Frontend limits data points to prevent memory issues
2. **Binary Parsing**: Efficient binary parsing reduces CPU usage
3. **Connection Pooling**: Single WebSocket connection for multiple tokens
4. **Caching**: Redis caching for tick data (optional)
5. **Type Safety**: Prevents runtime errors and improves development experience

## Security

1. **Environment Variables**: Sensitive data stored in `.env` file
2. **JWT Authentication**: WebSocket connections require valid JWT tokens
3. **API Key Validation**: Backend validates API keys for authentication
4. **HTTPS/WSS**: Production should use secure connections
5. **Input Validation**: Comprehensive data validation and sanitization

## Dependencies

### Backend Dependencies
```bash
# Core
fastapi==0.115.13
uvicorn==0.32.1
pydantic==2.11.0a2
python-dotenv==1.0.1

# WebSocket and real-time data
kiteconnect==6.1.0
websockets==13.0
msgpack==1.0.8

# Authentication and security
PyJWT==2.10.0
python-multipart==0.0.20

# Data processing
pandas==2.2.3
numpy==2.0.2

# Optional: Redis for caching
redis==5.2.1
```

### Frontend Dependencies
```json
{
  "react": "^18.0.0",
  "typescript": "^5.0.0",
  "lightweight-charts": "^4.0.0"
}
```

## Next Steps

1. **Market Hours Detection**: Add automatic market hours detection
2. **Multiple Timeframes**: Support for multiple chart timeframes
3. **Technical Indicators**: Real-time indicator calculations
4. **Alert System**: Price and pattern alerts
5. **Historical Data**: Seamless historical + live data integration
6. **Performance Monitoring**: Add metrics and monitoring
7. **Production Deployment**: Docker containers and CI/CD

## References

- [Zerodha WebSocket Documentation](https://kite.trade/docs/connect/v3/websocket/)
- [KiteConnect Python Library](https://kite.trade/docs/kiteconnect/v3/)
- [FastAPI WebSocket Guide](https://fastapi.tiangolo.com/advanced/websockets/)
- [React WebSocket Hooks](https://reactjs.org/docs/hooks-custom.html)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/) 