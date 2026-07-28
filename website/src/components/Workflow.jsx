const stages = [
  { num: '0', title: '建目录', desc: '初始化项目骨架和决策日志' },
  { num: '1', title: '深度审题', desc: '逐问拆解，挖掘隐性约束和评分陷阱' },
  { num: '2', title: '方法选型', desc: '判定 ML/DL 需求，匹配算法，预审可行性' },
  { num: '3', title: '数据获取', desc: '联网搜索 + API 管线 + 质量检查' },
  { num: '4', title: '编程求解', desc: '编码前算法审计(P1) → 编写 → 编码后质检(P2)' },
  { num: '5', title: '可视化', desc: '16 种图表，300dpi，色觉友好配色' },
  { num: '6', title: '论文写作', desc: '证据大纲审计(W1) → 写作 → 论文终检(W2)' },
  { num: '7', title: '对抗审稿', desc: '三角色并行打分 → 写作者逐条修改 → 复评', extra: '≤ 4 轮，均分 ≥ 7.5 放行' },
]

const gates = [
  { id: 'M1', stage: '阶段 1 后', check: '审题完整性', agent: 'mm-verifier' },
  { id: 'P1', stage: '阶段 4 编码前', check: '算法正确性论证', agent: 'mm-reasoner' },
  { id: 'P2', stage: '阶段 4 编码后', check: '代码可运行 + 结果可追溯', agent: 'mm-verifier' },
  { id: 'W1', stage: '阶段 6 写作前', check: '证据完整性', agent: 'mm-verifier' },
  { id: 'W2', stage: '阶段 6 编译后', check: '论文五维度评分 ≥ 6.0', agent: 'mm-reviewer' },
]

export default function Workflow() {
  return (
    <section id="workflow" className="py-24 px-6 border-t border-zinc-800/50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-zinc-100">工作流程</h2>
          <p className="mt-3 text-zinc-500">7 阶段流水线 + 5 道独立质检门禁</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-16">
          {stages.map((s, i) => (
            <div key={i} className="border border-zinc-800 rounded-lg p-5 bg-zinc-900/30">
              <div className="flex items-center gap-2 mb-3">
                <span className="flex items-center justify-center w-6 h-6 rounded bg-green-500/10 text-green-500 text-xs font-mono font-bold">
                  {s.num}
                </span>
                <h3 className="text-sm font-semibold text-zinc-200">{s.title}</h3>
              </div>
              <p className="text-sm text-zinc-500 leading-relaxed">{s.desc}</p>
              {s.extra && (
                <p className="mt-1 text-xs text-zinc-600">{s.extra}</p>
              )}
            </div>
          ))}
        </div>

        <div className="border border-zinc-800 rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-900/50">
            <h3 className="text-sm font-semibold text-zinc-200">Subagent 独立质检门禁 (v2.0)</h3>
            <p className="text-xs text-zinc-500 mt-1">写作者和质检者角色分离，主 Agent 自检不能替代独立验收</p>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left py-3 px-6 text-zinc-400 font-medium">门禁</th>
                <th className="text-left py-3 px-6 text-zinc-400 font-medium">触发时机</th>
                <th className="text-left py-3 px-6 text-zinc-400 font-medium">检查内容</th>
                <th className="text-left py-3 px-6 text-zinc-400 font-medium">质检角色</th>
              </tr>
            </thead>
            <tbody>
              {gates.map((g, i) => (
                <tr key={i} className="border-b border-zinc-800/50 last:border-0">
                  <td className="py-3 px-6">
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-green-500/10 text-green-500 font-semibold">
                      {g.id}
                    </span>
                  </td>
                  <td className="py-3 px-6 text-zinc-400">{g.stage}</td>
                  <td className="py-3 px-6 text-zinc-300">{g.check}</td>
                  <td className="py-3 px-6 text-zinc-500 font-mono text-xs">{g.agent}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
