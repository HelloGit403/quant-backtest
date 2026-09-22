"""动量策略：过去 lookback 日收益率为正则持有。"""

from __future__ import annotations

import pandas as pd

from .base import Strategy


class Momentum(Strategy):
    name = "momentum"

    def __init__(self, lookback: int = 20):
        if lookback < 2:
            raise ValueError("lookback 至少为 2")
        self.lookback = lookback

    def generate(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        ret = close.pct_change(self.lookback)
        pos = (ret > 0).astype(float)
        pos[ret.isna()] = 0.0
        return pos.rename("position")
