# Frontend Split Architecture Guide

This document explains how the frontend has been updated to work with the new split backend architecture.

## 🏗️ Architecture Overview

The frontend now communicates with two separate backend services:

### **Data Service (Port 8000)**
- Historical data retrieval
- Real-time data streaming via WebSocket
- Market data and status
- Token/symbol mapping
- Authentication

### **Analysis Service (Port 8001)**
- Stock analysis and AI processing
- Technical indicators
- Pattern recognition
- Chart generation
- Sector analysis and benchmarking

## 📁 Updated Files

### **Configuration**
- `frontend/src/config.ts` - Updated with split service endpoints

### **Services**
- `frontend/src/services/api.ts` - Updated to use split architecture
- `frontend/src/services/liveDataService.ts` - Updated for data service
- `frontend/src/services/analysisService.ts` - New service for analysis operations

## 🔧 Configuration Changes

### **New Configuration Structure**

```typescript
// frontend/src/config.ts
export const DATA_SERVICE_URL = "http://localhost:8000";
export const ANALYSIS_SERVICE_URL = "http://localhost:8001";

// WebSocket URL for real-time data
export const WEBSOCKET_URL = "ws://localhost:8000/ws/stream";

// Service endpoints mapping
export const ENDPOINTS = {
  // Data Service endpoints (Port 8000)
  DATA: {
    HEALTH: `${DATA_SERVICE_URL}/health`,
    STOCK_HISTORY: `${DATA_SERVICE_URL}/stock`,
    STOCK_INFO: `${DATA_SERVICE_URL}/stock`,
    MARKET_STATUS: `${DATA_SERVICE_URL}/market/status`,
    WEBSOCKET: WEBSOCKET_URL,
    // ... more endpoints
  },
  
  // Analysis Service endpoints (Port 8001)
  ANALYSIS: {
    HEALTH: `${ANALYSIS_SERVICE_URL}/health`,
    ANALYZE: `${ANALYSIS_SERVICE_URL}/analyze`,
    ENHANCED_ANALYZE: `${ANALYSIS_SERVICE_URL}/analyze/enhanced`,
    STOCK_INDICATORS: `${ANALYSIS_SERVICE_URL}/stock`,
    // ... more endpoints
  }
};
```

## 🔄 Service Updates

### **1. API Service (`api.ts`)**

The API service has been completely restructured to use the split architecture:

```typescript
// Analysis Service endpoints (Port 8001)
async analyzeStock(request: AnalysisRequest): Promise<AnalysisResponse> {
  const resp = await fetch(ENDPOINTS.ANALYSIS.ANALYZE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  // ...
}

// Data Service endpoints (Port 8000)
async getHistoricalData(symbol: string, interval: string = '1day'): Promise<HistoricalDataResponse> {
  const resp = await fetch(`${ENDPOINTS.DATA.STOCK_HISTORY}/${symbol}/history?${params}`);
  // ...
}
```

### **2. Live Data Service (`liveDataService.ts`)**

Updated to use the data service for all data operations:

```typescript
// Get historical data (Data Service - Port 8000)
async getHistoricalData(symbol: string, interval: string = '1d'): Promise<HistoricalDataResponse> {
  const response = await fetch(`${ENDPOINTS.DATA.STOCK_HISTORY}/${symbol}/history?${params}`);
  // ...
}

// Connect to WebSocket (Data Service - Port 8000)
async connectWebSocket(tokens: string[], onData: (data: any) => void): Promise<WebSocket> {
  const wsUrl = `${ENDPOINTS.DATA.WEBSOCKET}?token=${token}`;
  this.wsConnection = new WebSocket(wsUrl);
  // ...
}
```

### **3. Analysis Service (`analysisService.ts`)**

New service specifically for analysis operations:

```typescript
// Comprehensive stock analysis (Analysis Service - Port 8001)
async analyzeStock(request: AnalysisRequest): Promise<AnalysisResponse> {
  const response = await fetch(ENDPOINTS.ANALYSIS.ANALYZE, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  // ...
}

// Technical indicators (Analysis Service - Port 8001)
async getIndicators(symbol: string, interval: string = '1day'): Promise<IndicatorsResponse> {
  const response = await fetch(`${ENDPOINTS.ANALYSIS.STOCK_INDICATORS}/${symbol}/indicators?${params}`);
  // ...
}
```

