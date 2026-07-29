# Math Modeling Multi-Agent Paper Generation System

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Version](https://img.shields.io/badge/version-v2.2-6f42c1)](https://github.com/Linference/math_model/blob/main/skill/CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-008080?logo=latex)
![Claude Code](https://img.shields.io/badge/Claude_Code-v2.2-D97757)
![CUMCM / MCM / HiMCM](https://img.shields.io/badge/CUMCM_|_MCM_|_HiMCM-e74c3c)

---

**中文** ← current · **English** · [日本語](../ja/README.md) · [한국어](../ko/README.md)

---

**v2.2** — Multi-agent adversarial collaboration + 9 independent QA gates + anti-pattern hard blocks + human-in-the-loop checkpoints + cross-stage state management. 21 reference manuals, 6 algorithm cookbooks, bilingual phrase bank, anti-pattern knowledge base, environment doctor script.

Drop in a contest problem PDF, and the system automatically runs through: problem analysis → method selection → web data hunting → Python solving → visualization → LaTeX paper compilation → 3-role parallel adversarial review → final PDF. Supports CUMCM (China), MCM/ICM (USA), and HiMCM.

---

## Quick Start

### Prerequisites

- **Node.js** ≥ v18 — [nodejs.org](https://nodejs.org/)
- **Claude Code**: `npm install -g @anthropic-ai/claude-code`

### Install

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

Or download the ZIP from [Releases](https://github.com/Linference/math_model/releases).

### Run

```bash
claude
/math-modeling
[paste contest problem or drag in PDF]
```

---

## 7-Stage Pipeline

| Stage | Task | Output |
|:--:|------|------|
| 0 | Project scaffolding | Standard directory skeleton |
| 1 | Deep problem analysis | Structured analysis report (2000+ words) |
| 2 | Method selection + ML/DL decision | Modeling plan with chart checklist |
| 3 | Web data hunting | CSV files + SOURCES.md |
| 4 | Python implementation | Runnable scripts + numerical results |
| 5 | Visualization (16 chart types) | High-quality figures (300 DPI) |
| 6 | LaTeX writing + compilation | Paper draft |
| 7 | 3-role adversarial review | Final PDF (score ≥ 7.5/10) |

## 8 Sub-agents

| Agent | Role |
|------|------|
| `mm-problem-analyst` | Problem analysis: decompose questions, find constraints & traps |
| `mm-modeler` | Method selection: ML/DL decisions, chart planning |
| `mm-data-hunter` | Data: search Wikipedia/GitHub/Kaggle/sklearn |
| `mm-coder` | Implementation: Python solving + visualization |
| `mm-writer` | Writing: fill LaTeX template, address review feedback |
| `mm-reviewer` | Review: 5-dimension scoring, find weaknesses |
| `mm-verifier` | Verification: cross-check numbers, units, boundary conditions |
| `mm-reasoner` | Reasoning: audit formula derivations, fill proof gaps |

## Adversarial Review

Three reviewer roles evaluate the same paper in parallel — Reviewer (modeling quality), Verifier (numerical accuracy), Reasoner (mathematical rigor). The Writer addresses each issue, then all three re-score. Loop continues until average score ≥ 7.5 or max 4 rounds.

## Quality Gates (v2.2)

9 independent Subagent QA gates + anti-pattern hard blocks + human-in-the-loop checkpoints ensuring output quality at every stage.

---

## Project Structure

```
math_model/
├── README.md
├── samples/                      # Full example projects
│   ├── 2024_CUMCM_A/             # CUMCM Problem A
│   └── 2025_HiMCM_Problem_B/     # HiMCM Problem B
└── skill/                        # Skill installation package
    ├── SKILL.md                  # Main skill definition
    ├── references/               # 15 manuals + 6 cookbooks
    ├── scripts/                  # Helper scripts
    ├── templates/                # LaTeX templates (CN/EN)
    └── workflows/                # Review workflows
```

---

## Sample Projects

### 2024 CUMCM A — Dragon Bench Motion

Model the motion trajectory of 223 bench sections along an Archimedean spiral, detect collisions, and optimize turnaround paths. Techniques: chord-length constrained binary search, SAT collision detection, constrained nonlinear optimization.

### 2025 HiMCM B — Super Bowl Sustainable Host City Selection

Build an environmental-only site selection model for NFL, evaluate 19 historical + 3 candidate cities, extend to Olympics. Techniques: AHP + TOPSIS two-tier decision making, Scope 1/2/3 carbon emission analysis, sensitivity analysis.

---

## Changelog

### v2.2.0 — Deep Fix (current)
- **Bug fix**: scoring aggregation upgraded from simple average to role×dimension weighted matrix + hard caps + outlier arbitration
- **Anti-pattern hard blocks (A1/A2/A3)**: code/writing/full-dimension anti-pattern scans, High hits must be fixed
- **Data quality gate (D1)**: missing values + outliers + multi-source alignment checks at stage 3
- **Human-in-the-loop checkpoints**: pause after stages 1/4/6 for user confirmation
- Gates expanded from 5 to 9

### v2.1.0 — Knowledge Embedding + Literature Review
- 8 agent definitions fully upgraded (thin→thick), embedding domain knowledge
- New stage 1.5: literature review (required for national first prize)
- Enhanced innovation validation: ablation studies + 3 baseline comparisons + multi-scenario validation

### v2.0.0 — Architecture Upgrade
- Independent Subagent QA protocol (5 gates)
- Cross-stage state management
- Reference manuals major upgrade (6 manuals, 3-13x length growth)

### v1.2 — Initial Release
- 7-stage mandatory pipeline + 8 sub-agents + 3-role adversarial review

---

## License

MIT
