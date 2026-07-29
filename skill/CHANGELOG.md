# Changelog

## v2.2.0 (2026-07-29) — 国一冲刺版：Agent 知识嵌入 + 文献综述 + 创新增强

### 核心升级：Agent 从"薄提示"到"厚知识体"
v2.1 及之前版本的 Agent 定义仅 25-47 行，本质是角色描述，没有嵌入参考手册的领域知识。
v2.2 将全部 8 个 Agent 重写为 60-120 行，嵌入：
- **开工前必读指令**：每个 Agent 开工前必须读取的关键参考文件
- **决策框架/检查清单**：将参考手册的核心方法论嵌入 Agent 的 system prompt
- **反模式自检**：直接引用 11-anti-patterns.md 的具体条目
- **评分锚点**（mm-reviewer/mm-verifier/mm-reasoner）：嵌入五维度评分锚定值和角色权重

| Agent | v2.1 行数 | v2.2 行数 | 嵌入知识 |
|------|:--:|:--:|------|
| mm-problem-analyst | 30 | 70 | 01-problem-analysis.md 方法论 + 反模式陷阱 |
| mm-modeler | 47 | 85 | 02-framework.md 三级判定 + 8 选型反例 + 09-innovation-playbook |
| mm-data-hunter | 32 | 55 | 03-data-acquisition.md 质量检查 + 12-data-sources.md |
| mm-coder | 35 | 95 | 11-anti-patterns §4 代码反模式 + 防错机制 + 05-visualization |
| mm-writer | 29 | 115 | 13-phrase-bank 黑名单 + 四项深度 + 审题贯穿 + 06-writing |
| mm-reviewer | 26 | 100 | 15-scoring-rubric 锚点 + 07 角色权重 + 反模式检查清单 |
| mm-verifier | 28 | 95 | 11-anti-patterns §2+§4 + 统计陷阱清单 + 检查清单 |
| mm-reasoner | 25 | 90 | 07 数学严谨性清单 + 15-scoring-rubric §3.2 + 反模式 §2 |

### 新增阶段 1.5：文献综述（国一必备）
- 检索 ≥ 8 篇相关文献（中英文各 ≥ 3 篇）
- ≥ 5 篇有批判性评述（贡献+不足+与本题关系）
- 研究空白定位：现有方法留下什么缺口？
- 文献写入 `paper/refs.bib`

### 国一创新验证标准升级
- 若 innovation 目标 ≥ 8.0，必须包含**消融实验**（逐一移除创新组件证明独立贡献）
- 对比基线从 ≥ 2 升级为 ≥ 3（经典 + 最近 + 消融）
- 验证场景 ≥ 2 个（不同数据集/时间段/参数配置）

### 08-stage-verification.md 同步
- 新增 D1/A1/A2/A3 门禁的详细验证协议
- 新增缺失值/异常值检查命令

### 依赖链升级
```
v2.1: 0→1[M1+H1]→2→3[D1]→4[P1/P2/A1+H2]→5→6[W1/A2/W2+H3]→7[A3]
v2.2: 0→1[M1+H1]→1.5[文献综述]→2→3[D1]→4[P1/P2/A1+H2]→5→6[W1/A2/W2+H3]→7[A3]
```

---

## v2.1.0 (2026-07-28) — 深度剖析修复版

### Bug 修复（紧急）
- **修复 Workflow 评分聚合 bug**：`aggregate()` 从简单平均改为角色×维度加权聚合
  - 实现 `07-adversarial-review.md` §1.3 中定义的角色权重矩阵（审稿人/验证者/推理者在 5 个维度上的差异化权重）
  - 实现 `15-scoring-rubric.md` §4.2 硬上限规则（rigor<5 → ≤6.0, results<5 → ≤5.5 等）
  - 实现 `15-scoring-rubric.md` §4.3 离群值仲裁（极差≥4.0 → 中位数 + `[ARBITRATED]` 标记）
  - 评审返回值携带 `_role` 标签以匹配权重矩阵
  - 最终返回值新增 `dimScores` / `hardCaps` / `arbitrated` 字段
- **修复 verify_results.py 浮点匹配漏检**：`round(n,4)` 集合匹配 → `math.isclose(rtol=1e-3)` 相对容差匹配
  - 避免了 0.76371 vs 0.7637 的 round 边界值漏检
  - 新增二次宽松确认（rtol=5e-3）
- **修复 auditFailed 检测逻辑**：脆弱的字符串匹配（`includes('FAIL')` / `includes('❌')`）→ 结构化 `AUDIT_SCHEMA`
  - 审计 Agent 现在使用 `schema: AUDIT_SCHEMA` 输出 `auditPassed: boolean`，杜绝误判

