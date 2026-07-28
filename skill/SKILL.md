---
name: math-modeling
description: 端到端数学建模竞赛论文生成系统（国赛 CUMCM 中文 / 美赛 MCM 英文）。v2.0 新增 Subagent 独立质检协议、跨阶段状态管理、反模式知识库、中英句式库、环境自检脚本。多智能体对抗协作：深度审题→建模框架与方法选型(含是否用ML/DL)→联网找数据(维基/GitHub/Kaggle/官方统计/sklearn)→编程求解与可视化→LaTeX写作→编译PDF→写作者/审稿人/验证者/推理者多轮对抗审稿(评分5.0→7.5)，产出国赛级别论文。当用户给出一道数学建模赛题、或说"数学建模""建模论文""国赛/美赛论文""/math-modeling"时使用。
---

# 数学建模多智能体系统 v2.0

把一道赛题，经 7 个阶段、多智能体对抗协作 + 独立质检，产出可编译为 PDF 的国赛级别论文。

## 版本

- **当前版本**: v2.0.0
- **更新日志**: `<skill>/CHANGELOG.md`
- **环境自检**: `python <skill>/scripts/doctor.py`

## 环境（本机 Windows，已验证）
- 编译：`xelatex`(MiKTeX) + `ctex`/`xeCJK`，中文字体 SimHei/SimSun → 中文 PDF 可编。
- Python：anaconda `python`（numpy/pandas/scipy/sklearn/matplotlib 全就绪）。命令行显式用 `python`。
- 联网：内置 WebSearch / WebFetch。
- Skill 根目录：`C:/Users/HUAWEI/.claude/skills/math-modeling/`（下称 `<skill>`）。

## 路径解析协议

| 类型 | 位置 | 示例 |
|------|------|------|
| skill 内通用 | `<skill>/` 下的相对路径 | `references/02-framework.md` |
| 用户产物 | 用户工作目录的相对路径 | `<cwd>/REPORT.md`, `<cwd>/code/`, `<cwd>/paper/` |
| 状态持久化 | `<cwd>/state/decision_log.json` | 每阶段必读必写 |
| Python 脚本 | `<skill>/scripts/` | 使用绝对路径调用 |

开工时，先运行 `python <skill>/scripts/doctor.py` 验证环境完整性。

## 何时用哪种执行方式
- **子智能体**（`Agent` 工具，agentType 见下）：单阶段专项工作。
- **对抗审稿**：用 `Workflow` 跑 `<skill>/workflows/adversarial-review.js`（真实多智能体并行对抗，≤4 轮）。
- **独立质检 Subagent**：关键节点（M1/P1/P2/W1/W2）派发只读质检，详见下方 Subagent 质检协议。
- 只有当用户明确要"多智能体/工作流/对抗"或说了触发词时才启动 Workflow（它会开多个子智能体，耗 token）。

---

## Subagent 质检协议（v2.0 新增）

**角色分离原则**：写代码/写论文的 Agent 不能同时质检自己的产出。质检 Subagent 必须是独立的只读实例。

### 五道门禁

