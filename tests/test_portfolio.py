from __future__ import annotations

from mini_backtester import Portfolio
from mini_backtester.types import TradeRecord, TradeSide


def test_cash_updates_after_buy_and_sell(dates):
    portfolio = Portfolio(cash=1000.0)
    buy = TradeRecord(dates[0], "AAA", TradeSide.BUY, 5, 10.0, 50.0, 0.5, 0.0)
    sell = TradeRecord(dates[1], "AAA", TradeSide.SELL, 2, 12.0, 24.0, 0.0, 0.0)
    portfolio.apply_trade(buy)
    portfolio.apply_trade(sell)
    assert portfolio.cash == 973.5


def test_holdings_and_value_calculation(dates):
    portfolio = Portfolio(cash=1000.0)
    trade = TradeRecord(dates[0], "AAA", TradeSide.BUY, 5, 10.0, 50.0, 0.5, 0.0)
    portfolio.apply_trade(trade)
    assert portfolio.position_quantity("AAA") == 5
    assert portfolio.total_value({"AAA": 12.0}) == 1009.5


def test_mark_to_market_updates_prices(dates):
    portfolio = Portfolio(cash=1000.0)
    trade = TradeRecord(dates[0], "AAA", TradeSide.BUY, 5, 10.0, 50.0, 0.5, 0.0)
    portfolio.apply_trade(trade)
    portfolio.mark_to_market({"AAA": 13.0})
    assert portfolio.positions["AAA"].last_price == 13.0


def test_weight_calculation(dates):
    portfolio = Portfolio(cash=1000.0)
    trade = TradeRecord(dates[0], "AAA", TradeSide.BUY, 5, 10.0, 50.0, 0.5, 0.0)
    portfolio.apply_trade(trade)
    weights = portfolio.weights({"AAA": 10.0})
    assert weights["AAA"] == 50.0 / 999.5