### 新增门禁（从 5 道扩展到 9 道）
- **D1 数据质量独立质检**：阶段 3 后新增，检查 CSV 可读性 + 缺失值比例 + 异常值报告 + 多源对齐
  - 新增验证项：缺失值检查（缺失>20% 须说明策略）、异常值扫描（IQR/Z-score）、多源数据对齐
- **A1 反模式硬阻断（代码级）**：阶段 4 P2 通过后，对代码+建模逻辑执行反模式扫描
- **A2 反模式硬阻断（写作级）**：阶段 6 正文写作后、编译前，检查写作反模式+套话
- **A3 反模式硬阻断（终扫）**：阶段 7 审稿完成前，全维度反模式终扫（22 条逐条检查）

### 新增人工在环检查点
- **H1**：阶段 1 审题 + M1 通过后 → 用户确认问题类型+隐性约束
- **H2**：阶段 4 编码 + P2/A1 通过后 → 用户确认结果合理性
- **H3**：阶段 6 编译 + W2 通过后 → 用户确认论文整体质量
- 执行规则：不可跳过 / 用户不在时写入 `state/human_checkpoint.md` 并暂停 / 不等于替代质检

### 依赖链升级
- 旧：`0→1[M1]→2→3→4[P1]/[P2]→5→6[W1]/main.pdf[W2]→7`
- 新：`0→1[M1+🛑H1]→2→3[D1]→4[P1]/[P2]/[A1]+[🛑H2]→5→6[W1]/[A2]/main.pdf[W2]+[🛑H3]→7/[A3]`

### 原则升级
- 从 11 条升级为 13 条
- 新增：**⛔ 反模式是硬阻断**（v2.1 从软建议升级）、**⛔ 人工在环是安全阀**、**⛔ 加权评分是真实度量**

---

## v2.0.0 (2026-07-28)

### 架构升级
- **新增 Subagent 独立质检协议**：M1/P1/P2/W1/W2 五道门禁，角色分离（写作者和质检者必须是不同 Agent 实例），FAIL 回溯机制
- **新增跨阶段状态管理**：`state/decision_log.json` 记录每阶段决策/参数/评分，支持流水线中断恢复
- **新增路径解析协议**：统一 skill 内部、用户产物、状态文件的路径约定
- **SKILL.md 重写**：从 405 行升级为 350+ 行精简版，新增质检协议、状态管理、参考手册速查表

### 参考手册升级
- **02-framework.md**：61→541 行。三级问题判定体系、44 种方法速查表、ML/DL 决策框架、8 个选型反例
- **03-data-acquisition.md**：97→695 行。8 类数据源速查表（含 API URL 模板）、6 段完整获取代码、数据质量检查函数、缺失值处理决策树
- **05-visualization.md**：85→1144 行。9 维选图决策表、16 种图表含代码骨架、5 套色觉友好配色方案、10 个 wrong→right 画图错误对照
- **07-adversarial-review.md**：69→250+ 行。三角色评分锚点（0/2/4/6/8/10）、评审意见模板、修改-复评循环协议、20+ 常见弱点库
- **data-sources.md**：33→250+ 行。分类数据源大全（经济/环境/气候/人口/交通/能源/医疗/教育），每源含 API 端点/URL/数据格式/更新频率
- **scoring-rubric.md**：128→300+ 行。国赛+美赛双评分标准、五维度锚定描述、评分校准规则

### 新增文件
- **anti-patterns.md**：建模常见错误手册（症状→诊断→修复三段式），覆盖建模逻辑/数学统计/论文写作/代码四大类
- **phrase-bank.md**：中英双语句式库，按章节组织（摘要/问题分析/模型假设/结果分析/结论），含美赛 Memo 专用句式
- **doctor.py**：环境自检脚本，检查 Python/LaTeX/pip 依赖/中文字体/目录完整性
- **decision_log.json**：跨阶段状态文件模板
- **assumption_table.md**：模型假设标准化表格模板（5 栏：假设/论证/影响/违背后果）
- **CHANGELOG.md**：本文件

### 原则升级
- 从 8 条原则升级为 11 条，新增：质检是根基、反模式即防线、状态持久化
- 每个阶段增加"反模式检查"验证项
- 阶段依赖链标注质检节点

---

## v1.2 (2026-07-27)

### 初始版本
- 7 阶段强制流水线（0-7）
- 8 个子智能体（problem-analyst / modeler / data-hunter / coder / writer / reviewer / verifier / reasoner）
- 三角色并行对抗审稿（Workflow 驱动，≤4 轮，targetScore 7.5）
- 12 本参考手册（01-10 + data-sources + scoring-rubric）
- 5 个辅助脚本（new_project / fetch_data / compile / plot_helpers / verify_results）
- 中英双版 LaTeX 模板（cumcm-zh / mcm-en）
- 每阶段验证门禁
- 四项深度内容要求
- 数据引擎增强（World Bank API + 质量报告 + 多源合并 + 小样本增强）
