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

## 一、数据源速查表

### 1.1 宏观经济

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **World Bank Open Data** | `https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json` | JSON/CSV/XML | 年度更新 | CC BY 4.0 |
| **IMF Data** | `https://www.imf.org/en/Data` → 下载 `IFS` / `WEO` | CSV/Excel | 季度/年度 | 免费+引用 |
| **中国国家统计局** | `https://data.stats.gov.cn/easyquery.htm?cn=E0103` | JSON/CSV | 月度/年度 | 免费+署名 |
| **FRED (美联储)** | `https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key={key}&file_type=json` | JSON/CSV | 日/月/季 | 免费+引用 |
| **Our World in Data** | `https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/` + 文件名 | CSV (直链) | 不定期 | CC BY 4.0 |
| **中国统计年鉴** | `https://www.stats.gov.cn/sj/ndsj/` | HTML/PDF | 年度 | 免费+署名 |

常用 World Bank Indicator 代码速查：
- `NY.GDP.MKTP.CD` — GDP (现价美元)
- `NY.GDP.PCAP.PP.KD` — 人均 GDP (购买力平价)
- `SP.POP.TOTL` — 人口总数
- `EN.ATM.CO2E.KT` — CO2 排放量 (千吨)
- `SL.UEM.TOTL.ZS` — 失业率 (%)
- `FP.CPI.TOTL.ZG` — 通胀率 (CPI 年增长率)

### 1.2 环境与气候

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **NOAA NCEI** | `https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations={station}&startDate={date}&endDate={date}&format=csv` | CSV | 每日 | 免费 (Public Domain) |
| **NASA POWER** | `https://power.larc.nasa.gov/api/temporal/{daily/ monthly}/point?parameters={params}&community=RE&longitude={lon}&latitude={lat}&start={date}&end={date}&format=CSV` | CSV/JSON | 每日 | 免费+引用 |
| **中国气象局** | `http://data.cma.cn/` (需注册) | CSV/NetCDF | 每日 | 注册免费 |
| **Copernicus Climate** | `https://cds.climate.copernicus.eu/api/v2` → ERA5 reanalysis | NetCDF/GRIB | 月度滞后 | 免费注册 (CC BY) |
| **AQICN (空气质量)** | `https://api.waqi.info/feed/{city}/?token={token}` | JSON | 实时/每日 | 免费额度 |
| **全球碳计划 (GCP)** | `https://www.globalcarbonproject.org/carbonbudget/` | Excel/CSV | 年度 | CC BY 4.0 |

NASA POWER 常用参数：`T2M`(温度), `PRECTOTCORR`(降水), `WS2M`(风速), `ALLSKY_SFC_SW_DWN`(太阳辐射), `RH2M`(相对湿度)

### 1.3 交通与地理

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **OpenStreetMap** | Overpass API `https://overpass-api.de/api/interpreter?data={query}` 或 `osmnx` Python 库 | GeoJSON/XML | 实时 | ODbL |
| **中国交通运输部** | `https://www.mot.gov.cn/shuju/` | HTML/PDF | 月度 | 免费+署名 |
| **GTFS (公交时刻表)** | `https://transitfeeds.com/` 聚合全球 GTFS | ZIP/CSV | 不定期 | 各运营商自定 |
| **FlightRadar24** | 需商业 API | JSON | 实时 | 商业 |
| **MarineTraffic** | 需 API key | JSON/CSV | 实时 | 商业 |
| **百度/高德地图 API** | `https://restapi.amap.com/v3/direction/transit/integrated?key={key}&origin={ori}&destination={dest}` | JSON | 实时 | 免费额度 |

OSMnx 一键获取路网：`osmnx.graph_from_place("Beijing, China", network_type="drive")`

