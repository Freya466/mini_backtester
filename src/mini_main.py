"""Mini Backtester Main Placeholder script
     takes placeholder returns and signals data and runs a backtest using the EqualWeightTopKStrategy"""

import pandas as pd

from mini_backtester.backtest import BacktestEngine
from mini_backtester.types import BacktestConfig
from mini_backtester.strategy import EqualWeightTopKStrategy
from mini_backtester.metrics import calculate_metrics
from mini_backtester.report import build_report

"""Hardcoded returns and signals data for testing purposes"""
dates = pd.date_range("2024-01-01", periods=14, freq="D")
returns = pd.DataFrame(
    {
        "AAA": [0.012, -0.005, 0.024, 0.011, -0.008, 0.015, 0.007, -0.003, 0.009, 0.002, -0.004, 0.006, 0.001, -0.002],
        "BBB": [0.001, 0.033, -0.021, 0.014, 0.005, -0.009, 0.012, 0.004, -0.006, 0.008, 0.003, -0.002, 0.007, 0.002],
        "CCC": [0.032, 0.025, -0.013, 0.018, -0.007, 0.022, 0.009, -0.004, 0.011, 0.003, -0.005, 0.007, 0.002, -0.003],
    },
    index=dates,
)
signals = pd.DataFrame(
    {
        "AAA": [1.0, 0.2, 0.9, 0.4, 0.8, 0.1, 0.7, 0.3, 0.6, 0.2, 0.5, 0.9, 0.4, 0.8],
        "BBB": [0.5, 0.8, 0.1, 0.6, 0.9, 0.2, 0.7, 0.4, 0.3, 0.5, 0.1, 0.8, 0.6, 0.2],
        "CCC": [0.3, 0.6, 0.4, 0.7, 0.1, 0.9, 0.2, 0.5, 0.8, 0.4, 0.6, 0.3, 0.7, 0.1],
    },
    index=dates,
)

""" initial_cash: cash portfolio starts with
     rebalance_frequency: how often to rebalance the portfolio (in days)
     strategy: the strategy to use for generating target weights
     top_k: the number of top assets to select for equal weighting"""
engine = BacktestEngine(
    config=BacktestConfig(initial_cash=100000.0, rebalance_frequency=1),
    strategy=EqualWeightTopKStrategy(top_k=2),
)

""" runs engine with the provided returns and signals data, returning a BacktestResult object"""
result = engine.run(returns=returns, signals=signals)
metrics = calculate_metrics(result)
report = build_report(result)
print(metrics.total_return)
print(report["summary"])
print(report["table"])