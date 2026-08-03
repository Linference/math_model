# data-sources — 数学建模数据源完整参考手册

> **用途**：供 AI agent 快速查找可用数据源、判断适用场景、生成数据获取代码。
> **使用原则**：优先 WebSearch/WebFetch 取直链 CSV/JSON，再用 `fetch_data.py` 落盘到 `data/`，并在 `data/SOURCES.md` 登记来源。
> **铁律**：绝不编造数据；找不到真实数据时，标注"题目附件提供/需自采"或用显著标注的模拟数据并说明生成方式。

---

## 一、经济与金融

| # | 名称 | URL | 数据类型 | 更新频率 | 访问方式 | 典型建模用途 |
|---|------|-----|---------|---------|---------|------------|
| 1 | **World Bank Open Data** | https://data.worldbank.org | GDP、人口、贸易、教育、环境等 1400+ 指标，覆盖 217 经济体 | 年度为主，部分季度/月度 | 免费，无需注册；API: `https://api.worldbank.org/v2/country/{CODE}/indicator/{INDICATOR}?format=json`；Python: `pip install wbgapi` | 宏观经济分析、国家发展水平聚类、面板数据回归 |
| 2 | **IMF Data** | https://data.imf.org | 国际收支、政府财政、金融稳健指标、汇率、CPI | 月度/季度/年度 | 免费，API: `https://www.imf.org/external/datamapper/api/v1/`；Python: `pip install imfpy` | 汇率预测、金融危机预警、财政政策评估 |
| 3 | **中国国家统计局** | https://data.stats.gov.cn | 中国 GDP、CPI、PPI、人口、就业、工业增加值、房地产 | 月度/季度/年度 | 免费，部分需注册；有 JSON API (`https://data.stats.gov.cn/easyquery.htm`)；可下载统计年鉴 CSV | 中国经济建模、区域发展评价、时间序列预测 |
| 4 | **FRED (Federal Reserve)** | https://fred.stlouisfed.org | 美国利率、就业、通胀、GDP 分项、货币供应量等 80 万+ 时序 | 日/周/月/季度 | 免费，API key 注册即得；Python: `pip install fredapi` | 利率期限结构、通胀预测、宏观经济 VAR 模型 |
| 5 | **Yahoo Finance** | https://finance.yahoo.com | 全球股票、ETF、期货、外汇历史价格与基本面 | 实时/日级别 | 免费；Python: `pip install yfinance`；`yf.download("AAPL", start="2020-01-01")` | 投资组合优化、CAPM 实证、GARCH 波动率建模、时间序列预测 |
| 6 | **OECD Data** | https://data.oecd.org | 教育、健康、就业、创新、GDP 预测等 OECD 成员国数据 | 年度/季度 | 免费，API: `https://stats.oecd.org/SDMX-JSON/`；Python: `pip install pandaSDMX` | 跨国比较研究、政策效果评估、人力资本指数 |
| 7 | **中国人民银行** | http://www.pbc.gov.cn/diaochatongjisi | 货币供应量(M0/M1/M2)、贷款基准利率、外汇储备、社会融资规模 | 月度/季度 | 免费公开数据；HTML 表格可 WebFetch 提取或手工整理 CSV | 货币政策建模、信贷风险分析、利率市场化研究 |
| 8 | **CSMAR (国泰安)** | https://www.gtarsc.com | 中国上市公司财务、股票交易、公司治理全量数据 | 日/年 | 高校 IP 登录（多数大学已购买）；Python API 受限，导出 CSV 使用 | A 股实证研究、公司金融、事件研究法 |

### 常用 API 调用示例

```python
# World Bank: 获取中国 2000-2023 年 GDP (current US$)
import wbgapi as wb
df = wb.data.DataFrame('NY.GDP.MKTP.CD', 'CHN', range(2000, 2024))

# FRED: 获取美国联邦基金利率
from fredapi import Fred
fred = Fred(api_key='YOUR_KEY')
data = fred.get_series('FEDFUNDS')

# yfinance: 批量下载股票数据
import yfinance as yf
data = yf.download(['AAPL', 'MSFT', 'GOOGL'], start='2023-01-01', end='2024-01-01')
```

---

## 二、环境与气候

