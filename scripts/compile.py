#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compile.py — 编译 LaTeX 为 PDF（数学建模 skill 工具链）。

特性：
- 中文源码自动使用 xelatex（ctex/xeCJK），英文可用 pdflatex/xelatex
- 跑两遍以解交叉引用；有 .bib 时插入 bibtex 流程
- 编译失败时回读 .log，抓取报错行与上下文，便于定位
- Windows(MiKTeX) / Linux(TeXLive) 通用

用法：
    python compile.py main.tex                 # 自动选引擎
    python compile.py main.tex --engine xelatex
    python compile.py main.tex --bib           # 强制走 bibtex
    python compile.py main.tex --clean         # 编译后清理中间文件
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

AUX_EXTS = (".aux", ".log", ".out", ".toc", ".lof", ".lot", ".bbl", ".blg",
            ".fls", ".fdb_latexmk", ".synctex.gz", ".nav", ".snm", ".vrb")


def has_cjk(path):
    """判断源文件是否含中文（决定是否必须用 xelatex）。"""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
    except OSError:
        return False
    if re.search(r"[一-鿿]", txt):
        return True
    # 显式引入 ctex 也算
    return "ctex" in txt or "xeCJK" in txt


def find_engine(preferred=None):
    """返回可用的 LaTeX 引擎绝对路径名。"""
    candidates = [preferred] if preferred else []
    candidates += ["xelatex", "pdflatex", "latexmk"]
    for c in candidates:
        if c and shutil.which(c):
            return c
    return None


def run(cmd, cwd):
    print(">>", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="ignore")


def show_errors(log_path):
    """从 .log 提取 LaTeX 报错，打印行号与上下文。"""
    if not os.path.exists(log_path):
        print("（无 .log 文件可分析）")
        return
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    hits = []
    for i, ln in enumerate(lines):
        if ln.startswith("!") or "Error" in ln or "Undefined control" in ln:
            ctx = "".join(lines[i:i + 4])
            hits.append(ctx)
    if hits:
        print("\n===== 检测到 LaTeX 报错 =====")
        for h in hits[:12]:
            print(h.rstrip())
            print("-" * 40)
    else:
        print("未在 .log 中找到显式报错标记，请手动检查", log_path)


def compile_tex(tex, engine=None, use_bib=False, clean=False, passes=2):
    tex = os.path.abspath(tex)
    if not os.path.exists(tex):
        print("找不到文件:", tex)
        return 1
    cwd = os.path.dirname(tex)
    base = os.path.splitext(os.path.basename(tex))[0]

    if engine is None:
        engine = "xelatex" if has_cjk(tex) else "pdflatex"
    engine = find_engine(engine)
    if engine is None:
        print("未找到 LaTeX 引擎（xelatex/pdflatex）。请安装 MiKTeX 或 TeXLive。")
        return 2
    print(f"使用引擎: {engine}  |  源文件: {tex}")

    common = [engine, "-interaction=nonstopmode", "-halt-on-error",
              os.path.basename(tex)]

    r = run(common, cwd)
    if use_bib and shutil.which("bibtex"):
        run(["bibtex", base], cwd)
        passes = max(passes, 2)

    for _ in range(passes - 1):
        r = run(common, cwd)

    pdf = os.path.join(cwd, base + ".pdf")
    if os.path.exists(pdf) and r.returncode == 0:
        print("\n✅ 编译成功:", pdf)
        rc = 0
    else:
        print("\n❌ 编译失败（returncode=%s）" % r.returncode)
        show_errors(os.path.join(cwd, base + ".log"))
        rc = 3

    # ---- PDF 版本留存 ----
    if os.path.exists(pdf):
        version_dir = os.path.join(cwd, "versions")
        os.makedirs(version_dir, exist_ok=True)
        # 自动编号版本文件: main_v000.pdf, main_v001.pdf ...
        existing = sorted([f for f in os.listdir(version_dir)
                          if f.startswith(base + "_v") and f.endswith(".pdf")])
        next_num = len(existing)
        ver_name = f"{base}_v{next_num:03d}.pdf"
        ver_path = os.path.join(version_dir, ver_name)
        try:
            shutil.copy2(pdf, ver_path)
            print(f"📄 版本留存: {ver_name}  (versions/ 共 {next_num + 1} 个版本)")
        except OSError as e:
            print(f"⚠ 版本留存失败: {e}")

    if clean:
        for ext in AUX_EXTS:
            p = os.path.join(cwd, base + ext)
            if os.path.exists(p):
                os.remove(p)
        print("已清理中间文件。")
    return rc


def main():
    ap = argparse.ArgumentParser(description="编译 LaTeX 为 PDF")
    ap.add_argument("tex", help="主 .tex 文件")
    ap.add_argument("--engine", choices=["xelatex", "pdflatex", "latexmk"],
                    default=None)
    ap.add_argument("--bib", action="store_true", help="启用 bibtex")
    ap.add_argument("--clean", action="store_true", help="编译后清理中间文件")
    ap.add_argument("--passes", type=int, default=2)
    args = ap.parse_args()
    sys.exit(compile_tex(args.tex, args.engine, args.bib, args.clean, args.passes))


if __name__ == "__main__":
    main()
