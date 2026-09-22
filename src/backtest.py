"""向量化回测引擎：目标仓位 → 日收益 → 净值。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    position: pd.Series
    price: pd.Series
    fee_rate: float
    slippage: float

    @property
    def trades(self) -> int:
        pos = self.position.fillna(0)
        return int((pos.diff().abs() > 1e-9).sum())


def run_backtest(
    df: pd.DataFrame,
    position: pd.Series,
    fee_rate: float = 0.0003,
    slippage: float = 0.001,
    initial_capital: float = 1.0,
) -> BacktestResult:
    """
    简化假设：
    - position[t] 表示 t 日收盘时的目标仓位（收盘调仓）
    - t 日收益用 position[t-1] 乘上 t 日价格变动（避免未来函数）
    - 换仓时按 |Δposition| 收取 fee + slippage
    """
    if not df.index.equals(position.index):
        position = position.reindex(df.index).fillna(0.0)

    price = df["close"].astype(float)
    daily_ret = price.pct_change().fillna(0.0)

    pos = position.astype(float).fillna(0.0)
    prev_pos = pos.shift(1).fillna(0.0)

    gross = prev_pos * daily_ret
    turnover = (pos - prev_pos).abs()
    cost = turnover * (fee_rate + slippage)
    net = gross - cost

    equity = initial_capital * (1.0 + net).cumprod()
    equity.iloc[0] = initial_capital

    return BacktestResult(
        equity=equity,
        returns=net,
        position=pos,
        price=price,
        fee_rate=fee_rate,
        slippage=slippage,
    )


def buy_and_hold(df: pd.DataFrame, fee_rate: float = 0.0, slippage: float = 0.0) -> BacktestResult:
    ones = pd.Series(1.0, index=df.index, name="position")
    return run_backtest(df, ones, fee_rate=fee_rate, slippage=slippage)
