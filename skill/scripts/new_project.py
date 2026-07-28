#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""new_project.py — 为一道赛题创建标准工作目录。

用法：
    python new_project.py "2024国赛A题" --lang zh
    python new_project.py "2024_MCM_C" --lang en

会在当前目录下创建：
    <slug>/
      problem.md      赛题原文 + 审题报告落点
      data/           数据与 SOURCES.md
      code/           求解代码
      figures/        图片
      paper/          main.tex（从模板复制）+ refs.bib
      REPORT.md       阶段性产出汇总（审题/框架/评审记录）
"""
import argparse
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)


def slugify(name):
    s = re.sub(r"\s+", "_", name.strip())
    return re.sub(r"[^\w一-鿿.-]", "", s) or "mm_project"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    ap.add_argument("--dir", default=".")
    args = ap.parse_args()

    slug = slugify(args.name)
    root = os.path.join(args.dir, slug)
    for sub in ["data", "code", "figures", "paper"]:
        os.makedirs(os.path.join(root, sub), exist_ok=True)

    tmpl = "cumcm-zh" if args.lang == "zh" else "mcm-en"
    src = os.path.join(SKILL, "templates", tmpl, "main.tex")
    dst = os.path.join(root, "paper", "main.tex")
    if os.path.exists(src):
        shutil.copy(src, dst)
    # 复制绘图风格
    style = os.path.join(SKILL, "templates", "figures.mplstyle")
    if os.path.exists(style):
        shutil.copy(style, os.path.join(root, "code", "figures.mplstyle"))

    with open(os.path.join(root, "problem.md"), "w", encoding="utf-8") as f:
        f.write(f"# {args.name}\n\n## 赛题原文\n\n<在此粘贴题目>\n\n## 审题报告\n\n<mm-problem-analyst 输出>\n")
    with open(os.path.join(root, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write(f"# {args.name} — 建模过程记录\n\n"
                "## 1 审题\n\n## 2 框架/方法选型\n\n## 3 数据\n\n"
                "## 4 求解\n\n## 5 图表\n\n## 6 评审记录（对抗轮次/评分）\n")
    with open(os.path.join(root, "paper", "refs.bib"), "w", encoding="utf-8") as f:
        f.write("% 参考文献。示例：\n"
                "@book{example2020, author={张三}, title={数学建模方法}, "
                "year={2020}, publisher={高等教育出版社}}\n")

    print(f"✅ 工作目录已创建: {root}")
    print(f"   模板语言: {args.lang}  ({tmpl})")
    print(f"   下一步: 把赛题粘进 {slug}/problem.md，然后运行 skill 流水线。")


if __name__ == "__main__":
    main()
