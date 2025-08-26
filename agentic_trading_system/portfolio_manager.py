"""
Portfolio Manager for Agentic Trading System
Manages holdings, budget, and trade execution
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from decimal import Decimal, ROUND_HALF_UP

from models import PortfolioState, Holding, TradeRequest, ActionType
from config import TradingConfig

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Manages trading portfolio, holdings, and trade execution"""
    
    def __init__(self, initial_budget: float = None):
        self.initial_budget = initial_budget or TradingConfig.INITIAL_BUDGET
        self.available_cash = self.initial_budget
        self.holdings: Dict[str, Holding] = {}
        self.trade_history: List[TradeRequest] = []
        self.total_pnl = 0.0
        self.total_pnl_percentage = 0.0
        
    def get_portfolio_state(self) -> PortfolioState:
        """Get current portfolio state"""
        total_value = self.available_cash
        holdings_dict = {}
        
        for symbol, holding in self.holdings.items():
            total_value += holding.current_value
            holdings_dict[symbol] = {
                "quantity": holding.quantity,
                "avg_price": holding.avg_price,
                "current_price": holding.current_price,
                "current_value": holding.current_value,
                "unrealized_pnl": holding.unrealized_pnl,
                "unrealized_pnl_percentage": holding.unrealized_pnl_percentage,
                "percentage_of_portfolio": holding.percentage_of_portfolio
            }
        
        # Calculate total PnL
        total_invested = self.initial_budget - self.available_cash
        if total_invested > 0:
            self.total_pnl_percentage = (self.total_pnl / total_invested) * 100
        
        return PortfolioState(
            total_budget=self.initial_budget,
            available_cash=self.available_cash,
            total_value=total_value,
            holdings=holdings_dict,
            total_pnl=self.total_pnl,
            total_pnl_percentage=self.total_pnl_percentage
        )
    
    def update_holding_price(self, symbol: str, current_price: float):
        """Update current price for a holding"""
        if symbol in self.holdings:
            holding = self.holdings[symbol]
            holding.current_price = current_price
            holding.current_value = holding.quantity * current_price
            holding.unrealized_pnl = holding.current_value - (holding.quantity * holding.avg_price)
            
            if holding.quantity * holding.avg_price > 0:
                holding.unrealized_pnl_percentage = (holding.unrealized_pnl / (holding.quantity * holding.avg_price)) * 100
            
            # Update percentage of portfolio
            portfolio_state = self.get_portfolio_state()
            if portfolio_state.total_value > 0:
                holding.percentage_of_portfolio = (holding.current_value / portfolio_state.total_value) * 100
            
            logger.info(f"Updated {symbol} price to {current_price}, PnL: {holding.unrealized_pnl:.2f}")
    
    def can_buy(self, symbol: str, quantity: int, price: float) -> Tuple[bool, str]:
        """Check if we can buy the specified quantity"""
        total_cost = quantity * price
        
        if total_cost > self.available_cash:
            return False, f"Insufficient cash. Need {total_cost:.2f}, have {self.available_cash:.2f}"
        
        # Check position size limits
        portfolio_state = self.get_portfolio_state()
        position_percentage = (total_cost / portfolio_state.total_value) * 100
        
        if position_percentage > TradingConfig.MAX_POSITION_SIZE * 100:
            return False, f"Position too large. {position_percentage:.1f}% exceeds {TradingConfig.MAX_POSITION_SIZE * 100}% limit"
        
        if position_percentage < TradingConfig.MIN_POSITION_SIZE * 100:
            return False, f"Position too small. {position_percentage:.1f}% below {TradingConfig.MIN_POSITION_SIZE * 100}% minimum"
        
        return True, "OK"
    
    def can_sell(self, symbol: str, quantity: int) -> Tuple[bool, str]:
        """Check if we can sell the specified quantity"""
        if symbol not in self.holdings:
            return False, f"No holdings in {symbol}"
        
        holding = self.holdings[symbol]
        if quantity > holding.quantity:
            return False, f"Insufficient holdings. Need {quantity}, have {holding.quantity}"
        
        return True, "OK"
    
    def execute_buy(self, trade_request: TradeRequest) -> Tuple[bool, str]:
        """Execute a buy order"""
        if trade_request.action != ActionType.BUY:
            return False, "Invalid action for buy execution"
        
        symbol = trade_request.symbol
        price = trade_request.price or 0.0
        
        if price <= 0:
            return False, "Invalid price for buy order"
        
        # Calculate quantity based on percentage or fixed quantity
        if trade_request.percentage:
            # Buy based on percentage of available cash
            amount_to_spend = self.available_cash * (trade_request.percentage / 100)
            quantity = int(amount_to_spend / price)
        elif trade_request.quantity:
            quantity = trade_request.quantity
        else:
            return False, "Must specify either quantity or percentage"
        
        # Validate the trade
        can_buy, message = self.can_buy(symbol, quantity, price)
        if not can_buy:
            return False, message
        
        # Execute the trade
        total_cost = quantity * price
        self.available_cash -= total_cost
        
        if symbol in self.holdings:
            # Add to existing holding
            holding = self.holdings[symbol]
            total_quantity = holding.quantity + quantity
            total_cost_basis = (holding.quantity * holding.avg_price) + total_cost
            holding.avg_price = total_cost_basis / total_quantity
            holding.quantity = total_quantity
            holding.current_price = price
            holding.current_value = holding.quantity * price
        else:
            # Create new holding
            self.holdings[symbol] = Holding(
                symbol=symbol,
                quantity=quantity,
                avg_price=price,
                current_price=price,
                current_value=quantity * price,
                unrealized_pnl=0.0,
                unrealized_pnl_percentage=0.0,
                percentage_of_portfolio=0.0
            )
        
        # Update portfolio percentages
        self._update_portfolio_percentages()
        
        # Record the trade
        self.trade_history.append(trade_request)
        
        logger.info(f"Executed BUY: {quantity} {symbol} at {price:.2f}, total cost: {total_cost:.2f}")
        return True, f"Successfully bought {quantity} {symbol} at {price:.2f}"
    
    def execute_sell(self, trade_request: TradeRequest) -> Tuple[bool, str]:
        """Execute a sell order"""
        if trade_request.action != ActionType.SELL:
            return False, "Invalid action for sell execution"
        
        symbol = trade_request.symbol
        price = trade_request.price or 0.0
        
        if price <= 0:
            return False, "Invalid price for sell order"
        
        if symbol not in self.holdings:
            return False, f"No holdings in {symbol}"
        
        holding = self.holdings[symbol]
        
        # Calculate quantity to sell
        if trade_request.percentage:
            # Sell based on percentage of holdings
            quantity = int(holding.quantity * (trade_request.percentage / 100))
        elif trade_request.quantity:
            quantity = trade_request.quantity
        else:
            return False, "Must specify either quantity or percentage"
        
        # Validate the trade
        can_sell, message = self.can_sell(symbol, quantity)
        if not can_sell:
            return False, message
        
        # Execute the trade
        total_proceeds = quantity * price
        self.available_cash += total_proceeds
        
        # Calculate realized PnL
        cost_basis = quantity * holding.avg_price
        realized_pnl = total_proceeds - cost_basis
        self.total_pnl += realized_pnl
        
        # Update holding
        holding.quantity -= quantity
        if holding.quantity == 0:
            # Sold all holdings
            del self.holdings[symbol]
        else:
            # Update current value and PnL
            holding.current_value = holding.quantity * price
            holding.unrealized_pnl = holding.current_value - (holding.quantity * holding.avg_price)
            if holding.quantity * holding.avg_price > 0:
                holding.unrealized_pnl_percentage = (holding.unrealized_pnl / (holding.quantity * holding.avg_price)) * 100
        
        # Update portfolio percentages
        self._update_portfolio_percentages()
        
        # Record the trade
        self.trade_history.append(trade_request)
        
        logger.info(f"Executed SELL: {quantity} {symbol} at {price:.2f}, proceeds: {total_proceeds:.2f}, PnL: {realized_pnl:.2f}")
        return True, f"Successfully sold {quantity} {symbol} at {price:.2f}, PnL: {realized_pnl:.2f}"
    
    def _update_portfolio_percentages(self):
        """Update percentage of portfolio for all holdings"""
        portfolio_state = self.get_portfolio_state()
        if portfolio_state.total_value > 0:
            for holding in self.holdings.values():
                holding.percentage_of_portfolio = (holding.current_value / portfolio_state.total_value) * 100
    
    def get_holding_summary(self, symbol: str) -> Optional[Dict]:
        """Get summary of a specific holding"""
        if symbol not in self.holdings:
            return None
        
        holding = self.holdings[symbol]
        return {
            "symbol": symbol,
            "quantity": holding.quantity,
            "avg_price": holding.avg_price,
            "current_price": holding.current_price,
            "current_value": holding.current_value,
            "unrealized_pnl": holding.unrealized_pnl,
            "unrealized_pnl_percentage": holding.unrealized_pnl_percentage,
            "percentage_of_portfolio": holding.percentage_of_portfolio
        }
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        portfolio_state = self.get_portfolio_state()
        
        return {
            "total_budget": portfolio_state.total_budget,
            "available_cash": portfolio_state.available_cash,
            "total_value": portfolio_state.total_value,
            "total_pnl": portfolio_state.total_pnl,
            "total_pnl_percentage": portfolio_state.total_pnl_percentage,
            "num_holdings": len(self.holdings),
            "holdings": [self.get_holding_summary(symbol) for symbol in self.holdings.keys()],
            "cash_percentage": (portfolio_state.available_cash / portfolio_state.total_value) * 100 if portfolio_state.total_value > 0 else 100
        }
    
    def calculate_position_size(self, symbol: str, confidence: float, risk_level: str) -> float:
        """
        Calculate recommended position size based on confidence and risk
        
        Args:
            symbol: Stock symbol
            confidence: Confidence level (0-100)
            risk_level: Risk level (Low/Medium/High/Very High)
        
        Returns:
            Recommended position size as percentage of budget
        """
        # Base position size on confidence
        base_size = (confidence / 100) * TradingConfig.MAX_POSITION_SIZE
        
        # Adjust for risk level
        risk_multipliers = {
            "Very Low": 1.2,
            "Low": 1.0,
            "Medium": 0.8,
            "High": 0.6,
            "Very High": 0.4
        }
        
        risk_multiplier = risk_multipliers.get(risk_level, 0.8)
        adjusted_size = base_size * risk_multiplier
        
        # Ensure within limits
        adjusted_size = max(adjusted_size, TradingConfig.MIN_POSITION_SIZE)
        adjusted_size = min(adjusted_size, TradingConfig.MAX_POSITION_SIZE)
        
        return adjusted_size * 100  # Return as percentage

