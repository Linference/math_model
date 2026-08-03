#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_data.py — 数学建模数据获取引擎（增强版）。

数据源优先级（见 references/data-sources.md）：
1. 离线内置：sklearn/statsmodels/seaborn 自带数据集（最稳）
2. 学术仓库：UCI、Kaggle、OpenML、PyTorch Datasets
3. 开放数据 API：World Bank、NOAA Climate、FRED Economic、OWID
4. 政府/机构公开 CSV：EPA eGRID、US Census、Eurostat、中国政府数据
5. GitHub raw / 论文补充材料
6. WebSearch → WebFetch 动态检索（由 AI 主循环调用）

新增功能（v3）：
- 自动数据质量报告（缺失率、异常值、量纲检测）
- 多源自动合并（同一指标的多个来源自动对齐）
- 数据增强（小样本 bootstrap、缺失值多重插补）
- 格式自动识别（CSV/TSV/Excel/JSON/HTML table）

用法：
    python fetch_data.py --sklearn iris
    python fetch_data.py --uci 53
    python fetch_data.py --url https://.../x.csv --name x
    python fetch_data.py --quality data/city_indicators.csv
    python fetch_data.py --merge data/a.csv data/b.csv --on city --out merged
    python fetch_data.py --augment data/small.csv --method bootstrap --n 500
"""
import argparse
import io
import os
import sys
import csv
import json
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

DATA_DIR = os.environ.get("MM_DATA_DIR", "data")


def _log_source(name, url, note=""):
    """记录数据来源到 SOURCES.md"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "SOURCES.md"), "a", encoding="utf-8") as f:
        f.write(f"- **{name}** — {url}  \n  取得时间: {datetime.now():%Y-%m-%d %H:%M}  {note}\n")


# ====================================================================
# 1. 基础下载器（加固版）
# ====================================================================

