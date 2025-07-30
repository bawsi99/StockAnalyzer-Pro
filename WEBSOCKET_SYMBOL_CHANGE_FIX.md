# WebSocket Symbol Change Fix Documentation

## Issue Description

**Problem**: When users changed the stock symbol in the frontend, the WebSocket connection remained subscribed to the old symbol instead of switching to the new one. Users would receive historical data for the new symbol but continue to receive live tick data from the old symbol.

**Symptoms**:
- Historical data loads correctly for new symbol
- Live tick data continues to come from the previous symbol
- WebSocket connection status shows as connected but data is wrong
- No error messages in console

## Root Cause Analysis

### 1. Frontend Connection Management Issues

**File**: `frontend/src/hooks/useLiveChart.ts`

#### Problem 1: Early Return Preventing Reconnection
```typescript
// BEFORE (Problematic Code)
if (isConnectingRef.current || wsRef.current?.readyState === WebSocket.OPEN) {
  console.log('🔌 WebSocket already connected or connecting, skipping...');
  return;
}
```
**Issue**: This prevented reconnection when the symbol changed because the WebSocket was already connected.

#### Problem 2: Incomplete Symbol Change Handling
```typescript
// BEFORE (Problematic Code)
if (previousSymbol !== symbol) {
  symbolRef.current = symbol;
  setState(prev => ({
    ...prev,
    data: [],
    isLoading: true,
    error: null,
    isLive: false
  }));
  loadHistoricalDataRef.current?.(); // Only loaded historical data
  // Missing: WebSocket reconnection logic
}
```
**Issue**: Symbol changes only triggered historical data loading but not WebSocket reconnection.

#### Problem 3: Connection Management Conflicts
**Issue**: The `useLiveChart` hook was managing WebSocket connections directly while `liveDataService` was also trying to manage connections, causing conflicts.

### 2. Backend Subscription Management

**File**: `backend/data_service.py`

The backend's `live_pubsub.update_filter()` method was working correctly, but the frontend wasn't properly triggering subscription changes.

## Solution Implemented

### 1. Fixed Symbol Change Detection and Reconnection

**File**: `frontend/src/hooks/useLiveChart.ts`

#### Updated useEffect for Prop Changes
```typescript
// AFTER (Fixed Code)
useEffect(() => {
  console.log('🔄 useLiveChart props changed:', { symbol, timeframe, 'at': new Date().toISOString() });
  
  const previousSymbol = symbolRef.current;
  const previousTimeframe = timeframeRef.current;
  
  // Check if symbol has changed
  if (previousSymbol !== symbol) {
    console.log(`🔄 Symbol changed from ${previousSymbol || 'undefined'} to ${symbol}`);
    symbolRef.current = symbol;
    
    // Clear data and reload for new symbol
    setState(prev => ({
      ...prev,
      data: [],
      isLoading: true,
      error: null,
      isLive: false,
      lastTickPrice: undefined,
      lastTickTime: undefined
    }));
    
    // Disconnect current WebSocket to stop receiving old symbol data
    disconnectRef.current?.();
    
    // Load new historical data
    loadHistoricalDataRef.current?.();
    
    // Reconnect WebSocket for new symbol if autoConnect is enabled
    if (autoConnect) {
      console.log('🔄 Reconnecting WebSocket for new symbol...');
      setTimeout(() => {
        connectRef.current?.();
      }, 100);
    }
  }
  
  // Similar logic for timeframe changes...
}, [symbol, timeframe, autoConnect]);
```

### 2. Fixed WebSocket Connection Management

#### Removed Early Return Blocking Reconnection
```typescript
// AFTER (Fixed Code)
if (isConnectingRef.current) {
  console.log('🔌 WebSocket already connecting, skipping...');
  return;
}
```

