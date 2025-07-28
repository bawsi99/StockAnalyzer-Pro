# Chart Zoom/Pan Fix Implementation - Adapted to Current Codebase

## 🎯 Problem Description

The chart was automatically resetting to its original position whenever new data arrived, causing the user's zoom and pan state to be lost. This happened because the chart was calling `fitContent()` on every data update, which resets the view to show all data.

## 🔍 Root Cause Analysis

The issue was in the `LiveSimpleChart.tsx` component where `fitContent()` was being called in multiple places:

1. **Line 730**: In the initial data update effect
2. **Line 850**: In the main data update effect when new data was loaded  
3. **Line 640**: In the reset function callback

This caused the chart to reset to its original position every time new data arrived, regardless of whether the user had zoomed or panned the chart.

## ✅ Solution Implemented

### 1. Chart State Management System

Added a comprehensive chart state management system to preserve user interactions:

```typescript
// Chart state management for preserving zoom/pan
const hasUserInteractedRef = useRef<boolean>(false);
const chartStateRef = useRef<ChartState | null>(null);

// Save current chart state
const saveChartState = useCallback(() => {
  if (!chartRef.current) return;
  
  try {
    const timeScale = chartRef.current.timeScale();
    const priceScale = chartRef.current.priceScale('right');
    
    const currentState: ChartState = {
      visibleRange: timeScale.getVisibleRange() as any,
      timeScale: {
        rightOffset: timeScale.options().rightOffset,
        barSpacing: timeScale.options().barSpacing,
        fixLeftEdge: timeScale.options().fixLeftEdge,
        fixRightEdge: timeScale.options().fixRightEdge,
        lockVisibleTimeRangeOnResize: timeScale.options().lockVisibleTimeRangeOnResize,
        rightBarStaysOnScroll: timeScale.options().rightBarStaysOnScroll,
        borderVisible: timeScale.options().borderVisible,
        visible: timeScale.options().visible,
        timeVisible: timeScale.options().timeVisible,
        secondsVisible: timeScale.options().secondsVisible,
      },
      priceScale: {
        autoScale: priceScale.options().autoScale,
        scaleMargins: priceScale.options().scaleMargins,
      }
    };
    
    chartStateRef.current = currentState;
    
    if (debug) {
      console.log('💾 Chart state saved:', currentState);
    }
  } catch (error) {
    console.warn('Error saving chart state:', error);
  }
}, [debug]);

// Restore chart state
const restoreChartState = useCallback(() => {
  if (!chartRef.current || !chartStateRef.current?.visibleRange) return;
  
  try {
    const timeScale = chartRef.current.timeScale();
    const priceScale = chartRef.current.priceScale('right');
    
    // Restore time scale options
    if (chartStateRef.current.timeScale) {
      timeScale.applyOptions(chartStateRef.current.timeScale);
    }
    
    // Restore price scale options
    if (chartStateRef.current.priceScale) {
      priceScale.applyOptions(chartStateRef.current.priceScale);
    }
    
    // Restore visible range
    timeScale.setVisibleRange(chartStateRef.current.visibleRange as any);
    
    if (debug) {
      console.log('🔄 Chart state restored:', chartStateRef.current);
    }
  } catch (error) {
    console.warn('Error restoring chart state:', error);
  }
}, [debug]);
```

### 2. User Interaction Detection

Added event listeners to detect when users interact with the chart:

```typescript
// Handle user interaction (zoom, pan, etc.)
const handleUserInteraction = useCallback(() => {
  hasUserInteractedRef.current = true;
  if (debug) {
    console.log('👆 User interaction detected');
  }
}, [debug]);

// Subscribe to time scale changes (zoom/pan)
timeScale.subscribeVisibleTimeRangeChange(() => {
  handleUserInteraction();
});
```

### 3. Smart Data Update Logic

Modified the data update logic to preserve user's view state:

```typescript
// Initial data update effect (Line 730)
if (isInitialLoadRef.current || isNewSymbolRef.current) {
  if (chartRef.current) {
    chartRef.current.timeScale().fitContent();
  }
  isInitialLoadRef.current = false;
} else if (hasUserInteractedRef.current) {
  // Restore user's previous view state for same symbol updates
  setTimeout(() => {
    restoreChartState();
  }, 0);
}

// Main data update effect (Line 850)
if (isNewDataset || isNewSymbolRef.current) {
  // Save current chart state before updating data
  if (hasUserInteractedRef.current) {
    saveChartState();
  }
  
  // Full dataset update
  candlestickSeriesRef.current.setData(candlestickData as any);
  lastDataRef.current = candlestickData as any;
  
  // Only fit content for new symbol, preserve user's view for same symbol
  if (isNewSymbolRef.current) {
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  } else if (hasUserInteractedRef.current) {
    // Restore user's previous view state
    setTimeout(() => {
      restoreChartState();
    }, 0);
  }
}
```

