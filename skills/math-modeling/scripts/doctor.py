#!/usr/bin/env python3
"""
math-modeling skill 环境自检脚本 (Environment Self-Check)

用法:
    python doctor.py            # 运行全部检查
    python doctor.py --json     # 输出 JSON 格式结果
    python doctor.py --verbose  # 详细输出

支持: Windows (primary), macOS, Linux
"""

import sys
import os
import subprocess
import importlib
import shutil
import json
from pathlib import Path

# ── ANSI color codes ──────────────────────────────────────────────
GREEN   = "\033[92m"
RED     = "\033[91m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

def cprint(text, color=""):
    """Print text with optional ANSI color, resetting at end."""
    print(f"{color}{text}{RESET}")

# ── Check functions ───────────────────────────────────────────────

def check_python_version() -> dict:
    """Check Python >= 3.10"""
    version = sys.version_info
    major, minor, micro = version[:3]
    ok = (major == 3 and minor >= 10) or major > 3
    installed = f"{major}.{minor}.{micro}"
    required = "3.10"
    return {
        "name": "Python version",
        "status": "PASS" if ok else "FAIL",
        "installed": installed,
        "required": f">= {required}",
        "detail": f"Python {installed} {'meets' if ok else 'does NOT meet'} requirement >= {required}"
    }


def check_latex() -> dict:
    """Check xelatex/pdflatex available on system PATH"""
    # Try xelatex first (preferred for CJK), then pdflatex
    found_exe = None
    for exe in ["xelatex", "pdflatex"]:
        if shutil.which(exe):
            found_exe = exe
            break

    if found_exe:
        try:
            result = subprocess.run(
                [found_exe, "--version"],
                capture_output=True, timeout=15,
                encoding="utf-8", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
            )
            version_line = result.stdout.split("\n")[0] if result.stdout else "unknown"
        except Exception:
            version_line = "found but version check failed"
        return {
            "name": "LaTeX",
            "status": "PASS",
            "installed": version_line,
            "required": "xelatex or pdflatex",
            "detail": f"Found: {found_exe}"
        }
    else:
        # On Windows, check common install paths
        if sys.platform == "win32":
            candidates = [
                r"C:\texlive\2024\bin\windows\xelatex.exe",
                r"C:\texlive\2023\bin\windows\xelatex.exe",
                r"C:\MiKTeX\miktex\bin\x64\xelatex.exe",
            ]
            for candidate in candidates:
                if os.path.isfile(candidate):
                    return {
                        "name": "LaTeX",
                        "status": "WARN",
                        "installed": candidate,
                        "required": "xelatex or pdflatex (on PATH)",
                        "detail": f"Found at {candidate} but NOT on PATH. Add to PATH or use full path."
                    }

        return {
            "name": "LaTeX",
            "status": "WARN",
            "installed": "not found",
            "required": "xelatex or pdflatex",
            "detail": "Neither xelatex nor pdflatex found on PATH. LaTeX compilation will fail."
        }


def check_packages() -> list[dict]:
    """Check numpy, pandas, scipy, sklearn, matplotlib, seaborn, openpyxl"""
    required = {
        "numpy":      "numpy",
        "pandas":     "pandas",
        "scipy":      "scipy",
        "sklearn":    "scikit-learn",
        "matplotlib": "matplotlib",
        "seaborn":    "seaborn",
        "openpyxl":   "openpyxl",
    }
    # Extended: useful but not critical
    extended = {
        "networkx":    "networkx",
        "pulp":        "pulp",
        "statsmodels": "statsmodels",
        "sympy":       "sympy",
    }

    results = []
    # Critical packages
    for imp_name, pkg_name in required.items():
        try:
            mod = importlib.import_module(imp_name)
            version = getattr(mod, "__version__", "installed")
            results.append({
                "name": pkg_name,
                "status": "PASS",
                "installed": str(version),
                "required": "required",
                "detail": f"{pkg_name} {version}"
            })
        except ImportError:
            results.append({
                "name": pkg_name,
                "status": "FAIL",
                "installed": "not found",
                "required": "required",
                "detail": f"{pkg_name} NOT installed. Run: pip install {pkg_name}"
            })

    # Extended packages
    for imp_name, pkg_name in extended.items():
        try:
            mod = importlib.import_module(imp_name)
            version = getattr(mod, "__version__", "installed")
            results.append({
                "name": pkg_name,
                "status": "PASS",
                "installed": str(version),
                "required": "optional",
                "detail": f"{pkg_name} {version}"
            })
        except ImportError:
            results.append({
                "name": pkg_name,
                "status": "WARN",
                "installed": "not found",
                "required": "optional",
                "detail": f"{pkg_name} NOT installed. Run: pip install {pkg_name}"
            })

    return results


