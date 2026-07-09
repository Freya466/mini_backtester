"""Strategy interface and simple built-in strategies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from .types import PortfolioState

"""Strategy interface
    generate_target_weights: method to generate target weights for a given date, signals, and portfolio state"""
class Strategy(Protocol):
	def generate_target_weights(
		self,
		date: pd.Timestamp,
		signals: pd.Series,
		portfolio: PortfolioState,
	) -> dict[str, float]:
		...

"""EqualWeightTopKStrategy: selects the top K assets based on signals and assigns equal weights to them"""
@dataclass(frozen=True)
class EqualWeightTopKStrategy:
	top_k: int = 3
	min_signal: float = 0.0

	def generate_target_weights(
		self,
		date: pd.Timestamp,
		signals: pd.Series,
		portfolio: PortfolioState,
	) -> dict[str, float]:
		ranked = signals.dropna().sort_values(ascending=False)
		chosen = ranked[ranked > self.min_signal].head(self.top_k)
		if chosen.empty:
			return {}
		weight = 1.0 / len(chosen)
		return {symbol: weight for symbol in chosen.index}

"""DirectWeightStrategy: uses the signals directly as weights, filtering out any below a minimum weight"""
@dataclass(frozen=True)
class DirectWeightStrategy:
	minimum_weight: float = 0.0

	def generate_target_weights(
		self,
		date: pd.Timestamp,
		signals: pd.Series,
		portfolio: PortfolioState,
	) -> dict[str, float]:
		weights = signals.dropna().to_dict()
		return {symbol: float(weight) for symbol, weight in weights.items() if float(weight) > self.minimum_weight}
