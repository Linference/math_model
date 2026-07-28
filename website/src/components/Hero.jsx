export default function Hero() {
  return (
    <section className="pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-zinc-800 bg-zinc-900/50 text-xs text-zinc-400 mb-8">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          v2.0 已发布 — 新增 Subagent 质检 + 6 本算法手册
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-zinc-100 tracking-tight leading-tight">
          数学建模
          <span className="text-green-500"> 多智能体</span>
          <br />
          论文生成系统
        </h1>

        <p className="mt-6 text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed">
          8 个 AI 子智能体协作，7 阶段流水线，5 道独立质检门禁。
          从赛题 PDF 到终版论文，一个命令跑完。
        </p>

        <div className="mt-10 flex items-center justify-center gap-4 flex-wrap">
          <a
            href="#download"
            className="px-6 py-2.5 rounded-lg bg-green-500 text-zinc-950 font-semibold text-sm hover:bg-green-400 transition-colors"
          >
            下载 v2.0
          </a>
          <a
            href="https://github.com/Linference/math_model"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2.5 rounded-lg border border-zinc-700 text-zinc-300 text-sm font-medium hover:border-zinc-500 hover:text-zinc-100 transition-colors"
          >
            GitHub →
          </a>
        </div>

        <div className="mt-8 text-sm text-zinc-500">
          支持国赛 CUMCM · 美赛 MCM/ICM · HiMCM
        </div>
      </div>
    </section>
  )
}
