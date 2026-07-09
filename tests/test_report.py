from __future__ import annotations

import pandas as pd

from mini_backtester import BacktestConfig, BacktestResult
from mini_backtester.report import build_report, performance_table, summary_text


def test_summary_contains_expected_numbers(dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0, 105000.0],
            "cash": [100000.0, 100000.0],
            "gross_exposure": [0.0, 0.0],
            "net_exposure": [0.0, 0.0],
            "daily_return": [0.0, 0.05],
        },
        index=dates[:2],
    )
    result = BacktestResult(config=BacktestConfig(initial_cash=100000.0), history=history)
    summary = summary_text(result)
    assert "105000.00" in summary
    assert "5.00%" in summary


def test_table_generation(dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0, 105000.0],
            "cash": [100000.0, 100000.0],
            "gross_exposure": [0.0, 0.0],
            "net_exposure": [0.0, 0.0],
            "daily_return": [0.0, 0.05],
        },
        index=dates[:2],
    )
    result = BacktestResult(config=BacktestConfig(initial_cash=100000.0), history=history)
    table = performance_table(result)
    assert set(table.columns) == {"metric", "value"}
    assert "Final portfolio value" in table["metric"].values


def test_report_reads_stored_history_not_engine_internals(dates):
    history = pd.DataFrame(
        {
            "portfolio_value": [100000.0, 105000.0],
            "cash": [100000.0, 100000.0],
            "gross_exposure": [0.0, 0.0],
            "net_exposure": [0.0, 0.0],
            "daily_return": [0.0, 0.05],
        },
        index=dates[:2],
    )
    result = BacktestResult(config=BacktestConfig(initial_cash=100000.0), history=history)
    report = build_report(result)
    assert "summary" in report and "table" in report
