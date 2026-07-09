from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def dates() -> pd.DatetimeIndex:
    return pd.date_range("2024-01-01", periods=4, freq="D")


@pytest.fixture
def universe() -> list[str]:
    return ["AAA", "BBB"]


@pytest.fixture
def prices(dates: pd.DatetimeIndex, universe: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "AAA": [100.0, 101.0, 102.0, 104.0],
            "BBB": [50.0, 50.5, 51.0, 51.5],
        },
        index=dates,
    )


@pytest.fixture
def returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().fillna(0.0)


@pytest.fixture
def signals(dates: pd.DatetimeIndex, universe: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "AAA": [0.9, 0.4, 0.8, 0.2],
            "BBB": [0.1, 0.7, 0.3, 0.9],
        },
        index=dates,
    )


@pytest.fixture
def config():
    from mini_backtester import BacktestConfig

    return BacktestConfig(initial_cash=100000.0, rebalance_frequency=1, transaction_cost_bps=10.0)