### 1.4 人口与社会

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **UN Population Division** | `https://population.un.org/dataportal/api/v1/data/indicators/{id}/locations/{code}/start/{year}/end/{year}` | JSON | 2年一次 | CC BY 3.0 |
| **中国人口普查** | `https://www.stats.gov.cn/sj/pcsj/` | Excel/PDF | 10年一次 | 免费+署名 |
| **IPUMS International** | `https://international.ipums.org/` (需注册) | CSV/TXT | 不定期 | 注册使用 |
| **UN HDI** | `https://hdr.undp.org/data-center` | CSV | 年度 | CC BY 3.0 |
| **World Inequality Database** | `https://wid.world/data/` | CSV | 年度 | 免费+引用 |

### 1.5 能源

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **IEA Data** | `https://www.iea.org/data-and-statistics` (部分免费) | CSV/Excel | 年度 | 免费部分 CC BY 4.0 |
| **BP Statistical Review** | `https://www.energyinst.org/statistical-review` (Energy Institute 接管) | Excel/CSV | 年度 | 免费+引用 |
| **EIA (美国能源署)** | `https://api.eia.gov/v2/?api_key={key}` | JSON | 月/年 | 免费+注册 |
| **中国国家能源局** | `http://www.nea.gov.cn/sjzz/` | HTML/PDF | 月度 | 免费+署名 |
| **IRENA** | `https://www.irena.org/Data` | Excel | 年度 | 免费+引用 |
| **EMBER Climate** | `https://ember-climate.org/data/` | CSV | 月度 | CC BY 4.0 |

### 1.6 医疗与健康

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **WHO GHO** | `https://ghoapi.azureedge.net/api/{indicator_code}` | JSON | 年度 | CC BY-NC-SA 3.0 |
| **WHO GHO CSV 入口** | `https://apps.who.int/gho/data/node.main.{id}?lang=en` 底部有 CSV 下载 | CSV | 年度 | CC BY-NC-SA 3.0 |
| **CDC (美国疾控)** | `https://data.cdc.gov/` 多种数据集 → API/SODA 接口 | JSON/CSV | 不定期 | Public Domain |
| **中国卫生健康委** | `http://www.nhc.gov.cn/wjw/tjxx/tjxx.shtml` | HTML/PDF | 年度 | 免费+署名 |
| **IHME (健康指标)** | `https://ghdx.healthdata.org/` | CSV | 不定期 | 需引用 |
| **DXY (丁香园)** | 需爬虫，时效性强 | HTML | 实时 | 仅短期分析 |

常用 WHO Indicator 代码示例：`WHOSIS_000001`(预期寿命), `MDG_0000000001`(5岁以下死亡率), `NCD_BMI_18A`(肥胖率), `HWF_0001`(每千人医生数)

### 1.7 教育

| 数据源 | 入口/API模板 | 格式 | 更新频率 | 许可 |
|--------|-------------|------|---------|------|
| **UNESCO UIS** | `http://data.uis.unesco.org/` → API / CSV bulk download | CSV/JSON | 年度 | CC BY-SA 3.0 |
| **中国教育部** | `http://www.moe.gov.cn/jyb_sjzl/` | HTML/PDF | 年度 | 免费+署名 |
| **OECD Education** | `https://data.oecd.org/education.htm` | JSON/CSV | 年度 | 免费+引用 |
| **World Bank EdStats** | `https://api.worldbank.org/v2/country/all/indicator/SE.PRM.ENRR` | JSON/CSV | 年度 | CC BY 4.0 |

### 1.8 常用指标速查 (World Bank API 代码速查表)

| 领域 | 指标代码 | 中文名称 | 单位 |
|------|---------|---------|------|
| 经济 | `NY.GDP.MKTP.CD` | GDP (现价美元) | 美元 |
| 经济 | `NY.GDP.PCAP.PP.KD` | 人均 GDP (购买力平价) | 国际元 |
| 环境 | `EN.ATM.CO2E.KT` | CO2 排放量 | 千吨 |
| 环境 | `EG.USE.PCAP.KG.OE` | 人均能源使用 | 千克石油当量 |
| 人口 | `SP.POP.TOTL` | 人口总数 | 人 |
| 人口 | `SP.URB.TOTL.IN.ZS` | 城镇化率 | % |
| 健康 | `SH.XPD.CHEX.GD.ZS` | 卫生支出占 GDP | % |
| 健康 | `SP.DYN.LE00.IN` | 预期寿命 | 岁 |
| 教育 | `SE.PRM.ENRR` | 小学毛入学率 | % |
| 交通 | `IS.RRS.PASG.KM` | 铁路客运量 | 百万乘客-公里 |

