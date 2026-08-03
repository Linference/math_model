---
name: math-modeling
description: 端到端数学建模竞赛论文生成系统（国赛 CUMCM 中文 / 美赛 MCM 英文）。v2.2：反模式硬阻断门禁(A1/A2/A3)、数据质量独立质检(D1)、人工在环检查点、加权评分聚合+硬上限+仲裁、结构化算法审计、文献综述(阶段1.5)、消融实验国一标准。多智能体对抗协作：深度审题→文献综述→建模框架与方法选型(含是否用ML/DL)→联网找数据(维基/GitHub/Kaggle/官方统计/sklearn)→编程求解与可视化→LaTeX写作→编译PDF→写作者/审稿人/验证者/推理者多轮对抗审稿(评分5.0→7.5)，产出国赛级别论文。当用户给出一道数学建模赛题、或说"数学建模""建模论文""国赛/美赛论文""/math-modeling"时使用。
---

# 数学建模多智能体系统 v2.2

把一道赛题，经 7 个阶段、多智能体对抗协作 + 独立质检，产出可编译为 PDF 的国赛级别论文。

## 版本

- **当前版本**: v2.2.0
- **更新日志**: `<skill>/CHANGELOG.md`
- **环境自检**: `python <skill>/scripts/doctor.py`

## 环境（本机 Windows，已验证）
- 编译：`xelatex`(MiKTeX) + `ctex`/`xeCJK`，中文字体 SimHei/SimSun → 中文 PDF 可编。
- Python：`C:/Users/HUAWEI/AppData/Local/Programs/Python/Python311/python.exe`（numpy/pandas/scipy/sklearn/matplotlib 全就绪）。命令行一律用完整路径调用，勿用系统默认 `python`。
- 联网：内置 WebSearch / WebFetch。
- Skill 根目录：`${SKILL_ROOT}` 环境变量（下称 `<skill>`；未设置时按本 SKILL.md 所在目录）。Python 一律用 `C:/Users/HUAWEI/AppData/Local/Programs/Python/Python311/python.exe`。

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

**角色分离原则**：写代码/写论文的 Agent 不能同时质检自己的产出。质检 Subagent 必须是独立实例。

> ⚠️ **只读说明（best-effort）**：质检 Subagent 通过提示词约束为"只读评估、不修改文件"，实际只读隔离取决于运行时权限模式，**无绝对强制保证**。判定以评估报告为准，不以是否改文件为准。

### 九道门禁（v2.2 从 v2.0 的 5 道扩展）