## 📊 Service Mapping

### **Data Service Operations (Port 8000)**
| Operation | Endpoint | Method | Description |
|-----------|----------|--------|-------------|
| Historical Data | `/stock/{symbol}/history` | GET | Get OHLCV data |
| Stock Info | `/stock/{symbol}/info` | GET | Get stock information |
| Market Status | `/market/status` | GET | Get market status |
| WebSocket | `/ws/stream` | WebSocket | Real-time data streaming |
| Token Mapping | `/mapping/token-to-symbol` | GET | Token to symbol mapping |
| Optimized Data | `/data/optimized` | POST | Optimized data fetching |
| Authentication | `/auth/token` | POST | Get JWT token |

### **Analysis Service Operations (Port 8001)**
| Operation | Endpoint | Method | Description |
|-----------|----------|--------|-------------|
| Stock Analysis | `/analyze` | POST | Comprehensive analysis |
| Enhanced Analysis | `/analyze/enhanced` | POST | Enhanced with code execution |
| Technical Indicators | `/stock/{symbol}/indicators` | GET | Get technical indicators |
| Pattern Recognition | `/patterns/{symbol}` | GET | Get pattern analysis |
| Chart Generation | `/charts/{symbol}` | GET | Generate charts |
| Sector List | `/sector/list` | GET | Get all sectors |
| Sector Benchmark | `/sector/benchmark` | POST | Sector benchmarking |
| Sector Stocks | `/sector/{sector}/stocks` | GET | Get sector stocks |
| Sector Performance | `/sector/{sector}/performance` | GET | Get sector performance |
| Sector Comparison | `/sector/compare` | POST | Compare sectors |
| Stock Sector | `/stock/{symbol}/sector` | GET | Get stock sector info |

## 🔌 Usage Examples

### **Data Operations**

```typescript
import { liveDataService } from '@/services/liveDataService';
import { apiService } from '@/services/api';

// Get historical data
const historicalData = await liveDataService.getHistoricalData('RELIANCE', '1d');

// Get stock information
const stockInfo = await liveDataService.getStockInfo('RELIANCE');

// Get market status
const marketStatus = await liveDataService.getMarketStatus();

// Connect to WebSocket for real-time data
const ws = await liveDataService.connectWebSocket(['RELIANCE'], (data) => {
  console.log('Real-time data:', data);
});
```

### **Analysis Operations**

```typescript
import { analysisService } from '@/services/analysisService';

// Perform stock analysis
const analysis = await analysisService.analyzeStock({
  stock: 'RELIANCE',
  exchange: 'NSE',
  period: 365,
  interval: 'day'
});

// Get technical indicators
const indicators = await analysisService.getIndicators('RELIANCE', '1day', 'NSE', 'rsi,macd,sma');

// Get pattern recognition
const patterns = await analysisService.getPatterns('RELIANCE', '1day', 'NSE', 'all');

// Get sector information
const sectors = await analysisService.getSectors();
const sectorStocks = await analysisService.getSectorStocks('IT');
```

### **Health Checks**

```typescript
import { apiService } from '@/services/api';

// Check data service health
const dataHealth = await apiService.getDataServiceHealth();

// Check analysis service health
const analysisHealth = await apiService.getAnalysisServiceHealth();

// Check WebSocket health
const wsHealth = await apiService.getWebSocketHealth();
```

## 🔄 Migration Guide

### **For Existing Components**

1. **Update imports** to use the new services:
   ```typescript
   // Old
   import { apiService } from '@/services/api';
   
   // New - for data operations
   import { liveDataService } from '@/services/liveDataService';
   
   // New - for analysis operations
   import { analysisService } from '@/services/analysisService';
   ```

2. **Update API calls** to use the appropriate service:
   ```typescript
   // Old
   const data = await apiService.getHistoricalData('RELIANCE');
   const analysis = await apiService.analyzeStock(request);
   
   // New
   const data = await liveDataService.getHistoricalData('RELIANCE');
   const analysis = await analysisService.analyzeStock(request);
   ```

3. **Update WebSocket connections**:
   ```typescript
   // Old
   const ws = new WebSocket('ws://localhost:8000/ws/stream');
   
   // New
   const ws = await liveDataService.connectWebSocket(['RELIANCE'], onData);
   ```

### **For New Components**