---

## 二、Python 数据获取代码片段

### 2.1 pandas 直接读取 URL CSV

```python
import pandas as pd

# 直链 CSV 下载（无需 API key 的首选方案）
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
df = pd.read_csv(url)
print(f"Shape: {df.shape}, Columns: {list(df.columns)}")
df.to_csv("data/owid_covid.csv", index=False)
```

### 2.2 requests + API key 模式

```python
import requests
import pandas as pd

# 模板：含 API key 的 JSON API 请求
def fetch_worldbank(indicator: str, country: str = "all", date_range: str = "2010:2023"):
    """
    从 World Bank API 获取数据，无需 API key。
    indicator: 如 'NY.GDP.MKTP.CD'
    country: ISO3 代码或 'all'
    """
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {"format": "json", "date": date_range, "per_page": 20000}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()  # World Bank 返回 [{meta}, [{data}]]
    records = data[1] if len(data) > 1 and data[1] else []
    return pd.DataFrame([{
        "country": r["country"]["value"],
        "year": r["date"],
        "value": r["value"]
    } for r in records if r["value"] is not None])

# 使用示例
gdp_df = fetch_worldbank("NY.GDP.MKTP.CD")
gdp_df.to_csv("data/gdp_worldbank.csv", index=False)
print(gdp_df.head())
```

### 2.3 NASA POWER API（无需 key，速率限制 30次/分钟）

```python
import requests
import pandas as pd

def fetch_nasa_power(lat: float, lon: float, start: str, end: str,
                     params: str = "T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN"):
    """
    获取 NASA POWER 气象数据。免费，无需 API key。
    lat/lon: 纬度/经度 (WGS84)
    start/end: YYYYMMDD
    params: 逗号分隔参数名
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    payload = {
        "parameters": params,
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }
    resp = requests.get(url, params=payload)
    resp.raise_for_status()
    data = resp.json()
    records = data["properties"]["parameter"]
    df = pd.DataFrame(records)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df

# 使用示例：北京 2023年全年温度降水
weather = fetch_nasa_power(39.9, 116.4, "20230101", "20231231")
print(weather.describe())
```

### 2.4 sklearn 内置数据集（离线可用）

```python
from sklearn import datasets
import pandas as pd

# --- 分类 ---
iris = datasets.load_iris()                    # 鸢尾花 150×4, 3类
wine = datasets.load_wine()                    # 葡萄酒 178×13, 3类
digits = datasets.load_digits()                # 手写数字 1797×64, 10类
breast_cancer = datasets.load_breast_cancer()  # 乳腺癌 569×30, 2类

# --- 回归 ---
diabetes = datasets.load_diabetes()  # 糖尿病 442×10, 连续目标
boston = datasets.fetch_california_housing()  # 替代波士顿房价，20640×8

# --- 聚类/降维 ---
from sklearn.datasets import make_blobs, make_classification, make_regression

X_cluster, y_cluster = make_blobs(n_samples=300, centers=4, n_features=2, random_state=42)
X_class, y_class = make_classification(n_samples=500, n_features=20, n_informative=5, random_state=42)
X_reg, y_reg = make_regression(n_samples=200, n_features=10, noise=0.1, random_state=42)

# 转为 DataFrame 便于检查
df_iris = pd.DataFrame(iris.data, columns=iris.feature_names)
df_iris["target"] = iris.target
```

### 2.5 yfinance — 金融数据一键获取

