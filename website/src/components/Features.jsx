const features = [
  {
    title: '7 阶段强制流水线',
    desc: '审题 → 选方法 → 找数据 → 求解 → 可视化 → 写论文 → 对抗审稿。每阶段落盘验证，不可跳步。',
  },
  {
    title: '8 个专项子智能体',
    desc: '审题专家、方法顾问、数据猎人、编程求解、论文写手、审稿人、验证者、推理者，各司其职。',
  },
  {
    title: '5 道独立质检门禁',
    desc: 'M1/P1/P2/W1/W2 — 写作者和质检者角色分离，FAIL 强制回溯修正，主 Agent 自检不能替代独立验收。',
  },
  {
    title: '三角色并行对抗审稿',
    desc: '审稿人（建模合理性）+ 验证者（数值核对）+ 推理者（公式审计）同时批改，写作者逐条回应，多轮迭代直到 7.5 分。',
  },
  {
    title: '联网数据自动获取',
    desc: '内置数据猎人，搜索维基/GitHub/Kaggle/World Bank/官方统计/sklearn，落盘 CSV 并记录来源。',
  },
  {
    title: '21 本参考手册 + 6 本算法 Cookbook',
    desc: '审题方法论、44 种方法速查、数据源大全、16 种图表骨架、评分细则、中英句式库、反模式手册。',
  },
  {
    title: '中英双版 LaTeX 模板',
    desc: '国赛 ctex/xelatex 中文模板 + 美赛 pdflatex 英文模板，编译即得盲审就绪 PDF。',
  },
  {
    title: '跨阶段状态管理',
    desc: 'decision_log.json 记录每阶段决策和参数，中断后可恢复，不依赖聊天上下文。',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-24 px-6 border-t border-zinc-800/50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-zinc-100">功能</h2>
          <p className="mt-3 text-zinc-500 max-w-xl mx-auto">
            不是提示词模板，而是结构化流水线 + 独立质检体系
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-px bg-zinc-800/50 rounded-xl overflow-hidden">
          {features.map((f, i) => (
            <div key={i} className="bg-zinc-950 p-6">
              <h3 className="text-sm font-semibold text-zinc-200 mb-2">{f.title}</h3>
              <p className="text-sm text-zinc-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
