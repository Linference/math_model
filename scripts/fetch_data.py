#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_data.py — 数据获取骨架（数学建模 skill）。

优先级策略（见 references/data-sources.md）：
1. 首选内置 WebSearch/WebFetch（由 AI 主循环调用）拿到直链后，用本脚本下载/解析
2. sklearn / statsmodels 自带数据集（离线可用，最稳）
3. UCI、Kaggle（需 kaggle.json）、GitHub raw、政府开放数据 CSV/API
4. 国内站（百度百科/知网/国家统计局）易被墙或需登录 —— 本脚本给出容错下载

所有下载会：落盘到 data/、记录来源 URL 到 data/SOURCES.md（便于论文引用）。

用法：
    python fetch_data.py --url https://.../foo.csv --name foo
    python fetch_data.py --sklearn iris
    python fetch_data.py --uci 53            # UCI id
"""
import argparse
import io
import os
import sys
from datetime import datetime

DATA_DIR = os.environ.get("MM_DATA_DIR", "data")


def _log_source(name, url, note=""):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "SOURCES.md"), "a", encoding="utf-8") as f:
        f.write(f"- **{name}** — {url}  \n  取得时间: {datetime.now():%Y-%m-%d}  {note}\n")


def fetch_url(url, name):
    """下载任意 CSV/文本资源，容错。"""
    import urllib.request
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, name if "." in name else name + ".csv")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(out, "wb") as f:
            f.write(data)
        _log_source(name, url)
        print(f"✅ 已下载 {out} ({len(data)} bytes)")
        return out
    except Exception as e:
        print(f"❌ 下载失败: {e}\n   国内站点可能需要登录/被墙，改用 WebFetch 或换镜像源。")
        return None


def fetch_sklearn(name):
    """sklearn 自带数据集，离线可用。"""
    import pandas as pd
    from sklearn import datasets as ds
    loaders = {
        "iris": ds.load_iris, "wine": ds.load_wine,
        "breast_cancer": ds.load_breast_cancer, "diabetes": ds.load_diabetes,
        "digits": ds.load_digits,
    }
    if name not in loaders:
        print("可用 sklearn 数据集:", ", ".join(loaders)); return None
    d = loaders[name]()
    df = pd.DataFrame(d.data, columns=getattr(d, "feature_names", None))
    if hasattr(d, "target"):
        df["target"] = d.target
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, f"sklearn_{name}.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    _log_source(f"sklearn::{name}", "scikit-learn built-in dataset")
    print(f"✅ 已保存 {out}  形状={df.shape}")
    return out


def fetch_uci(uci_id):
    """UCI ML Repository（需 pip install ucimlrepo）。"""
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError:
        print("需要: pip install ucimlrepo"); return None
    d = fetch_ucirepo(id=int(uci_id))
    df = d.data.original if d.data.original is not None else d.data.features
    os.makedirs(DATA_DIR, exist_ok=True)
    out = os.path.join(DATA_DIR, f"uci_{uci_id}.csv")
    df.to_csv(out, index=False, encoding="utf-8-sig")
    _log_source(f"UCI::{d.metadata.name}", d.metadata.repository_url or f"UCI id={uci_id}")
    print(f"✅ 已保存 {out}  形状={df.shape}")
    return out


def main():
    ap = argparse.ArgumentParser(description="数据获取骨架")
    ap.add_argument("--url"); ap.add_argument("--name", default="data")
    ap.add_argument("--sklearn"); ap.add_argument("--uci")
    args = ap.parse_args()
    if args.sklearn:
        fetch_sklearn(args.sklearn)
    elif args.uci:
        fetch_uci(args.uci)
    elif args.url:
        fetch_url(args.url, args.name)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
