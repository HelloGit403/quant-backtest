"""多标的对比 + 样本内/样本外拆分。

用法:
  # 真实多标的（东财）
  python scripts/compare_symbols.py --source akshare --symbols 510300,159915,000001

  # 样例数据（CI 可复现）
  python scripts/compare_symbols.py --source sample
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.backtest import buy_and_hold, run_backtest
from src.data_loader import load_ohlcv, load_sample
from src.metrics import summarize
from src.strategies import get_strategy

DEFAULT_SYMBOLS = "510300,159915,000001"


def eval_one(df: pd.DataFrame, strategy_name: str, split: float | None) -> dict:
    if split is not None and 0 < split < 1:
        cut = df.index[int(len(df) * split)]
        in_df = df.loc[:cut]
        out_df = df.loc[cut:]
    else:
        in_df, out_df = df, None

    def _run(part: pd.DataFrame) -> dict:
        if len(part) < 50:
            return {}
        if strategy_name == "ma_cross":
            st = get_strategy("ma_cross", fast=10, slow=30)
        else:
            st = get_strategy("momentum", lookback=20)
        pos = st.generate(part)
        res = run_backtest(part, pos, fee_rate=0.0003, slippage=0.001)
        m = summarize(res.equity, res.returns)
        bh = buy_and_hold(part)
        m["buy_and_hold_total"] = round(float(bh.equity.iloc[-1] / bh.equity.iloc[0] - 1), 4)
        m["n_trades"] = res.trades
        return m

    row = {"in_sample": _run(in_df)}
    if out_df is not None:
        row["out_sample"] = _run(out_df)
    return row


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="sample", choices=["sample", "akshare", "auto"])
    p.add_argument("--symbols", default=DEFAULT_SYMBOLS)
    p.add_argument("--strategy", default="ma_cross", choices=["ma_cross", "momentum"])
    p.add_argument("--start", default="20180101")
    p.add_argument("--split", type=float, default=0.7, help="样本内比例，0 表示不拆分")
    args = p.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)

    results: dict[str, dict] = {}
    equities: dict[str, pd.Series] = {}

    for sym in symbols:
        print(f"--- {sym} ---")
        try:
            if args.source == "sample":
                df = load_sample()
                # 样例只有一条路径：用不同 seed 视角意义不大，仍对同一序列做 IS/OS
            else:
                df = load_ohlcv(symbol=sym, source=args.source, start=args.start)
        except Exception as exc:  # noqa: BLE001
            print(f"  skip: {exc}")
            results[sym] = {"error": str(exc)}
            continue

        results[sym] = eval_one(df, args.strategy, args.split if args.split > 0 else None)

        # 全样本净值（作图）
        st = (
            get_strategy("ma_cross", fast=10, slow=30)
            if args.strategy == "ma_cross"
            else get_strategy("momentum", lookback=20)
        )
        res = run_backtest(df, st.generate(df))
        equities[sym] = res.equity
        in_m = results[sym].get("in_sample", {})
        out_m = results[sym].get("out_sample", {})
        print(f"  IS  total={in_m.get('total_return')} sharpe={in_m.get('sharpe')}")
        if out_m:
            print(f"  OOS total={out_m.get('total_return')} sharpe={out_m.get('sharpe')}")

    out_json = reports / "compare_metrics.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {"strategy": args.strategy, "source": args.source, "split": args.split, "results": results},
            f,
            ensure_ascii=False,
            indent=2,
        )

    # 汇总表
    rows = []
    for sym, r in results.items():
        if "error" in r:
            rows.append({"symbol": sym, "error": r["error"]})
            continue
        for period in ("in_sample", "out_sample"):
            m = r.get(period)
            if not m:
                continue
            rows.append(
                {
                    "symbol": sym,
                    "period": period,
                    "total_return": m.get("total_return"),
                    "sharpe": m.get("sharpe"),
                    "max_drawdown": m.get("max_drawdown"),
                    "n_trades": m.get("n_trades"),
                    "buy_and_hold_total": m.get("buy_and_hold_total"),
                }
            )
    table = pd.DataFrame(rows)
    table_path = reports / "compare_table.csv"
    table.to_csv(table_path, index=False, encoding="utf-8-sig")
    print("\n=== compare_table ===")
    print(table.to_string(index=False))

    # 净值对比图
    if equities:
        fig, ax = plt.subplots(figsize=(10, 5))
        for name, eq in equities.items():
            ax.plot(eq.index, eq.values, lw=1.4, label=name)
        ax.set_title(f"Multi-symbol equity ({args.strategy})")
        ax.set_ylabel("Normalized equity")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(reports / "compare_equity.png", dpi=140)
        plt.close(fig)

    # 样本内 vs 样本外散点（若拆分）
    pairs = []
    for sym, r in results.items():
        if r.get("in_sample") and r.get("out_sample"):
            pairs.append(
                (
                    r["in_sample"].get("total_return", 0),
                    r["out_sample"].get("total_return", 0),
                    sym,
                )
            )
    if pairs:
        fig, ax = plt.subplots(figsize=(6, 6))
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        ax.scatter(xs, ys, s=60)
        for x, y, lab in pairs:
            ax.annotate(lab, (x, y), textcoords="offset points", xytext=(6, 4), fontsize=9)
        lim = [min(xs + ys + [-0.1]), max(xs + ys + [0.1])]
        ax.plot(lim, lim, "k--", lw=0.8, alpha=0.5, label="y=x")
        ax.set_xlabel("In-sample total return")
        ax.set_ylabel("Out-of-sample total return")
        ax.set_title("IS vs OOS")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(reports / "is_oos_scatter.png", dpi=140)
        plt.close(fig)

    print(f"\nWrote {out_json}")
    print(f"Wrote {table_path}")


if __name__ == "__main__":
    main()