| # | 名称 | URL | 数据类型 | 更新频率 | 访问方式 | 典型建模用途 |
|---|------|-----|---------|---------|---------|------------|
| 9 | **NOAA Climate Data Online** | https://www.ncdc.noaa.gov/cdo-web | 全球气象站：温度、降水、风速、气压、积雪深度 | 日/小时级别 | 免费，API token 注册即得；Python: `pip install noaa-sdk` | 气候趋势分析、极值分布拟合、农业气象建模 |
| 10 | **NASA POWER** | https://power.larc.nasa.gov | 全球 0.5x0.5 度网格气象+太阳辐射：温度、降水、湿度、风速、太阳辐射、光合有效辐射 | 日/月/年，1981-至今 | 免费 API，无需 key；`https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR&community=AG&longitude=X&latitude=Y&start=20200101&end=20201231&format=JSON` | 太阳能评估、作物产量模型、可再生能源选址 |
| 11 | **中国环境监测总站** | http://www.cnemc.cn | 中国城市实时 AQI、PM2.5、PM10、SO2、NO2、O3、CO | 小时级别 | 公开数据；API: `https://air.cnemc.cn:18007` 或通过各地环保局开放平台 | 空气质量预测、污染源解析、环境 Kuznets 曲线验证 |
| 12 | **Copernicus Climate Data Store** | https://cds.climate.copernicus.eu | ERA5 再分析数据(0.25度)、季节预报、卫星观测、气候变化指标 | 小时/月，1950-至今 | 免费，注册即得 API key；Python: `pip install cdsapi` | 气候变暖归因、极端天气频率分析、海洋热含量估算 |
| 13 | **World Air Quality Index** | https://aqicn.org | 全球 130+ 国家 2000+ 城市实时 AQI 与 PM2.5/PM10/O3/NO2/SO2/CO | 实时/历史 | 免费，API token 注册即得；`https://api.waqi.info/feed/{city}/?token=YOUR_TOKEN` | 跨国空气污染对比、健康风险暴露评估 |
| 14 | **中国气象数据网** | http://data.cma.cn | 中国地面气象站观测、高空探测、雷达、卫星产品 | 日/小时 | 实名注册，部分免费；SURF_CLI_CHN_MUL_DAY 数据集含 800+ 站点 | 中国区域气候区划、极端降水建模、干旱指数计算 |
| 15 | **USGS EarthExplorer** | https://earthexplorer.usgs.gov | Landsat/Sentinel-2/MODIS 卫星影像（NDVI、地表温度、土地覆盖等） | 5-16 天重访 | 免费，注册即下 | 土地利用分类、植被覆盖变化、城市热岛效应 |
| 16 | **全球潮汐数据 (FES2014)** | https://www.aviso.altimetry.fr | 全球潮汐调和常数、海平面异常 | 静态模型 | 免费，需申请；Python: `pip install pyfes` | 海岸工程水位预测、潮汐能评估、风暴潮耦合 |

### 气象数据获取示例

```python
# NASA POWER: 获取北京 2023 年逐日温度与降水
import requests
url = ("https://power.larc.nasa.gov/api/temporal/daily/point?"
       "parameters=T2M,PRECTOTCORR&community=AG&longitude=116.407&latitude=39.904"
       "&start=20230101&end=20231231&format=JSON")
data = requests.get(url).json()

# Copernicus ERA5: 下载 2m 温度月均值
import cdsapi
c = cdsapi.Client()
c.retrieve('reanalysis-era5-single-levels-monthly-means', {
    'product_type': 'monthly_averaged_reanalysis',
    'variable': '2m_temperature',
    'year': '2023', 'month': [f'{i:02d}' for i in range(1,13)],
    'time': '00:00', 'format': 'netcdf',
}, 'era5_temp_2023.nc')
```

---

## 三、人口与社会

