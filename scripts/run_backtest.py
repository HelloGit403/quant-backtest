"""数据 → 回测 → 报告 一键入口。

用法:
  python scripts/run_backtest.py
  python scripts/run_backtest.py --strategy momentum --symbol 000001 --source sample
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backtest import buy_and_hold, run_backtest
from src.data_loader import load_ohlcv
from src.metrics import summarize
from src.strategies import get_strategy


def plot_report(equity, bh_equity, df, pos, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(equity.index, equity.values, label="Strategy", lw=1.5)
    ax.plot(bh_equity.index, bh_equity.values, label="Buy & Hold", lw=1.2, alpha=0.8)
    ax.set_title("Equity Curve")
    ax.set_ylabel("Normalized Equity")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "equity_curve.png", dpi=140)
    plt.close(fig)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    ax1.plot(df.index, df["close"], color="#1f4e79", lw=1.2, label="Close")
    hold = pos > 0.5
    if bool(hold.any()):
        ax1.fill_between(
            df.index,
            float(df["close"].min()),
            float(df["close"].max()),
            where=hold.reindex(df.index).fillna(False),
            color="#2e7d32",
            alpha=0.12,
            label="In position",
            interpolate=True,
        )
    ax1.set_title("Price & Position")
    ax1.set_ylabel("Price")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    ax2.step(df.index, pos, where="post", color="#c62828", lw=1.0)
    ax2.set_ylim(-0.1, 1.1)
    ax2.set_ylabel("Pos")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "price_signal.png", dpi=140)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run vectorized backtest")
    parser.add_argument("--strategy", default="ma_cross", choices=["ma_cross", "momentum"])
    parser.add_argument("--symbol", default="000001")
    parser.add_argument("--source", default="sample", choices=["auto", "akshare", "sample"])
    parser.add_argument("--start", default="20180101")
    parser.add_argument("--fee", type=float, default=0.0003)
    parser.add_argument("--slippage", type=float, default=0.001)
    parser.add_argument("--fast", type=int, default=10)
    parser.add_argument("--slow", type=int, default=30)
    parser.add_argument("--lookback", type=int, default=20)
    args = parser.parse_args()

    print(f"[1/4] 加载数据 source={args.source} symbol={args.symbol}")
    df = load_ohlcv(symbol=args.symbol, source=args.source, start=args.start)
    print(f"      bars={len(df)} range={df.index[0].date()} -> {df.index[-1].date()}")

    print(f"[2/4] 生成信号 strategy={args.strategy}")
    if args.strategy == "ma_cross":
        strategy = get_strategy("ma_cross", fast=args.fast, slow=args.slow)
    else:
        strategy = get_strategy("momentum", lookback=args.lookback)
    pos = strategy.generate(df)

    print(f"[3/4] 回测 fee={args.fee} slippage={args.slippage}")
    result = run_backtest(df, pos, fee_rate=args.fee, slippage=args.slippage)
    bh = buy_and_hold(df)

    metrics = summarize(result.equity, result.returns)
    bh_metrics = summarize(bh.equity, bh.returns)
    metrics["n_trades"] = result.trades
    metrics["strategy"] = args.strategy
    metrics["symbol"] = args.symbol
    metrics["buy_and_hold"] = bh_metrics

    print("[4/4] 写出报告")
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    with open(reports / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    plot_report(result.equity, bh.equity, df, result.position, reports)

    print("\n=== 指标 ===")
    for k in [
        "strategy",
        "total_return",
        "annualized_return",
        "max_drawdown",
        "sharpe",
        "calmar",
        "win_rate",
        "n_trades",
        "start",
        "end",
    ]:
        print(f"  {k:22s}: {metrics[k]}")
    print(f"  buy_and_hold_return   : {bh_metrics['total_return']}")
    print(f"\n报告目录: {reports}")


if __name__ == "__main__":
    main()
