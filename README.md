# mini_backtester

`mini_backtester` is a small, deterministic daily backtesting package for learning the architecture of a quantitative research engine.

## Installation

This project uses:

- Python 3.12+
- numpy
- pandas
- pytest for tests

Install the project in editable mode from the repository root:

```bash
python -m pip install -e .
python -m pip install -e .[test]
```

## Canonical Imports

Use the module-level imports below as the canonical application surface:

```python
from mini_backtester.backtest import BacktestEngine
from mini_backtester.types import BacktestConfig
from mini_backtester.strategy import EqualWeightTopKStrategy
from mini_backtester.metrics import calculate_metrics
from mini_backtester.report import build_report
```

The canonical module layout is:

- `mini_backtester.backtest`
- `mini_backtester.account`
- `mini_backtester.execution`
- `mini_backtester.strategy`
- `mini_backtester.metrics`
- `mini_backtester.report`
- `mini_backtester.types`

You can also import the remaining modules directly when needed:

```python
from mini_backtester.execution import Exchange
from mini_backtester.account import Portfolio
from mini_backtester.types import BacktestResult, TradeRecord
```

## Architectural Mapping

The project follows a simple top-down flow:

Strategy -> Target Weights -> Execution -> Executed Trades -> Portfolio State -> Portfolio History -> Metrics -> Report

Module responsibilities:

- `mini_backtester.strategy` decides target weights from signals and current state.
- `mini_backtester.execution` converts target weights into executed trades.
- `mini_backtester.account` owns cash, holdings, valuation, and state transitions.
- `mini_backtester.backtest` coordinates the daily loop.
- `mini_backtester.metrics` summarizes recorded history and trade records.
- `mini_backtester.report` formats the final results for presentation.
- `mini_backtester.types` defines shared data objects such as config, orders, trades, snapshots, and results.

## Quickstart

```python
import pandas as pd

from mini_backtester.backtest import BacktestEngine
from mini_backtester.types import BacktestConfig
from mini_backtester.strategy import EqualWeightTopKStrategy

dates = pd.date_range("2024-01-01", periods=3, freq="D")
returns = pd.DataFrame(
    {
        "AAA": [0.01, 0.00, 0.02],
        "BBB": [0.00, 0.01, -0.01],
    },
    index=dates,
)
signals = pd.DataFrame(
    {
        "AAA": [1.0, 0.2, 0.9],
        "BBB": [0.5, 0.8, 0.1],
    },
    index=dates,
)

engine = BacktestEngine(
    config=BacktestConfig(initial_cash=100000.0, rebalance_frequency=1),
    strategy=EqualWeightTopKStrategy(top_k=2),
)

result = engine.run(returns=returns, signals=signals)
print(result.final_value)
```

To inspect the analytics and the presentation layer:

```python
from mini_backtester.metrics import calculate_metrics
from mini_backtester.report import build_report

metrics = calculate_metrics(result)
report = build_report(result)
print(metrics.total_return)
print(report["summary"])
print(report["table"])
```

## Inputs

The engine accepts:

- `returns`: a `pandas.DataFrame` of daily returns indexed by `DatetimeIndex`
- `signals`: an optional `pandas.DataFrame` of daily signal values aligned to the same dates and asset columns
- `config`: a `BacktestConfig` object that controls initial cash, rebalance frequency, transaction costs, annualization factor, and share rounding behavior
- `strategy`: an object that implements `generate_target_weights(date, signals, portfolio)`

The current v1 design derives prices internally from the return series using a starting price of 100.0 per asset.

## Final Outputs

The simulation returns a `BacktestResult` containing:

- `history`: the recorded daily portfolio history as a `pandas.DataFrame`
- `trades`: the executed trade records as a `pandas.DataFrame`
- `config`: the `BacktestConfig` used for the run
- `final_value`: the final portfolio value as a convenience property

The analytics layer produces a `MetricSummary` with:

- final portfolio value
- total return
- daily returns
- annualized return
- annualized volatility
- Sharpe ratio
- max drawdown
- trade count and trade cost statistics when trades exist

The reporting layer produces:

- a short text summary
- a compact performance table

## Version-one Contract

- Input data is a `pandas.DataFrame` of daily returns indexed by date.
- Prices are derived internally from a starting price of 100.0 per asset.
- A strategy converts signals into target weights.
- The engine rebalances on a fixed schedule, applies execution at the prior close, and marks the portfolio to market at the end of each day.
- Analytics are computed from stored history only.

## Minimal Flow

1. Start with cash.
2. Build a synthetic price path from the return series.
3. On rebalance dates, ask the strategy for target weights.
4. Let the exchange translate target weights into fills.
5. Update the portfolio and record the day-end value.
6. Compute metrics from the recorded history.