| # | 名称 | URL | 数据类型 | 更新频率 | 访问方式 | 典型建模用途 |
|---|------|-----|---------|---------|---------|------------|
| 17 | **UN Population Division** | https://population.un.org/wpp/Download | 各国人口总量、年龄结构、生育率、死亡率、迁移（1950-2100，含预测情景 SSP1-5） | 每 2 年更新 | 免费，CSV/Excel 直下 | 人口预测模型(Leslie/Lotka)、老龄化分析、劳动力供给 |
| 18 | **WHO Global Health Observatory** | https://www.who.int/data/gho | 期望寿命、疾病负担(DALY)、卫生支出、疫苗接种率、SDG 健康指标 | 年度 | 免费，JSON/CSV API: `https://ghoapi.azureedge.net/api/{indicator}` | 流行病 SIR/SEIR 建模、卫生资源配置、健康不平等测度 |
| 19 | **中国人口普查** | https://www.stats.gov.cn/sj/pcsj/ | 第七次(2020)、第六次(2010)全国人口普查：分省分县年龄/性别/教育/住房 | 每 10 年 | 免费公开，年鉴 PDF/Excel | 人口迁移引力模型、城镇化率预测、学区规划 |
| 20 | **UNDP Human Development Data** | https://hdr.undp.org/data-center | HDI、IHDI、GII、MPI 等人类发展指标，覆盖 190+ 国家 | 年度 | 免费，CSV/Excel 直下；API: `https://api.hdr.undp.org/` | 综合发展评价(TOPSIS/AHP)、SDG 进展评估 |
| 21 | **UNESCO 教育数据** | http://data.uis.unesco.org | 入学率、识字率、教育支出占 GDP、师生比 | 年度 | 免费，CSV 直下 | 教育基尼系数、人力资本生产函数 |
| 22 | **ILOSTAT (国际劳工组织)** | https://ilostat.ilo.org/data | 失业率、劳动参与率、工资水平、工作时间、职业伤害 | 年度/季度 | 免费，SDMX API: `https://www.ilo.org/sdmx/rest/data/{dataset}` | 就业预测、收入不平等建模、移民劳动力影响 |
| 23 | **World Value Survey** | https://www.worldvaluessurvey.org | 全球 120+ 国家价值观调查：政治态度、宗教信仰、社会信任 | 每 5 年一波 | 免费下载，注册后获取 | 跨文化比较、因子分析/结构方程、社会资本测量 |
| 24 | **GDELT Project** | https://www.gdelproject.org | 全球新闻事件数据库：冲突、合作、社会动荡实时计数 | 每 15 分钟 | 免费，BigQuery 查询或 CSV 下载 | 政治风险建模、舆论传播网络分析、冲突预测 |

---

## 四、交通与基础设施

| # | 名称 | URL | 数据类型 | 更新频率 | 访问方式 | 典型建模用途 |
|---|------|-----|---------|---------|---------|------------|
| 25 | **OpenStreetMap** | https://www.openstreetmap.org | 全球道路网络、建筑轮廓、POI、公共交通线路 | 实时社区更新 | 免费；Python: `pip install osmnx`；`ox.graph_from_place("Beijing, China", network_type="drive")` | 最短路径算法、设施选址、交通网络鲁棒性、物流配送 TSP/VRP |
| 26 | **中国交通运输部** | https://www.mot.gov.cn/shuju | 公路里程、铁路客运量、民航吞吐量、快递业务量 | 月度/年度 | 统计公报公开数据，WebFetch+PDF 解析或手工整理 | 交通需求预测、物流网络优化、碳排放核算 |
| 27 | **中国国家铁路集团** | https://www.12306.cn | 列车时刻表（爬取需注意 robots.txt） | 实时 | 公开查询，大规模爬取需谨慎；替代：开放数据竞赛 | 铁路调度优化、旅客流量分配、票价定价模型 |
| 28 | **FlightRadar24 / FlightAware** | https://www.flightaware.com/commercial/aeroapi | 全球航班实时位置、历史轨迹、延误信息 | 实时/历史 | FlightAware AeroAPI 付费商用，免费试用层有限 | 航路网络拓扑分析、延误传播模型、空域容量评估 |
| 29 | **NYC Taxi & Limousine Commission** | https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page | 纽约市黄色/绿色出租车与网约车每次行程：上下车时间/地点、距离、费用 | 月度（数亿条） | 免费，Parquet/CSV 直下 | 短时交通流预测(LSTM/Transformer)、出行 OD 矩阵、动态定价 |
| 30 | **中国城市规划设计研究院** | http://www.caupd.com | 中国城市建成区边界、路网密度、公共设施覆盖 | 项目制发布 | 部分公开报告，数据需申请或从公开竞赛获取 | 城市蔓延度测量、15 分钟生活圈评价、设施可达性 |