| 门禁 | 触发阶段 | 被审产物 | 质检 Subagent | 通过标准 |
|:--:|:--:|------|------|------|
| **M1** | 阶段 1 后 | `REPORT.md` §1 审题报告 | `mm-verifier` | 审题完整性 6 项全部通过 |
| **P1** | 阶段 4 前（算法设计后） | 算法设计文档 | `mm-reasoner` | 算法正确性论证无漏洞 |
| **P2** | 阶段 4 后 | code/*.py + 运行结果 | `mm-verifier` | 代码可运行 + 输出可追溯 + 公式一致 |
| **W1** | 阶段 6 前（写作规划后） | 论文大纲 + 证据映射 | `mm-verifier` | 每个主张有对应代码输出支撑 |
| **W2** | 阶段 7 前 | 完整论文 PDF | `mm-reviewer` | 五维度评分 ≥ 6.0 |

### 质检规则

1. **派发时机**：M1 在阶段 1 落盘后立即派发；P1 在阶段 4 编码前派发；P2 在阶段 4 编码后派发；W1 在阶段 6 写作规划后派发；W2 在阶段 6 编译成功后派发。
2. **只读质检**：Subagent 只能读取产物、返回评估报告，**不得修改文件**。
3. **FAIL 回溯**：任一门禁 FAIL → 退回对应阶段按证据修正 → 重新派发复验。已通过的后续门禁在相关产物变化后自动失效。
4. **PASS 签名**：PASS 结果含 Subagent ID + 时间戳 + 检查摘要，写入 REPORT.md。
5. **不可跳过**：主 Agent 自检不能替代 Subagent 独立验收。环境不支持 Subagent 时记为 BLOCKED，不得谎称通过。

---

## ⛔ 强制流程门禁（不允许跳步）

**这是硬性约束，优先级高于一切效率考量。必须严格按阶段 0→1→2→3→4→5→6→7 顺序执行，禁止跳过、合并、颠倒任何阶段。**

### 核心规则

1. **每个阶段三步骤**：执行 → 验证 → 确认。验证不通过不得进入下一阶段。
2. **落盘即证据**：每个阶段的产出必须写入对应文件，产出不存在 = 该阶段未完成。
3. **状态持久化**：每阶段开始前读取 `state/decision_log.json`，完成后写入决策记录。状态文件让流水线可在中断后恢复。
4. **禁止心算跳过**：不允许因为"这题简单""数据不用找""图随便画"而略过任何阶段。
5. **阶段门禁清单**：开工时 `TaskCreate` 建 8 个任务（阶段 0–7），每进入一个阶段 `TaskUpdate` 设为 in_progress，验证通过后才设 completed。任何时刻只允许一个阶段是 in_progress。
6. **审题结论贯穿全流程**：阶段 1 的审题报告是后续所有阶段的"宪法"——阶段 2 选型必须引用审题结论，阶段 4 求解必须回应审题中的约束，阶段 6 写作必须覆盖审题中的每问和隐性要求。
7. **可视化是必经阶段**：阶段 5 必须为每个模型至少产出 1 张图到 `figures/`，且阶段 6 的论文里每张图都要被正文引用并解读。
8. **对抗审稿不可省**：阶段 7 是核心创新，除非用户明确说"不要审稿"，否则必须跑。
9. **Subagent 质检不可省**：M1/P1/P2/W1/W2 五道门禁必须逐道通过。
10. **反模式意识**：每个阶段决策前，查阅 `references/11-anti-patterns.md` 确认规避已知错误。

### 阶段依赖链

```
0 目录 → 1 审题报告 [M1质检] → 2 建模方案表
  → 3 data/*.csv+SOURCES → 4 [P1算法审计] → code/solve_qN.py+结果 [P2质检]
  → 5 figures/*.png → 6 [W1证据大纲] → main.pdf [W2质检]
  → 7 评分记录+终版PDF
```

### 每阶段验证门禁

**每个阶段完成后，必须执行以下验证步骤，验证不通过则退回该阶段重做。**

#### 阶段 1 验证：审题完整性

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| 每小问逐一拆解 | 核对 `problem.md` 问数与 REPORT.md §1 拆解数一致 | 补拆缺失小问 |
| 隐性约束全部识别 | 逐条列出：数据来源约束、假设边界、输出格式要求 | 补识别遗漏约束 |
| 评分点与陷阱标注 | 每条陷阱必须有"如果踩了会怎样"的具体后果 | 补陷阱分析 |
| **问题类型判定** | 判定题目类型（优化/评价/预测/机理/混合），存入 REPORT.md §1.7 | 类型判定错误会导致后续方法选偏 |
| 审题报告 ≥ 2000 字 | 检查 REPORT.md §1 字数 | 展开细节，不可浓缩 |
| **审题结论可被后续阶段引用** | 检查 §1.7 问题类型判定是否明确，§1.2 逐问拆解是否每问独立可引用 | 补全 §1.7 或 §1.2 |

**M1 独立质检**：阶段 1 验证通过后，立即派发 `mm-verifier` Subagent 执行 M1 质检。

#### 阶段 2 验证：方法选型合理性

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| 每问有对应方法 | 核对问数 = 方案表行数 | 补遗漏问题 |
| ML/DL 决策有理由 | 每行必须有具体理由（非"不需要"三个字） | 补理由 |
| 方法匹配问题类型 | 对照 §1.7 的问题类型，检查方法是否偏离 | 如优化题选了纯评价方法→重选 |
| 图表清单完整 | 每行至少 2 张图 | 补图 |
| 验证方式可行 | 每行验证列不是"分析"等空话 | 补具体验证方案 |
| 反模式检查 | 对照 `11-anti-patterns.md` 自查 | 修正反模式 |

#### 阶段 3 验证：数据质量

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| CSV 可读且非空 | `python -c "import pandas as pd; df=pd.read_csv(...); print(df.shape)"` | 重新获取 |
| SOURCES.md 记录来源 | 每个 CSV 文件至少一条来源记录，含 URL | 补来源 |
| 数据量 ≥ 建模需求 | 样本数 ≥ 指标数 × 3（基本统计要求） | 补充数据或标注限制 |
| 模拟数据已标注 | 若数据为生成/模拟，须在 SOURCES.md 显式标注"模拟" | 补标注 |

#### 阶段 4 验证：算法正确性（⛔ 最关键门禁）

**P1 算法审计**（编码前）：派发 `mm-reasoner` Subagent 审计算法设计文档。

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| **代码可运行** | 终端执行 `python code/solve_qN.py`，确认无报错 | 修 bug |
| **输出有具体数值** | 检查结果文件含具体数字（非占位符） | 确保真实跑通 |
| **边界条件测试** | 极端参数（0、极大值、负值）跑一次不崩溃 | 加固代码 |
| **量纲一致性** | 所有输出数字带单位，且单位体系统一 | 统一单位 |
| **公式一致性审计** | 对照阶段 2 方案表公式，检查代码实现变量名/参数/正负号一致 | 修正不一致 |
| **随机种子固定** | 所有随机代码含 `np.random.seed(N)` | 补种子 |
| **关键数字可追溯** | 论文中引用的每个关键数字须在代码输出中有对应来源 | 确保数字有出处 |

**P2 独立质检**：阶段 4 验证通过后，派发 `mm-verifier` Subagent 执行，运行 `verify_results.py`。

#### 阶段 5 验证：图表覆盖

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| 每模型 ≥ 1 张图 | 统计 `figures/` 下 PNG 数 ≥ 模型数 | 补图 |
| 每图 300dpi | 抽查 1-2 张图属性 | 重出 |
| 每图有解读文案 | 检查 REPORT.md §5 每张图有解读 | 补解读 |
| 图表配色规范 | 对照 `05-visualization.md` 配色方案 | 调整配色 |
| 避免可视化反模式 | 对照 `11-anti-patterns.md` 自查 | 修正 |

#### 阶段 6 验证：论文质量

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| **页面约束（摘要 1 页）** | 打开 PDF 检查 | 压缩 |
| **页面约束（目录 1 页）** | 打开 PDF 检查 | 调 tocdepth |
| **无大空白/溢出** | 逐页翻 PDF | 修浮动体 |
| **每图被 \ref 引用** | 搜索 `\ref{fig:` 次数 vs PNG 数量 | 补引用 |
| **摘要含量化数字** | 摘要中数字出现次数 ≥ 4 个 | 补量化结论 |
| **四项深度要求** | 逐项核对 | 补内容 |
| **代码输出与论文数字交叉验证** | `python <skill>/scripts/verify_results.py <slug>` | 修正不一致 |
| **写作反模式检查** | 对照 `11-anti-patterns.md` + `13-phrase-bank.md` | 修正表述 |

**W1 证据大纲质检**：写作规划后派发 `mm-verifier` Subagent。
**W2 论文终检**：编译后派发 `mm-reviewer` Subagent。

#### 阶段 7 验证：审稿闭环

| 验证项 | 方法 | 不通过处理 |
|---|---|---|
| 每轮评分记录在案 | 检查 REPORT.md §7 有评分表 | 补记录 |
| 终版 PDF 已编译 | `paper/main.pdf` 更新时间 > 审稿开始时间 | 重新编译 |
| 版本 PDF 齐全 | `paper/versions/` 含基线+每轮+终版 | 补编译 |
| High 级别弱点清零或降级 | 终版残留 high 弱点 ≤ 1 个 | 继续修改 |
| 最终均分 ≥ 7.5 | 检查最后一轮评分 | 继续直到达标或满4轮 |

---

## 可用子智能体（已装于 ~/.claude/agents）
| agentType | 角色 | 阶段 | 也可用于质检 |
|---|---|---|---|
| mm-problem-analyst | 审题 | 1 | — |
| mm-modeler | 方法选型(含ML/DL决策) | 2 | — |
| mm-data-hunter | 联网找数据 | 3 | — |
| mm-coder | 编程求解+可视化 | 4-5 | — |
| mm-writer | 论文写作/修改 | 6,7 | — |
| mm-reviewer | 批判审稿 | 7 | W2 |
| mm-verifier | 交叉验证 | 4,5,6,7 | M1, P2, W1 |
| mm-reasoner | 数学推理/证明 | 2,4,7 | P1 |

## 参考手册速查

| 文件 | 内容 | 何时读 |
|------|------|--------|
| `references/01-problem-analysis.md` | 审题方法论 | 阶段 1 |
| `references/02-framework.md` | 方法选型框架（决策树+对比矩阵） | 阶段 2 |
| `references/03-data-acquisition.md` | 数据获取策略与质量检查 | 阶段 3 |
| `references/04-modeling-cookbook.md` | 算法手册 | 阶段 2,4 |
| `references/05-visualization.md` | 图表决策树+配色方案+代码骨架 | 阶段 5 |
| `references/06-writing.md` | LaTeX 写作标准 | 阶段 6 |
| `references/07-adversarial-review.md` | 三角色对抗审稿协议+评分锚点 | 阶段 7 |
| `references/08-stage-verification.md` | 阶段验证门禁详情 | 每阶段 |
| `references/09-innovation-playbook.md` | 12 种创新策略选型指南 | 阶段 2 |
| `references/10-modeling-tricks.md` | 数学建模 33 讲优化技巧 | 阶段 2,4 |
| `references/11-anti-patterns.md` | 建模常见错误清单（症状→诊断→修复） | 每阶段 |
| `references/13-phrase-bank.md` | 中英双语句式库（按章节组织） | 阶段 6 |
| `references/12-data-sources.md` | 分类数据源大全（URL+API） | 阶段 3 |
| `references/15-scoring-rubric.md` | 五维度评分细则（0-10 锚定） | 阶段 7 |
| `references/14-playbook-guide.md` | Playbook 使用与创建指南 | 参考 |
| `references/cookbooks/` | 6 本独立算法手册（优化/评价/预测/机理/统计ML/网络博弈） | 阶段 2,4 |

---

## 执行流程（7 阶段，含验证 + 独立质检）

### 阶段 0 — 建立工作目录
先问/推断赛制语言：国赛→`zh`，美赛→`en`。然后：
```bash
python <skill>/scripts/new_project.py "<赛题名>" --lang zh   # 或 en
```
把赛题原文粘进 `<slug>/problem.md`。初始化 `state/decision_log.json`。之后所有产物落在该工作目录。
用 `TaskCreate` 建立阶段 0–7 共 8 个门禁任务。

> ✅ 门禁：工作目录+8 个任务已建、`state/decision_log.json` 已初始化、`problem.md` 已填。

---

### 阶段 1 — 深度审题（决定一切的方向盘）

用 `Agent`（agentType=`mm-problem-analyst`）读 `problem.md`，产出结构化审题报告。

**⛔ 审题深度要求：**

1. **逐问拆解**（每小问独立一段）：输入/输出/约束/问间依赖（画 ASCII 依赖图）
2. **显性约束清单**：从题目原文逐句提取
3. **隐性约束推导**（最重要！）：现实合理性/数据可获得性/模型可求解/评分标准暗示
4. **数据情况评估**：题目给什么？缺什么？从哪获取？质量风险
5. **评分点与陷阱**：每条标注"如果踩了会怎样"的具体后果和分值影响
6. **问题间依赖关系图**
7. **⛔ 问题类型判定**：优化/评价/预测/机理/混合，含判定依据（≥3条）、策略要点、典型错误

写入 `REPORT.md` §1。审题报告 ≥ **2000 字**。

> ⛔ 验证 → **M1 独立质检**（派发 mm-verifier）→ 进入阶段 2。
> 参考：`01-problem-analysis.md`。

---

### 阶段 2 — 建模框架与方法选型

用 `Agent`（`mm-modeler`）基于 §1.7 问题类型，为每问选方法。

1. **问题类型驱动方法选择**
2. **ML/DL 决策**（每问必判，具体理由）
3. **每问方案表**：方法 | 创新策略 | 输入 | 输出 | ML/DL 理由 | 必备图 | 验证 | 风险
4. **创新策略选型**（从 `09-innovation-playbook.md` 12 种策略选 1-2 种）
5. **算法可行性预审**：复杂度/收敛性/坑点/数据前提
6. **反模式检查**：对照 `11-anti-patterns.md`

写入 `REPORT.md` §2。更新 `state/decision_log.json`。

> 参考：`02-framework.md`、`04-modeling-cookbook.md`、`09-innovation-playbook.md`、`10-modeling-tricks.md`、`11-anti-patterns.md`。

---

### 阶段 3 — 数据获取

三级搜索策略（优先用管线，兜底用 AI）：

```bash
python <skill>/scripts/fetch_data.py --sklearn iris
python <skill>/scripts/fetch_data.py --worldbank EN.ATM.CO2E.KT
python <skill>/scripts/fetch_data.py --search climate energy
python <skill>/scripts/fetch_data.py --url <直链> --name <名>
python <skill>/scripts/fetch_data.py --quality data/cities.csv
```

落盘到 `data/`，来源记入 `SOURCES.md`。

> 参考：`03-data-acquisition.md`、`12-data-sources.md`。

---

### 阶段 4 — 建模求解 + 编程（⛔ 最关键阶段）

用 `Agent`（`mm-coder`）用 anaconda `python` 实现模型。

**P1 算法审计（编码前）**：mm-coder 先输出算法设计文档 → 派发 `mm-reasoner` Subagent 审计。

**编码规范**：每问 `code/solve_qN.py`，固定种子 `np.random.seed(42)`，docstring 注明问题/算法/公式。

**P2 独立质检（编码后）**：派发 `mm-verifier` Subagent，运行 `verify_results.py`。

> P1→编码→P2，P2 通过才进入阶段 5。

---

### 阶段 5 — 可视化

仍由 `mm-coder` 出图到 `figures/`。每个模型 ≥ 1 张图，300dpi PNG，配色用 `05-visualization.md` 方案。出图后写解读文案。

> 参考：`05-visualization.md`、`11-anti-patterns.md`。

---

### 阶段 6 — LaTeX 写作 + 编译

用 `Agent`（`mm-writer`）填充 `paper/main.tex`。

**W1 证据大纲（写作前）**：派发 `mm-verifier` 验证每个论文主张有代码输出支撑。

**四项深度内容**：假设局限性量化 + 对比模型验证（≥2 基准/≥3 指标）+ 创新点声明 + 多指标评估。

写作风格参考 `13-phrase-bank.md`，避 `11-anti-patterns.md` 写作反模式。

```bash
python <skill>/scripts/compile.py paper/main.tex
python <skill>/scripts/verify_results.py <slug> --stage 6
```

**W2 论文终检**：派发 `mm-reviewer` Subagent 五维度评分，≥ 6.0 才进入阶段 7。

> W1→写作→W2，W2 通过才进入阶段 7。

---

### 阶段 7 — 多轮对抗审稿（核心创新）

用 `Workflow` 运行对抗审稿：

```
Workflow({ scriptPath: "<skill>/workflows/adversarial-review.js",
           args: { draftPath: "<slug>/paper/main.tex", lang: "zh",
                   targetScore: 7.5, maxRounds: 4,
                   projectRoot: "<skill>",
                   dataContext: "<关键结果数值摘要>" } })
```

审稿人/验证者/推理者并行打分（五维度 0-10）→ 写作者逐条修改 → 编译版本 PDF → 复评，均分 ≥ 7.5 或满 4 轮停止。

> 参考：`07-adversarial-review.md`、`15-scoring-rubric.md`。

---

## 交付物
- `<slug>/paper/main.pdf` —— 终版论文
- `<slug>/paper/versions/` —— 全部 PDF 版本
- `<slug>/paper/main.tex`、`code/`、`figures/`、`data/`、`REPORT.md`
- `<slug>/state/decision_log.json` —— 跨阶段决策记录
- `<slug>/REPORT.md` 含每阶段验证 + Subagent 质检记录

## 原则
- **稳中求新**：先保基础分，再加创新
- **不造假**：数据/结果/引用真实；模拟数据显著标注
- **可复现**：固定种子、相对路径
- **量化摘要**：摘要必须有具体数字
- **排版即分数**：摘要/目录各一页、无大空白
- **对比即说服力**：每个模型必须有对比基准
- **深度即区分度**：讨论到"放宽→误差X%→结论逆转"粒度
- **版本即安全网**：每次编译留存 PDF
- **⛔ 质检是根基**：M1/P1/P2/W1/W2 逐道通过，主 Agent 自检不是独立验收
- **⛔ 审题是宪法**：阶段 1 结论是后续最高指导
- **⛔ 反模式即防线**：每阶段决策前查阅 `11-anti-patterns.md`
