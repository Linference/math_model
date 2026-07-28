# data-sources — 数据源清单与备注

优先内置 WebSearch/WebFetch 取直链，再用 `fetch_data.py` 落盘。记录来源到 `data/SOURCES.md`。

## 稳定可用（推荐）
| 源 | 用途 | 备注 |
|---|---|---|
| sklearn / statsmodels 自带集 | 分类/回归/聚类练手与对照 | **离线最稳**，`--sklearn iris/wine/diabetes` |
| UCI ML Repository | 经典数据集 | `pip install ucimlrepo`，`--uci <id>`；uci.edu |
| Kaggle Datasets | 各领域数据 | 需 `kaggle.json` 凭证；kaggle.com/datasets |
| Our World in Data | 人口/能源/疫情/经济 | CSV 直下，ourworldindata.org |
| World Bank Open Data | 各国宏观指标 | API+CSV，data.worldbank.org |
| WHO / UN Data | 卫生/人口 | who.int, data.un.org |
| GitHub raw | 复现数据/论文附件 | raw.githubusercontent.com/... .csv |
| Wikipedia | 背景+数据表 | 英文版数据更全；表格可 WebFetch 提取 |

## 学术参数来源
- Google Scholar / Nature / Science / arXiv：取模型参数、系数、经验公式（**须标引用**，别直接爬全文）。

## 国内站点（谨慎）
| 源 | 备注 |
|---|---|
| 百度百科 | 仅作背景，数据别直接采信；常可 WebFetch |
| 知网 CNKI | 多需登录/付费，正文难取；用摘要或换开放源 |
| 国家统计局 | 有公开 CSV/年鉴，但页面可能反爬；优先 WebFetch 公开页 |
| 中国政府数据开放平台 | 地方开放数据，质量不一 |

**易失败**：以上国内站可能被墙/需登录/反爬。取不到时：换英文/国际源或镜像，并在 SOURCES.md **如实注明**"原源不可得，已用替代源"。

## 铁律
- 绝不编造数据。
- 找不到真实数据 → 标"题目附件提供/需自采"，或用**显著标注为模拟**的数据并说明生成方式。
- 每条数据登记：名称、URL、日期、字段、单位、许可 → 论文可引用。
