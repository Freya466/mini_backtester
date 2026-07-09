from __future__ import annotations

import pandas as pd

from mini_backtester import BacktestConfig, BacktestEngine, EqualWeightTopKStrategy


def test_one_asset_rising_market(dates):
    returns = pd.DataFrame({"AAA": [0.0, 0.01, 0.02, 0.03]}, index=dates)
    signals = pd.DataFrame({"AAA": [1.0, 1.0, 1.0, 1.0]}, index=dates)
    engine = BacktestEngine(config=BacktestConfig(initial_cash=100000.0), strategy=EqualWeightTopKStrategy(top_k=1))
    result = engine.run(returns=returns, signals=signals)
    assert result.final_value > 100000.0
    assert len(result.history) == 4


def test_flat_market(dates):
    returns = pd.DataFrame({"AAA": [0.0, 0.0, 0.0, 0.0]}, index=dates)
    signals = pd.DataFrame({"AAA": [1.0, 1.0, 1.0, 1.0]}, index=dates)
    engine = BacktestEngine(config=BacktestConfig(initial_cash=100000.0), strategy=EqualWeightTopKStrategy(top_k=1))
    result = engine.run(returns=returns, signals=signals)
    assert result.final_value <= 100000.0


def test_missing_data_behavior(dates):
    returns = pd.DataFrame({"AAA": [0.0, 0.01, float("nan"), 0.02]}, index=dates)
    signals = pd.DataFrame({"AAA": [1.0, 1.0, 1.0, 1.0]}, index=dates)
    engine = BacktestEngine(config=BacktestConfig(initial_cash=100000.0), strategy=EqualWeightTopKStrategy(top_k=1))
    result = engine.run(returns=returns, signals=signals)
    assert len(result.history) == 4


def test_rebalance_frequency(dates):
    returns = pd.DataFrame({"AAA": [0.0, 0.01, 0.02, 0.03]}, index=dates)
    signals = pd.DataFrame({"AAA": [1.0, 0.0, 1.0, 0.0]}, index=dates)
    config = BacktestConfig(initial_cash=100000.0, rebalance_frequency=2)
    engine = BacktestEngine(config=config, strategy=EqualWeightTopKStrategy(top_k=1))
    result = engine.run(returns=returns, signals=signals)
    assert len(result.history) == 4


def test_history_recording(dates):
    returns = pd.DataFrame({"AAA": [0.0, 0.01, 0.01, 0.01]}, index=dates)
    signals = pd.DataFrame({"AAA": [1.0, 1.0, 1.0, 1.0]}, index=dates)
    engine = BacktestEngine(config=BacktestConfig(initial_cash=100000.0), strategy=EqualWeightTopKStrategy(top_k=1))
    result = engine.run(returns=returns, signals=signals)
    assert {"portfolio_value", "cash", "gross_exposure", "net_exposure", "daily_return"}.issubset(result.history.columns)

