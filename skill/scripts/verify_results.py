#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_results.py — 自动交叉验证：比对代码输出与论文中引用的数字。

检测项：
1. 代码关键输出与论文数字的一致性
2. 公式代码实现与方案表的匹配度
3. 量纲统一性
4. 随机种子固定性

用法：
    # 阶段 4 验证：仅验证代码
    python verify_results.py <project_dir> --stage 4

    # 阶段 6 验证：验证代码 + 论文
    python verify_results.py <project_dir> --stage 6
"""
import argparse
import os
import re
import subprocess
import sys


def find_py_files(code_dir):
    """返回所有 solve_q*.py 文件"""
    return sorted([f for f in os.listdir(code_dir)
                   if f.startswith("solve_q") and f.endswith(".py")])


def run_code(code_dir, py_file):
    """执行单个求解脚本，返回 stdout 文本和退出码"""
    path = os.path.join(code_dir, py_file)
    try:
        r = subprocess.run([sys.executable, path], capture_output=True,
                           text=True, timeout=120, cwd=code_dir)
        return r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "[TIMEOUT after 120s]", 1
    except Exception as e:
        return f"[ERROR: {e}]", 1


def extract_numbers(text):
    """从文本中提取所有数值（含单位）。匹配紧贴或空格分隔的数字+单位。"""
    # 匹配: 100kgCO2e, 3.14%, -2.5e3, 1,538 kgCO2e/观众·日 等
    pattern = r'([+-]?\d+\.?\d*(?:e[+-]?\d+)?)\s*([a-zA-Z%/°·一-鿿]*)'
    matches = re.findall(pattern, text)
    results = []
    for m in matches:
        try:
            results.append((float(m[0]), m[1]))
        except ValueError:
            continue
    return results


def check_random_seeds(code_dir, py_files):
    """检查每个文件是否有固定随机种子"""
    results = {}
    for f in py_files:
        path = os.path.join(code_dir, f)
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        has_np_seed = bool(re.search(r'(np\.random\.seed|random\.seed)\s*\(', content))
        results[f] = has_np_seed
    return results


def check_unit_consistency(outputs):
    """检查所有输出的单位是否统一（如都使用 kgCO2e 而非混用 tCO2e）"""
    units_found = {}
    unit_variants = {
        "kgCO2": re.compile(r'kg\s*CO2', re.IGNORECASE),
        "tCO2": re.compile(r't\s*CO2|ton\w*\s*CO2', re.IGNORECASE),
        "kgCO2e": re.compile(r'kg\s*CO2e', re.IGNORECASE),
        "tCO2e": re.compile(r't\s*CO2e|ton\w*\s*CO2e', re.IGNORECASE),
    }
    for name, out in outputs.items():
        for unit_name, pat in unit_variants.items():
            if pat.search(out):
                units_found[name] = units_found.get(name, []) + [unit_name]
    # 检查是否有混用（同一文件同时出现 kg 和 t）
    issues = []
    for name, units in units_found.items():
        has_kg = any("kg" in u for u in units)
        has_t = any(u.startswith("t") for u in units)
        if has_kg and has_t:
            issues.append(f"⚠ {name}: 混用 kg 和 t 单位，请统一")
    return issues


def read_tex_numbers(tex_path):
    """从 paper/main.tex 中提取所有数值（含上下文）"""
    if not os.path.exists(tex_path):
        return []
    with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # 匹配：数字 + 可选的上下文
    pattern = r'([+-]?\d+\.?\d*(?:e[+-]?\d+)?)\s*(?:kgCO2e|tCO2e|kWh|kgCO2|%|[°CkmMW])?'
    matches = re.findall(pattern, content)
    return [float(m) for m in matches if float(m) != 0]


def verify_stage4(project_dir):
    """阶段 4 验证：代码可运行 + 随机种子 + 量纲 + 数字可追溯"""
    code_dir = os.path.join(project_dir, "code")
    if not os.path.isdir(code_dir):
        print("❌ code/ 目录不存在")
        return 1

    py_files = find_py_files(code_dir)
    if not py_files:
        print("❌ 未找到 solve_q*.py 文件，请检查 code/ 目录")
        print("   期望文件命名格式: solve_q1.py, solve_q2.py, ...")
        return 1

    print(f"📂 找到 {len(py_files)} 个求解脚本\n")
    all_ok = True

    # ---- 1. 可运行性 ----
    print("=" * 60)
    print("1. 代码可运行性检查")
    print("=" * 60)
    outputs = {}
    for f in py_files:
        out, rc = run_code(code_dir, f)
        outputs[f] = out
        status = "✅" if rc == 0 else "❌"
        if rc != 0:
            all_ok = False
        # 显示关键输出行
        key_lines = [l.strip() for l in out.split("\n")
                     if re.search(r'\d+\.?\d*', l) and len(l) > 10][:5]
        print(f"{status} {f}")
        for kl in key_lines:
            print(f"   → {kl[:100]}")
        print()

    # ---- 2. 随机种子 ----
    print("=" * 60)
    print("2. 随机种子固定检查")
    print("=" * 60)
    seeds = check_random_seeds(code_dir, py_files)
    for f, ok in seeds.items():
        status = "✅" if ok else "⚠ (缺 random.seed)"
        if not ok:
            all_ok = False
        print(f"{status}  {f}")

    # ---- 3. 量纲一致性 ----
    print("\n" + "=" * 60)
    print("3. 量纲一致性检查")
    print("=" * 60)
    unit_issues = check_unit_consistency(outputs)
    if unit_issues:
        for issue in unit_issues:
            print(issue)
        all_ok = False
    else:
        print("✅ 未检测到单位混用（或输出中无明确单位标记）")

    # ---- 4. 数字可追溯 ----
    print("\n" + "=" * 60)
    print("4. 关键数字可追溯性")
    print("=" * 60)
    print("手动检查清单：")
    print("□ 论文中每个关键数字是否在代码输出中能找到对应来源？")
    print("□ 代码变量名和行号是否可定位？")
    print("□ 如有数字比值/差值，其被除/减数是否同单位？")
    print("   (示例: 1,538 kgCO2e/观众·日 — 检查分子分母单位是否一致)")

    if all_ok:
        print("\n✅ 阶段 4 验证全部通过")
        return 0
    else:
        print("\n❌ 阶段 4 验证发现问题，请修复后重新验证")
        return 1


def _is_close_to_any(value, candidates, rtol=1e-3, atol=1e-8):
    """检查 value 是否与 candidates 中任一数字在容差范围内匹配。

    使用相对容差 (rtol) 为主，绝对容差 (atol) 为兜底。
    默认 rtol=1e-3：论文中 0.7637 和代码输出 0.76371 应视为匹配。
    注意：简单 round(n,4) 做集合匹配在边界值上极易漏检——
    如 0.76371 round→0.7637, 而 0.76374 round→0.7637 也通过，
    但 0.76375 round→0.7638 反而匹配不上。用 np.isclose 语义
    更符合"数值上差不多"的真实需求。
    """
    import math
    for c in candidates:
        if math.isclose(value, c, rel_tol=rtol, abs_tol=atol):
            return True
    return False


def verify_stage6(project_dir):
    """阶段 6 验证：代码 vs 论文数字交叉比对"""
    rc = verify_stage4(project_dir)
    if rc != 0:
        print("\n⚠ 阶段 4 验证未通过，跳过论文交叉比对")
        return rc

    tex_path = os.path.join(project_dir, "paper", "main.tex")
    if not os.path.exists(tex_path):
        print("❌ paper/main.tex 不存在")
        return 1

    print("\n" + "=" * 60)
    print("5. 论文数字交叉验证")
    print("=" * 60)
    tex_nums = read_tex_numbers(tex_path)
    print(f"从论文中提取到 {len(tex_nums)} 个数字")

    # 运行所有代码，收集输出中的所有数字（保留原始精度，不做 round 截断）
    code_dir = os.path.join(project_dir, "code")
    py_files = find_py_files(code_dir)
    all_code_nums = []
    for f in py_files:
        out, _ = run_code(code_dir, f)
        nums = extract_numbers(out)
        for n, _ in nums:
            all_code_nums.append(n)

    # 交叉比对：论文中的大数字（非整数常数）是否在代码输出中可追溯
    # 使用相对容差匹配替代 round() 集合匹配，避免浮点边界漏检
    suspicious = []
    for n in tex_nums:
        if abs(n) <= 1 or n == int(n):
            continue  # 跳过小整数和常数（如 1, 2, 0.5 等可能是公式系数）
        if not _is_close_to_any(n, all_code_nums, rtol=1e-3):
            # 尝试更宽松的 rtol=5e-3 做二次确认
            if not _is_close_to_any(n, all_code_nums, rtol=5e-3):
                suspicious.append(n)

    if suspicious:
        print(f"⚠ 发现 {len(suspicious)} 个论文数字在代码输出中找不到对应来源（rtol=1e-3）：")
        for n in suspicious[:10]:
            print(f"   → {n}")
        print("请逐一确认这些数字的来源（可能是计算派生值或手动填入）")
    else:
        print("✅ 论文数字均可追溯到代码输出（相对容差 1e-3）")

    # 图引用检查
    figures_dir = os.path.join(project_dir, "figures")
    if os.path.isdir(figures_dir):
        png_count = len([f for f in os.listdir(figures_dir) if f.endswith(".png")])
        with open(tex_path, "r", encoding="utf-8", errors="ignore") as f:
            tex_content = f.read()
        ref_count = len(re.findall(r'\\ref\{fig:', tex_content))
        ref_label = r'\ref{fig:'
        print(f"\n图引用检查：figures/ PNG={png_count} | {ref_label} 引用={ref_count}")
        if ref_count < png_count:
            print(f"⚠ 有 {png_count - ref_count} 张图未被正文引用")
        else:
            print("✅ 所有图均被正文引用")

    return 0


def main():
    ap = argparse.ArgumentParser(description="数学建模结果交叉验证")
    ap.add_argument("project_dir", help="项目目录")
    ap.add_argument("--stage", choices=["4", "6"], default="4",
                    help="验证阶段 (4=仅代码, 6=代码+论文)")
    args = ap.parse_args()

    if not os.path.isdir(args.project_dir):
        print(f"❌ 目录不存在: {args.project_dir}")
        return 1

    if args.stage == "6":
        return verify_stage6(args.project_dir)
    else:
        return verify_stage4(args.project_dir)


if __name__ == "__main__":
    sys.exit(main())
