"""
Backend Client for Agentic Trading System
Handles communication with the backend analysis service
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from models import BackendAnalysisResponse, AnalysisData
from config import TradingConfig

logger = logging.getLogger(__name__)

class BackendClient:
    """Client for interacting with backend analysis service"""
    
    def __init__(self):
        self.analysis_url = TradingConfig.BACKEND_ANALYSIS_URL
        self.data_url = TradingConfig.BACKEND_DATA_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=TradingConfig.ANALYSIS_TIMEOUT)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_analysis(self, symbol: str, exchange: str = "NSE", 
                          period: int = None, interval: str = None) -> Optional[AnalysisData]:
        """
        Get analysis from backend service
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (default: NSE)
            period: Analysis period in days (default: from config)
            interval: Time interval (default: from config)
        
        Returns:
            AnalysisData object or None if failed
        """
        if not self.session:
            raise RuntimeError("BackendClient not initialized. Use async context manager.")
        
        period = period or TradingConfig.DEFAULT_ANALYSIS_PERIOD
        interval = interval or TradingConfig.DEFAULT_INTERVAL
        
        try:
            # Request enhanced analysis
            payload = {
                "stock": symbol,
                "exchange": exchange,
                "period": period,
                "interval": interval,
                "enable_code_execution": True
            }
            
            logger.info(f"Requesting analysis for {symbol} from backend")
            
            async with self.session.post(
                f"{self.analysis_url}/analyze/enhanced",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_analysis_response(data)
                else:
                    error_text = await response.text()
                    logger.error(f"Backend analysis failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting analysis for {symbol}: {str(e)}")
            return None
    
    async def get_stock_data(self, symbol: str, exchange: str = "NSE", 
                           interval: str = "1day", period: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get historical stock data
        
        Args:
            symbol: Stock symbol
            exchange: Exchange
            interval: Time interval
            period: Number of periods
        
        Returns:
            Stock data dictionary or None if failed
        """
        if not self.session:
            raise RuntimeError("BackendClient not initialized. Use async context manager.")
        
        try:
            payload = {
                "symbol": symbol,
                "exchange": exchange,
                "interval": interval,
                "period": period
            }
            
            async with self.session.post(
                f"{self.data_url}/data/fetch",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Data fetch failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {str(e)}")
            return None
    
    async def get_technical_indicators(self, symbol: str, exchange: str = "NSE", 
                                     interval: str = "1day") -> Optional[Dict[str, Any]]:
        """
        Get technical indicators for a stock
        
        Args:
            symbol: Stock symbol
            exchange: Exchange
            interval: Time interval
        
        Returns:
            Technical indicators dictionary or None if failed
        """
        if not self.session:
            raise RuntimeError("BackendClient not initialized. Use async context manager.")
        
        try:
            url = f"{self.analysis_url}/stock/{symbol}/indicators"
            params = {
                "exchange": exchange,
                "interval": interval
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Technical indicators failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {str(e)}")
            return None
    
    async def get_sector_benchmarking(self, symbol: str, sector: str = None) -> Optional[Dict[str, Any]]:
        """
        Get sector benchmarking analysis
        
        Args:
            symbol: Stock symbol
            sector: Sector name (optional, will auto-detect)
        
        Returns:
            Sector benchmarking data or None if failed
        """
        if not self.session:
            raise RuntimeError("BackendClient not initialized. Use async context manager.")
        
        try:
            payload = {
                "stock": symbol,
                "sector": sector or ""
            }
            
            async with self.session.post(
                f"{self.analysis_url}/sector/benchmark",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Sector benchmarking failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting sector benchmarking for {symbol}: {str(e)}")
            return None
    
    def _parse_analysis_response(self, response_data: Dict[str, Any]) -> Optional[AnalysisData]:
        """
        Parse backend analysis response into AnalysisData model
        
        Args:
            response_data: Raw response from backend
        
        Returns:
            AnalysisData object or None if parsing failed
        """
        try:
            if not response_data.get("success", False):
                logger.error(f"Backend analysis failed: {response_data.get('error', 'Unknown error')}")
                return None
            
            results = response_data.get("results", {})
            
            return AnalysisData(
                symbol=results.get("symbol", ""),
                exchange=results.get("exchange", ""),
                timestamp=results.get("analysis_timestamp", ""),
                current_price=results.get("current_price", 0.0),
                price_change=results.get("price_change", 0.0),
                price_change_percentage=results.get("price_change_percentage", 0.0),
                technical_indicators=results.get("technical_indicators", {}),
                risk_level=results.get("risk_level", "Medium"),
                recommendation=results.get("recommendation", "Hold"),
                ai_analysis=results.get("ai_analysis", {}),
                sector_context=results.get("sector_context", {}),
                multi_timeframe_analysis=results.get("multi_timeframe_analysis", {}),
                ml_predictions=results.get("ml_predictions", {}),
                enhanced_metadata=results.get("enhanced_metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check if backend services are healthy
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.session:
            raise RuntimeError("BackendClient not initialized. Use async context manager.")
        
        try:
            # Check analysis service
            async with self.session.get(f"{self.analysis_url}/health") as response:
                if response.status != 200:
                    return False
            
            # Check data service
            async with self.session.get(f"{self.data_url}/health") as response:
                if response.status != 200:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

