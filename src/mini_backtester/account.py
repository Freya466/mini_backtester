from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .types import PortfolioState, Position, TradeRecord, TradeSide

"""Portfolio: Represents the trading portfolio, including available cash, 
    current positions, portfolio valuation, trade updates, and portfolio snapshots.

	---
    position_quantity()
    What it does: Returns the quantity currently held for a given symbol.

    Input
    symbol: Stock/asset ticker to query.
    Output
    Returns the position quantity (float). Returns 0.0 if the position does not exist.
	
	---
    market_value()
    What it does: Calculates the total market value of all positions in the portfolio based on current prices.

    Input
    prices: A mapping of symbols to their current market prices.
    Output
    Returns the total market value (float) of all positions.
	
	---
	total_value()
    What it does: Calculates the total value of the portfolio, including cash and market value of positions.
	
	Input
    prices: A mapping of symbols to their current market prices.
	Output
    Returns the total portfolio value (float).
	
	---
	weights()
    What it does: Calculates the portfolio weight of each position as a percentage of the total portfolio value.

    Input
    prices: Mapping of {symbol: current_price}.
    Output
    Returns a dictionary {symbol: portfolio_weight}.
	
	---
	apply_trade()
    What it does: Updates the portfolio after a trade by adjusting cash and positions.

    Input
    trade: Executed trade record containing symbol, side, quantity, price, and transaction cost.
    Output
    None (updates the portfolio in place).
	
	---
	mark_to_market()
    What it does: Updates each position's stored price to the latest market price.

    Input
    prices: Mapping of {symbol: current_price}.
    Output
    None (updates positions in place).
	
	---
	snapshot()
    What it does: Creates an immutable snapshot of the current portfolio state for recording or analysis.

    Input
    prices: Mapping of {symbol: current_price}.
    Output
    Returns a PortfolioState containing cash, positions, and total portfolio value.
	"""

@dataclass
class Portfolio:
	cash: float
	positions: dict[str, Position] = field(default_factory=dict)

	def position_quantity(self, symbol: str) -> float:
		return self.positions.get(symbol, Position()).quantity

	def market_value(self, prices: Mapping[str, float]) -> float:
		return float(
			sum(
				position.quantity * prices.get(symbol, position.last_price)
				for symbol, position in self.positions.items()
			)
		)

	def total_value(self, prices: Mapping[str, float]) -> float:
		return float(self.cash + self.market_value(prices))

	def weights(self, prices: Mapping[str, float]) -> dict[str, float]:
		total = self.total_value(prices)
		if total == 0:
			return {symbol: 0.0 for symbol in self.positions}
		return {
			symbol: (position.quantity * prices.get(symbol, position.last_price)) / total
			for symbol, position in self.positions.items()
		}

	def apply_trade(self, trade: TradeRecord) -> None:
		quantity = float(trade.quantity)
		if trade.side == TradeSide.SELL:
			quantity = -quantity
		self.cash -= quantity * trade.price
		self.cash -= trade.cost

		current = self.positions.get(trade.symbol, Position())
		updated = Position(quantity=current.quantity + quantity, last_price=trade.price)
		if abs(updated.quantity) < 1e-12:
			self.positions.pop(trade.symbol, None)
		else:
			self.positions[trade.symbol] = updated

	def mark_to_market(self, prices: Mapping[str, float]) -> None:
		for symbol, position in list(self.positions.items()):
			price = prices.get(symbol, position.last_price)
			self.positions[symbol] = Position(quantity=position.quantity, last_price=price)

	def snapshot(self, prices: Mapping[str, float]) -> PortfolioState:
		total_value = self.total_value(prices)
		copied_positions = {
			symbol: Position(quantity=position.quantity, last_price=position.last_price)
			for symbol, position in self.positions.items()
		}
		return PortfolioState(cash=self.cash, positions=copied_positions, total_value=total_value)