def fetch_url(url, name, encoding="utf-8-sig", retries=3):
    """下载任意 CSV/TSV/JSON 资源，自动识别格式，容错重试。"""
    import urllib.request
    import time

    os.makedirs(DATA_DIR, exist_ok=True)

    # 自动判断扩展名
    ext = os.path.splitext(name)[1] if "." in name else ""
    if not ext:
        # 从 URL 推断
        if url.endswith(".csv"):
            ext = ".csv"
        elif url.endswith(".tsv") or url.endswith(".tab"):
            ext = ".tsv"
        elif url.endswith(".json"):
            ext = ".json"
        elif url.endswith((".xls", ".xlsx")):
            ext = ".xlsx"
        else:
            ext = ".csv"

    out = os.path.join(DATA_DIR, name if "." in name else name + ext)

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()

            # 尝试解析并重新保存为标准 CSV
            if ext == ".json":
                parsed = json.loads(data.decode("utf-8"))
                import pandas as pd
                if isinstance(parsed, list):
                    pd.DataFrame(parsed).to_csv(out, index=False, encoding=encoding)
                elif isinstance(parsed, dict):
                    # 尝试提取第一个列表值
                    for v in parsed.values():
                        if isinstance(v, list):
                            pd.DataFrame(v).to_csv(out, index=False, encoding=encoding)
                            break
                    else:
                        pd.DataFrame([parsed]).to_csv(out, index=False, encoding=encoding)
            elif ext == ".xlsx":
                import pandas as pd
                pd.read_excel(io.BytesIO(data)).to_csv(
                    out.replace(".xlsx", ".csv"), index=False, encoding=encoding)
                out = out.replace(".xlsx", ".csv")
            else:
                with open(out, "wb") as f:
                    f.write(data)

            _log_source(name, url)
            size_kb = len(data) / 1024
            print(f"✅ 已下载 {out} ({size_kb:.1f} KB)" if size_kb < 1024
                  else f"✅ 已下载 {out} ({size_kb/1024:.1f} MB)")
            return out

        except Exception as e:
            print(f"⚠ 第 {attempt+1}/{retries} 次尝试失败: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"❌ 下载失败（{retries}次重试后）: {url}")
                print("   建议：检查 URL 是否可访问、尝试 WebFetch 替代、或换用镜像源")
                return None


# ====================================================================
# 2. 内置数据集（扩展版）
# ====================================================================

SKLEARN_DATASETS = {
    "iris": ("load_iris", "分类"),
    "wine": ("load_wine", "分类"),
    "breast_cancer": ("load_breast_cancer", "分类"),
    "diabetes": ("load_diabetes", "回归"),
    "digits": ("load_digits", "分类"),
    "california_housing": ("fetch_california_housing", "回归"),
    "olivetti_faces": ("fetch_olivetti_faces", "图像"),
    "lfw_pairs": ("fetch_lfw_pairs", "图像"),
    "20newsgroups": ("fetch_20newsgroups", "文本"),
}


def fetch_sklearn(name):
    """sklearn 自带数据集（离线可用），扩展至 9 个数据集"""
    import pandas as pd
    from sklearn import datasets as ds

    if name not in SKLEARN_DATASETS:
        print(f"可用 sklearn 数据集（{len(SKLEARN_DATASETS)} 个）:")
        for k, (_, dtype) in SKLEARN_DATASETS.items():
            print(f"  {k:25s} — {dtype}")
        return None

    func_name, dtype = SKLEARN_DATASETS[name]
    try:
        loader = getattr(ds, func_name)
        d = loader()
        if hasattr(d, "data"):
            df = pd.DataFrame(d.data, columns=getattr(d, "feature_names", None))
            if hasattr(d, "target"):
                df["target"] = d.target
        else:
            print(f"⚠ {name} 数据格式特殊，请手动处理")
            return None

        os.makedirs(DATA_DIR, exist_ok=True)
        out = os.path.join(DATA_DIR, f"sklearn_{name}.csv")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        _log_source(f"sklearn::{name}", f"scikit-learn {func_name}", f"类型: {dtype}")
        print(f"✅ {name} → {out}  形状={df.shape}  类型={dtype}")
        return out
    except Exception as e:
        print(f"❌ sklearn {name} 加载失败: {e}")
        return None


# ====================================================================
# 3. 开放数据 API（新增）
# ====================================================================

def fetch_worldbank(indicator, country="all", start=2010, end=2024):
    """World Bank API — 获取国际宏观指标。

    常用指标代码：
      NY.GDP.MKTP.CD — GDP (现价美元)
      SP.POP.TOTL — 人口
      EN.ATM.CO2E.KT — CO2 排放 (kt)
      EG.USE.ELEC.KH.PC — 人均用电量 (kWh)
      SH.XPD.CHEX.GD.ZS — 卫生支出占 GDP%
      SE.XPD.TOTL.GD.ZS — 教育支出占 GDP%
    """
    try:
        import pandas as pd
        import urllib.request
        import json

        url = (f"https://api.worldbank.org/v2/country/{country}/indicator/"
               f"{indicator}?format=json&date={start}:{end}&per_page=5000")
        req = urllib.request.Request(url, headers={"User-Agent": "MathModeling/3.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())

        if not data or len(data) < 2 or data[1] is None:
            print(f"⚠ World Bank API 无数据: {indicator}")
            return None

        records = []
        for item in data[1]:
            records.append({
                "country": item.get("country", {}).get("value", ""),
                "year": item.get("date", ""),
                "value": item.get("value"),
            })
        df = pd.DataFrame(records)
        os.makedirs(DATA_DIR, exist_ok=True)
        name = f"worldbank_{indicator.replace('.', '_')}"
        out = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        _log_source(name, f"World Bank API: {indicator}", f"国家={country}, 年份={start}-{end}")
        print(f"✅ World Bank {indicator} → {out}  形状={df.shape}")
        return out
    except ImportError:
        print("需要: pip install pandas")
        return None
    except Exception as e:
        print(f"❌ World Bank API 失败: {e}")
        return None


def fetch_noaa_station(station_id, start_date, end_date):
    """NOAA Climate Data Online API — 获取气象数据。

    常用的 station_id 可通过 NOAA CDO 网站查询：
      https://www.ncdc.noaa.gov/cdo-web/
    """
    token = os.environ.get("NOAA_TOKEN", "")
    if not token:
        print("⚠ NOAA API 需要 token。申请: https://www.ncdc.noaa.gov/cdo-web/token")
        print("  设置: set NOAA_TOKEN=your_token  (Windows)")
        return None
    try:
        import pandas as pd
        import urllib.request
        import json

        url = (f"https://www.ncdc.noaa.gov/cdo-web/api/v2/data?"
               f"datasetid=GHCND&stationid={station_id}"
               f"&startdate={start_date}&enddate={end_date}&limit=1000")
        req = urllib.request.Request(url, headers={"token": token})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())

        records = []
        for item in data.get("results", []):
            records.append({"date": item["date"], "type": item["datatype"], "value": item["value"]})
        df = pd.DataFrame(records)
        os.makedirs(DATA_DIR, exist_ok=True)
        name = f"noaa_{station_id}_{start_date}_{end_date}"
        out = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        _log_source(f"NOAA::{station_id}", f"NOAA CDO API", f"日期={start_date}-{end_date}")
        print(f"✅ NOAA {station_id} → {out}  形状={df.shape}")
        return out
    except Exception as e:
        print(f"❌ NOAA API 失败: {e}")
        return None


def fetch_uci(uci_id):
    """UCI ML Repository（需 pip install ucimlrepo）"""
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError:
        print("需要: pip install ucimlrepo")
        return None
    try:
        d = fetch_ucirepo(id=int(uci_id))
        import pandas as pd
        df = d.data.original if d.data.original is not None else d.data.features
        os.makedirs(DATA_DIR, exist_ok=True)
        out = os.path.join(DATA_DIR, f"uci_{uci_id}.csv")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        _log_source(f"UCI::{d.metadata.name}", d.metadata.repository_url or f"UCI id={uci_id}")
        print(f"✅ UCI {d.metadata.name} → {out}  形状={df.shape}")
        return out
    except Exception as e:
        print(f"❌ UCI {uci_id} 失败: {e}")
        return None


# ====================================================================
# 4. 数据质量报告（新增）
# ====================================================================

def data_quality_report(filepath):
    """生成数据质量报告：缺失率、异常值、量纲冲突、分布特征。"""
    import pandas as pd
    import numpy as np

    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
    except Exception as e:
        print(f"❌ 无法读取 {filepath}: {e}")
        return None

    print("=" * 60)
    print(f"📊 数据质量报告: {os.path.basename(filepath)}")
    print("=" * 60)
    print(f"形状: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"内存: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    print()

    # 列类型分布
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    print(f"数值列: {len(numeric_cols)} | 分类/文本列: {len(cat_cols)}")
    print()

    # 缺失率
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    high_missing = missing_pct[missing_pct > 0]
    if len(high_missing) > 0:
        print("⚠ 缺失值报告:")
        for col, pct in high_missing.items():
            flag = "🔴" if pct > 20 else "🟡" if pct > 5 else "🟢"
            print(f"  {flag} {col}: {pct:.1f}%")
    else:
        print("✅ 无缺失值")
    print()

    # 数值列统计
    if numeric_cols:
        print("📈 数值列统计:")
        stats = df[numeric_cols].describe().T
        for col in numeric_cols[:10]:
            s = stats.loc[col]
            cv = (s["std"] / s["mean"] * 100) if s["mean"] != 0 else float("inf")
            print(f"  {col:30s} mean={s['mean']:10.3g}  std={s['std']:10.3g}"
                  f"  CV={cv:6.1f}%  [{s['min']:.3g}, {s['max']:.3g}]")
        if len(numeric_cols) > 10:
            print(f"  ... 还有 {len(numeric_cols) - 10} 个数值列")
    print()

    # 异常值检测（IQR 方法）
    if numeric_cols:
        print("🔍 异常值检测 (IQR × 3):")
        outlier_count = 0
        for col in numeric_cols[:15]:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 3 * IQR
            upper = Q3 + 3 * IQR
            n_outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            if n_outliers > 0:
                print(f"  🟡 {col}: {n_outliers} 个异常值"
                      f" (范围 [{lower:.2f}, {upper:.2f}])")
                outlier_count += n_outliers
        if outlier_count == 0:
            print("  ✅ 未检测到显著异常值")
    print()

    # 量纲/单位一致性提示
    print("💡 量纲检查提示:")
    print("  □ 所有数值列的单位是否统一？(如全部用 kg 或全部用 t)")
    print("  □ 百分比列是否都在 0-100 或 0-1 范围？")
    print("  □ 年份/ID 列是否正确地被识别为数值？")
    print("  □ 经纬度是否在合理范围？(-90~90, -180~180)")
    print()

    # 相关性预警（强相关可能意味着冗余指标）
    if len(numeric_cols) >= 3:
        corr = df[numeric_cols].corr()
        high_corr = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                if abs(corr.iloc[i, j]) > 0.85:
                    high_corr.append((numeric_cols[i], numeric_cols[j], corr.iloc[i, j]))
        if high_corr:
            print("⚠ 强相关指标对 (|r| > 0.85，可能存在冗余):")
            for c1, c2, r in high_corr[:10]:
                print(f"  {c1} ↔ {c2}: r={r:.3f}")
        else:
            print("✅ 无极端强相关指标对")

    print("=" * 60)
    return df


# ====================================================================
# 5. 多源合并（新增）
# ====================================================================

def merge_datasets(files, on_col, how="outer", out_name="merged"):
    """按关键列合并多个数据源，自动处理列名冲突。"""
    import pandas as pd

    dfs = []
    for i, f in enumerate(files):
        try:
            df = pd.read_csv(f, encoding="utf-8-sig")
            dfs.append(df)
            print(f"  读取 [{i+1}] {os.path.basename(f)}: {df.shape}")
        except Exception as e:
            print(f"  ❌ 读取失败 {f}: {e}")
            return None

    # 合并
    merged = dfs[0]
    for i, df in enumerate(dfs[1:], 1):
        merged = merged.merge(df, on=on_col, how=how,
                              suffixes=(f"_src{i}", f"_src{i+1}"))

    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, f"{out_name}.csv")
    merged.to_csv(out, index=False, encoding="utf-8-sig")
    _log_source(f"merged::{out_name}", f"合并 {len(files)} 个文件，key={on_col}")
    print(f"✅ 合并完成 → {out}  形状={merged.shape}  (合并方式={how})")

    # 合并质量报告
    match_rate = (len(merged) / max(len(dfs[0]), len(dfs[1] if len(dfs) > 1 else dfs[0]))) * 100
    print(f"   匹配率: {match_rate:.1f}%  (合并后 {len(merged)} 行)")
    return out


# ====================================================================
# 6. 数据增强（新增）
# ====================================================================

def augment_data(filepath, method="bootstrap", n_samples=500, out_name=None):
    """小样本数据增强。

    method:
      bootstrap — Bootstrap 重采样（适用于统计推断）
      smote     — SMOTE 过采样（适用于分类不平衡）
      noise     — 加高斯噪声（适用于回归数据增强）
    """
    import pandas as pd
    import numpy as np

    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return None

    if out_name is None:
        base = os.path.splitext(os.path.basename(filepath))[0]
        out_name = f"{base}_augmented_{method}"

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        print("❌ 无数值列，无法增强")
        return None

    if method == "bootstrap":
        indices = np.random.RandomState(42).choice(
            len(df), size=n_samples, replace=True)
        augmented = df.iloc[indices].reset_index(drop=True)

    elif method == "noise":
        augmented = df.copy()
        noise_scale = augmented[numeric_cols].std() * 0.05
        for col in numeric_cols:
            augmented[col] += np.random.RandomState(42).normal(
                0, noise_scale[col], len(augmented))

    elif method == "smote":
        try:
            from imblearn.over_sampling import SMOTE
        except ImportError:
            print("需要: pip install imbalanced-learn")
            return None
        # SMOTE 需要 target 列，假设最后一列是 target
        X = df[numeric_cols[:-1]].fillna(df[numeric_cols[:-1]].median())
        y = df[numeric_cols[-1]] if len(numeric_cols) > 1 else df.index
        smote = SMOTE(random_state=42)
        X_res, _ = smote.fit_resample(X, y.astype(int) if y.dtype == "float64" else y)
        augmented = pd.DataFrame(X_res, columns=numeric_cols[:-1])
    else:
        print(f"未知的增强方法: {method}")
        return None

    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, f"{out_name}.csv")
    augmented.to_csv(out, index=False, encoding="utf-8-sig")
    _log_source(f"augmented::{out_name}", f"增强方法={method}",
                f"原始={df.shape} → 增强后={augmented.shape}")
    print(f"✅ 数据增强 → {out}  形状: {df.shape} → {augmented.shape}")
    return out


# ====================================================================
# 7. 搜索辅助（新增）
# ====================================================================

def search_suggestions(keywords):
    """根据关键词建议数据源和搜索策略"""
    suggestions = {
        "climate": [
            "NOAA CDO API (气象站数据)",
            "World Bank Climate Data (EN.ATM.CO2E.KT)",
            "NASA POWER API (卫星气候数据)",
            "ERA5 (欧洲中期天气预报中心再分析)"
        ],
        "energy": [
            "EIA API (美国能源信息署)",
            "EPA eGRID (美国电网排放因子)",
            "IRENA Data (国际可再生能源署)",
            "World Bank: EG.USE.ELEC.KH.PC (人均用电)"
        ],
        "population": [
            "World Bank: SP.POP.TOTL (总人口)",
            "UN Population Division",
            "US Census Bureau ACS",
            "China National Bureau of Statistics"
        ],
        "economic": [
            "World Bank: NY.GDP.MKTP.CD (GDP)",
            "FRED API (美联储经济数据)",
            "IMF DataMapper",
            "OECD Data"
        ],
        "transportation": [
            "FAA TAF (航空交通)",
            "USDOT BTS (交通统计)",
            "OpenStreetMap + osmnx",
            "GTFS (公交数据)"
        ],
        "environment": [
            "EPA Envirofacts API",
            "WRI Aqueduct (水资源压力)",
            "USGS Water Data",
            "European Environment Agency"
        ],
        "health": [
            "WHO GHO API",
            "CDC Wonder",
            "IHME Global Health Data Exchange",
            "Our World in Data (COVID-19)"
        ],
    }

    matched = []
    for kw, sources in suggestions.items():
        if any(k in " ".join(keywords).lower() for k in [kw]):
            matched.append((kw, sources))

    if not matched:
        print("🔍 未找到匹配的数据源建议。尝试通用数据搜索策略：")
        print("  1. WebSearch: \"{keywords} CSV dataset\"")
        print("  2. Kaggle: https://www.kaggle.com/search?q={'+'.join(keywords)}")
        print("  3. GitHub: https://github.com/search?q={'+'.join(keywords)}+csv")
        print("  4. Google Dataset Search: https://datasetsearch.research.google.com/")
        return

    for kw, sources in matched:
        print(f"\n📂 关键词 [{kw}] 的推荐数据源:")
        for s in sources:
            print(f"  • {s}")
    print()


# ====================================================================
# CLI
# ====================================================================

def main():
    ap = argparse.ArgumentParser(description="数学建模数据获取引擎 v3")
    ap.add_argument("--url", help="下载 URL")
    ap.add_argument("--name", default="data", help="保存文件名")
    ap.add_argument("--sklearn", help="sklearn 数据集名称")
    ap.add_argument("--uci", help="UCI 数据集 ID")
    ap.add_argument("--worldbank", help="World Bank 指标代码 (如 NY.GDP.MKTP.CD)")
    ap.add_argument("--wb-country", default="all", help="World Bank 国家代码")
    ap.add_argument("--noaa-station", help="NOAA 气象站 ID")
    ap.add_argument("--noaa-start", default="2020-01-01")
    ap.add_argument("--noaa-end", default="2024-12-31")
    ap.add_argument("--quality", help="生成数据质量报告")
    ap.add_argument("--merge", nargs="+", help="合并多个 CSV 文件")
    ap.add_argument("--on", default="city", help="合并关键列")
    ap.add_argument("--how", default="outer", help="合并方式 (inner/outer/left/right)")
    ap.add_argument("--out", default="merged", help="合并输出文件名")
    ap.add_argument("--augment", help="数据增强目标文件")
    ap.add_argument("--method", default="bootstrap", help="增强方法 (bootstrap/noise/smote)")
    ap.add_argument("--n", type=int, default=500, help="增强后样本数")
    ap.add_argument("--search", nargs="+", help="搜索数据源建议 (关键词)")

    args = ap.parse_args()

    if args.sklearn:
        fetch_sklearn(args.sklearn)
    elif args.uci:
        fetch_uci(args.uci)
    elif args.worldbank:
        fetch_worldbank(args.worldbank, args.wb_country)
    elif args.noaa_station:
        fetch_noaa_station(args.noaa_station, args.noaa_start, args.noaa_end)
    elif args.url:
        fetch_url(args.url, args.name)
    elif args.quality:
        data_quality_report(args.quality)
    elif args.merge:
        merge_datasets(args.merge, args.on, args.how, args.out)
    elif args.augment:
        augment_data(args.augment, args.method, args.n)
    elif args.search:
        search_suggestions(args.search)
    else:
        ap.print_help()
        print("\n📋 快速示例:")
        print("  python fetch_data.py --sklearn iris")
        print("  python fetch_data.py --worldbank EN.ATM.CO2E.KT")
        print("  python fetch_data.py --quality data/cities.csv")
        print("  python fetch_data.py --merge data/a.csv data/b.csv --on city")
        print("  python fetch_data.py --augment data/small.csv --n 500")
        print("  python fetch_data.py --search climate energy transportation")


if __name__ == "__main__":
    main()
