"""双均线策略：快线上穿慢线持有，下穿空仓。"""

from __future__ import annotations

import pandas as pd

from .base import Strategy


class MACross(Strategy):
    name = "ma_cross"

    def __init__(self, fast: int = 10, slow: int = 30):
        if fast >= slow:
            raise ValueError("fast 必须小于 slow")
        self.fast = fast
        self.slow = slow

    def generate(self, df: pd.DataFrame) -> pd.Series:
        close = df["close"]
        fast_ma = close.rolling(self.fast).mean()
        slow_ma = close.rolling(self.slow).mean()
        pos = (fast_ma > slow_ma).astype(float)
        pos[fast_ma.isna() | slow_ma.isna()] = 0.0
        return pos.rename("position")
