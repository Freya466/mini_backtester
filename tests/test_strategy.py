from __future__ import annotations

from mini_backtester import EqualWeightTopKStrategy, PortfolioState
from mini_backtester.types import Position


def test_signal_to_weight_conversion(dates, signals):
    strategy = EqualWeightTopKStrategy(top_k=2)
    portfolio = PortfolioState(cash=100000.0, positions={"AAA": Position(quantity=0, last_price=100.0)}, total_value=100000.0)
    weights = strategy.generate_target_weights(dates[0], signals.loc[dates[0]], portfolio)
    assert weights == {"AAA": 0.5, "BBB": 0.5}


def test_rebalance_behavior(dates, signals):
    strategy = EqualWeightTopKStrategy(top_k=1)
    portfolio = PortfolioState(cash=100000.0, positions={}, total_value=100000.0)
    weights = strategy.generate_target_weights(dates[0], signals.loc[dates[0]], portfolio)
    assert weights == {"AAA": 1.0}