```python
# pip install yfinance
import yfinance as yf

# 单支股票历史数据
tsla = yf.download("TSLA", start="2020-01-01", end="2024-12-31")
print(tsla.head())

# 多股票批量下载
tickers = yf.download(["AAPL", "MSFT", "GOOGL"], start="2023-01-01", end="2024-12-31")
print(tickers["Close"].corr())  # 收盘价相关系数矩阵

# 指数/ETF
sp500 = yf.download("^GSPC", period="5y")       # 标普500
shanghai = yf.download("000001.SS", period="2y") # 上证指数
csi300 = yf.download("510300.SS", period="1y")   # 沪深300 ETF
```

### 2.6 BeautifulSoup 最小爬虫示例

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_wikipedia_table(url: str, table_index: int = 0) -> pd.DataFrame:
    """
    抓取 Wikipedia 页面中的第 table_index 个表格。
    仅用于数据采集，遵守 robots.txt 和 ToS。
    """
    resp = requests.get(url, headers={"User-Agent": "MathModelEdu/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table", class_="wikitable")
    if table_index >= len(tables):
        raise ValueError(f"Page has {len(tables)} tables, requested index {table_index}")
    df = pd.read_html(str(tables[table_index]))[0]
    return df

# 示例：Wikipedia GDP 排名表
# url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
# gdp_table = scrape_wikipedia_table(url, 0)
# gdp_table.to_csv("data/gdp_wikipedia.csv", index=False)
```

---

## 三、数据质量检查清单

Agent 获取数据后**必须运行**以下检查流程：

### 3.1 完整性检查 — 缺失值筛查

```python
def completeness_report(df: pd.DataFrame) -> dict:
    """返回每列缺失率及高风险列标记"""
    missing = df.isnull().mean().sort_values(ascending=False)
    high_risk = missing[missing > 0.20]
    report = {
        "总行数": len(df),
        "总列数": len(df.columns),
        "缺失率>20%的列": list(high_risk.index),
        "完全缺失的列": list(missing[missing == 1.0].index),
        "各列缺失率(%)": (missing * 100).round(2).to_dict(),
    }
    return report
```

判定标准：
- **缺失率 <5%** → 可直接删除缺失行或简单填补
- **缺失率 5%~20%** → 需使用插补方法 (见第四节)
- **缺失率 20%~50%** → 插补 + 标记插补来源列；在论文中说明
- **缺失率 >50%** → 考虑删除该列，或仅作为辅助变量

### 3.2 一致性检查

```python
def consistency_check(df: pd.DataFrame) -> list:
    """检查数据类型、日期格式、类别值一致性"""
    issues = []

    # 1. 日期列格式检查
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower() or "year" in c.lower()]
    for col in date_cols:
        try:
            pd.to_datetime(df[col])
        except Exception:
            issues.append(f"列 '{col}' 无法解析为日期格式")

    # 2. 类别列值异常检查
    for col in df.select_dtypes(include=["object"]).columns:
        n_unique = df[col].nunique()
        if n_unique < 50:  # 可能是类别列
            vals = df[col].dropna().unique()
            issues.append(f"类别列 '{col}': {n_unique} 个唯一值 → {list(vals[:10])}")

    # 3. 单位一致性（启发式：同一列中位数/均值比值偏离1）
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        nonzero = df[col][df[col] > 0]
        if len(nonzero) > 10:
            ratio = nonzero.median() / nonzero.mean()
            if ratio < 0.1 or ratio > 10:
                issues.append(f"列 '{col}' 中位数/均值比={ratio:.3f}，可能存在单位不一致")

    return issues
```

### 3.3 准确性检查 — 异常值检测 (IQR 方法)

```python
def outlier_report(df: pd.DataFrame, method: str = "iqr", k: float = 1.5) -> dict:
    """
    IQR 异常值检测：|x - Q1| > k*IQR 或 |x - Q3| > k*IQR
    返回每列异常值数量和比例。
    """
    report = {}
    num_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - k * IQR
        upper = Q3 + k * IQR
        outlier_mask = (df[col] < lower) | (df[col] > upper)
        n_out = outlier_mask.sum()
        if n_out > 0:
            report[col] = {
                "异常值数": int(n_out),
                "异常值比例%": round(n_out / len(df) * 100, 2),
                "下界": round(lower, 4),
                "上界": round(upper, 4),
                "min": round(df[col].min(), 4),
                "max": round(df[col].max(), 4),
            }
    return report
