export default function Comparison() {
  return (
    <section id="comparison" className="py-24 px-6 border-t border-zinc-800/50">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-zinc-100">和其他项目的区别</h2>
          <p className="mt-3 text-zinc-500">
            大多数数学建模仓库是资料合集，本仓库是自动化流水线
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800">
                <th className="text-left py-3 px-4 text-zinc-400 font-medium" />
                <th className="text-center py-3 px-4 text-zinc-500 font-normal">资料合集</th>
                <th className="text-center py-3 px-4 text-zinc-500 font-normal">算法代码库</th>
                <th className="text-center py-3 px-4 text-zinc-500 font-normal">经验分享</th>
                <th className="text-center py-3 px-4 text-green-500 font-semibold">本仓库</th>
              </tr>
            </thead>
            <tbody className="text-zinc-400">
              {[
                ['教程 / 资料', '有', '有', '有', '含 2 个完整案例'],
                ['可运行代码', '—', '部分', '部分', '6 本 Cookbook 全覆盖'],
                ['联网获取数据', '—', '—', '—', '内置数据猎人'],
                ['AI 流水线编排', '—', '—', '—', '8 智能体 + 7 阶段'],
                ['独立质检机制', '—', '—', '—', '5 道 Subagent 门禁'],
                ['对抗审稿', '—', '—', '—', '三角色并行 + 多轮迭代'],
                ['论文自动编译', '—', '—', '—', '中英双版 LaTeX'],
                ['跨阶段状态管理', '—', '—', '—', 'decision_log.json'],
              ].map((row, i) => (
                <tr key={i} className="border-b border-zinc-800/50">
                  <td className="py-3 px-4 text-zinc-300">{row[0]}</td>
                  <td className="text-center py-3 px-4">{row[1]}</td>
                  <td className="text-center py-3 px-4">{row[2]}</td>
                  <td className="text-center py-3 px-4">{row[3]}</td>
                  <td className="text-center py-3 px-4 text-green-400 font-medium">{row[4]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
