from __future__ import annotations

import pandas as pd

from mini_backtester import BacktestConfig, BacktestResult
from mini_backtester.metrics import calculate_metrics


def test_total_return_and_final_value(dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0, 101000.0, 102000.0],
            "cash": [100000.0, 100000.0, 100000.0],
            "gross_exposure": [0.0, 0.0, 0.0],
            "net_exposure": [0.0, 0.0, 0.0],
            "daily_return": [0.0, 0.01, 0.00990099],
        },
        index=dates[:3],
    )
    result = BacktestResult(config=BacktestConfig(initial_cash=100000.0), history=history)
    metrics = calculate_metrics(result)
    assert metrics.final_portfolio_value == 102000.0
    assert metrics.total_return == 0.02


def test_annualized_stats(dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0, 101000.0, 100500.0],
            "cash": [100000.0, 100000.0, 100000.0],
            "gross_exposure": [0.0, 0.0, 0.0],
            "net_exposure": [0.0, 0.0, 0.0],
            "daily_return": [0.0, 0.01, -0.0049505],
        },
        index=dates[:3],
    )
    result = BacktestResult(config=BacktestConfig(initial_cash=100000.0), history=history)
    metrics = calculate_metrics(result)
    assert metrics.annualized_volatility >= 0.0
    assert metrics.max_drawdown <= 0.0


def test_trade_based_metrics(dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0, 100000.0],
            "cash": [100000.0, 99900.0],
            "gross_exposure": [0.0, 100.0],
            "net_exposure": [0.0, 100.0],
            "daily_return": [0.0, 0.0],
        },
        index=dates[:2],
    )
    trades = pd.DataFrame(
        {
            "date": [dates[0]],
            "symbol": ["AAA"],
            "side": ["buy"],
            "quantity": [1.0],
            "price": [100.0],
            "notional": [100.0],
            "cost": [1.0],
            "target_weight": [0.5],
        }
    )
    result = BacktestResult(config=BacktestConfig(initial_cash=100000.0), history=history, trades=trades)
    metrics = calculate_metrics(result)
    assert metrics.total_trades == 1
    assert metrics.total_cost == 1.0

