const versions = [
  {
    version: 'v2.0.0',
    date: '2026-07-28',
    tag: '架构升级',
    sections: [
      {
        title: 'Subagent 独立质检协议',
        items: [
          '五道门禁：M1（审题完整性）/ P1（算法审计）/ P2（代码可运行+可追溯）/ W1（证据完整性）/ W2（论文五维度评分≥6.0）',
          '角色分离原则：写代码/写论文的 Agent 不能同时质检自己的产出',
          'FAIL 强制回溯机制：任一质检 FAIL → 退回对应阶段按证据修正 → 重新派发复验',
          'PASS 签名：通过时记录 Subagent ID + 时间戳 + 检查摘要，写入 REPORT.md',
        ]
      },
      {
        title: '跨阶段状态管理',
        items: [
          'state/decision_log.json：记录每阶段决策、参数、评分、时间戳，流水线中断后可精确恢复',
          '拒绝依赖聊天上下文——关闭 Claude Code 后重启，读取 decision_log 即可继续',
        ]
      },
      {
        title: '6 本参考手册全面升级（3-13 倍行数）',
        items: [
          '02-framework.md：61→541 行。三级问题判定体系、44 种方法速查表、ML/DL 决策框架',
          '03-data-acquisition.md：97→695 行。8 类数据源速查表（含 API URL）、6 段获取代码、缺失值处理决策树',
          '05-visualization.md：85→1144 行。16 种图表代码骨架、5 套色觉友好配色、10 个 wrong→right 对照',
          '07-adversarial-review.md：69→449 行。三角色评分锚点、评审模板、修改-复评循环协议、22 个弱点库',
          'data-sources.md：33→367 行。分类数据源大全（经济/环境/气候/人口/交通/能源/医疗/教育）',
          'scoring-rubric.md：128→303 行。国赛+美赛双标准、五维度锚定（5.0/7.5/9.0 论文分别什么样）',
        ]
      },
      {
        title: '新增 8 个文件',
        items: [
          'anti-patterns.md（654 行）：24 个建模常见错误，症状→诊断→修复三段式',
          'phrase-bank.md（401 行）：中英双语句式库，按章节组织，含美赛 Memo 专用句式',
          'cookbooks/（6 本，~2,200 行）：优化/评价/预测/机理/统计ML/网络博弈',
          'doctor.py：37 项环境自检脚本',
          'decision_log.json：跨阶段状态文件模板',
          'assumption_table.md：标准化假设表格（5 列：假设→论证→影响→违反后果）',
          'playbook-guide.md：Playbook 使用与创建指南',
          'CHANGELOG.md：本更新记录',
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
          '7 阶段强制流水线 + 硬性门禁（执行→验证→确认）',
          '8 个子智能体：审题/建模/数据/编程/写作/审稿/验证/推理',
          '三角色并行对抗审稿（审稿人+验证者+推理者 → 写作者修 → 复评）',
          'Workflow 驱动审稿（≤4 轮，targetScore 7.5）',
        ]
      },
      {
        title: '参考手册（12 本）',
        items: ['01-10：审题/建模/数据/算法/可视化/写作/审稿/验证/创新/技巧', 'data-sources.md + scoring-rubric.md']
      },
      {
        title: '辅助脚本（5 个）',
        items: ['new_project.py / fetch_data.py / compile.py / plot_helpers.py / verify_results.py']
      },
      {
        title: '其他',
        items: [
          '中英双版 LaTeX 模板（cumcm-zh / mcm-en）',
          '四项深度内容要求 + 数据引擎增强',
          '两个完整样本项目（2024 国赛 A + 2025 HiMCM B）',
        ]
      },
    ]
  },
]

export default function Changelog() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-16 fade-in">
        <h1 className="text-3xl font-bold text-slate-900 mb-3">更新日志</h1>
        <p className="text-slate-500">每一次改动的完整记录</p>
      </div>

      <div className="space-y-16">
        {versions.map((v, vi) => (
          <div key={vi} className={`fade-in fade-in-${Math.min(vi + 1, 4)}`}>
            <div className="flex items-center gap-3 mb-6">
              <span className="font-mono text-lg font-bold text-green-600">{v.version}</span>
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-50 text-green-700 border border-green-200">{v.tag}</span>
              <span className="text-sm text-slate-400">{v.date}</span>
            </div>

            <div className="space-y-4">
              {v.sections.map((s, si) => (
                <div key={si} className="border border-slate-200 rounded-xl p-6 bg-white/80 backdrop-blur-sm">
                  <h3 className="text-sm font-semibold text-slate-800 mb-3">{s.title}</h3>
                  <ul className="space-y-2">
                    {s.items.map((item, ii) => (
                      <li key={ii} className="text-sm text-slate-500 leading-relaxed pl-4 border-l-2 border-slate-200">
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
