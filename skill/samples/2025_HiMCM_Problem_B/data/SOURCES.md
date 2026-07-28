# 数据来源记录 (Data Sources)

## 1. 城市环境指标 (`city_indicators.csv`)

### 数据来源

| 指标 | 来源 | URL | 取得日期 |
|------|------|-----|----------|
| 电网碳排放因子 (kgCO2/kWh) | EPA eGRID2022 子区域数据 | https://www.epa.gov/egrid | 2026-07-27 |
| 可再生能源占比 (%) | EIA State Energy Profiles | https://www.eia.gov/state/ | 2026-07-27 |
| 2月平均温度 (°C) | NOAA 1991-2020 Climate Normals | https://www.ncei.noaa.gov/access/us-climate-normals/ | 2026-07-27 |
| 年降水量 (inches) | NOAA 1991-2020 Climate Normals | https://www.ncei.noaa.gov/access/us-climate-normals/ | 2026-07-27 |
| 水资源压力指数 (WRI) | WRI Aqueduct Water Risk Atlas | https://www.wri.org/aqueduct | 2026-07-27 |
| 废物回收率 (%) | EPA Sustainable Materials Management, 各市/州环保部门 | https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling | 2026-07-27 |
| 公共交通分担率 (%) | American Community Survey (ACS) 2023 5-Year Estimates | https://www.census.gov/acs | 2026-07-27 |
| 机场旅客吞吐量 | FAA Terminal Area Forecast 2024 / 各机场年度报告 | https://www.faa.gov/data_research/aviation/taf/ | 2026-07-27 |
| 体育场LEED认证 | USGBC LEED Project Database | https://www.usgbc.org/projects | 2026-07-27 |
| 体育场穹顶信息 | 各体育场官方网站 / Wikipedia | - | 2026-07-27 |
| 人口密度 | US Census Bureau | https://www.census.gov/ | 2026-07-27 |
| 绿地面积 | Trust for Public Land ParkScore | https://www.tpl.org/parkscore | 2026-07-27 |

### 数据质量说明
- **已办城市（10个）**：数据完整度 85-90%。部分城市废物回收率为州级估算值。
- **未办城市（3个）**：数据完整度 80%。废物回收率、公共交通分担率为估算。
- **水资源压力指数**：基于WRI Aqueduct基线水压力评分（所在流域级），标注为估算值。
- **体育场LEED等级**：0=未认证, 1=认证级, 2=银级, 3=金级, 4=铂金级。已通过USGBC数据库核实。

### 候选城市选取说明
**已办城市（10个，覆盖主要地理区域和NFL可持续性评估时期）**：
新奥尔良、迈阿密、坦帕、亚特兰大、英格尔伍德(洛杉矶)、格兰岱尔(凤凰城)、拉斯维加斯、休斯顿、达拉斯(阿灵顿)、圣克拉拉

**未办城市（3个，有NFL球队且数据可得性好）**：
纳什维尔(Titans)、夏洛特(Panthers)、西雅图(Seahawks)

## 2. 超级碗LIX基线数据 (`superbowl_lix_baseline.csv`)

| 来源 | URL | 取得日期 | 备注 |
|------|-----|----------|------|
| NFL Green Initiative | https://www.nfl.com/causes/nfl-green/ | 2026-07-27 | 官方环保计划 |
| ENGIE Impact (NFL能源顾问) | https://www.engieimpact.com/ | 2026-07-27 | REC采购数据 |
| EPA eGRID2022 | https://www.epa.gov/egrid | 2026-07-27 | SRMV子区域电网因子 |
| Entergy New Orleans | https://www.entergy-neworleans.com/ | 2026-07-27 | 清洁能源置换数据 |
| NOAA 1991-2020 Normals | https://www.ncei.noaa.gov/ | 2026-07-27 | 新奥尔良2月气候 |
| Coalition to Restore Coastal Louisiana | https://www.crcl.org/ | 2026-07-27 | 牡蛎壳回收项目 |
| Second Harvest Food Bank | https://no-hunger.org/ | 2026-07-27 | 食物回收数据 |

### 数据局限性
- **Scope 1（场馆直接排放）**：无完整公开的LCA清单数据，标注为"不可得"。
- **Scope 3（观众航空/住宿等）**：NFL未公布完整Scope 3估计，我们基于观众估计数和平均航班碳排放进行估算。
- **碳抵消**：REC采购的碳抵消效果存在方法论争议（附加性问题），在报告中将标注此不确定性。

## 3. 环境评分体系参考

| 体系 | 来源 | URL |
|------|------|-----|
| Council for Responsible Sport (CRS) | 官方网站 | https://www.councilforresponsiblesport.org/ |
| ISO 20121 (Event Sustainability Management) | ISO | https://www.iso.org/standard/70269.html |
| LEED Building Certification | USGBC | https://www.usgbc.org/leed |
| GRI Event Organizers Sector Standard | Global Reporting Initiative | https://www.globalreporting.org/ |

## 4. 未获得数据说明

| 缺失数据 | 原因 | 处理方式 |
|----------|------|----------|
| 各城市完整Scope 3排放清单 | 多数城市不公布赛事级别Scope 3 | 使用机场客流量+平均飞行距离+排放因子估算 |
| 体育场精确能耗数据 | 商业敏感信息 | 使用LEED等级和穹顶状态做代理变量 |
| 2月精确水资源数据 | 多数水源机构仅公布年度数据 | 使用WRI年度水压力评分替代 |
| 城市级别废物回收率（标准化） | 各市统计口径不一致 | 取最可得数据，标注为"州级估算"或"市级估算" |

## 重要提示

- **标注为"ESTIMATED"或"SIMULATED"的数据为推算/模拟值**，非官方公布精确数据，论文中使用时需显著标注。
- **所有电网数据来自eGRID2022（2025年1月发布）**，为最新可得版本。
- **气候数据来自NOAA 1991-2020气候标准值**，为当前气象学标准参考期。
- 本数据集仅供本次数学建模竞赛使用，不应作为实际选址决策依据。