1. **Data operations** - Use `liveDataService`
2. **Analysis operations** - Use `analysisService`
3. **Health checks** - Use `apiService`

## 🧪 Testing

### **Service Health Checks**

```typescript
// Test data service
const dataHealth = await apiService.getDataServiceHealth();
console.log('Data Service:', dataHealth);

// Test analysis service
const analysisHealth = await apiService.getAnalysisServiceHealth();
console.log('Analysis Service:', analysisHealth);

// Test WebSocket
const wsHealth = await apiService.getWebSocketHealth();
console.log('WebSocket:', wsHealth);
```

### **End-to-End Testing**

```typescript
// Test complete workflow
async function testWorkflow() {
  try {
    // 1. Get historical data (Data Service)
    const data = await liveDataService.getHistoricalData('RELIANCE', '1d');
    console.log('Historical data:', data.success);
    
    // 2. Get technical indicators (Analysis Service)
    const indicators = await analysisService.getIndicators('RELIANCE', '1d');
    console.log('Indicators:', indicators.success);
    
    // 3. Perform analysis (Analysis Service)
    const analysis = await analysisService.analyzeStock({
      stock: 'RELIANCE',
      exchange: 'NSE',
      period: 365,
      interval: 'day'
    });
    console.log('Analysis:', analysis.success);
    
    console.log('✅ All services working correctly!');
  } catch (error) {
    console.error('❌ Service error:', error);
  }
}
```

## 🚨 Error Handling

### **Service-Specific Errors**

```typescript
try {
  const data = await liveDataService.getHistoricalData('RELIANCE');
} catch (error) {
  if (error.message.includes('Authentication failed')) {
    // Handle auth error
  } else if (error.message.includes('Stock not found')) {
    // Handle not found error
  } else {
    // Handle other errors
  }
}
```

### **Service Availability**

```typescript
// Check if services are available before making calls
async function checkServices() {
  try {
    const [dataHealth, analysisHealth] = await Promise.all([
      apiService.getDataServiceHealth(),
      apiService.getAnalysisServiceHealth()
    ]);
    
    if (dataHealth.status === 'healthy' && analysisHealth.status === 'healthy') {
      console.log('✅ Both services are available');
      return true;
    } else {
      console.log('❌ Some services are not available');
      return false;
    }
  } catch (error) {
    console.error('❌ Service check failed:', error);
    return false;
  }
}
```

## 🔧 Environment Configuration

### **Development**

```bash
# .env.local
VITE_DATA_SERVICE_URL=http://localhost:8000
VITE_ANALYSIS_SERVICE_URL=http://localhost:8001
VITE_WEBSOCKET_URL=ws://localhost:8000/ws/stream
```

### **Production**

```bash
# .env.production
VITE_DATA_SERVICE_URL=https://data.yourdomain.com
VITE_ANALYSIS_SERVICE_URL=https://analysis.yourdomain.com
VITE_WEBSOCKET_URL=wss://data.yourdomain.com/ws/stream
```

## 📈 Benefits

### **1. Performance**
- Data service optimized for high-frequency operations
- Analysis service optimized for CPU-intensive tasks
- Better resource utilization

### **2. Scalability**
- Each service can be scaled independently
- Load balancing can be applied per service
- Better fault isolation

### **3. Maintainability**
- Clear separation of concerns
- Easier to debug and maintain
- Independent deployment and updates

### **4. Development**
- Teams can work on services independently
- Clear API boundaries
- Better testing isolation

## 🔮 Future Enhancements

### **1. Service Discovery**
- Implement service discovery for dynamic scaling
- Health check integration
- Automatic failover

### **2. Caching Layer**
- Redis integration for data caching
- CDN for static assets
- Browser caching optimization

### **3. Monitoring**
- Service-specific metrics
- Performance monitoring
- Error tracking and alerting

### **4. Load Balancing**
- Client-side load balancing
- Service mesh integration
- Circuit breaker patterns

## 📝 Summary

The frontend has been successfully updated to work with the split backend architecture:

- **Data operations** now use the Data Service (Port 8000)
- **Analysis operations** now use the Analysis Service (Port 8001)
- **WebSocket connections** remain with the Data Service
- **Authentication** is handled by the Data Service
- **Health checks** are available for both services

This architecture provides better performance, scalability, and maintainability while keeping the same functionality as the original monolithic approach. 