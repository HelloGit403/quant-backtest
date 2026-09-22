# 发布到 GitHub（HelloGit403）

本地仓库已初始化，分支 `main`。  
项目路径：`C:\Users\USTC\Desktop\量化`

## 仓库信息建议

- **Name**: `quant-backtest`
- **Description**: `A股风格量化回测模板：数据 → 双均线/动量策略 → 绩效报告（Python）`
- **Topics**: `quantitative-finance`, `backtest`, `python`, `pandas`, `akshare`
- **Visibility**: Public（作品集需要）

## 方式 A：浏览器建仓 + 命令行推送（推荐）

1. 打开 https://github.com/new
2. 登录账号 `HelloGit403`
3. Repository name 填 `quant-backtest`，选 **Public**，**不要**勾选 Add a README / .gitignore
4. 创建后在 PowerShell 执行：

```powershell
cd "C:\Users\USTC\Desktop\量化"
git remote add origin https://github.com/HelloGit403/quant-backtest.git
git push -u origin main
```

首次 push 会弹出 GitHub 登录，按提示完成即可。

## 方式 B：安装 gh CLI 一键建仓推送

```powershell
winget install --id GitHub.cli -e
# 重开终端后：
gh auth login
cd "C:\Users\USTC\Desktop\量化"
gh repo create quant-backtest --public --source=. --push
```

## 推送后检查

1. 打开 `https://github.com/HelloGit403/quant-backtest`
2. README 正常渲染，`reports/equity_curve.png` 可预览
3. About 补上 topics

## 本地重跑回测

```powershell
& "D:\anconda\python.exe" scripts\run_backtest.py
& "D:\anconda\python.exe" scripts\run_backtest.py --strategy momentum
```

## 注意

- 不要提交密钥、Token、`.env`
- 当前 git 身份：`HelloGit403 <HelloGit403@users.noreply.github.com>`（noreply，可改）
- 样例数据为合成序列，回测结果仅供学习展示
