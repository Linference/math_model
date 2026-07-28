export default function Thanks() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-16 text-center fade-in">
        <h1 className="text-3xl font-bold text-zinc-100 mb-3">致谢</h1>
        <p className="text-zinc-500">这个项目建立在许多优秀工具和项目的基础上</p>
      </div>

      <div className="space-y-8">
        {/* Tools */}
        <div className="fade-in fade-in-1">
          <h2 className="text-lg font-semibold text-zinc-200 mb-4">依赖工具</h2>
          <div className="glass rounded-xl p-6 space-y-3 text-sm text-zinc-400">
            {[
              { name: 'Claude Code', url: 'https://claude.ai/code', desc: 'Anthropic 推出的 AI 编程助手，本系统的多智能体编排引擎。' },
              { name: 'CCSwitch', url: 'https://ccswitch.io', desc: 'Claude Code 代理切换工具，让国内用户通过 DeepSeek 使用 Claude Code。' },
              { name: 'DeepSeek', url: 'https://platform.deepseek.com', desc: '高性能大模型，数学推理和中文写作能力出色。国内用户的首选后端。' },
              { name: 'Python', url: 'https://python.org', desc: '科学计算基础平台。numpy / scipy / pandas / scikit-learn / matplotlib。' },
              { name: 'LaTeX', url: 'https://latex-project.org', desc: '学术论文排版标准。MiKTeX (Windows) / TeXLive (macOS/Linux)。' },
              { name: 'React + Tailwind', url: 'https://react.dev', desc: '本网站的技术栈。' },
            ].map((t, i) => (
              <div key={i} className="flex items-start gap-3">
                <a href={t.url} target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline shrink-0 font-medium min-w-[100px]">
                  {t.name}
                </a>
                <span>{t.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Inspired by */}
        <div className="fade-in fade-in-2">
          <h2 className="text-lg font-semibold text-zinc-200 mb-4">参考项目</h2>
          <div className="glass rounded-xl p-6 space-y-3 text-sm text-zinc-400">
            {[
              { name: 'XiaoMaColtAI/math-modeling-skill', desc: '三阶段建模流程 + Subagent 质检设计，启发了本项目的独立质检体系。' },
              { name: 'handsomeZR-netizen/mathmodel-skill', desc: '10 阶段状态机 + 竞赛特化包 + 决策日志持久化，启发了跨阶段状态管理。' },
              { name: 'Lupynow/math-modeling-skills', desc: 'Solver + Paper 分离设计 + 丰富的算法手册 + 去 AI 味写作指南，启发了 Cookbook 拆分。' },
            ].map((p, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-zinc-300 font-medium shrink-0 min-w-[220px]">{p.name}</span>
                <span>{p.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Community */}
        <div className="fade-in fade-in-3">
          <h2 className="text-lg font-semibold text-zinc-200 mb-4">社区支持</h2>
          <div className="glass rounded-xl p-6 text-sm text-zinc-400 leading-relaxed">
            <p>感谢每一位 Star、Fork、提 Issue 和 PR 的贡献者。你们的反馈让这个项目变得更好。</p>
            <p className="mt-3">
              如果你也想参与贡献，欢迎提交{' '}
              <a href="https://github.com/Linference/math_model/issues" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">Issue</a>
              {' '}或{' '}
              <a href="https://github.com/Linference/math_model/pulls" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">Pull Request</a>。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
