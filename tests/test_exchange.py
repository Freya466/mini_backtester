from __future__ import annotations

from mini_backtester import Exchange, Portfolio
from mini_backtester.types import BacktestConfig, Order, TradeSide


def test_price_selection_and_cost_calculation(dates):
    config = BacktestConfig(transaction_cost_bps=10.0)
    exchange = Exchange(config)
    portfolio = Portfolio(cash=1000.0)
    order = Order(date=dates[0], symbol="AAA", target_weight=0.5)
    trade = exchange.execute_order(order, portfolio, {"AAA": 10.0})
    assert trade is not None
    assert trade.price == 10.0
    assert trade.cost == 0.5
    assert trade.side == TradeSide.BUY


def test_fillable_vs_non_fillable_orders(dates):
    config = BacktestConfig(transaction_cost_bps=0.0)
    exchange = Exchange(config, volume_limit=0.1)
    portfolio = Portfolio(cash=1000.0)
    fillable = exchange.execute_order(Order(dates[0], "AAA", 0.5), portfolio, {"AAA": 10.0}, volume=100)
    non_fillable = exchange.execute_order(Order(dates[0], "AAA", 1.0), portfolio, {"AAA": 10.0}, volume=5)
    assert fillable is not None
    assert non_fillable is None


def test_amount_rounding(dates):
    config = BacktestConfig(transaction_cost_bps=0.0, whole_shares=True)
    exchange = Exchange(config)
    portfolio = Portfolio(cash=1000.0)
    trade = exchange.execute_order(Order(dates[0], "AAA", 0.33), portfolio, {"AAA": 7.0})
    assert trade is not None
    assert trade.quantity == round((1000.0 * 0.33) / 7.0)