```

### 3.4 合理性范围检查

```python
def range_validity_check(df: pd.DataFrame) -> list:
    """基于常识的范围校验"""
    rules = {
        "gdp": (0, 5e13),          # GDP 应在 0~50万亿美元
        "population": (0, 1.5e9),  # 人口应在 0~15亿（国家级别）
        "temperature_c": (-90, 60), # 摄氏度
        "precipitation_mm": (0, 5000), # 年降水量 mm
        "co2_kt": (0, 2e7),        # CO2排放(kiloton) 0~20M
        "unemployment_rate": (0, 100), # 失业率 0-100%
        "life_expectancy": (30, 90), # 预期寿命 30-90岁
        "urbanization_rate": (0, 100), # 城镇化率 0-100%
        "latitude": (-90, 90),
        "longitude": (-180, 180),
    }
    issues = []
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        col_lower = col.lower()
        for key, (lo, hi) in rules.items():
            if key in col_lower:
                bad = df[(df[col] < lo) | (df[col] > hi)]
                if len(bad) > 0:
                    issues.append(f"列 '{col}' ({key}): {len(bad)} 行超出合理范围 [{lo}, {hi}]")
    return issues
```

### 3.5 时效性检查

```python
def timeliness_check(df, data_start_year: int, data_end_year: int, competition_year: int = 2026):
    """检查数据覆盖时间与赛题年份的差距"""
    gap = competition_year - data_end_year
    coverage = data_end_year - data_start_year + 1
    issues = []
    if gap > 5:
        issues.append(f"数据截至 {data_end_year}，距今 {gap} 年（>5年，时效性差）")
    if gap > 3:
        issues.append(f"数据截至 {data_end_year}，距今 {gap} 年（>3年，需注明时间局限）")
    if coverage < 3:
        issues.append(f"数据跨度仅 {coverage} 年（<3年，趋势分析可信度受限）")
    if not issues:
        issues.append(f"时效性良好：{data_start_year}-{data_end_year}，覆盖 {coverage} 年，距今 {gap} 年")
    return issues
```

---

## 四、缺失值和异常值处理

### 4.1 缺失机制识别

| 机制 | 含义 | 识别方法 | 处理策略 |
|------|------|---------|---------|
| **MCAR** (完全随机缺失) | 缺失与任何变量无关 | 缺失指示变量与其他变量无显著相关 (t检验/卡方 p>0.05) | 删除缺失行 / 均值填补 / 多重插补均可 |
| **MAR** (随机缺失) | 缺失与观测变量相关，与缺失值本身无关 | 缺失指示变量与某观测变量显著相关 | MICE / KNN / 回归插补 |
| **MNAR** (非随机缺失) | 缺失与缺失值本身有关 | 专业判断（如高收入者不愿报告收入） | 需建模缺失机制；在论文中讨论偏倚 |

### 4.2 插补方法决策树

```python
def impute_decision(col_missing_rate: float, col_type: str, missing_mechanism: str,
                    n_samples: int, n_features: int) -> str:
    """
    根据列特征返回推荐插补方法。
    col_missing_rate: 缺失率 (0~1)
    col_type: 'numeric' | 'categorical'
    missing_mechanism: 'MCAR' | 'MAR' | 'MNAR'
    """
    if col_missing_rate > 0.5:
        return "删除该列（缺失率>50%），或转为二值指示变量「是否观测到」"
    if col_missing_rate < 0.05:
        return "删除缺失行（缺失率<5%）"

    # 5% ~ 50% 缺失率
    if col_type == "categorical":
        return "众数填充；若MAR则考虑分类模型预测"
    if col_type == "numeric":
        if missing_mechanism == "MCAR" and col_missing_rate < 0.20:
            return "均值/中位数填充（MCAR + <20%），中位数对偏态更稳健"
        if n_samples > n_features * 5 and missing_mechanism == "MAR":
            return "MICE（多重插补）— 若样本量足够（n > 5p），首选"
        if n_samples > 100:
            return "KNN插补（k=5），捕捉局部样本相似性"
        return "中位数填充（保守策略）+ 标记插补来源列"
    return "均值/众数填充 + 标记插补来源列"
