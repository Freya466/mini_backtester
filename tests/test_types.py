from __future__ import annotations

import pandas as pd

from mini_backtester import BacktestConfig, BacktestResult, Position, TradeRecord, TradeSide


def test_config_defaults():
    config = BacktestConfig()
    assert config.initial_cash == 100000.0
    assert config.rebalance_frequency == 1
    assert config.transaction_cost_bps == 0.0


def test_position_value_calculation():
    position = Position(quantity=10, last_price=12.5)
    assert position.market_value == 125.0


def test_trade_record_fields(dates):
    trade = TradeRecord(
        date=dates[0],
        symbol="AAA",
        side=TradeSide.BUY,
        quantity=10,
        price=100.0,
        notional=1000.0,
        cost=1.0,
        target_weight=0.5,
    )
    assert trade.symbol == "AAA"
    assert trade.side == TradeSide.BUY
    assert trade.notional == 1000.0


def test_result_object_construction(config, dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0],
            "cash": [100000.0],
            "gross_exposure": [0.0],
            "net_exposure": [0.0],
            "daily_return": [0.0],
        },
        index=dates[:1],
    )
    result = BacktestResult(config=config, history=history)
    assert result.final_value == 100000.0