#### Simplified Connection Logic
```typescript
// AFTER (Fixed Code)
const connect = useCallback(async () => {
  if (isConnectingRef.current) {
    console.log('🔌 WebSocket already connecting, skipping...');
    return;
  }

  console.log('🔌 Starting WebSocket connection for:', symbolRef.current, timeframeRef.current);
  isConnectingRef.current = true;

  // Disconnect any existing connection first
  liveDataService.disconnectWebSocket();

  setState(prev => ({ 
    ...prev, 
    connectionStatus: 'connecting',
    error: null 
  }));

  try {
    console.log(`🔌 Connecting to WebSocket for ${symbolRef.current}`);

    wsRef.current = await liveDataService.connectWebSocket(
      [symbolRef.current],
      (wsData: WebSocketMessage) => {
        // Message handling logic...
      }
    );

    console.log('WebSocket connected to Data Service');
    setState(prev => ({
      ...prev,
      connectionStatus: 'connected',
      isConnected: true,
      reconnectAttempts: 0
    }));

    // Reset connecting flag on successful connection
    isConnectingRef.current = false;

  } catch (error) {
    // Error handling...
  }
}, [maxReconnectAttempts, reconnectInterval]);
```

### 3. Fixed Disconnect Function

```typescript
// AFTER (Fixed Code)
const disconnect = useCallback(() => {
  console.log('Disconnecting WebSocket...');
  
  // Use the liveDataService disconnect method
  liveDataService.disconnectWebSocket();
  
  // Clear our local reference
  wsRef.current = null;

  if (reconnectTimeoutRef.current) {
    clearTimeout(reconnectTimeoutRef.current);
    reconnectTimeoutRef.current = null;
  }

  isConnectingRef.current = false;
  lastTickRef.current = null;

  setState(prev => ({
    ...prev,
    connectionStatus: 'disconnected',
    isConnected: false,
    isLive: false,
    reconnectAttempts: 0,
    lastTickPrice: undefined,
    lastTickTime: undefined
  }));
}, []);
```

## How the Fix Works

### Step-by-Step Process

1. **Symbol Change Detection**
   - `useEffect` watches for changes in `symbol` prop
   - Compares current symbol with previous symbol
   - Triggers reconnection process when different

2. **Clean Disconnect**
   - Calls `disconnectRef.current?.()` to properly close old connection
   - Uses `liveDataService.disconnectWebSocket()` for proper cleanup
   - Clears all relevant state variables

3. **Historical Data Loading**
   - Loads new historical data for the new symbol
   - Updates chart with correct historical data

4. **WebSocket Reconnection**
   - Creates new WebSocket connection with new symbol
   - Subscribes to live data for the new symbol
   - Updates connection status

5. **State Management**
   - Clears old data and state
   - Sets loading states appropriately
   - Updates connection status

### Data Flow

```
User Changes Symbol
       ↓
useEffect Detects Change
       ↓
Disconnect Old WebSocket
       ↓
Load Historical Data (New Symbol)
       ↓
Connect New WebSocket (New Symbol)
       ↓
Subscribe to Live Data (New Symbol)
       ↓
Receive Live Ticks (New Symbol)
```

## Testing the Fix

### Manual Testing Steps

1. **Open the application** and navigate to the Charts page
2. **Select a stock symbol** (e.g., RELIANCE)
3. **Verify live data** is coming from the selected symbol
4. **Change to a different symbol** (e.g., TCS)
5. **Verify**:
   - Historical data loads for new symbol
   - Live tick data comes from new symbol (not old)
   - WebSocket connection status remains connected
   - No console errors

### Console Logs to Monitor

Look for these log messages during symbol changes:

```
🔄 useLiveChart props changed: { symbol: "TCS", timeframe: "1d", at: "..." }
🔄 Symbol changed from RELIANCE to TCS
Disconnecting WebSocket...
🔌 Starting WebSocket connection for: TCS 1d
🔌 Connecting to WebSocket for TCS
WebSocket connected to Data Service
✅ Successfully subscribed to WebSocket feed
```

### Automated Testing