### 4. State Reset on Symbol/Timeframe Changes

Properly reset the chart state management when switching symbols or timeframes:

```typescript
// Reset chart state management for new symbol
chartStateRef.current = null;
hasUserInteractedRef.current = false;
isInitialLoadRef.current = true;

// Reset chart state management for new timeframe
chartStateRef.current = null;
hasUserInteractedRef.current = false;
isInitialLoadRef.current = true;
```

### 5. Manual Reset Function

Enhanced the reset function to properly clear user interaction state:

```typescript
// Register reset function if callback provided
if (onRegisterReset) {
  onRegisterReset(() => {
    if (chart) {
      // Reset user interaction state when manually resetting
      hasUserInteractedRef.current = false;
      chartStateRef.current = null;
      chart.timeScale().fitContent();
    }
  });
}
```

### 6. Integration with Charts Page

Added proper integration with the Charts page to enable manual reset functionality:

```typescript
// In Charts.tsx
const chartResetRef = useRef<(() => void) | null>(null);

// In LiveSimpleChart component
onResetScale={() => {
  if (chartResetRef.current) {
    chartResetRef.current();
  }
}}
onRegisterReset={(resetFn) => {
  chartResetRef.current = resetFn;
}}
```

## 🧪 Testing Features

Added debug controls to test the chart state management:

- **User Interacted**: Shows whether the user has zoomed/panned the chart
- **Chart State**: Shows whether a chart state has been saved
- **Save State**: Manually save the current chart state
- **Restore State**: Manually restore the saved chart state
- **Reset Chart**: Manually reset the chart and clear all state

## 🎯 Expected Behavior

### Before Fix
- User zooms in/out or pans the chart
- New data arrives (live updates, symbol change, etc.)
- Chart automatically resets to original position ❌

### After Fix
- User zooms in/out or pans the chart
- New data arrives (live updates)
- Chart preserves user's zoom/pan position ✅
- Only resets to fit content when:
  - New symbol is selected
  - New timeframe is selected
  - Manual reset button is clicked
  - Initial load

## 🔧 Technical Details

### ChartState Interface
```typescript
interface ChartState {
  visibleRange?: {
    from: number;
    to: number;
  };
  timeScale: {
    rightOffset: number;
    barSpacing: number;
    fixLeftEdge: boolean;
    fixRightEdge: boolean;
    lockVisibleTimeRangeOnResize: boolean;
    rightBarStaysOnScroll: boolean;
    borderVisible: boolean;
    visible: boolean;
    timeVisible: boolean;
    secondsVisible: boolean;
  };
  priceScale: {
    autoScale: boolean;
    scaleMargins: {
      top: number;
      bottom: number;
    };
  };
}
```

### Key Functions
- `saveChartState()`: Captures current chart view state
- `restoreChartState()`: Restores previously saved chart state
- `handleUserInteraction()`: Marks that user has interacted with chart
- `handleChartReset()`: Resets all state management on manual reset

## 🚀 Performance Considerations

- Chart state is only saved when user has actually interacted
- State restoration uses `setTimeout` to ensure it happens after data updates
- Minimal overhead as state management only activates when needed
- Debug controls only appear when `debug={true}` prop is set

## ✅ Verification

To verify the fix is working:

1. Load a chart with data
2. Zoom in/out or pan the chart
3. Wait for live data updates or trigger new data
4. Verify the chart maintains your zoom/pan position
5. Switch symbols/timeframes and verify it resets appropriately
6. Use the debug controls to manually test state saving/restoration

## 🔄 Changes Made

### Files Modified:
1. **frontend/src/components/charts/LiveSimpleChart.tsx**
   - Added chart state management system
   - Modified data update logic to preserve user interactions
   - Enhanced reset function to clear user interaction state
   - Added debug controls for testing

2. **frontend/src/pages/Charts.tsx**
   - Added chart reset ref for manual reset functionality
   - Integrated onResetScale and onRegisterReset props

### Key Improvements:
- ✅ Preserves zoom/pan state during live data updates
- ✅ Only resets view when appropriate (new symbol/timeframe)
- ✅ Provides manual reset functionality
- ✅ Includes comprehensive debug controls
- ✅ Maintains performance with minimal overhead
- ✅ Handles edge cases and error conditions

The fix ensures a smooth user experience while maintaining the chart's functionality for data updates and symbol/timeframe changes. 