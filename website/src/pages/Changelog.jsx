const versions = [
  {
    version: 'v2.0.0',
    date: '2026-07-28',
    tag: '架构升级',
    sections: [
      {
        title: '新增 Subagent 独立质检协议',
        items: [
          '五道门禁：M1（审题完整性）/ P1（算法审计）/ P2（代码可运行+可追溯）/ W1（证据完整性）/ W2（论文五维度评分≥6.0）',
          '角色分离原则：写代码/写论文的 Agent 不能同时质检自己的产出，质检 Subagent 必须是独立只读实例',
          'FAIL 强制回溯机制：任一质检 FAIL → 退回对应阶段按证据修正 → 重新派发复验 → 相关后续门禁自动失效',
          'PASS 签名：通过时记录 Subagent ID + 时间戳 + 检查摘要，写入 REPORT.md',
        ]
      },
      {
        title: '新增跨阶段状态管理',
        items: [
          'state/decision_log.json：记录每阶段决策、参数、评分、时间戳，流水线中断后可精确恢复',
          '竞争信息（名称/年份/题目/语言）、每阶段状态（pending→in_progress→completed）、质检门禁状态',
          '拒绝依赖聊天上下文——关闭 Claude Code 后重启，读取 decision_log 即可继续',
        ]
      },
      {
        title: '6 本参考手册全面升级（3-13 倍行数增长）',
        items: [
          '02-framework.md：61→541 行。三级问题判定体系、44 种方法速查表、ML/DL 决策框架、8 个选型反例',
          '03-data-acquisition.md：97→695 行。8 类数据源速查表（含 API URL 模板）、6 段完整获取代码、缺失值处理决策树',
          '05-visualization.md：85→1144 行。9 维选图决策表、16 种图表含代码骨架、5 套色觉友好配色方案、10 个 wrong→right 错误对照',
          '07-adversarial-review.md：69→449 行。三角色评分锚点（0-10 五档）、评审意见模板、修改-复评循环协议、22 个常见弱点库',
          'data-sources.md：33→367 行。分类数据源大全（经济/环境/气候/人口/交通/能源/医疗/教育），每源含 API 端点/URL/数据格式/更新频率',
          'scoring-rubric.md：128→303 行。国赛+美赛双评分标准、五维度锚定描述（5.0/7.5/9.0 论文分别什么样）、评分校准规则',
        ]
      },
      {
        title: '新增 8 个文件',
        items: [
          '11-anti-patterns.md（654 行）：24 个建模常见错误，覆盖建模逻辑/数学统计/论文写作/代码四大类，每个条目含 症状→诊断→修复 三段式',
          '13-phrase-bank.md（401 行）：中英双语句式库，按章节组织（摘要/问题分析/模型假设/模型建立/结果分析/结论），含美赛 Memo/Letter 专用句式',
          'cookbooks/ 目录（6 本，~2,200 行）：优化/评价/预测/机理/统计ML/网络博弈，每本自包含（读一本即可实现算法），含代码骨架和常见错误',
          'doctor.py：37 项环境自检脚本（Python版本/LaTeX引擎/pip依赖/中文字体/目录完整性），支持 --json 和 --verbose 模式',
          'decision_log.json：跨阶段状态文件模板（含所有字段注释）',
          'assumption_table.md：标准化假设表格模板（5 列：假设内容/合理性论证/对模型的影响/违反后果与补救方案/参考文献），含 5 个完整示例和 5 个不良假设反例',
          'playbook-guide.md：Playbook 使用与创建指南',
          'CHANGELOG.md：本更新记录',
        ]
      },
      {
        title: 'SKILL.md 重写',
        items: [
          '新增 Subagent 质检协议章节（五道门禁表格 + 质检规则）',
          '新增路径解析协议（skill内/用户产物/状态文件三类路径约定）',
          '新增参考手册速查表（15 本手册 + 6 本 cookbook，按阶段标注查阅时机）',
          '每阶段增加"反模式检查"验证项',
          '阶段依赖链标注质检节点（M1→P1→P2→W1→W2）',
          '从 404 行精简为 370 行',
        ]
      },
    ]
  },
  {
    version: 'v1.2',
    date: '2026-07-27',
    tag: '初始版本',
    sections: [
      {
        title: '核心架构',
        items: [
          '7 阶段强制流水线（0 建目录 → 1 审题 → 2 选方法 → 3 找数据 → 4 求解 → 5 可视化 → 6 写论文 → 7 对抗审稿）',
          '硬性门禁：每阶段必须落盘、验证、确认后才可进入下一阶段，禁止跳步',
          '8 个子智能体：mm-problem-analyst / mm-modeler / mm-data-hunter / mm-coder / mm-writer / mm-reviewer / mm-verifier / mm-reasoner',
          '三角色并行对抗审稿：审稿人（建模合理性）+ 验证者（数值核对）+ 推理者（公式审计）→ 写作者修 → 复评',
          'Workflow 驱动审稿流程（≤4 轮，targetScore 7.5）',
        ]
      },
      {
        title: '参考手册（12 本）',
        items: [
          '01-problem-analysis.md：审题方法论',
          '02-framework.md：建模框架与方法选型',
          '03-data-acquisition.md：数据获取策略',
          '04-modeling-cookbook.md：建模算法手册',
          '05-visualization.md：可视化规范',
          '06-writing.md：LaTeX 写作标准',
          '07-adversarial-review.md：对抗审稿机制',
          '08-stage-verification.md：阶段验证门禁',
          '09-innovation-playbook.md：12 种创新策略',
          '10-modeling-tricks.md：数学建模 33 讲优化技巧',
          'data-sources.md：数据源速查',
          'scoring-rubric.md：评分细则',
        ]
      },
      {
        title: '辅助脚本（5 个）',
        items: [
          'new_project.py：新建项目骨架',
          'fetch_data.py：数据获取（World Bank API + sklearn + 关键词搜索 + 直链下载）',
          'compile.py：LaTeX 编译（xelatex/pdflatex）',
          'plot_helpers.py：图表绘制（6 种基础图 + 10 种高端图）',
          'verify_results.py：交叉验证（代码输出 vs 论文数字）',
        ]
      },
      {
        title: '其他',
        items: [
          '中英双版 LaTeX 模板（cumcm-zh / mcm-en）',
          '四项深度内容要求（假设量化/对比模型/创新声明/多指标评估）',
          '数据引擎增强（World Bank API + 质量报告 + 多源合并 + 小样本增强）',
          '两个完整样本项目（2024 国赛 A 题 + 2025 HiMCM B 题）',
          '对抗审稿 Workflow 脚本',
        ]
      },
    ]
  },
]

export default function Changelog() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-16 fade-in">
        <h1 className="text-3xl font-bold text-zinc-100 mb-3">更新日志</h1>
        <p className="text-zinc-500">每一次改动的完整记录</p>
      </div>

      <div className="space-y-16">
        {versions.map((v, vi) => (
          <div key={vi} className={`fade-in fade-in-${Math.min(vi + 1, 4)}`}>
            <div className="flex items-center gap-3 mb-6">
              <span className="font-mono text-lg font-bold text-green-400">{v.version}</span>
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-white/10 text-zinc-300">{v.tag}</span>
              <span className="text-sm text-zinc-600">{v.date}</span>
            </div>

            <div className="space-y-8">
              {v.sections.map((s, si) => (
                <div key={si} className="glass rounded-xl p-6">
                  <h3 className="text-sm font-semibold text-zinc-200 mb-4">{s.title}</h3>
                  <ul className="space-y-2">
                    {s.items.map((item, ii) => (
                      <li key={ii} className="text-sm text-zinc-400 leading-relaxed pl-4 border-l-2 border-white/10">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