```typescript
// Test case for symbol change
describe('WebSocket Symbol Change', () => {
  it('should reconnect WebSocket when symbol changes', async () => {
    // Setup initial symbol
    render(<Charts />);
    await waitFor(() => screen.getByText('RELIANCE'));
    
    // Change symbol
    fireEvent.click(screen.getByText('TCS'));
    
    // Verify WebSocket reconnection
    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });
    
    // Verify data is from new symbol
    // (Implementation depends on your testing setup)
  });
});
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: WebSocket Still Receiving Old Symbol Data

**Symptoms**: Live data continues to come from previous symbol after change

**Possible Causes**:
- Old WebSocket connection not properly closed
- Backend subscription not updated
- Frontend state not cleared

**Solutions**:
1. Check console for disconnect logs
2. Verify `liveDataService.disconnectWebSocket()` is called
3. Check backend logs for subscription updates
4. Clear browser cache and reload

#### Issue 2: WebSocket Connection Fails After Symbol Change

**Symptoms**: Connection status shows "error" or "disconnected"

**Possible Causes**:
- Authentication token expired
- Backend service down
- Network connectivity issues

**Solutions**:
1. Check authentication status
2. Verify backend service is running
3. Check network connectivity
4. Review console error messages

#### Issue 3: Historical Data Loads But No Live Data

**Symptoms**: Chart shows historical data but no live updates

**Possible Causes**:
- WebSocket connection failed silently
- Subscription message not sent
- Backend not processing subscription

**Solutions**:
1. Check WebSocket connection status
2. Verify subscription message in console
3. Check backend logs for subscription processing
4. Test with different symbol

### Debug Commands

#### Frontend Debugging

```javascript
// In browser console
// Check current WebSocket state
console.log('WebSocket state:', window.liveChartState);

// Force symbol change
window.forceSymbolChange = (symbol) => {
  // Implementation depends on your app structure
};

// Check connection status
window.checkConnection = () => {
  // Implementation depends on your app structure
};
```

#### Backend Debugging

```python
# Check WebSocket connections
curl http://localhost:8000/ws/connections

# Check WebSocket health
curl http://localhost:8000/ws/health

# Check subscribed tokens
curl http://localhost:8000/ws/test
```

## Performance Considerations

### Memory Management

- **WebSocket Cleanup**: Properly close connections to prevent memory leaks
- **State Cleanup**: Clear old data and references when symbol changes
- **Event Listener Cleanup**: Remove listeners to prevent memory accumulation

### Connection Efficiency

- **Reconnection Logic**: Implement exponential backoff for failed connections
- **Subscription Management**: Only subscribe to necessary symbols
- **Data Throttling**: Consider implementing data rate limiting for high-frequency updates

## Future Improvements

### Potential Enhancements

1. **Connection Pooling**: Maintain multiple WebSocket connections for different symbols
2. **Smart Reconnection**: Implement intelligent reconnection based on market hours
3. **Data Caching**: Cache historical data to reduce API calls
4. **Error Recovery**: Implement automatic error recovery mechanisms
5. **Connection Monitoring**: Add real-time connection health monitoring

### Code Quality Improvements

1. **Type Safety**: Add comprehensive TypeScript types for WebSocket messages
2. **Error Boundaries**: Implement React error boundaries for WebSocket errors
3. **Testing**: Add comprehensive unit and integration tests
4. **Documentation**: Maintain up-to-date API documentation
5. **Monitoring**: Add application performance monitoring (APM) integration

## Related Files

### Frontend Files
- `frontend/src/hooks/useLiveChart.ts` - Main WebSocket hook
- `frontend/src/services/liveDataService.ts` - WebSocket service
- `frontend/src/pages/Charts.tsx` - Chart component using the hook

### Backend Files
- `backend/data_service.py` - WebSocket endpoint and pub/sub system
- `backend/websocket_stream_service.py` - Alternative WebSocket service

### Configuration Files
- `frontend/src/config.ts` - API endpoints configuration
- `backend/config.py` - Backend configuration

## Version History

### v1.0 (Current Fix)
- **Date**: [Current Date]
- **Changes**: Initial implementation of WebSocket symbol change fix
- **Files Modified**: `frontend/src/hooks/useLiveChart.ts`

### Future Versions
- Track any additional improvements or fixes here

---

**Note**: This documentation should be updated whenever changes are made to the WebSocket symbol change functionality. Keep it synchronized with the actual implementation to ensure accurate troubleshooting guidance. 