def check_fonts() -> dict:
    """Check Chinese fonts (SimHei, SimSun on Windows; Noto CJK on Linux)"""
    if sys.platform == "win32":
        try:
            import matplotlib.font_manager as fm
            fonts = {f.name for f in fm.fontManager.ttflist}
        except Exception:
            # Fallback: check system font dir
            fonts = set()
            font_dir = r"C:\Windows\Fonts"
            if os.path.isdir(font_dir):
                for fname in os.listdir(font_dir):
                    fonts.add(os.path.splitext(fname)[0])

        simhei = "SimHei" in fonts
        simsun = "SimSun" in fonts
        msyh   = "Microsoft YaHei" in fonts

        found = []
        missing = []
        if simhei:
            found.append("SimHei (黑体)")
        else:
            missing.append("SimHei (黑体)")
        if simsun:
            found.append("SimSun (宋体)")
        else:
            missing.append("SimSun (宋体)")
        if msyh:
            found.append("Microsoft YaHei (微软雅黑)")
        else:
            missing.append("Microsoft YaHei (微软雅黑)")

        status = "PASS" if (simhei or msyh) else ("WARN" if len(found) > 0 else "FAIL")
        detail = f"Found: {', '.join(found)}" if found else "No Chinese fonts found"
        if missing:
            detail += f" | Missing: {', '.join(missing)}"

        return {
            "name": "Chinese fonts (Windows)",
            "status": status,
            "installed": ", ".join(found) if found else "none",
            "required": "SimHei or Microsoft YaHei",
            "detail": detail
        }

    else:  # Linux / macOS
        try:
            import matplotlib.font_manager as fm
            fonts = {f.name for f in fm.fontManager.ttflist}
        except Exception:
            fonts = set()

        cjk_fonts = [name for name in fonts if any(
            kw in name.lower() for kw in ["noto cjk", "wqy", "wenquan", "simhei", "source han"]
        )]
        # Also check system font dirs
        system_font_dirs = [
            "/usr/share/fonts", "/usr/local/share/fonts",
            "~/Library/Fonts", "/Library/Fonts",
            "/System/Library/Fonts",
        ]
        for d in system_font_dirs:
            expanded = os.path.expanduser(d)
            if os.path.isdir(expanded):
                for root, _, files in os.walk(expanded):
                    for f in files:
                        if any(kw in f.lower() for kw in ["cjk", "wqy", "noto", "simhei", "source-han"]):
                            cjk_fonts.append(f)

        cjk_fonts = list(set(cjk_fonts))
        status = "PASS" if len(cjk_fonts) > 0 else "WARN"
        detail = f"Found: {', '.join(cjk_fonts[:5])}" if cjk_fonts else "No CJK fonts found. Install fonts-noto-cjk or similar."

        return {
            "name": "Chinese fonts (*nix)",
            "status": status,
            "installed": ", ".join(cjk_fonts[:5]) if cjk_fonts else "none",
            "required": "Noto CJK, WQY, or similar",
            "detail": detail
        }


