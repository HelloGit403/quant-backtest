"""自实现东财日线拉取（绕过 akshare 内部代理/UA 问题）。"""

from __future__ import annotations

import json
import os
import ssl
import urllib.request
from urllib.parse import urlencode

import pandas as pd

EM_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Referer": "https://quote.eastmoney.com/",
}


def _no_proxy_opener() -> urllib.request.OpenerDirector:
    """强制直连，忽略系统/环境代理。"""
    proxy_handler = urllib.request.ProxyHandler({})
    ctx = ssl.create_default_context()
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    return urllib.request.build_opener(proxy_handler, https_handler)


def fetch_em_daily(
    symbol: str = "000001",
    start: str = "20180101",
    end: str | None = None,
    market: int | None = None,
) -> pd.DataFrame:
    """
    symbol: 6 位代码，如 000001 / 600519
    market: 0=深市 1=沪市；None 时按首位推断
    """
    symbol = str(symbol).strip().zfill(6)
    if market is None:
        market = 1 if symbol.startswith(("6", "9", "5")) else 0
    end = end or pd.Timestamp.today().strftime("%Y%m%d")

    params = {
        "secid": f"{market}.{symbol}",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",  # 日线
        "fqt": "1",    # 前复权
        "beg": str(start),
        "end": str(end),
        "lmt": "1000000",
    }
    url = f"{EM_URL}?{urlencode(params)}"
    opener = _no_proxy_opener()
    req = urllib.request.Request(url, headers=HEADERS)
    # 短时清空代理环境变量
    saved = {
        k: os.environ.pop(k)
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy")
        if k in os.environ
    }
    try:
        with opener.open(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
    finally:
        for k, v in saved.items():
            os.environ[k] = v

    payload = json.loads(raw)
    data = (payload or {}).get("data") or {}
    klines = data.get("klines") or []
    if not klines:
        raise RuntimeError(f"东财无数据: {payload}")

    rows = []
    for line in klines:
        # date,open,close,high,low,volume,amount,amp,pct,chg,turnover
        parts = line.split(",")
        if len(parts) < 6:
            continue
        rows.append(
            {
                "date": parts[0],
                "open": float(parts[1]),
                "close": float(parts[2]),
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": float(parts[5]),
            }
        )
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df