```

### 4.3 具体插补实现

```python
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer  # MICE

# --- 方法1: 简单统计量插补 ---
def simple_impute(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """
    strategy: 'mean' | 'median' | 'most_frequent' | 'constant'
    返回填补后的 DataFrame。
    """
    from sklearn.impute import SimpleImputer
    imp = SimpleImputer(strategy=strategy)
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df_imputed = df.copy()
    df_imputed[numeric_cols] = imp.fit_transform(df[numeric_cols])
    return df_imputed

# --- 方法2: KNN 插补 ---
def knn_impute(df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    """KNN 插补，仅对数值列。k 建议 3~7。"""
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    imp = KNNImputer(n_neighbors=k, weights="uniform")
    df_imputed = df.copy()
    df_imputed[numeric_cols] = imp.fit_transform(df[numeric_cols])
    return df_imputed

# --- 方法3: MICE (多重插补) ---
def mice_impute(df: pd.DataFrame, max_iter: int = 10, random_state: int = 42) -> pd.DataFrame:
    """
    MICE (IterativeImputer) — BayesianRidge 回归模型迭代填补。
    适用于 MAR 机制，样本量 > 5×特征数。
    """
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    imp = IterativeImputer(max_iter=max_iter, random_state=random_state)
    df_imputed = df.copy()
    df_imputed[numeric_cols] = imp.fit_transform(df[numeric_cols])
    return df_imputed

# --- 方法4: 时间序列插补 ---
def time_series_impute(series: pd.Series, method: str = "linear") -> pd.Series:
    """
    时间序列专用插补。
    method: 'linear' | 'quadratic' | 'spline' | 'ffill' | 'bfill'
    """
    if method in ["linear", "quadratic", "spline"]:
        return series.interpolate(method=method)
    elif method == "ffill":
        return series.fillna(method="ffill")
    elif method == "bfill":
        return series.fillna(method="bfill")
    # 默认：linear 插值 + 前向填充残余
    return series.interpolate(method="linear").fillna(method="ffill").fillna(method="bfill")
```

### 4.4 异常值处理策略

| 策略 | 方法 | 适用场景 | 风险 |
|------|------|---------|------|
| **Winsorize (缩尾)** | 将超出 [P1, P99] 或 [Q1-1.5IQR, Q3+1.5IQR] 的值截断到边界 | 少量异常值，希望保留样本量 | 损失极值信息 |
| **Log 变换** | `np.log(x)` 或 `np.log1p(x)` | 右偏分布 (GDP、收入等) | 仅对正值有效 |
| **Box-Cox 变换** | `scipy.stats.boxcox` | 需正态性的模型 | 参数需估计 |
| **删除** | 直接删除异常行 | 异常值占 <1%，且确认是录入错误 | 信息损失 |
| **标记保留** | 保留原值，添加二值列"is_outlier" | 异常值本身可能是重要信息 | 需模型能处理 |

```python
from scipy import stats

def winsorize_series(series: pd.Series, limits: tuple = (0.01, 0.01)) -> pd.Series:
    """缩尾处理：将 (lower_pctl, upper_pctl) 之外的值截断。limits=(0.01, 0.01) = 1% 双尾"""
    return stats.mstats.winsorize(series, limits=limits)

def transform_log(series: pd.Series) -> pd.Series:
    """Log 变换，自动处理零值 (log1p)"""
    return np.log1p(series)

def mark_outliers(df: pd.DataFrame, col: str, k: float = 1.5) -> pd.DataFrame:
    """标记异常值（添加 is_outlier 列），保留原始值"""
    Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    IQR = Q3 - Q1
    df = df.copy()
    df[f"{col}_is_outlier"] = ((df[col] < Q1 - k * IQR) | (df[col] > Q3 + k * IQR)).astype(int)
    return df
```

---

## 五、数据来源记录规范

### 5.1 强制模板 — `data/SOURCES.md`

每获取一个数据集，**必须**在 `data/SOURCES.md` 中按以下格式追加一条记录：

```markdown
### [数据集简短名称]

| 字段 | 内容 |
|------|------|
| **数据文件名** | `data/specific_filename.csv` |
| **来源 URL** | https://example.com/dataset/download |
| **下载/获取日期** | 2026-07-28 |
| **数据时间范围** | 2010-01-01 至 2023-12-31 |
| **行数 × 列数** | 5000 × 12 |
| **变量说明** | col1: GDP (美元), col2: 人口 (万人), col3: CO2排放 (千吨) |
| **预处理步骤** | 1) 删除缺失率>50%的3列; 2) 对col3 KNN(k=5)插补2.3%缺失值; 3) col1 经 log 变换; 4) 合并了 data/aux.csv 按 city 列 |
| **许可/授权** | CC BY 4.0 — 可自由使用，需署名 |
| **引用格式** | World Bank (2024). World Development Indicators. https://data.worldbank.org |
| **备注** | 原始 csv 含合并单元格，已用 pandas.melt 转为长格式 |
```

### 5.2 自动化记录脚本

```python
import json
from datetime import datetime

