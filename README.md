# Quant Backtest Portfolio

面向兼职量化作品集的**数据 → 回测 → 报告**流水线。
用 Python 完成 A 股风格日线策略回测，输出绩效指标与图表，适合放到 GitHub 展示。

> **定位**：这不是「稳赚策略」，而是可复现的研究模板。回测漂亮 ≠ 实盘赚钱。

## 功能

- 数据层：优先 AkShare 拉真实行情；无网络/无依赖时自动使用内置样例数据
- 回测层：向量化回测，支持手续费与滑点
- 策略层：双均线（SMA Cross）、动量（Momentum）可插拔
- 报告层：总收益、年化、最大回撤、夏普比率、胜率 + 净值曲线图

## 快速开始

```bash
# 建议使用 conda
conda activate base   # 或你的专属环境

# 可选：真实行情需要 akshare
pip install -r requirements.txt

# 一键回测（默认样例数据 + 双均线）
python scripts/run_backtest.py

# 指定策略与数据源
python scripts/run_backtest.py --strategy momentum --symbol 000001 --source sample
```

输出：

- `reports/metrics.json` — 绩效指标
- `reports/equity_curve.png` — 净值曲线
- `reports/price_signal.png` — 价格与信号

## 项目结构

```
.
├── README.md
├── requirements.txt
├── data/sample/           # 内置样例行情（可复现）
├── reports/               # 回测输出
├── scripts/run_backtest.py
└── src/
    ├── data_loader.py     # 数据获取（akshare / csv）
    ├── backtest.py        # 向量化回测引擎
    ├── metrics.py         # 绩效指标
    └── strategies/
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