| 门禁 | 触发阶段 | 被审产物 | 质检 Subagent | 通过标准 |
|:--:|:--:|------|------|------|
| **M1** | 阶段 1 后 | `REPORT.md` §1 审题报告 | `mm-verifier` | 审题完整性 6 项全部通过 |
| **D1** | 阶段 3 后 | `data/*.csv` + `SOURCES.md` | `mm-verifier` | CSV 可读 + 缺失值报告 + 来源可追溯 + 数据量达标 |
| **P1** | 阶段 4 前（算法设计后） | 算法设计文档 | `mm-reasoner` | 算法正确性论证无漏洞 |
| **P2** | 阶段 4 后 | code/*.py + 运行结果 | `mm-verifier` | 代码可运行 + 输出可追溯 + 公式一致 |
| **A1** | 阶段 4 后（P2 通过后） | code/*.py + 建模逻辑 | `mm-verifier` | 反模式扫描 0 个 High 命中（⛔ v2.2 硬阻断） |
| **W1** | 阶段 6 前（写作规划后） | 论文大纲 + 证据映射 | `mm-verifier` | 每个主张有对应代码输出支撑 |
| **A2** | 阶段 6 中（正文写作后） | `paper/main.tex` 正文部分 | `mm-reviewer` | 写作反模式扫描 + 句式库合规（⛔ v2.2 硬阻断） |
| **W2** | 阶段 7 前 | 完整论文 PDF | `mm-reviewer` | 五维度评分 ≥ 6.0 |
| **A3** | 阶段 7 后（审稿完成前） | 终版论文 | `mm-reviewer` | 全维度反模式终扫 0 个 High 命中（⛔ v2.2 硬阻断） |

### 质检规则

1. **派发时机**：M1 在阶段 1 落盘后；D1 在阶段 3 落盘后；P1 在阶段 4 编码前；P2 在阶段 4 编码后；A1 在 P2 通过后；W1 在阶段 6 写作规划后；A2 在阶段 6 正文写作后；W2 在阶段 6 编译成功后；A3 在阶段 7 审稿完成前。
2. **只读质检（best-effort）**：Subagent 应以"只读取、不改写、返回评估报告"为准则；提示词层约束 + 权限模式尽力隔离，但不作为硬性保证。
3. **FAIL 回溯**：任一门禁 FAIL → 退回对应阶段按证据修正 → 重新派发复验。已通过的后续门禁在相关产物变化后自动失效。
4. **PASS 签名**：PASS 结果含 Subagent ID + 时间戳 + 检查摘要，写入 REPORT.md。
5. **不可跳过**：主 Agent 自检不能替代 Subagent 独立验收。环境不支持 Subagent 时记为 BLOCKED，不得谎称通过。
6. **⛔ A1/A2/A3 是硬阻断**：反模式门禁 FAIL（任何 High 命中）→ 必须退回修复，不允许携带 High 反模式进入下一阶段。这与 v2.0 中"查阅反模式"的软性建议有本质区别。

---

## ⛔ 强制流程门禁（允许受控 Fast Path）

**这是硬性约束，优先级高于一切效率考量。默认严格按阶段 0→1→2→3→4→5→6→7 顺序执行。唯一的受控例外是下方"Fast Path"——由复杂度判定触发，且跳过的仅限高开销非核心阶段，核心验证与人工在环不可省。**

### ⚡ Fast Path（v2.2：为简单题省 Token）

阶段 1 审题报告完成后，判定题目复杂度，写入 `state/decision_log.json`：

| 判定 | 条件（满足任一即倾向 Fast） |
|------|------|
| **Fast** | 单问/两问、题目自带数据、方法为评价或简单预测类、无外部数据依赖 |
| **Full** | 多问、需联网找数据、优化/机理/混合类、创新目标 ≥ 8.0 |

**Fast Path 可跳过**（其余阶段与门禁不变）：
- 阶段 1.5 文献综述（标记为"Fast: 跳过"，refs.bib 用 3-5 篇核心文献即可）
- 阶段 7 对抗审稿降为 **1 轮**（审稿人+验证者并行，无复评循环）

**Fast Path 不可省**：M1/D1/P2/A1/A2/W2 门禁、H1/H2/H3 人工检查点、阶段 4 求解、阶段 6 写作、反模式硬阻断。

### 核心规则

1. **每个阶段三步骤**：执行 → 验证 → 确认。验证不通过不得进入下一阶段。
2. **落盘即证据**：每个阶段的产出必须写入对应文件，产出不存在 = 该阶段未完成。
3. **状态持久化**：每阶段开始前读取 `state/decision_log.json`，完成后写入决策记录。状态文件让流水线可在中断后恢复。
4. **禁止心算跳过**：不允许因为"这题简单""数据不用找""图随便画"而略过任何阶段。
5. **阶段门禁清单**：开工时 `TaskCreate` 建 8 个任务（阶段 0–7），每进入一个阶段 `TaskUpdate` 设为 in_progress，验证通过后才设 completed。任何时刻只允许一个阶段是 in_progress。
6. **审题结论贯穿全流程**：阶段 1 的审题报告是后续所有阶段的"宪法"——阶段 2 选型必须引用审题结论，阶段 4 求解必须回应审题中的约束，阶段 6 写作必须覆盖审题中的每问和隐性要求。
7. **可视化是必经阶段**：阶段 5 必须为每个模型至少产出 1 张图到 `figures/`，且阶段 6 的论文里每张图都要被正文引用并解读。
8. **对抗审稿不可省**：阶段 7 是核心创新，除非用户明确说"不要审稿"或触发 Fast Path，否则必须跑。
9. **Subagent 质检不可省**：M1/D1/P1/P2/A1/W1/A2/W2/A3 九道门禁必须逐道通过。**相邻门禁可合并派发**：P2+A1（同一 mm-verifier 一次派发，输出代码验证+反模式双报告）、W1+A2（写作前后各一次，不合并）；M1/D1/W2/A3 保持独立。
10. **⛔ 反模式是硬阻断**：A1/A2/A3 门禁中，任何 High 级别的反模式命中 → 必须退回修复。不可像 v2.0 那样仅是"查阅建议"。
11. **⛔ 人工在环不可省**：阶段 1/4/6 结束后必须暂停，将关键产物呈现给用户确认后再继续（详见下方"人工在环检查点"）。

### 阶段依赖链

```
0 目录 → 1 审题报告 [M1质检+🛑人工确认]
  → 1.5 文献综述 [≥8篇文献+研究空白定位]
  → 2 建模方案表
  → 3 data/*.csv+SOURCES [D1质检]
  → 4 [P1算法审计] → code/solve_qN.py+结果 [P2质检] → [A1反模式硬阻断] [🛑人工确认]
  → 5 figures/*.png
  → 6 [W1证据大纲] → 正文写作 → [A2写作反模式硬阻断] → main.pdf [W2质检] [🛑人工确认]
  → 7 对抗审稿 → [A3全维度反模式终扫] → 评分记录+终版PDF
```

### 每阶段验证门禁

**每个阶段完成后，必须执行以下验证步骤，验证不通过则退回该阶段重做。**

---

### ⛔ 人工在环检查点（v2.2）

**AI 不是数学建模专家——它在以下节点必须暂停，将关键产物呈现给用户做"合理性 sniff test"。**

| 检查点 | 时机 | 暂停产物 | 确认问题 | 不通过处理 |
|:--:|------|------|------|------|
| **🛑H1** | 阶段 1 审题 + M1 通过后 | §1.7 问题类型判定 + §1.3 隐性约束 | "问题类型判定是否正确？隐性约束有无遗漏？" | 用户纠正 → 更新审题报告 → 重新 M1 |
| **🛑H2** | 阶段 4 编码 + P2/A1 通过后 | 关键数值结果 + 代码运行输出摘要 | "结果数量级是否合理？有无明显荒谬的输出？" | 用户指出问题 → 回到阶段 4 修复 |
| **🛑H3** | 阶段 6 编译 + W2 通过后 | PDF 全文（或摘要+结论+关键图表） | "摘要是否每问量化？结论是否自洽？整体印象是否达到省一水平？" | 用户不满意 → 回到阶段 6 修改或进入阶段 7 重点提升 |

**执行规则**：
- 人工检查点不可跳过。用户不在时（异步运行），将产物 + 确认问题写入 `state/human_checkpoint.md`，标记 `AWAITING_HUMAN`，暂停流水线。
- 用户确认（或给出修改指示）后，记录确认结果和时间戳到 `state/decision_log.json`。
- 人工确认不等同于质检——Subagent 质检仍须独立执行。

---

**每阶段验证项的完整清单（检查项、方法、命令、不通过处理）见 `references/08-stage-verification.md`。以下为门禁速查：**

| 阶段 | 核心验证 | 质检 Subagent | 通过标准 |
|:--:|------|------|------|
| 1 | 审题完整性：逐问拆解、隐性约束、问题类型判定、审题结论可引用 | M1: `mm-verifier` | 6 项全通过 |
| 1.5 | 文献综述：≥8 篇 + 批判性梳理 + 研究空白定位 + refs.bib | — | 见阶段 1.5 门禁 |
| 2 | 方法选型：每问有方法、ML/DL 决策有理由、图表清单、反模式自查 | — | 方法匹配 §1.7 问题类型 |
| 3 | 数据质量：CSV 可读、缺失/异常值、SOURCES.md 来源 | D1: `mm-verifier` | `fetch_data.py --quality` 通过 |
| 4 | 算法正确性：代码可运行、公式一致、数字可追溯、量纲 | P1: `mm-reasoner`(编码前) / P2: `mm-verifier`(编码后) / A1: `mm-verifier` | 代码跑通 + A1 0 High |
| 5 | 图表覆盖：每模型 ≥1 图、300dpi、解读文案 | — | 图数 ≥ 模型数 |
| 6 | 论文质量：摘要 1 页、每图 \ref 引用、摘要量化、代码交叉验证 | W1: `mm-verifier`(写作前) / A2: `mm-reviewer`(写作后) / W2: `mm-reviewer`(编译后) | W2 五维 ≥ 6.0 |
| 7 | 审稿闭环：版本 PDF、High 弱点清零、均分 ≥ 7.5 | A3: `mm-reviewer`(终扫) | A3 0 High + 均分 ≥ 7.5 |

> ⛔ 依赖链、人工在环（H1/H2/H3）、九道门禁的派发时机与 PASS/FAIL 规则见上文。验证不通过一律退回该阶段重做；已通过的后续门禁在相关产物变化后自动失效。

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

写入 `REPORT.md` §1。审题报告必须覆盖 **§1.1–§1.7 七个维度，每维度 ≥ 150 字**（防止只堆字数、缺结构）。

> ⛔ 验证 → **M1 独立质检**（派发 mm-verifier）→ **🛑H1 人工确认**（问题类型+隐性约束 sniff test）→ 进入阶段 1.5。
> 参考：`01-problem-analysis.md`。

---

### 阶段 1.5 — 文献综述（v2.2 新增 ⛔ 国一必备）

**国一论文与省二论文的分水岭之一就是文献综述**。国一论文通常引用 15-25 篇参考文献，其中 ≥60% 来自期刊/会议/官方报告，且有对现有方法的批判性回顾——"现有方法 A 在 X 方面不足，方法 B 在 Y 方面有局限，本文结合并改进"。

用 `Agent`（agentType=`mm-problem-analyst`）执行文献检索：

1. **检索关键文献**：围绕赛题核心问题，用 WebSearch 检索 ≥ 8 篇相关文献（中英文各 ≥ 3 篇）
   - 中文：知网/万方检索相关学位论文和期刊论文
   - 英文：Google Scholar / Web of Science 检索近 5 年方法论文
2. **批判性梳理**：对每篇核心文献（≥ 5 篇）写 2-3 句评述——该方法贡献是什么？不足是什么？与本题的关系？
3. **研究空白定位**：基于文献综述，明确"现有方法留下了什么缺口？本文的定位是什么？"
4. **参考管理**：将文献信息写入 `paper/refs.bib`（BibTeX 格式），供 LaTeX 引用。

写入 `REPORT.md` §1.8 文献综述。

> ✅ 门禁：≥ 8 篇文献已检索 + ≥ 5 篇有评述 + 研究空白已定位 + refs.bib 已更新。
> 参考：`06-writing.md` 参考文献规范。

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

> P1→编码→P2→A1→🛑H2 人工确认（结果合理性 sniff test），全部通过才进入阶段 5。

---

### 阶段 5 — 可视化

仍由 `mm-coder` 出图到 `figures/`。每个模型 ≥ 1 张图，300dpi PNG，配色用 `05-visualization.md` 方案。出图后写解读文案。

> 参考：`05-visualization.md`、`11-anti-patterns.md`。

---

### 阶段 6 — LaTeX 写作 + 编译

用 `Agent`（`mm-writer`）填充 `paper/main.tex`。

**W1 证据大纲（写作前）**：派发 `mm-verifier` 验证每个论文主张有代码输出支撑。

**四项深度内容**：假设局限性量化 + 对比模型验证（≥2 基准/消融 + ≥3 指标 + **⛔ v2.2：消融实验证明每个创新组件贡献**）+ 创新点声明 + 多指标评估。

**⛔ 国一创新验证标准（v2.2 新增）**：
- 若声称方法创新（innovation 目标 ≥ 8.0），必须包含**消融实验**：逐一移除创新组件，证明每个组件对性能的独立贡献
- 对比基线 ≥ 3 个（经典方法 + 最近方法 + 消融版本）
- 验证场景 ≥ 2 个（如不同数据集/不同时间段/不同参数配置），证明创新的泛化性


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
- **⛔ 质检是根基**：M1/D1/P1/P2/A1/W1/A2/W2/A3 九道逐道通过，主 Agent 自检不是独立验收
- **⛔ 审题是宪法**：阶段 1 结论是后续最高指导
- **⛔ 反模式是硬阻断**：A1/A2/A3 门禁中 High 命中必须退回修复（v2.2 从软建议升级为硬阻断）
- **⛔ 人工在环是安全阀**：阶段 1/4/6 后暂停确认，AI 不是数模专家
- **⛔ 加权评分是真实度量**：角色×维度加权 + 硬上限规则 + 离群值仲裁（v2.2 修复简单平均 bug）
