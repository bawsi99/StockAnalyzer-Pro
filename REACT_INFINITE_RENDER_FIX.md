# React Infinite Render Fix

## Problem
The application was experiencing a "React maximum update depth exceeded" error, which is caused by infinite re-renders. This was happening in the `Charts.tsx` component and the `useLiveChart` hook.

## Root Cause Analysis
The infinite re-render was caused by:

1. **Function Dependencies in useCallback**: The `updateSymbol` and `updateTimeframe` functions in `useLiveChart` had dependencies on other functions (`connect`, `disconnect`, `loadHistoricalData`) that were being recreated on every render.

2. **Function Dependencies in useEffect**: The `useEffect` hooks in `Charts.tsx` were depending on these functions, causing them to run infinitely.

3. **Missing Memoization**: The component and its event handlers weren't properly memoized, leading to unnecessary re-renders.

## Solution Implemented

### 1. Function Reference Management
- **Created function refs** in `useLiveChart` to store stable references to functions:
  ```typescript
  const connectRef = useRef<(() => Promise<void>) | null>(null);
  const disconnectRef = useRef<(() => void) | null>(null);
  const loadHistoricalDataRef = useRef<((retryCount?: number) => Promise<void>) | null>(null);
  ```

- **Updated function definitions** to store themselves in refs:
  ```typescript
  const connect = useCallback(async () => { /* ... */ }, [maxReconnectAttempts, reconnectInterval]);
  connectRef.current = connect;
  ```

### 2. Optimized useCallback Dependencies
- **Removed function dependencies** from `updateSymbol` and `updateTimeframe`:
  ```typescript
  // Before
  const updateSymbol = useCallback(async (newSymbol: string) => {
    // ...
  }, [disconnect, loadHistoricalData, autoConnect, connect]);

  // After
  const updateSymbol = useCallback(async (newSymbol: string) => {
    // ...
  }, []); // Empty dependency array
  ```

- **Used function refs** instead of direct function calls:
  ```typescript
  disconnectRef.current?.();
  loadHistoricalDataRef.current?.();
  connectRef.current?.();
  ```

### 3. Component Optimization
- **Wrapped Charts component** with `React.memo`:
  ```typescript
  const Charts = React.memo(function Charts() {
    // Component logic
  });
  ```

- **Added useCallback** to event handlers:
  ```typescript
  const handleChartDataLoaded = useCallback((data: ChartData[]) => {
    // Handler logic
  }, []);
  ```

- **Optimized useEffect dependencies**:
  ```typescript
  // Before
  useEffect(() => {
    updateSymbol(stockSymbol);
  }, [stockSymbol, updateSymbol]);

  // After
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      updateSymbol(stockSymbol);
    }, 100);
    return () => clearTimeout(timeoutId);
  }, [stockSymbol]); // Removed updateSymbol dependency
  ```

### 4. Data Processing Optimization
- **Added useMemo** for expensive calculations:
  ```typescript
  const memoizedChartStats = useMemo(() => {
    if (chartData) {
      return calculatePriceStatistics(chartData);
    }
    return null;
  }, [chartData]);
  ```

- **Optimized live data updates**:
  ```typescript
  useEffect(() => {
    if (liveData && liveData.length > 0) {
      // Update logic
    }
  }, [liveData?.length, lastUpdate]); // Only depend on length and lastUpdate
  ```

### 5. Debounced Updates
- **Added debouncing** to prevent rapid state updates:
  ```typescript
  const timeoutId = setTimeout(() => {
    updateSymbol(stockSymbol);
  }, 100);
  return () => clearTimeout(timeoutId);
  ```

## Files Modified

### 1. `frontend/src/hooks/useLiveChart.ts`
- Added function refs for stable function references
- Removed function dependencies from useCallback hooks
- Updated function calls to use refs
- Optimized initialization useEffect

### 2. `frontend/src/pages/Charts.tsx`
- Wrapped component with React.memo
- Added useCallback to event handlers
- Optimized useEffect dependencies
- Added useMemo for expensive calculations
- Added debounced updates
- Removed unnecessary state

## Performance Improvements

1. **Eliminated Infinite Re-renders**: The main issue causing the React maximum update depth error has been resolved.

2. **Reduced Function Recreation**: Functions are now stable references, preventing unnecessary re-renders.

3. **Optimized Data Processing**: Expensive calculations are memoized and only run when necessary.

4. **Debounced Updates**: Rapid state updates are prevented, reducing render frequency.

5. **Better Memory Management**: Proper cleanup and ref management prevent memory leaks.

## Testing
The fix has been tested by:
1. Running the development server
2. Monitoring console logs for infinite re-render patterns
3. Verifying that chart updates work correctly without causing infinite loops
4. Ensuring WebSocket connections and data updates function properly

## Prevention Measures
To prevent similar issues in the future:
1. Always use `useCallback` for functions passed as props or used in useEffect dependencies
2. Use `useMemo` for expensive calculations
3. Avoid including functions in useEffect dependency arrays unless absolutely necessary
4. Use refs for functions that need to be called from within callbacks
5. Implement proper debouncing for rapid state updates
6. Use React.memo for components that receive stable props 