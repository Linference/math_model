import { Link } from 'react-router-dom'

const features = [
  { title: '7 阶段强制流水线', desc: '审题→选方法→找数据→求解→可视化→写论文→对抗审稿。每阶段落盘验证，不可跳步。' },
  { title: '8 个专项子智能体', desc: '审题专家、方法顾问、数据猎人、编程求解、论文写手、审稿人、验证者、推理者。' },
  { title: '5 道独立质检门禁', desc: 'M1/P1/P2/W1/W2 — 写作者与质检者角色分离，FAIL 强制回溯修正。' },
  { title: '三角色并行对抗审稿', desc: '审稿人（建模）+ 验证者（数值）+ 推理者（公式）同时批改，写作者逐条回应，迭代至 7.5 分。' },
  { title: '联网数据自动获取', desc: '数据猎人搜索维基/GitHub/Kaggle/World Bank/sklearn，自动落盘并记录来源。' },
  { title: '21 本参考手册 + 6 本 Cookbook', desc: '审题方法论、44 种方法速查、16 种图表骨架、中英句式库、反模式手册。' },
  { title: '中英双版 LaTeX 模板', desc: '国赛 ctex/xelatex + 美赛 pdflatex，编译即得盲审就绪 PDF。' },
  { title: '跨阶段状态管理', desc: 'decision_log.json 记录每阶段决策，中断后可恢复执行。' },
]

const comparisonRows = [
  ['教程 / 资料', '有', '有', '有', '含 2 个完整案例'],
  ['可运行代码', '—', '部分', '部分', '6 本 Cookbook 全覆盖'],
  ['联网获取数据', '—', '—', '—', '内置数据猎人'],
  ['AI 流水线编排', '—', '—', '—', '8 Agent + 7 阶段'],
  ['独立质检机制', '—', '—', '—', '5 道 Subagent 门禁'],
  ['对抗审稿', '—', '—', '—', '三角色并行迭代'],
  ['自动编译论文', '—', '—', '—', '中英 LaTeX 模板'],
  ['状态持久化', '—', '—', '—', 'decision_log.json'],
]

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-4xl mx-auto px-6 pt-24 pb-20 text-center relative">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-green-200 bg-green-50 text-xs text-green-700 mb-8 fade-in">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
            v2.0 已发布 — 新增 Subagent 质检 + 6 本算法手册
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight leading-tight fade-in fade-in-1">
            数学建模{' '}
            <span className="text-green-600">多智能体</span>
            <br />
            论文生成系统
          </h1>

          <p className="mt-6 text-lg text-slate-500 max-w-xl mx-auto leading-relaxed fade-in fade-in-2">
            8 个 AI Agent 协作，7 阶段流水线，5 道独立质检门禁。从赛题 PDF 到终版论文，一个命令跑完。
          </p>

          <div className="mt-10 flex items-center justify-center gap-4 flex-wrap fade-in fade-in-3">
            <a href="https://github.com/Linference/math_model/releases/latest" target="_blank" rel="noopener noreferrer"
              className="px-6 py-2.5 rounded-lg bg-green-500 text-white font-semibold text-sm hover:bg-green-600 transition-all hover:scale-105 shadow-sm">
              下载 v2.0
            </a>
            <Link to="/docs"
              className="px-6 py-2.5 rounded-lg border border-slate-200 text-slate-600 text-sm font-medium hover:border-slate-300 hover:bg-slate-50 transition-all">
              使用文档 →
            </Link>
          </div>

          <div className="mt-8 text-sm text-slate-400 fade-in fade-in-4">
            支持国赛 CUMCM · 美赛 MCM/ICM · HiMCM
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 fade-in">
            <h2 className="text-3xl font-bold text-slate-900">功能</h2>
            <p className="mt-3 text-slate-500">不是提示词模板，而是结构化流水线 + 独立质检体系</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {features.map((f, i) => (
              <div key={i} className={`glass rounded-xl p-5 fade-in fade-in-${Math.min(i + 1, 4)}`}>
                <h3 className="text-sm font-semibold text-slate-800 mb-2">{f.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison */}
      <section className="py-24 px-6 bg-slate-50/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16 fade-in">
            <h2 className="text-3xl font-bold text-slate-900">对比</h2>
            <p className="mt-3 text-slate-500">大多数数学建模仓库是资料合集，本仓库是自动化流水线</p>
          </div>

          <div className="glass rounded-xl overflow-hidden fade-in">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-3 px-5 text-slate-500 font-medium" />
                  <th className="text-center py-3 px-5 text-slate-400 font-normal">资料合集</th>
                  <th className="text-center py-3 px-5 text-slate-400 font-normal">算法库</th>
                  <th className="text-center py-3 px-5 text-slate-400 font-normal">经验分享</th>
                  <th className="text-center py-3 px-5 text-green-600 font-semibold">本仓库</th>
                </tr>
              </thead>
              <tbody className="text-slate-500">
                {comparisonRows.map((row, i) => (
                  <tr key={i} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-5 text-slate-700">{row[0]}</td>
                    <td className="text-center py-3 px-5">{row[1]}</td>
                    <td className="text-center py-3 px-5">{row[2]}</td>
                    <td className="text-center py-3 px-5">{row[3]}</td>
                    <td className="text-center py-3 px-5 text-green-600 font-medium">{row[4]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center fade-in">
          <h2 className="text-3xl font-bold text-slate-900">开始使用</h2>
          <p className="mt-3 text-slate-500">三步跑起来，把赛题变成论文</p>
          <div className="mt-8 flex items-center justify-center gap-4">
            <Link to="/docs" className="px-6 py-2.5 rounded-lg border border-slate-200 text-slate-600 text-sm font-medium hover:border-slate-300 transition-all">
              阅读文档 →
            </Link>
            <a href="https://github.com/Linference/math_model/releases/latest" target="_blank" rel="noopener noreferrer"
              className="px-6 py-2.5 rounded-lg bg-green-500 text-white font-semibold text-sm hover:bg-green-600 transition-all hover:scale-105 shadow-sm">
              下载 Skills
            </a>
          </div>
        </div>
      </section>
    </>
  )
}
