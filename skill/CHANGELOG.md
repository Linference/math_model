# Changelog

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
