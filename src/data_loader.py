"""行情数据加载：AkShare 优先，失败则回落到内置样例 CSV。"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"


def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """统一列名为小写 open/high/low/close/volume，index 为日期。"""
    df = df.copy()
    rename = {
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    df = df.rename(columns=rename)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    df.index = pd.to_datetime(df.index)
    needed = ["open", "high", "low", "close", "volume"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"缺少字段: {missing}")
    out = df[needed].sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out.dropna()


def load_akshare(symbol: str, start: str = "20180101", end: str | None = None) -> pd.DataFrame:
    """
    拉取 A 股前复权日线。
    优先自实现东财客户端（直连、更稳）；失败再回落 akshare。
    """
    try:
        from .em_client import fetch_em_daily

        return fetch_em_daily(symbol=symbol, start=start, end=end)
    except Exception as primary_exc:  # noqa: BLE001
        print(f"[data] em_client 失败，尝试 akshare: {primary_exc}")

    import akshare as ak

    proxy_keys = (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    )
    saved = {k: os.environ.pop(k) for k in proxy_keys if k in os.environ}
    old_environ_no_proxy = os.environ.get("NO_PROXY")
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"
    try:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start,
            end_date=end or pd.Timestamp.today().strftime("%Y%m%d"),
            adjust="qfq",
        )
    finally:
        for k, v in saved.items():
            os.environ[k] = v
        if old_environ_no_proxy is None:
            os.environ.pop("NO_PROXY", None)
            os.environ.pop("no_proxy", None)
        else:
            os.environ["NO_PROXY"] = old_environ_no_proxy
            os.environ["no_proxy"] = old_environ_no_proxy
    return _normalize_ohlcv(df)


def load_sample(name: str = "sample_stock.csv") -> pd.DataFrame:
    path = SAMPLE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"样例数据不存在: {path}")
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return _normalize_ohlcv(df)


def load_ohlcv(
    symbol: str = "000001",
    source: str = "auto",
    start: str = "20180101",
) -> pd.DataFrame:
    """
    source:
      - auto: 先试 akshare，失败用样例
      - akshare: 仅真实行情
      - sample: 仅样例
    """
    source = source.lower()
    if source == "sample":
        return load_sample()
    if source == "akshare":
        return load_akshare(symbol, start=start)
    if source == "auto":
        try:
            return load_akshare(symbol, start=start)
        except Exception as exc:  # noqa: BLE001 — 展示用项目，宽捕获后回落
            print(f"[data] akshare 不可用，改用样例数据 ({exc})")
            return load_sample()
    raise ValueError(f"未知 source: {source}")