### OSM 路网提取示例

```python
import osmnx as ox
# 获取北京五环内可驾车路网
G = ox.graph_from_place("Beijing, China", network_type="drive")
# 计算节点数、边数
print(len(G.nodes), len(G.edges))
# 获取最短路径
orig = ox.distance.nearest_nodes(G, 116.397, 39.908)
dest = ox.distance.nearest_nodes(G, 116.484, 39.915)
route = ox.shortest_path(G, orig, dest, weight="length")
```

---

## 五、能源

| # | 名称 | URL | 数据类型 | 更新频率 | 访问方式 | 典型建模用途 |
|---|------|-----|---------|---------|---------|------------|
| 31 | **IEA Data & Statistics** | https://www.iea.org/data-and-statistics | 全球能源生产/消费/贸易、碳排放、可再生能源装机、能源效率指标 | 年度 | 部分免费，完整数据需订阅；World Energy Balances 等核心集可免费下载 CSV | 能源结构转型、碳达峰路径、各国能源效率 DEA 评价 |
| 32 | **EIA (US Energy Information Administration)** | https://www.eia.gov | 美国及全球原油/天然气产量、库存、消费、电价、排放 | 周/月/年 | 免费，API key 注册即得；`https://api.eia.gov/v2/`；Python: `pip install eiapy` | 能源价格预测、多目标能源调度、碳排放配额分配 |
| 33 | **BP Statistical Review (Energy Institute)** | https://www.energyinst.org/statistical-review | 全球分国家一次能源消费、分燃料产量、碳排放、关键矿产 | 年度（2023 起由 Energy Institute 发布） | 免费，Excel 直下 | 能源消费趋势外推、碳中和情景分析 |
| 34 | **IRENA (国际可再生能源署)** | https://www.irena.org/Data | 全球可再生能源装机容量、发电量、成本(LCOE)、就业人数 | 年度 | 免费，CSV/XLSX 直下 | 风光资源潜力评估、可再生能源投资优化、技术学习曲线 |
| 35 | **Ember Climate** | https://ember-climate.org/data | 全球各国电力结构（煤/气/风/光/水/核/生物质）及排放强度 | 年度（G20 月度） | 免费，CSV/JSON 直下 | 电源结构优化、碳减排路径、可再生能源渗透率 |
| 36 | **全球夜间灯光数据 (VIIRS/DMSP)** | https://eogdata.mines.edu/products/vnl | 全球 500m 分辨率夜间灯光月度/年度合成影像 | 月/年，2012-至今 | 免费，GeoTIFF 下载 | GDP 空间化代理变量、城市化测量、电力消费估计 |

---

## 六、Python 内置/自带数据集

> **地位**：离线最稳、即调即用、无需网络。用于快速验证模型、替代缺失数据、与真实数据对比。

### 6.1 `sklearn.datasets` --- 经典机器学习数据集

| # | 数据集 | 加载方式 | 样本数 | 特征数 | 任务类型 | 备注 |
|---|-------|---------|--------|--------|---------|------|
| 37 | **iris** | `load_iris()` | 150 | 4 | 3 类分类 | 鸢尾花，最经典入门集 |
| 38 | **wine** | `load_wine()` | 178 | 13 | 3 类分类 | 葡萄酒化学成分 |
| 39 | **breast_cancer** | `load_breast_cancer()` | 569 | 30 | 2 类分类 | 乳腺肿瘤良恶性 |
| 40 | **diabetes** | `load_diabetes()` | 442 | 10 | 回归 | 糖尿病进展量化 |
| 41 | **boston** | `load_boston()` | 506 | 13 | 回归 | 波士顿房价（v1.2 起移除，用 california_housing 替代） |
| 42 | **california_housing** | `fetch_california_housing()` | 20640 | 8 | 回归 | 加州房价，替代 boston |
| 43 | **digits** | `load_digits()` | 1797 | 64 | 10 类分类 | 手写数字 8x8 图 |
| 44 | **linnerud** | `load_linnerud()` | 20 | 3 | 多输出回归 | 体能测试数据 |
| 45 | **olivetti_faces** | `fetch_olivetti_faces()` | 400 | 4096 | 人脸识别 | 40 人各 10 张灰度 |
| 46 | **20newsgroups** | `fetch_20newsgroups()` | 18846 | --- | 文本分类 | 新闻组文档 |
| 47 | **make_classification** | `make_classification()` | 可配置 | 可配置 | 分类 | 合成分类数据，可控制类别分离度 |
| 48 | **make_regression** | `make_regression()` | 可配置 | 可配置 | 回归 | 合成回归数据，可控制噪声水平 |
| 49 | **make_blobs** | `make_blobs()` | 可配置 | 可配置 | 聚类 | 合成聚类数据，高斯各向同性 blob |
| 50 | **make_moons / make_circles** | `make_moons()` / `make_circles()` | 可配置 | 2 | 分类/聚类 | 非线性决策边界测试 |

