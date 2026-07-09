from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .account import Portfolio
from .execution import Exchange
from .strategy import Strategy
from .types import BacktestConfig, BacktestResult, HistoryRow, Order

"""BacktestEngine: Runs the backtesting simulation by coordinating the strategy,
    portfolio, exchange, and market data to produce portfolio history and trade records.

    ---
    __post_init__()
    What it does: Initializes a default Exchange if one is not provided.

    Input
    None.
    Output
    None.
	
	---
    run()
    What it does: Executes the complete backtest by validating inputs,
	generating target weights, executing trades, updating prices, tracking
	portfolio performance, and returning the results.

    Input
    returns: DataFrame of daily asset returns.
    signals: (Optional) DataFrame of strategy signals aligned with the returns.
    Output
    Returns a BacktestResult containing portfolio history and executed trades.

	---
    _execute_target_weights()
    What it does: Converts target portfolio weights into orders, executes 
	them through the exchange, and records any resulting trades.

    Input
    date: Current trading date.
    target_weights: Dictionary of {symbol: target_weight}.
    portfolio: Current portfolio state.
    prices: Current asset prices.
    trade_rows: List used to store executed trade records.
    Output
    None (updates trade_rows and portfolio through the exchange).

	---
    _advance_prices()
    What it does: Updates asset prices by applying one day's returns.

    Input
    prices: Current asset prices.
    row_returns: Daily returns for each asset.
    Output
    Returns a new Series of updated asset prices.

	---
    _align_signals()
    What it does: Aligns the signals DataFrame with the returns DataFrame, 
	filling any missing values with zero.

    Input
    returns: DataFrame of asset returns.
    signals: (Optional) DataFrame of strategy signals.
    Output
    Returns an aligned signals DataFrame.

	---
    _validate_inputs()
	What it does: Checks that the backtest inputs are valid before the simulation begins.

    Input
    returns: DataFrame of asset returns.
    signals: (Optional) DataFrame of strategy signals.
    Output
    None (raises an exception if validation fails).
    
	---
    run_backtest()
    What it does: Convenience function that creates a BacktestEngine 
	and runs a backtest in a single call.

    Input
    returns: DataFrame of daily asset returns.
    strategy: Strategy used to generate portfolio weights.
    config: Backtest configuration settings.
    signals: (Optional) DataFrame of strategy signals.
    exchange: (Optional) Custom exchange implementation.
    Output
    Returns a BacktestResult containing portfolio history and executed trades.
    """

@dataclass
class BacktestEngine:
	config: BacktestConfig
	strategy: Strategy
	exchange: Exchange | None = None

	def __post_init__(self) -> None:
		if self.exchange is None:
			self.exchange = Exchange(self.config)

	def run(self, returns: pd.DataFrame, signals: pd.DataFrame | None = None) -> BacktestResult:
		self._validate_inputs(returns, signals)

		assets = list(returns.columns)
		aligned_signals = self._align_signals(returns, signals)
		portfolio = Portfolio(cash=self.config.initial_cash)
		prices = pd.Series(self.config.starting_price, index=assets, dtype=float)

		history_rows: list[HistoryRow] = []
		trade_rows: list[dict[str, object]] = []
		previous_value = self.config.initial_cash

		for day_index, date in enumerate(returns.index):
			row_returns = returns.loc[date].reindex(assets)
			if day_index % self.config.rebalance_frequency == 0:
				signal_row = aligned_signals.loc[date].reindex(assets)
				target_weights = self.strategy.generate_target_weights(
					date=date,
					signals=signal_row,
					portfolio=portfolio.snapshot(prices.to_dict()),
				)
				self._execute_target_weights(date, target_weights, portfolio, prices, trade_rows)

			prices = self._advance_prices(prices, row_returns)
			portfolio.mark_to_market(prices.to_dict())
			current_value = portfolio.total_value(prices.to_dict())
			daily_return = 0.0 if day_index == 0 or previous_value == 0 else current_value / previous_value - 1.0
			previous_value = current_value

			gross_exposure = sum(abs(position.quantity * position.last_price) for position in portfolio.positions.values())
			net_exposure = sum(position.quantity * position.last_price for position in portfolio.positions.values())
			history_rows.append(
				HistoryRow(
					date=date,
					portfolio_value=current_value,
					cash=portfolio.cash,
					gross_exposure=gross_exposure,
					net_exposure=net_exposure,
					daily_return=daily_return,
				)
			)

		history = pd.DataFrame([row.__dict__ for row in history_rows]).set_index("date")
		trades = pd.DataFrame(trade_rows)
		if not trades.empty:
			trades = trades.sort_values(["date", "symbol"]).reset_index(drop=True)
		return BacktestResult(config=self.config, history=history, trades=trades)

	def _execute_target_weights(
		self,
		date: pd.Timestamp,
		target_weights: dict[str, float],
		portfolio: Portfolio,
		prices: pd.Series,
		trade_rows: list[dict[str, object]],
	) -> None:
		for symbol, target_weight in target_weights.items():
			order = Order(date=date, symbol=symbol, target_weight=float(target_weight))
			trade = self.exchange.execute_order(order, portfolio, prices.to_dict())  # type: ignore[union-attr]
			if trade is not None:
				trade_rows.append(trade.__dict__)

	def _advance_prices(self, prices: pd.Series, row_returns: pd.Series) -> pd.Series:
		next_prices = prices.copy()
		for symbol, daily_return in row_returns.items():
			if pd.notna(daily_return):
				next_prices[symbol] = prices[symbol] * (1.0 + float(daily_return))
		return next_prices

	def _align_signals(self, returns: pd.DataFrame, signals: pd.DataFrame | None) -> pd.DataFrame:
		if signals is None:
			return pd.DataFrame(0.0, index=returns.index, columns=returns.columns)
		return signals.reindex(index=returns.index, columns=returns.columns).fillna(0.0)

	def _validate_inputs(self, returns: pd.DataFrame, signals: pd.DataFrame | None) -> None:
		if returns.empty:
			raise ValueError("returns must not be empty")
		if not isinstance(returns.index, pd.DatetimeIndex):
			raise TypeError("returns must use a DatetimeIndex")
		if signals is not None and len(signals.index.intersection(returns.index)) == 0:
			raise ValueError("signals must overlap returns dates")
		if self.config.rebalance_frequency <= 0:
			raise ValueError("rebalance_frequency must be positive")


def run_backtest(
	returns: pd.DataFrame,
	strategy: Strategy,
	config: BacktestConfig,
	signals: pd.DataFrame | None = None,
	exchange: Exchange | None = None,
) -> BacktestResult:
	engine = BacktestEngine(config=config, strategy=strategy, exchange=exchange)
	return engine.run(returns=returns, signals=signals)
