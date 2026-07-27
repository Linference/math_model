# 03 — 数据获取策略

目标：为模型找真实、可引用的数据，落盘 `data/`，来源记入 `data/SOURCES.md`。见 `data-sources.md` 的站点直链。

## 检索优先级（稳→险）
1. **离线内置**：sklearn/statsmodels 自带集 —— 最稳，`python <skill>/scripts/fetch_data.py --sklearn iris`。
2. **权威开放数据**：世界银行、WHO、UN、OWID、国家统计局公开 CSV、UCI、Kaggle。
3. **GitHub raw / 论文补充材料**：可复现数据集。
4. **百科背景**：Wikipedia(英文数据表全)、百度百科(仅背景)。
5. **文献参数**：Nature/Science/Scholar 摘要里的系数、参数（标引用）。

## 流程
1. 列每个模型需要的数据/参数清单。
2. WebSearch 找候选 → WebFetch 确认字段/单位/时间/许可。
3. 拿直链 → `fetch_data.py --url <URL> --name <名>` 落盘（utf-8-sig）。
4. 记 `data/SOURCES.md`：名称、URL、日期、字段、许可 → 供论文引用。
5. 体检：缺失率、量纲、异常值，写数据说明。

## 国内站点
百度百科/知网常需登录或被墙：优先 WebFetch；取不到换英文源/镜像并**如实说明**。绝不编造；找不到就标"题目附件提供/需自采"，或用**显著标注的模拟数据**。

## fetch_data.py 用法
```bash
python <skill>/scripts/fetch_data.py --sklearn wine
python <skill>/scripts/fetch_data.py --uci 53
python <skill>/scripts/fetch_data.py --url https://.../x.csv --name x
```