### 6.2 `seaborn` --- 统计可视化内置集

| # | 数据集 | 加载方式 | 样本数 | 说明 | 典型用途 |
|---|-------|---------|--------|------|---------|
| 51 | **anscombe** | `sns.load_dataset("anscombe")` | 44 | Anscombe 四重奏：相同统计量，不同分布 | 数据可视化重要性演示 |
| 52 | **tips** | `sns.load_dataset("tips")` | 244 | 餐厅小费：总账单、小费、性别、吸烟、日期、时间、人数 | 线性回归、分类变量分析 |
| 53 | **penguins** | `sns.load_dataset("penguins")` | 344 | 企鹅：种类、喙长/深、鳍长、体重、性别（含缺失值） | 分类、缺失值处理、PCA |
| 54 | **diamonds** | `sns.load_dataset("diamonds")` | 53940 | 钻石：克拉、切工、颜色、净度、价格 | 价格预测（非线性和异方差） |
| 55 | **mpg** | `sns.load_dataset("mpg")` | 398 | 汽车燃油效率：MPG、马力、重量、产地、年份 | 多元回归、正则化 |
| 56 | **iris** | `sns.load_dataset("iris")` | 150 | 同 sklearn iris，seaborn 格式 | 分类、可视化 |
| 57 | **titanic** | `sns.load_dataset("titanic")` | 891 | 泰坦尼克：存活、舱位、年龄、性别、票价（含大量缺失） | 分类、缺失值插补 |
| 58 | **flights** | `sns.load_dataset("flights")` | 144 | 1949-1960 每月航空乘客数 | 时间序列分解、季节性检验 |
| 59 | **exercise** | `sns.load_dataset("exercise")` | 90 | 运动实验：饮食、脉搏、时间 | 重复测量方差分析 |
| 60 | **geyser** | `sns.load_dataset("geyser")` | 272 | 老忠实间歇泉喷发时长/间隔 | 双峰分布、聚类 |

### 6.3 `statsmodels` --- 计量经济学经典数据集

| # | 数据集 | 加载方式 | 样本数 | 说明 | 典型用途 |
|---|-------|---------|--------|------|---------|
| 61 | **longley** | `sm.datasets.longley.load_pandas()` | 16 | 美国宏观经济 1947-1962（就业/GNP 平减指数/GNP/军队/人口/年份） | 多重共线性诊断、岭回归演示 |
| 62 | **sunspots** | `sm.datasets.sunspots.load_pandas()` | 309 | 1700-2008 年太阳黑子数 | 时间序列周期性分析(SARIMA) |
| 63 | **co2** | `sm.datasets.co2.load_pandas()` | 2284 | 1958-2001 Mauna Loa CO2 月均浓度 | 趋势+季节性分解 |
| 64 | **spector** | `sm.datasets.spector.load_pandas()` | 32 | 大学生成绩：GPA/TUCE/PSI/GRADE | Logit/Probit 二元选择 |
| 65 | **stackloss** | `sm.datasets.stackloss.load_pandas()` | 21 | 化工厂 stack loss 与气流/水温/酸浓度 | 稳健回归（M-估计） |
| 66 | **anes96** | `sm.datasets.anes96.load_pandas()` | 944 | 1996 美国大选调查：党派、教育、年龄、收入、投票 | 定序 Logit、列联表 |
| 67 | **statecrime** | `sm.datasets.statecrime.load_pandas()` | 51 | 美国各州犯罪率与人口、贫困率 | Poisson/负二项回归 |

