# Quant Backtest Portfolio

[![Backtest](https://github.com/HelloGit403/quant-backtest/actions/workflows/backtest.yml/badge.svg)](https://github.com/HelloGit403/quant-backtest/actions/workflows/backtest.yml)

面向兼职量化作品集的**数据 → 回测 → 报告**流水线。  
用 Python 完成 A 股风格日线策略回测，输出绩效指标与图表，适合放到 GitHub 展示。

> **定位**：这不是「稳赚策略」，而是可复现的研究模板。回测漂亮 ≠ 实盘赚钱。

## 功能

- 数据层：东财直连客户端（`em_client`，无需 token）→ AkShare 回落 → 内置样例 CSV
- 回测层：向量化回测，支持手续费与滑点；`position.shift(1)` 避免未来函数
- 策略层：双均线、动量可插拔
- 报告层：总收益、年化、最大回撤、夏普、卡玛、胜率 + 净值/持仓图
- **多标的 IS/OOS**：`scripts/compare_symbols.py` 前 70% 调参视角 / 后 30% 只检验
- CI：GitHub Actions 在 push/PR/每周一自动跑样例回测并上传报告
- 接单说明：[FREELANCE.md](FREELANCE.md) · 研究笔记：[notes/is_oos_study.md](notes/is_oos_study.md)

## 快速开始

```bash
# 建议 conda；真实行情仅需 pandas/numpy/matplotlib（akshare 可选）
pip install -r requirements.txt

# 默认：样例数据 + 双均线（可复现）
python scripts/run_backtest.py

# 真实 A 股（东财直连，如平安银行）
python scripts/run_backtest.py --source akshare --symbol 000001 --start 20200101

# 动量策略
python scripts/run_backtest.py --strategy momentum --source sample

# 多标的 + 样本内/外对比
python scripts/compare_symbols.py --source akshare --symbols "510300,159915,000001" --split 0.7
```

输出：

- `reports/metrics.json`
- `reports/equity_curve.png`
- `reports/price_signal.png`
- `reports/compare_table.csv` / `compare_equity.png` / `is_oos_scatter.png`

## 真实数据示例（000001 平安银行，2020-01 → 2026-09）

| 指标 | 双均线 | 买入持有 |
|------|--------|----------|
| 总收益 | -47.2% | -16.6% |
| 最大回撤 | -64.1% | — |
| 夏普 | -0.33 | — |
| 交易次数 | 61 | 1 |

> 单一标的 + 单一参数的双均线在该区间**跑输买入持有**——这是常见结果，作品集里如实展示比回报率更重要。样例合成数据上的正收益仅用于验证流水线。

## 项目结构

```
.
├── .github/workflows/backtest.yml  # CI 自动回测
├── data/sample/                    # 可复现样例 OHLCV
├── reports/                        # 回测产物
├── scripts/
│   ├── generate_sample_data.py
│   └── run_backtest.py
└── src/
    ├── em_client.py                # 东财日线直连（绕过代理/UA）
    ├── data_loader.py              # em / akshare / sample
    ├── backtest.py
    ├── metrics.py
    └── strategies/
```
        ├── base.py
        ├── ma_cross.py
        └── momentum.py
```

## 学习路径（AI 协助版）

| 阶段 | 你做什么 | AI 做什么 |
|------|----------|-----------|
| 1. 数据 | 确认字段含义、复权方式 | 拉数、清洗、对齐代码 |
| 2. 策略 | 定义交易逻辑与风控约束 | 生成信号函数骨架 |
| 3. 回测 | 检查是否未来函数、手续费假设 | 写向量化实现 |
| 4. 报告 | 解读回撤与夏普，判断是否过拟合 | 出图、写摘要 |
| 5. 实盘 | 仓位、止损、心态 | 不参与 |

**必须人工把关**：过拟合、样本外验证、实盘滑点、合规与资金安全。

## 免责声明

本仓库仅用于学习与作品展示，不构成投资建议。市场有风险，入市需谨慎。

## License

MIT
