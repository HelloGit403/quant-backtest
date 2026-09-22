"""生成可复现的合成日线样例数据（类似 A 股风格随机游走+漂移）。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample" / "sample_stock.csv"


def gen_sample(
    start: str = "2018-01-01",
    end: str = "2024-12-31",
    seed: int = 99,
    s0: float = 10.0,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start, end)
    n = len(dates)

    # 趋势 + 噪声：AR(1) 对数动量，便于演示双均线/动量类策略
    phi = 0.85
    innov = 0.004
    drift = 0.0003

    trend = np.zeros(n)
    for i in range(1, n):
        trend[i] = phi * trend[i - 1] + rng.normal(0.0, innov)

    noise = np.clip(rng.normal(0.0, 0.008, n), -0.03, 0.03)
    log_ret = drift + trend + noise
    close = s0 * np.exp(np.cumsum(log_ret))

    open_ = np.empty(n)
    open_[0] = s0
    open_[1:] = close[:-1] * (1 + rng.normal(0, 0.004, n - 1))
    intraday = np.abs(rng.normal(0, 0.01, n)) + 0.005
    high = np.maximum(open_, close) * (1 + intraday * 0.5)
    low = np.minimum(open_, close) * (1 - intraday * 0.5)
    volume = rng.lognormal(mean=15.5, sigma=0.4, size=n).astype(int)

    df = pd.DataFrame(
        {
            "open": open_.round(4),
            "high": high.round(4),
            "low": low.round(4),
            "close": close.round(4),
            "volume": volume,
        },
        index=dates,
    )
    df.index.name = "date"
    return df


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = gen_sample()
    df.to_csv(OUT, encoding="utf-8")
    print(f"wrote {OUT} rows={len(df)}")


if __name__ == "__main__":
    main()