### 6.4 `scipy.datasets` --- 科学计算附属集

| # | 数据集 | 加载方式 | 说明 |
|---|-------|---------|------|
| 68 | **ascent** | `scipy.datasets.ascent()` | 512x512 灰度图像 |
| 69 | **face** | `scipy.datasets.face()` | 768x1024 RGB 浣熊脸图像 |
| 70 | **electrocardiogram** | `scipy.datasets.electrocardiogram()` | 心电信号时序 |

---

## 七、数据获取代码模板

### 7.1 直接 CSV/XLSX 下载 (pandas)

```python
import pandas as pd

# CSV 直链下载
url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
df = pd.read_csv(url)

# 需要 headers 认证的下载（如 Kaggle）
# 或带 encoding 参数（中文数据常见 GBK）
df = pd.read_csv("https://example.com/data.csv", encoding="gbk")

# Excel 文件
df = pd.read_excel("https://example.com/data.xlsx", sheet_name="Sheet1")

# 大数据集分块读取
for chunk in pd.read_csv(url, chunksize=10000):
    process(chunk)
```

### 7.2 RESTful API + JSON 解析 (requests)

```python
import requests
import pandas as pd

# GET 请求 + 参数
params = {"format": "json", "page": 1, "per_page": 1000}
resp = requests.get("https://api.example.com/v1/data", params=params, timeout=30)
resp.raise_for_status()
data = resp.json()

# 常见的 JSON 结构展开为 DataFrame
# 情况A: data["records"] -> list of dict
df = pd.DataFrame(data["records"])

# 情况B: 含嵌套结构的扁平化 (pd.json_normalize)
df = pd.json_normalize(data["items"], sep="_")

# 分页获取全量数据
all_records = []
page = 1
while True:
    params["page"] = page
    resp = requests.get(url, params=params, timeout=30).json()
    records = resp.get("data", [])
    if not records:
        break
    all_records.extend(records)
    page += 1
df = pd.DataFrame(all_records)
```

### 7.3 轻量网页爬取 (BeautifulSoup + pandas)

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://example.com/statistics-table"
html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

# 提取 HTML 表格
table = soup.find("table", {"class": "wikitable"})
df = pd.read_html(str(table))[0]

# 提取特定标签内容（如所有链接）
links = [a["href"] for a in soup.select("a.external") if a.has_attr("href")]
```

### 7.4 Kaggle 数据集下载 (kagglehub)

```python
# pip install kagglehub
import kagglehub
import pandas as pd

# 下载最新版本数据集，返回路径
path = kagglehub.dataset_download("uciml/iris")
# path: ~/.cache/kagglehub/datasets/uciml/iris/versions/1

# 读取数据
df = pd.read_csv(f"{path}/Iris.csv")
```

### 7.5 UCI Machine Learning Repository

```python
# pip install ucimlrepo
from ucimlrepo import fetch_ucirepo

