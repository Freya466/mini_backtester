from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from .account import Portfolio
from .types import BacktestConfig, Order, TradeRecord, TradeSide

"""Exchange: Simulates trade execution by converting target portfolio weights into 
    executable trades while applying execution rules such as whole-share constraints, volume limits, and transaction costs.

    ---
    execute_order()
    What it does: Executes an order by calculating the required trade size, validating execution constraints, 
	applying transaction costs, updating the portfolio, and returning the executed trade.

    Input
    order: Target portfolio order to execute.
    portfolio: Current portfolio to update.
    prices: Mapping of {symbol: current_price}.
    volume: (Optional) Maximum tradable volume for the asset.
    Output
    Returns a TradeRecord if the order is executed, otherwise None if the order cannot or should not be executed.
"""

@dataclass(frozen=True)
class Exchange:
	config: BacktestConfig
	volume_limit: float | None = None

	def execute_order(
		self,
		order: Order,
		portfolio: Portfolio,
		prices: Mapping[str, float],
		volume: float | None = None,
	) -> TradeRecord | None:
		price = float(prices.get(order.symbol, float("nan")))
		if pd.isna(price):
			return None
		if order.target_weight < 0:
			return None

		portfolio_value = portfolio.total_value(prices)
		desired_value = portfolio_value * order.target_weight
		desired_quantity = desired_value / price
		current_quantity = portfolio.position_quantity(order.symbol)
		delta_quantity = desired_quantity - current_quantity

		if self.config.whole_shares:
			delta_quantity = float(round(delta_quantity))
		if abs(delta_quantity) < 1e-12:
			return None

		if self.volume_limit is not None and volume is not None:
			max_shares = float(volume)
			if abs(delta_quantity) > max_shares:
				return None

		side = TradeSide.BUY if delta_quantity > 0 else TradeSide.SELL
		quantity = abs(delta_quantity)
		notional = quantity * price
		cost = notional * self.config.transaction_cost_bps / 10000.0
		trade = TradeRecord(
			date=order.date,
			symbol=order.symbol,
			side=side,
			quantity=quantity,
			price=price,
			notional=notional,
			cost=cost,
			target_weight=order.target_weight,
		)
		portfolio.apply_trade(trade)
		return trade
