# 数学建模多智能体论文生成系统

[![Stars](https://img.shields.io/github/stars/Linference/math_model?style=social)](https://github.com/Linference/math_model/stargazers)
[![Forks](https://img.shields.io/github/forks/Linference/math_model?style=social)](https://github.com/Linference/math_model/network/members)
[![Version](https://img.shields.io/badge/version-v2.2-6f42c1)](https://github.com/Linference/math_model/blob/main/skill/CHANGELOG.md)
[![Release](https://img.shields.io/github/v/release/Linference/math_model)](https://github.com/Linference/math_model/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![LaTeX](https://img.shields.io/badge/LaTeX-xelatex-008080?logo=latex)
![Claude Code](https://img.shields.io/badge/Claude_Code-v2.2-D97757?logo=claude)
![竞赛](https://img.shields.io/badge/CUMCM_|_MCM_|_HiMCM-e74c3c)
![Subagent](https://img.shields.io/badge/质检-9_Gates-2ecc71)

---

<div align="center">

### 🌐 语言 | Language | 言語 | 언어

**默认显示中文 · Click to switch language**

</div>

---

<details open>
<summary><b>🇨🇳 中文</b>（默认）</summary>

**v2.2** — 多智能体对抗协作 + Subagent 独立质检（9 道门禁）+ 反模式硬阻断 + 人工在环检查点 + 跨阶段状态管理。21 本参考手册、6 本算法 Cookbook、中英句式库、反模式知识库、环境自检脚本。

把赛题 PDF 丢进去，自动走完审题 → 选方法 → 联网找数据 → Python 求解 → 可视化 → LaTeX 论文编译 → 三角色并行对抗审稿 → 终版 PDF。国赛 CUMCM / 美赛 MCM / HiMCM 全支持。

---

## Star History

[查看 Star 趋势图](https://star-history.com/#Linference/math_model&Date)

---

## 环境搭建（国内用户）

Claude Code 的 API 在国内无法直连，需要用 CCSwitch 转发到 DeepSeek。下面是每一步的详细操作。

### 第一步：安装 Node.js

Claude Code 和 CCSwitch 都依赖 Node.js。如果你不确定装没装，打开终端（Win+R → 输入 `cmd` → 回车），输入 `node --version`，如果显示版本号且 ≥ v18 就跳过这一步。

**Windows：**

1. 打开 [nodejs.org/zh-cn](https://nodejs.org/zh-cn/)
2. 点左边绿色的 **LTS** 按钮下载（标题类似 "v20.x.x 长期支持"）
3. 双击 `.msi` 文件安装，一路点 Next 即可（所有选项保持默认）
4. 装完后关闭终端重新打开，输入 `node --version` 验证

**macOS：**

```bash
# 先装 Homebrew（如果没有）：去 https://brew.sh 复制安装命令
brew install node
```

**Linux（Ubuntu/Debian）：**

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

验证安装成功：

```bash
node --version   # 应显示 ≥ v18.0.0
npm --version    # 应显示 ≥ 9.0.0
```

---

### 第二步：装 Claude Code

打开终端，输入：

```bash
npm install -g @anthropic-ai/claude-code
```

装完后验证：

```bash
claude --version
```

> 如果装了 VSCode，也可以在扩展商店搜 `Claude Code` 安装图形界面版。安装后在 VSCode 设置里搜 `claude` 填 API Key。

---

### 第三步：装 CCSwitch，接入 DeepSeek

CCSwitch 让 Claude Code 的请求走到 DeepSeek 而非 Anthropic，国内就能用。

1. 打开 [ccswitch.io](https://ccswitch.io) → 点 Download
   - Windows：下载 `.msi` 安装包
   - macOS：下载 `.dmg`，或用 `brew install --cask cc-switch`
   - Linux：下载 `.deb` / `.rpm` / `.AppImage`
2. 安装后打开 CCSwitch，点左侧「提供商」→「添加」，按以下填写：

   | 配置项 | 填什么 |
   |--------|--------|
   | 提供商类型 | 选择 **DeepSeek** |
   | API Key | 去 [platform.deepseek.com](https://platform.deepseek.com/) 注册 → API Keys → 创建 Key → 复制过来 |
   | 模型 | 选 `deepseek-chat`（日常）或 `deepseek-reasoner`（推理更强） |
   | Base URL | 保持默认 `https://api.deepseek.com` |

   填完点「测试连接」，提示成功即可。

3. 回到主界面，把刚添加的 DeepSeek 设为**默认后端**，点「启动代理」。状态栏显示绿色连接即表示生效。

> CCSwitch 完全免费，只从 [ccswitch.io](https://ccswitch.io) 或 [GitHub](https://github.com/farion1231/cc-switch) 下载。任何收钱的都是假的。

---

### 第四步：安装本项目 Skills

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

没有 Git 的话，去 [Releases](https://github.com/Linference/math_model/releases) 下载 `skill-v3.1.zip`，手动解压到 `C:\Users\你的用户名\.claude\skills\math-modeling\`（Windows）或 `~/.claude/skills/math-modeling/`（macOS/Linux）。

---

### 第五步：跑起来

打开终端，输入 `claude` 启动，然后输入：

```
/math-modeling
[粘贴赛题原文，或拖入 PDF 文件]
```

系统会自动按阶段执行：审题 → 选方法 → 找数据 → 写代码 → 画图 → 写论文 → 编译 PDF → 对抗审稿。

---

### 如果实在不想折腾

直接把 `skill/SKILL.md` 的内容复制粘贴到 [DeepSeek 网页版](https://chat.deepseek.com) 的对话框里当系统提示词，然后把赛题贴进去，手动一步步让 AI 帮你做。麻烦一点，但也能用。

---

## 项目结构

```
math_model/
├── README.md
├── samples/                      # 完整示例
│   ├── 2024_CUMCM_A/             # 国赛A题：板凳龙
│   └── 2025_HiMCM_Problem_B/     # HiMCM B题：超级碗选址
└── skill/                        # Skills 安装包
    ├── SKILL.md                  # 主技能定义
    ├── references/               # 15本参考手册 + 6本Cookbook
    ├── scripts/                  # 辅助脚本
    ├── templates/                # LaTeX模板（中英双版）
    └── workflows/                # 审稿工作流
```

---

## 7 阶段流水线

| 阶段 | 做什么 | 产出 |
|:--:|--------|------|
| 0 | 建项目目录 | 标准骨架 |
| 1 | 逐问拆解题意，挖约束和陷阱 | 审题报告 |
| 2 | 给每问选建模方法 | 建模方案 + 图表清单 |
| 3 | 联网搜数据，落盘 CSV | 数据文件 + 来源记录 |
| 4 | Python 实现求解 | 可运行脚本 + 数值结果 |
| 5 | 画图（16种类型） | 高质量图表 |
| 6 | 填充 LaTeX 模板，编译 PDF | 论文初稿 |
| 7 | 3 角色并行审稿，写作者修改 | 终稿 PDF |

## 8 个子智能体

| 角色 | 干什么 |
|------|--------|
| `mm-problem-analyst` | 审题：逐问拆解，挖约束、评分点、陷阱 |
| `mm-modeler` | 方法选型：要不要 ML/DL，列图表清单 |
| `mm-data-hunter` | 数据：搜维基/GitHub/Kaggle/sklearn，记录来源 |
| `mm-coder` | 求解：Python 实现，跑通，出图 |
| `mm-writer` | 写作：填 LaTeX，回应审稿意见，补实验 |
| `mm-reviewer` | 审稿：五维度打分，找弱点 |
| `mm-verifier` | 验证：交叉核对数值、量纲、边界 |
| `mm-reasoner` | 推理：审计公式推导，补未证断言 |

## 对抗审稿

三个评审角色并行批改同一份论文——审稿人看建模合理性，验证者核对数值，推理者审计公式。写作者逐条修改后三评审重新打分，均分不到 7.5 继续改，最多 4 轮。

## 质量门禁（v2.2）

9 道 Subagent 独立质检门禁 + 反模式硬阻断 + 人工在环检查点，确保流水线每个环节的输出质量。

---

## 推荐 VSCode 扩展

```bash
# Markdown
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension yzhang.markdown-all-in-one

# LaTeX
code --install-extension james-yu.latex-workshop

# 表格/文档预览
code --install-extension grapecity.gc-excelviewer
code --install-extension mechatroner.rainbow-csv
code --install-extension tomoki1207.pdf
code --install-extension cweijan.vscode-office

# 效率
code --install-extension eamodio.gitlens
```

---

## 两个示例

### 2024 国赛 A 题 — 板凳龙闹元宵

223 节板凳沿阿基米德螺线盘入/调头/盘出。建模每节运动轨迹、检测碰撞、优化调头路径。

技术点：弦长约束二分搜索、SAT 碰撞检测、带约束非线性优化。

### 2025 HiMCM B 题 — 超级碗可持续选址

为 NFL 建立纯环境因素选址模型，评估 19 个历史城市 + 3 个候选城市，扩展到奥运会。

技术点：AHP + TOPSIS 双层决策、Scope 1/2/3 碳排放分析、敏感性分析。

---

## 安装

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

或去 [Releases](https://github.com/Linference/math_model/releases) 下载 ZIP，解压到同一目录。

---

## License

MIT

---

## 项目更新历程

### v2.2.0 — 深度剖析修复（当前版本）

- **Bug 修复**：评分聚合从简单平均改为角色×维度加权矩阵 + 硬上限规则 + 离群值仲裁
- **反模式硬阻断 (A1/A2/A3)**：代码/写作/全维度三道反模式扫描，High 命中必须退回
- **数据质量独立质检 (D1)**：阶段 3 新增缺失值+异常值+多源对齐门禁
- **人工在环检查点**：阶段 1/4/6 后暂停，将关键产物呈现给用户确认
- 门禁体系从 5 道扩展为 9 道

### v2.1.0 (2026-07-28) — 知识嵌入 + 文献综述

- 8 个 Agent 定义全面升级（薄→厚），嵌入领域知识
- 新增阶段 1.5 文献综述（国一必备）
- 增强创新验证：消融实验 + 3 基线对比 + 多场景验证

### v2.0.0 (2026-07-28) — 架构升级

- 新增 Subagent 独立质检协议（5 道门禁）
- 新增跨阶段状态管理
- 参考手册全面升级（6 本，3-13 倍行数增长）
- 新增 8 个文件（反模式手册、句式库、Cookbook、环境自检等）

### v1.2 (2026-07-27) — 初始版本

- 7 阶段强制流水线 + 8 个子智能体 + 三角色对抗审稿

</details>

<details>
<summary><b>🇺🇸 English</b></summary>

**v2.2** — Multi-agent adversarial collaboration + 9 independent QA gates + anti-pattern hard blocks + human-in-the-loop checkpoints + cross-stage state management. 21 reference manuals, 6 algorithm cookbooks, bilingual phrase bank, anti-pattern knowledge base, environment doctor script.

Drop in a contest problem PDF, and the system automatically runs through: problem analysis → method selection → web data hunting → Python solving → visualization → LaTeX paper compilation → 3-role parallel adversarial review → final PDF. Supports CUMCM (China), MCM/ICM (USA), and HiMCM.

---

## Quick Start

### Prerequisites

- **Node.js** ≥ v18 ([nodejs.org](https://nodejs.org/))
- **Claude Code**: `npm install -g @anthropic-ai/claude-code`
- (China users) **CCSwitch**: [ccswitch.io](https://ccswitch.io) — routes Claude Code API calls through DeepSeek

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

## License

MIT

</details>

<details>
<summary><b>🇯🇵 日本語</b></summary>

**v2.2** — マルチエージェント敵対的協調 + 9つの独立QAゲート + アンチパターンハードブロック + ヒューマンインザループチェックポイント + クロスステージ状態管理。21冊のリファレンスマニュアル、6冊のアルゴリズムクックブック、日中英フレーズバンク、アンチパターン知識ベース、環境診断スクリプト。

コンテスト問題のPDFを投入するだけで、問題分析 → 手法選択 → Webデータ収集 → Python求解 → 可視化 → LaTeX論文コンパイル → 3役割並列敵対的レビュー → 最終PDFまでを自動実行。CUMCM（中国）、MCM/ICM（米国）、HiMCMに対応。

---

## クイックスタート

### 前提条件

- **Node.js** ≥ v18 ([nodejs.org](https://nodejs.org/))
- **Claude Code**: `npm install -g @anthropic-ai/claude-code`

### インストール

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

または [Releases](https://github.com/Linference/math_model/releases) からZIPをダウンロード。

### 実行

```bash
claude
/math-modeling
[コンテスト問題を貼り付け、またはPDFをドラッグ]
```

---

## 7段階パイプライン

| 段階 | タスク | 成果物 |
|:--:|------|------|
| 0 | プロジェクト足場 | 標準ディレクトリ構造 |
| 1 | 詳細な問題分析 | 構造化分析レポート（2000字以上） |
| 2 | 手法選択 + ML/DL判断 | モデリング計画 + 図表チェックリスト |
| 3 | Webデータ収集 | CSVファイル + SOURCES.md |
| 4 | Python実装 | 実行可能スクリプト + 数値結果 |
| 5 | 可視化（16種類の図表） | 高品質図表（300 DPI） |
| 6 | LaTeX執筆 + コンパイル | 論文草稿 |
| 7 | 3役割敵対的レビュー | 最終PDF（スコア ≥ 7.5/10） |

## 8つのサブエージェント

| エージェント | 役割 |
|------|------|
| `mm-problem-analyst` | 問題分析：設問分解、制約・罠の発見 |
| `mm-modeler` | 手法選択：ML/DL判断、図表計画 |
| `mm-data-hunter` | データ：Wikipedia/GitHub/Kaggle/sklearn検索 |
| `mm-coder` | 実装：Python求解 + 可視化 |
| `mm-writer` | 執筆：LaTeXテンプレート記入、レビュー対応 |
| `mm-reviewer` | レビュー：5次元採点、弱点発見 |
| `mm-verifier` | 検証：数値・単位・境界条件クロスチェック |
| `mm-reasoner` | 推論：数式導出監査、証明ギャップ補完 |

## 敵対的レビュー

3つのレビュアー役割が同じ論文を並列評価 — レビュアー（モデリング品質）、検証者（数値正確性）、推論者（数学的厳密性）。ライターが各指摘に対応し、3者が再採点。平均スコア ≥ 7.5または最大4ラウンドまで繰り返し。

## 品質ゲート（v2.2）

9つの独立Subagent QAゲート + アンチパターンハードブロック + ヒューマンインザループチェックポイントにより、各段階の出力品質を確保。

---

## プロジェクト構成

```
math_model/
├── README.md
├── samples/                      # 完全なサンプルプロジェクト
│   ├── 2024_CUMCM_A/             # CUMCM 問題A
│   └── 2025_HiMCM_Problem_B/     # HiMCM 問題B
└── skill/                        # スキルインストールパッケージ
    ├── SKILL.md                  # メインスキル定義
    ├── references/               # 15冊マニュアル + 6冊クックブック
    ├── scripts/                  # ヘルパースクリプト
    ├── templates/                # LaTeXテンプレート（中/英）
    └── workflows/                # レビューワークフロー
```

---

## ライセンス

MIT

</details>

<details>
<summary><b>🇰🇷 한국어</b></summary>

**v2.2** — 다중 에이전트 적대적 협업 + 9개 독립 QA 게이트 + 안티패턴 하드 블록 + 휴먼인더루프 체크포인트 + 교차 단계 상태 관리. 21권의 참조 매뉴얼, 6권의 알고리즘 쿡북, 중영일 구문 은행, 안티패턴 지식 베이스, 환경 진단 스크립트.

대회 문제 PDF를 넣으면 문제 분석 → 방법 선택 → 웹 데이터 수집 → Python 해결 → 시각화 → LaTeX 논문 컴파일 → 3역할 병렬 적대적 검토 → 최종 PDF까지 자동 실행. CUMCM(중국), MCM/ICM(미국), HiMCM을 지원합니다.

---

## 빠른 시작

### 사전 요구사항

- **Node.js** ≥ v18 ([nodejs.org](https://nodejs.org/))
- **Claude Code**: `npm install -g @anthropic-ai/claude-code`

### 설치

```bash
git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling
```

또는 [Releases](https://github.com/Linference/math_model/releases)에서 ZIP 다운로드.

### 실행

```bash
claude
/math-modeling
[대회 문제 붙여넣기 또는 PDF 드래그]
```

---

## 7단계 파이프라인

| 단계 | 작업 | 산출물 |
|:--:|------|------|
| 0 | 프로젝트 스캐폴딩 | 표준 디렉토리 구조 |
| 1 | 심층 문제 분석 | 구조화된 분석 보고서 (2000자 이상) |
| 2 | 방법 선택 + ML/DL 결정 | 모델링 계획 + 차트 체크리스트 |
| 3 | 웹 데이터 수집 | CSV 파일 + SOURCES.md |
| 4 | Python 구현 | 실행 가능한 스크립트 + 수치 결과 |
| 5 | 시각화 (16가지 차트 유형) | 고품질 그림 (300 DPI) |
| 6 | LaTeX 작성 + 컴파일 | 논문 초안 |
| 7 | 3역할 적대적 검토 | 최종 PDF (점수 ≥ 7.5/10) |

## 8개 서브 에이전트

| 에이전트 | 역할 |
|------|------|
| `mm-problem-analyst` | 문제 분석: 질문 분해, 제약 조건 및 함정 발견 |
| `mm-modeler` | 방법 선택: ML/DL 결정, 차트 계획 |
| `mm-data-hunter` | 데이터: Wikipedia/GitHub/Kaggle/sklearn 검색 |
| `mm-coder` | 구현: Python 해결 + 시각화 |
| `mm-writer` | 작성: LaTeX 템플릿 작성, 검토 의견 반영 |
| `mm-reviewer` | 검토: 5차원 채점, 약점 발견 |
| `mm-verifier` | 검증: 수치, 단위, 경계 조건 교차 확인 |
| `mm-reasoner` | 추론: 공식 유도 감사, 증명 간격 보완 |

## 적대적 검토

세 명의 검토자 역할이 동일한 논문을 병렬 평가 — 검토자(모델링 품질), 검증자(수치 정확성), 추론자(수학적 엄격성). 작성자가 각 지적사항을 수정하고 세 명이 재채점. 평균 점수 ≥ 7.5 또는 최대 4라운드까지 반복.

## 품질 게이트 (v2.2)

9개 독립 Subagent QA 게이트 + 안티패턴 하드 블록 + 휴먼인더루프 체크포인트로 각 단계의 출력 품질을 보장합니다.

---

## 프로젝트 구조

```
math_model/
├── README.md
├── samples/                      # 완전한 예제 프로젝트
│   ├── 2024_CUMCM_A/             # CUMCM 문제 A
│   └── 2025_HiMCM_Problem_B/     # HiMCM 문제 B
└── skill/                        # 스킬 설치 패키지
    ├── SKILL.md                  # 메인 스킬 정의
    ├── references/               # 15개 매뉴얼 + 6개 쿡북
    ├── scripts/                  # 헬퍼 스크립트
    ├── templates/                # LaTeX 템플릿 (중/영)
    └── workflows/                # 검토 워크플로우
```

---

## 라이선스

MIT

</details>