def log_data_source(filename: str, source_url: str, variables: dict,
                    license_info: str, citation: str, preprocess_steps: list = [],
                    time_range: str = "N/A", notes: str = ""):
    """
    将数据源信息追加到 data/SOURCES.md。
    variables: {'col_name': '中文说明+单位'}
    """
    entry = f"""\n### {filename.split('/')[-1].split('.')[0]}

| 字段 | 内容 |
|------|------|
| **数据文件名** | `{filename}` |
| **来源 URL** | {source_url} |
| **下载/获取日期** | {datetime.now().strftime('%Y-%m-%d')} |
| **数据时间范围** | {time_range} |
| **变量说明** | {', '.join(f'{k}: {v}' for k, v in variables.items())} |
| **预处理步骤** | {'; '.join(preprocess_steps) if preprocess_steps else '无'} |
| **许可/授权** | {license_info} |
| **引用格式** | {citation} |
| **备注** | {notes} |

---
"""
    with open("data/SOURCES.md", "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"已记录数据源: {filename}")

# 使用示例
log_data_source(
    filename="data/gdp_worldbank.csv",
    source_url="https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json",
    variables={"country": "国家名称", "year": "年份", "value": "GDP (现价美元)"},
    license_info="CC BY 4.0",
    citation="World Bank (2024). World Development Indicators. https://data.worldbank.org",
    time_range="2010–2023",
    preprocess_steps=["删除缺失值行(缺失率<1%)", "按年份排序"],
    notes="World Bank API 返回 JSON，已转为 CSV"
)
```

---

## 六、数据质量控制（自动）

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

## 七、数据缺失的应对策略（优先级降序）

| 优先级 | 策略 | 适用条件 | 论文标注 |
|---|---|---|---|
| 1 | 找替代数据源 | 有相近指标的不同来源 | 标注替代来源 |
| 2 | 用代理变量 | 有相关但非直接的指标 | 标注"代理"并解释合理性 |
| 3 | 合理插值/外推 | 数据有趋势可循 | 标注插值方法和不确定性 |
| 4 | 场景假设 | 完全无数据但可合理推测范围 | 标注"假设"并做灵敏度 |
| 5 | 显著标注的模拟数据 | 以上都不可行 | **必须**标注"模拟"并说明生成方式 |

---

## 铁律
- 绝不编造数据
- 找不到真实数据 → 按上表逐级降级
- 模拟数据必须**显著标注**并说明生成方式
- 每条数据可追溯到原始来源
- **获取数据后立即运行质量检查清单（第三章），问题数据不进入建模**
- **所有预处理操作在 SOURCES.md 中完整记录，确保可复现**
