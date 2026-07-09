# AGENTS.md

# Mini Backtester

This file contains instructions for AI coding agents contributing to this repository.

---

# Project Overview

This project implements a **minimal quantitative backtesting package** inspired by the architecture of professional quantitative research frameworks.

The objective is to understand **how a backtesting engine is designed**, not to recreate every production feature.

The implementation should remain intentionally small, modular, and educational while preserving the architectural layering found in larger systems such as Alpha-Quant.

The package simulates how a portfolio evolves over time, records the simulation history, and computes performance statistics from that history.

---

# Project Philosophy

This project values:

- clear architecture over feature completeness
- readability over optimization
- deterministic simulations
- modular design
- explicit data flow
- reproducible results
- separation of responsibilities

The goal is to understand the architecture well enough to build a backtester independently, **not** to copy a production implementation.

When making design decisions, prefer the simplest implementation that preserves the architectural boundaries.

---

# Initial Scope

The first implementation intentionally excludes:

- benchmark-relative analytics
- optimizer frameworks
- ST rules
- VWAP execution
- volume constraints
- market impact
- partial fills
- advanced transaction cost models
- multi-account support
- multi-strategy support

Only implement additional functionality when explicitly requested.

---

# Package Structure

The initial scaffold should follow a standard Python package layout.

```
mini_backtester/

    pyproject.toml

    README.md

    src/
        mini_backtester/

            __init__.py

            backtest.py
            strategy.py
            execution.py
            account.py
            metrics.py
            report.py
            types.py

    tests/
```

The project should use:

- Python 3.12+
- numpy
- pandas
- pytest

Avoid introducing additional dependencies unless there is a clear architectural benefit.

---

# Architecture

The system follows the same high-level flow as larger quantitative backtesting frameworks.

```
Strategy
    ↓
Target Weights
    ↓
Execution
    ↓
Executed Trades
    ↓
Portfolio State
    ↓
Portfolio History
    ↓
Metrics
    ↓
Report
```

The Backtest Engine coordinates these components but should not own their logic.

---

# Core Data Objects

The system revolves around three primary data objects.

## Market State

Read-only market information.

Examples:

- prices
- returns
- trading calendar

The simulation never modifies market state.

---

## Portfolio State

Mutable simulation state.

Examples:

- cash
- holdings
- portfolio value
- portfolio weights

The portfolio state changes throughout the simulation.

---

## Portfolio History

Immutable simulation record.

Examples:

- portfolio value
- daily return
- turnover
- transaction cost
- positions
- executed trades

Portfolio history becomes the single source of truth for all analytics.

Once recorded, history should never be modified.

---

# Architectural Responsibilities

## strategy.py

Owns portfolio decisions.

Input:

- market state
- current portfolio state

Output:

- target weights

Never:

- execute trades
- update holdings
- compute metrics

---

## execution.py

Owns execution.

Input:

- target weights
- market prices

Output:

- executed trades

Responsible for:

- execution price
- transaction costs
- converting weights into fills

Never decides portfolio allocation.

---

## account.py

Owns portfolio state.

Responsible for:

- holdings
- cash
- valuation
- history recording

Never computes performance statistics.

---

## backtest.py

Owns orchestration.

Coordinates:

- strategy
- execution
- account

Never contains strategy logic.

Never computes metrics.

---

## metrics.py

Consumes:

- portfolio history
- trade records

Produces:

- performance statistics

Never modifies simulation state.

---

## report.py

Formats results for presentation.

Consumes:

- metrics
- history

Never reruns the simulation.

---

## types.py

Contains shared data structures.

Examples:

- Order
- Trade
- PortfolioState
- DailySnapshot
- BacktestResult

Keep data objects lightweight and reusable.

---

# Architectural Constraints

These rules should always remain true.

## Responsibility Boundaries

The Strategy decides.

The Execution layer executes.

The Account remembers.

The Metrics layer summarizes.

The Report presents.

No module should perform another module's responsibility.

---

## Dependency Direction

Dependencies should always flow in one direction.

```
Strategy

↓

Execution

↓

Account

↓

History

↓

Metrics

↓

Report
```

Higher layers should never depend on lower-level analysis components.

Metrics must never influence simulation.

Reports must never influence metrics.

---

## Simulation Boundary

The simulation produces history.

The analytics consume history.

```
Simulation

↓

Portfolio History

↓

Metrics

↓

Report
```

Performance statistics should always be recomputable from the recorded history without rerunning the simulation.

---

## State Transition Model

The simulation should be viewed as repeated state transitions.

For every trading day:

```
Portfolio State(t)

↓

Strategy Decision

↓

Execution

↓

Portfolio State(t+1)

↓

Record Daily Snapshot
```

The engine repeatedly transforms one portfolio state into the next.

---

# Development Plan

The implementation should follow this order.

## Phase 1

Create the package scaffold.

Define:

- pyproject.toml
- package structure
- source layout
- test layout

---

## Phase 2

Write the README.

The README acts as the project's behavioral contract.

It should define:

- package purpose
- architecture
- expected inputs
- daily simulation flow
- outputs
- metrics
- simple example run

Implementation should follow the README rather than the reverse.

---

## Phase 3

Define the shared data structures.

Examples:

- MarketData
- PortfolioState
- Order
- Trade
- DailySnapshot
- BacktestResult

---

## Phase 4

Implement:

- Account
- Execution
- Strategy interface
- Backtest Engine

---

## Phase 5

Implement:

- Metrics
- Reporting

---

## Phase 6

Validate using deterministic synthetic datasets.

Recommended scenarios:

- one rising stock
- flat market
- always-flat strategy
- missing prices
- manually verified two-day example

---

# Testing Philosophy

Prefer deterministic synthetic datasets over historical market data.

Every simulation should produce reproducible results.

Where practical, verify calculations by hand using small examples.

Tests should validate:

- portfolio evolution
- cash updates
- holdings
- daily returns
- recorded history
- performance metrics

---

# Agent Guidelines

When contributing to this repository:

- Preserve the architectural boundaries.
- Make the smallest cohesive change.
- Extend existing modules before creating new ones.
- Avoid unnecessary abstractions.
- Keep implementations simple and educational.
- Prefer explicit code over clever optimizations.
- Do not introduce production-level complexity unless explicitly requested.

If a proposed implementation violates the architecture described above, prefer refactoring the implementation rather than changing the architecture.

The architecture is considered the primary design contract of this project.