# 按 ID 获取数据集
dataset = fetch_ucirepo(id=320)  # 例如 Adult 数据集
X = dataset.data.features
y = dataset.data.targets
```

### 7.6 Our World in Data 批量下载

```python
# OWID 几乎全部数据在 GitHub 上以 CSV 公开
base = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/"
dataset_name = "World Development Indicators - World Bank (2022)"
url = base + dataset_name.replace(" ", "%20") + "/" + dataset_name.replace(" ", "%20") + ".csv"
df = pd.read_csv(url)
```

---

## 八、数据质量速查

### 8.1 各源典型问题一览

| 数据源 | 常见缺陷 | 应对措施 |
|-------|---------|---------|
| **World Bank** | 发展中国家数据高缺失率(30-60%)；更新滞后 1-2 年；官方数据可能与实际偏差大 | 多重插补(MICE)；用 IMF/UN 同指标互相验证；标注数据年份而非引用的年份 |
| **FRED** | 指标修订频繁(vintage 问题)；断点(break)需人工对齐 | 使用 `realtime_start` 参数锁定 vintage；绘制时序图目检断点 |
| **NOAA 气象站** | 站点分布不均（非洲稀疏）；数据缺口(设备故障)；异常值和人工记录错误 | 空间插值(IDW/Kriging)；3sigma/IQR 异常检测；航天再分析数据(ERA5)交叉验证 |
| **OpenStreetMap** | 发展中国家道路网络完整度仅 40-80%；建筑数据缺失严重；分类标签不一致 | 与卫星影像对比较正；用 `osmnx` 的 `clean_intersections` 处理拓扑错误；补充官方路网数据 |
| **yfinance** | 停牌/退市/并股处理复杂；盘后数据可能缺失；前复权计算方式不透明 | 使用 `auto_adjust=False` 获取原始数据自行复权；去除 ST/停牌记录 |
| **Kaggle 数据集** | 用户上传，质量参差；字段说明常不全；可能有授权限制 | 必读 Dataset Card 和讨论区；优先选高 vote 和 kernel 数量的数据集；检查缺失率报告 |
| **中国国家统计局** | 统计口径变动（如 2018 年后固定资产投资口径调整）；地方汇总与全国数不一致 | 标注使用的统计口径版本；优先用全国数据自洽性检验 |
| **NASA POWER** | 网格插值产品而非实测；极端事件可能被平滑；沿海/山区误差大 | 与最近气象站实测对比；报告 RMSE；对极端值场景优先用站点实测 |
| **Copernicus ERA5** | 再分析产品，非观测值；近实时版本(ERA5T)可能后续修订 | 明确标注数据产品名称与生成时间；敏感性分析用 NCEP/NCAR 再分析做对照 |

### 8.2 多源交叉验证建议

| 建模场景 | 验证策略 |
|---------|---------|
| 国家 GDP 比较 | World Bank + IMF WEO + UN National Accounts 三方对照，取中位数或均值，报告差异范围 |
| 人口年龄结构 | UN WPP 中位预测 + 该国最新人口普查微调，对迁移率做敏感性测试 |
| 城市空气质量 | 中国环境监测总站 + AQICN + 欧洲 Sentinel-5P 卫星柱浓度，地面-卫星互相验证 |
| 能源碳排放 | IEA + EDGAR(欧盟) + Global Carbon Budget 三方对照，差异通常 <5% |
| 交通路网 | OSM + 官方交通规划图 + 高德/百度地图 API(国内)交叉核实路网密度 |
| 气候变化指标 | ERA5 + NOAA 站点 + Berkeley Earth，取 ensemble 均值 |

### 8.3 快速质量检查脚本模板

```python
def quick_data_audit(df):
    """打印基础数据质量报告"""
    print(f"Shape: {df.shape}")
    print(f"dtypes:\n{df.dtypes.value_counts()}")
    print(f"Missing (%):\n{(df.isnull().sum()/len(df)*100).sort_values(ascending=False).head(20)}")
    print(f"Duplicates: {df.duplicated().sum()}")
    for col in df.select_dtypes('number').columns:
        print(f"{col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}, "
              f"min={df[col].min():.2f}, max={df[col].max():.2f}")
```

---

## 九、数据获取铁律与登记规范

1. **绝不编造数据**。找不到真实数据时，标注"题目附件提供/需自采"，或用**显著标注为"模拟数据"**的数据并说明生成算法与参数。
2. **每条外部数据登记到 `data/SOURCES.md`**，格式如下：

```
| 文件名 | 来源名称 | URL | 下载日期 | 字段说明 | 许可/引用方式 |
|--------|---------|-----|---------|---------|-------------|
| gdp_wb_2024.csv | World Bank | https://... | 2024-07-28 | country_code, year, gdp_usd | CC BY 4.0, cite: World Bank (2024) |
```

3. **国内站点谨慎**：百度百科仅作背景、知网多需付费、国家统计局偶有反爬。取不到时换英文/国际替代源，并在 SOURCES.md 如实注明"原源不可得，已使用替代源 X"。
4. **API key 安全**：代码中不硬编码 key，用环境变量 `os.getenv("API_KEY")` 或 `python-dotenv`。
5. **大文件策略**：大于100MB的数据集不上传git；登记到 `.gitignore`，在 SOURCES.md 中记录如何复现下载。
6. **结构化数据存储**：统一使用 CSV (UTF-8) 或 Parquet 格式；`data/raw/` 存放原始数据，`data/processed/` 存放清洗后的数据。

---

*最后更新：2024-07  |  本文档由人类指令驱动生成，内容涉及 URL 与 API 端点可能有变，以各源官网最新文档为准。*
