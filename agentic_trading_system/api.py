"""
FastAPI Server for Agentic Trading System
Provides REST API endpoints for trading sessions
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from trading_session import TradingSessionManager
from backend_client import BackendClient
from config import TradingConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agentic Trading System API",
    description="AI-powered trading system with multi-agent decision making",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize session manager
session_manager = TradingSessionManager()

# Pydantic models for API requests
class CreateSessionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to trade")
    initial_budget: Optional[float] = Field(TradingConfig.INITIAL_BUDGET, description="Initial budget in rupees")

class ProcessIntervalRequest(BaseModel):
    interval: Optional[str] = Field("1day", description="Time interval for analysis")

class ManualActionRequest(BaseModel):
    action: str = Field(..., description="Action to execute (BUY/SELL)")
    quantity: Optional[int] = Field(None, description="Quantity to trade")
    percentage: Optional[float] = Field(None, description="Percentage of budget/holdings to trade")

class AutoTradeRequest(BaseModel):
    max_iterations: int = Field(10, description="Maximum number of trading iterations")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check backend services
        async with BackendClient() as backend_client:
            backend_healthy = await backend_client.health_check()
        
        return {
            "status": "healthy" if backend_healthy else "degraded",
            "service": "Agentic Trading System",
            "timestamp": datetime.now().isoformat(),
            "backend_services": "healthy" if backend_healthy else "unhealthy",
            "active_sessions": len(session_manager.sessions)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Agentic Trading System",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Session management endpoints
@app.post("/sessions/create")
async def create_session(request: CreateSessionRequest):
    """Create a new trading session"""
    try:
        result = await session_manager.create_session(
            symbol=request.symbol,
            initial_budget=request.initial_budget
        )
        return result
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List all trading sessions"""
    try:
        return {
            "sessions": session_manager.list_sessions(),
            "total_sessions": len(session_manager.sessions)
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session_state(session_id: str):
    """Get current session state"""
    try:
        result = session_manager.get_session_state(session_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session state: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get session history"""
    try:
        result = session_manager.get_session_history(session_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def close_session(session_id: str):
    """Close a trading session"""
    try:
        result = session_manager.close_session(session_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Trading endpoints
@app.post("/sessions/{session_id}/process-interval")
async def process_data_interval(session_id: str, request: ProcessIntervalRequest):
    """Process data for a specific interval"""
    try:
        result = await session_manager.process_data_interval(
            session_id=session_id,
            interval=request.interval
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing interval: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/next-interval")
async def get_next_data_interval(session_id: str):
    """Get the next data interval based on last decision"""
    try:
        result = await session_manager.get_next_data_interval(session_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next interval: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/analyze-again")
async def analyze_again(session_id: str):
    """Trigger new analysis for the current symbol"""
    try:
        result = await session_manager.analyze_again(session_id)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing again: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/manual-action")
async def execute_manual_action(session_id: str, request: ManualActionRequest):
    """Execute manual trading action"""
    try:
        result = await session_manager.execute_manual_action(
            session_id=session_id,
            action=request.action,
            quantity=request.quantity,
            percentage=request.percentage
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing manual action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/auto-trade")
async def auto_trade_session(session_id: str, request: AutoTradeRequest, background_tasks: BackgroundTasks):
    """Run automated trading session"""
    try:
        # Run auto-trade in background
        async def run_auto_trade():
            try:
                result = await session_manager.auto_trade_session(
                    session_id=session_id,
                    max_iterations=request.max_iterations
                )
                logger.info(f"Auto-trade completed for session {session_id}: {result}")
            except Exception as e:
                logger.error(f"Auto-trade failed for session {session_id}: {str(e)}")
        
        background_tasks.add_task(run_auto_trade)
        
        return {
            "message": "Auto-trade started in background",
            "session_id": session_id,
            "max_iterations": request.max_iterations
        }
    except Exception as e:
        logger.error(f"Error starting auto-trade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@app.get("/config")
async def get_config():
    """Get system configuration"""
    return {
        "initial_budget": TradingConfig.INITIAL_BUDGET,
        "max_position_size": TradingConfig.MAX_POSITION_SIZE,
        "min_position_size": TradingConfig.MIN_POSITION_SIZE,
        "buy_confidence_threshold": TradingConfig.BUY_CONFIDENCE_THRESHOLD,
        "sell_confidence_threshold": TradingConfig.SELL_CONFIDENCE_THRESHOLD,
        "stop_loss_percentage": TradingConfig.STOP_LOSS_PERCENTAGE,
        "take_profit_percentage": TradingConfig.TAKE_PROFIT_PERCENTAGE,
        "available_stocks": TradingConfig.DEFAULT_STOCKS,
        "data_intervals": TradingConfig.DATA_INTERVALS
    }

@app.get("/available-stocks")
async def get_available_stocks():
    """Get list of available stocks for trading"""
    return {
        "stocks": TradingConfig.DEFAULT_STOCKS,
        "count": len(TradingConfig.DEFAULT_STOCKS)
    }

# WebSocket endpoint for real-time updates (placeholder)
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    try:
        await websocket.accept()
        
        # Send initial session state
        session_state = session_manager.get_session_state(session_id)
        await websocket.send_text(str(session_state))
        
        # Keep connection alive and send updates
        while True:
            await asyncio.sleep(30)  # Send updates every 30 seconds
            
            if session_id in session_manager.sessions:
                session_state = session_manager.get_session_state(session_id)
                await websocket.send_text(str(session_state))
            else:
                await websocket.send_text('{"error": "Session not found"}')
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )

