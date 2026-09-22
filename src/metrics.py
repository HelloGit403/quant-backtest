"""绩效指标：总收益、年化、最大回撤、夏普、卡玛、胜率。"""

from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def sharpe_ratio(returns: pd.Series, risk_free: float = 0.0, periods: int = 252) -> float:
    r = returns.dropna()
    if len(r) < 2:
        return 0.0
    excess = r - risk_free / periods
    vol = r.std(ddof=0)
    if vol <= 0:
        return 0.0
    return float(np.sqrt(periods) * excess.mean() / vol)


def cagr(equity: pd.Series, periods: int = 252) -> float:
    if len(equity) < 2:
        return 0.0
    total = float(equity.iloc[-1] / equity.iloc[0])
    years = len(equity) / periods
    if years <= 0 or total <= 0:
        return 0.0
    return float(total ** (1 / years) - 1)


def win_rate(returns: pd.Series) -> float:
    active = returns[returns != 0]
    if len(active) == 0:
        return 0.0
    return float((active > 0).mean())


def summarize(equity: pd.Series, returns: pd.Series) -> dict:
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1)
    mdd = max_drawdown(equity)
    sharpe = sharpe_ratio(returns)
    ann = cagr(equity)
    calmar = float(ann / abs(mdd)) if mdd < 0 else 0.0
    return {
        "total_return": round(total_return, 4),
        "annualized_return": round(ann, 4),
        "max_drawdown": round(mdd, 4),
        "sharpe": round(sharpe, 3),
        "calmar": round(calmar, 3),
        "win_rate": round(win_rate(returns), 4),
        "start": str(pd.Timestamp(equity.index[0]).date()),
        "end": str(pd.Timestamp(equity.index[-1]).date()),
        "n_days": int(len(equity)),
    }