def check_skill_structure() -> list[dict]:
    """Verify skill directory has all required files and directories"""
    skill_root = Path(__file__).resolve().parent.parent  # scripts/.. -> skill root

    required_dirs = [
        "scripts",
        "templates",
        "templates/cumcm-zh",
        "templates/mcm-en",
        "templates/shared",
        "references",
        "samples",
        "workflows",
        "state",
    ]
    required_files = [
        "SKILL.md",
        "README.md",
        "scripts/plot_helpers.py",
        "scripts/new_project.py",
        "scripts/compile.py",
        "scripts/verify_results.py",
        "scripts/doctor.py",
        "templates/figures.mplstyle",
        "templates/cumcm-zh/main.tex",
        "templates/mcm-en/main.tex",
        "templates/shared/assumption_table.md",
        "state/decision_log.json",
        "state/.gitkeep",
    ]

    results = []

    for rel_path in required_dirs:
        full = skill_root / rel_path
        exists = full.is_dir()
        results.append({
            "name": f"directory: {rel_path}/",
            "status": "PASS" if exists else "FAIL",
            "installed": "exists" if exists else "MISSING",
            "required": "required",
            "detail": f"Directory {rel_path}/ {'exists' if exists else 'is MISSING'}"
        })

    for rel_path in required_files:
        full = skill_root / rel_path
        exists = full.is_file()
        results.append({
            "name": f"file: {rel_path}",
            "status": "PASS" if exists else "FAIL",
            "installed": "exists" if exists else "MISSING",
            "required": "required" if "doctor" not in rel_path else "this file",
            "detail": f"File {rel_path} {'exists' if exists else 'is MISSING'}"
        })

    # Check sample project
    sample = skill_root / "samples" / "2025_HiMCM_Problem_B"
    if sample.is_dir():
        sample_files = list(sample.rglob("*"))
        results.append({
            "name": "sample project",
            "status": "PASS",
            "installed": f"{len(sample_files)} files",
            "required": "recommended",
            "detail": f"Sample project present with {len(sample_files)} files"
        })
    else:
        results.append({
            "name": "sample project",
            "status": "WARN",
            "installed": "missing",
            "required": "recommended",
            "detail": "No sample project found. Run new_project.py to add one."
        })

    return results


# ── Main ──────────────────────────────────────────────────────────

def collect_checks():
    """Run all checks, return flat list of result dicts."""
    results = []

    # Check 1: Python version
    results.append(check_python_version())

    # Check 2: LaTeX
    results.append(check_latex())

    # Check 3: Packages
    results.extend(check_packages())

    # Check 4: Fonts
    results.append(check_fonts())

    # Check 5: Skill structure
    results.extend(check_skill_structure())

    return results


def print_summary(results, verbose=False):
    """Print formatted results table and summary."""
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    n_warn = sum(1 for r in results if r["status"] == "WARN")
    total = len(results)

    # Header
    cprint("=" * 72, BOLD + CYAN)
    cprint("  math-modeling skill — 环境自检 (Environment Doctor)", BOLD + CYAN)
    cprint("=" * 72, BOLD + CYAN)
    print()

    # Determine label width for alignment
    max_name = max(len(r["name"]) for r in results) if results else 20

    for r in results:
        label = r["name"].ljust(max_name + 2)
        if r["status"] == "PASS":
            cprint(f"  [{GREEN}PASS{RESET}] {label}", GREEN)
        elif r["status"] == "FAIL":
            cprint(f"  [{RED}FAIL{RESET}] {label}", RED)
        else:
            cprint(f"  [{YELLOW}WARN{RESET}] {label}", YELLOW)

        if verbose or r["status"] != "PASS":
            print(f"         {r['detail']}")

    # Summary
    print()
    cprint("-" * 72, CYAN)
    cprint(f"  Summary: {GREEN}{n_pass} passed{RESET}, "
            f"{RED}{n_fail} failed{RESET}, "
            f"{YELLOW}{n_warn} warnings{RESET}  (total {total} checks)", BOLD)

    if n_fail == 0 and n_warn == 0:
        cprint(f"  {GREEN}All checks passed. Environment is ready!{RESET}", GREEN)
    elif n_fail == 0:
        cprint(f"  {YELLOW}Some warnings — environment mostly ready.{RESET}", YELLOW)
    else:
        cprint(f"  {RED}{n_fail} failure(s) must be fixed before use.{RESET}", RED)

    cprint("-" * 72, CYAN)

    return n_fail


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    json_out = "--json" in sys.argv

    results = collect_checks()

    if json_out:
        output = {
            "summary": {
                "passed":  sum(1 for r in results if r["status"] == "PASS"),
                "failed":  sum(1 for r in results if r["status"] == "FAIL"),
                "warned":  sum(1 for r in results if r["status"] == "WARN"),
                "total":   len(results),
            },
            "checks": results
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return output["summary"]["failed"]

    n_fail = print_summary(results, verbose=verbose)
    return n_fail


if __name__ == "__main__":
    sys.exit(min(main(), 127))  # cap at 127 per Unix convention
