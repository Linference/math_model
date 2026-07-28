# 03 — 数据获取策略（增强版）

目标：为模型找真实、可引用的数据，落盘 `data/`，来源记入 `data/SOURCES.md`。

---

## 三级搜索策略

### 第一级：自动化管线（优先）

```bash
# sklearn 内置数据集（9个可用，离线最稳）
python <skill>/scripts/fetch_data.py --sklearn iris

# World Bank 宏观指标（自动 API 调用）
python <skill>/scripts/fetch_data.py --worldbank EN.ATM.CO2E.KT

# NOAA 气象数据（需 token，免费申请）
python <skill>/scripts/fetch_data.py --noaa-station GHCND:USW00012918

# UCI 机器学习仓库
python <skill>/scripts/fetch_data.py --uci 53

# 任意 CSV/JSON URL 直链下载
python <skill>/scripts/fetch_data.py --url https://.../data.csv --name mydata
```

### 第二级：智能搜索（关键词 → 数据源建议）

```bash
python <skill>/scripts/fetch_data.py --search climate energy population
```

输出推荐数据源列表（API/开放数据/学术仓库）。

### 第三级：AI 辅助搜索（WebSearch + WebFetch）

1. 列出每个模型需要的数据/参数清单
2. WebSearch 找候选源 → WebFetch 确认字段/单位/时间/许可
3. 拿直链 → `fetch_data.py --url <URL>` 落盘
4. 记 `data/SOURCES.md`：名称、URL、日期、字段、许可 → 供论文引用

---

## 数据质量控制

### 自动质量报告
```bash
python <skill>/scripts/fetch_data.py --quality data/city_indicators.csv
```
输出：缺失率报告、异常值检测（IQR × 3）、强相关指标预警、量纲一致性提示。

### 数据合并
```bash
# 按关键列合并多个数据源（如多个来源的环境数据按城市名合并）
python <skill>/scripts/fetch_data.py --merge data/a.csv data/b.csv --on city --how outer
```

### 数据增强（小样本场景）
```bash
# Bootstrap 重采样（统计推断用）
python <skill>/scripts/fetch_data.py --augment data/small.csv --method bootstrap --n 500

# 加噪增强（回归数据用）
python <skill>/scripts/fetch_data.py --augment data/small.csv --method noise
```

---

## 数据缺失的应对策略（优先级降序）

| 优先级 | 策略 | 适用条件 | 论文标注 |
|---|---|---|---|
| 1 | 找替代数据源 | 有相近指标的不同来源 | 标注替代来源 |
| 2 | 用代理变量 | 有相关但非直接的指标 | 标注"代理"并解释合理性 |
| 3 | 合理插值/外推 | 数据有趋势可循 | 标注插值方法和不确定性 |
| 4 | 场景假设 | 完全无数据但可合理推测范围 | 标注"假设"并做灵敏度 |
| 5 | 显著标注的模拟数据 | 以上都不可行 | **必须**标注"模拟"并说明生成方式 |

---

## 数据来源记录规范

`data/SOURCES.md` 每条记录格式：
```markdown
- **数据集名称** — 来源 URL
  取得时间: YYYY-MM-DD
  字段: col1, col2, ... (共 N 个)
  许可: CC BY 4.0 / Public Domain / 需引用
  备注: 数据质量说明（缺失值、异常值处理方式）
```

## 铁律
- 绝不编造数据
- 找不到真实数据 → 按上表逐级降级
- 模拟数据必须**显著标注**并说明生成方式
- 每条数据可追溯到原始来源
