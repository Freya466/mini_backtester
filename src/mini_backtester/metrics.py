from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .types import BacktestResult

"""MetricSummary: Stores the performance metrics calculated from a completed backtest, 
    including returns, risk measures, trading statistics, and transaction cost metrics.

    ---
    calculate_metrics()
    What it does: Computes performance and trading statistics from a completed backtest result.

    Input
    result: Completed BacktestResult containing portfolio history, trades, and configuration.
    Output
    Returns a MetricSummary containing:
    Final portfolio value
    Total return
    Daily returns
    Annualized return
    Annualized volatility
    Sharpe ratio
    Maximum drawdown
    Total number of trades
    Total transaction cost
    Average transaction cost rate
    Average portfolio turnover
"""

@dataclass(frozen=True)
class MetricSummary:
    final_portfolio_value: float
    total_return: float
    daily_returns: pd.Series
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int = 0
    total_cost: float = 0.0
    average_cost_rate: float = 0.0
    average_turnover: float = 0.0


def calculate_metrics(result: BacktestResult) -> MetricSummary:
    history = result.history.copy()
    if history.empty:
        empty_returns = pd.Series(dtype=float)
        return MetricSummary(
            final_portfolio_value=result.config.initial_cash,
            total_return=0.0,
            daily_returns=empty_returns,
            annualized_return=0.0,
            annualized_volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
        )

    daily_returns = history["daily_return"].astype(float)
    final_value = float(history["portfolio_value"].iloc[-1])
    total_return = round(final_value / result.config.initial_cash - 1.0, 12)
    annual_factor = result.config.annualization_factor
    periods = max(len(daily_returns), 1)
    annualized_return = round((final_value / result.config.initial_cash) ** (annual_factor / periods) - 1.0, 12)
    volatility = float(daily_returns.std(ddof=1) * np.sqrt(annual_factor)) if len(daily_returns) > 1 else 0.0
    sharpe = 0.0 if volatility == 0 else float(daily_returns.mean() / daily_returns.std(ddof=1) * np.sqrt(annual_factor))
    running_max = history["portfolio_value"].cummax()
    drawdown = history["portfolio_value"] / running_max - 1.0
    max_drawdown = float(drawdown.min())

    total_trades = int(len(result.trades)) if not result.trades.empty else 0
    total_cost = float(result.trades["cost"].sum()) if not result.trades.empty and "cost" in result.trades else 0.0
    total_notional = float(result.trades["notional"].abs().sum()) if not result.trades.empty and "notional" in result.trades else 0.0
    average_cost_rate = 0.0 if total_notional == 0 else total_cost / total_notional
    if not result.trades.empty and "notional" in result.trades and "date" in result.trades:
        trades_by_day = result.trades.groupby("date")["notional"].sum().abs()
        aligned_values = history["portfolio_value"].reindex(trades_by_day.index, method="ffill")
        average_turnover = float((trades_by_day / aligned_values).mean()) if not trades_by_day.empty else 0.0
    else:
        average_turnover = 0.0

    return MetricSummary(
        final_portfolio_value=final_value,
        total_return=total_return,
        daily_returns=daily_returns,
        annualized_return=annualized_return,
        annualized_volatility=volatility,
        sharpe_ratio=sharpe,
        max_drawdown=max_drawdown,
        total_trades=total_trades,
        total_cost=total_cost,
        average_cost_rate=average_cost_rate,
        average_turnover=average_turnover,
    )

