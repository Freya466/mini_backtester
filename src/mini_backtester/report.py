from __future__ import annotations

import pandas as pd

from .metrics import calculate_metrics
from .types import BacktestResult

"""
	performance_table()
    What it does: Generates a tabular summary of the backtest performance metrics.

    Input
    result: Completed BacktestResult.
    Output
    Returns a DataFrame containing metric names and their values.
	
	---
    summary_text()
    What it does: Generates a human-readable text summary of the
	key backtest performance metrics.

    Input
    result: Completed BacktestResult.
    Output
    Returns a formatted summary string.
	
	---
    build_report()
    What it does: Creates a complete backtest report containing 
	both the text summary and performance table.

    Input
    result: Completed BacktestResult.
    Output
    Returns a dictionary containing:
    "summary": Formatted performance summary text.
    "table": Performance metrics table (DataFrame).
"""

def performance_table(result: BacktestResult) -> pd.DataFrame:
	metrics = calculate_metrics(result)
	rows = [
		("Final portfolio value", metrics.final_portfolio_value),
		("Total return", metrics.total_return),
		("Annualized return", metrics.annualized_return),
		("Annualized volatility", metrics.annualized_volatility),
		("Sharpe ratio", metrics.sharpe_ratio),
		("Max drawdown", metrics.max_drawdown),
		("Total trades", metrics.total_trades),
		("Total cost", metrics.total_cost),
		("Average cost rate", metrics.average_cost_rate),
		("Average turnover", metrics.average_turnover),
	]
	return pd.DataFrame(rows, columns=["metric", "value"])


def summary_text(result: BacktestResult) -> str:
	metrics = calculate_metrics(result)
	return "\n".join(
		[
			f"Final value: {metrics.final_portfolio_value:.2f}",
			f"Total return: {metrics.total_return:.2%}",
			f"Annualized return: {metrics.annualized_return:.2%}",
			f"Annualized volatility: {metrics.annualized_volatility:.2%}",
			f"Sharpe ratio: {metrics.sharpe_ratio:.2f}",
			f"Max drawdown: {metrics.max_drawdown:.2%}",
		]
	)


def build_report(result: BacktestResult) -> dict[str, object]:
	return {"summary": summary_text(result), "table": performance_table(result)}
