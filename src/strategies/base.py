"""策略基类：所有策略返回 0/1 目标仓位序列。"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """输入 OHLCV，输出目标仓位（1=持有，0=空仓）。"""

    name: str = "base"

    @abstractmethod
    def generate(self, df: pd.DataFrame) -> pd.Series:
        """df 需含 open/high/low/close/volume。返回与 index 对齐的仓位序列。"""
        raise NotImplementedError
