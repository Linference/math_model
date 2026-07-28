export default function Download() {
  return (
    <section id="download" className="py-24 px-6 border-t border-zinc-800/50">
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="text-3xl font-bold text-zinc-100">下载 v2.0</h2>
        <p className="mt-3 text-zinc-500">
          包含 21 本参考手册、6 本算法 Cookbook、完整流水线脚本、中英 LaTeX 模板
        </p>

        <div className="mt-10 flex items-center justify-center gap-4 flex-wrap">
          <a
            href="https://github.com/Linference/math_model/releases/latest"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3 rounded-lg bg-green-500 text-zinc-950 font-semibold text-sm hover:bg-green-400 transition-colors"
          >
            下载 skill-v2.0.zip
          </a>
          <a
            href="https://github.com/Linference/math_model"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-3 rounded-lg border border-zinc-700 text-zinc-300 text-sm font-medium hover:border-zinc-500 transition-colors"
          >
            GitHub 仓库
          </a>
        </div>

        <div className="mt-8 text-sm text-zinc-500">
          <p>或通过 Git 克隆安装：</p>
          <pre className="mt-2 bg-zinc-900 border border-zinc-800 rounded-md p-3 text-sm text-zinc-300 inline-block">
            <code>git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling</code>
          </pre>
        </div>

        <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
          {[
            { value: '94', label: '文件数' },
            { value: '10,738', label: '文档总行数' },
            { value: 'v2.0.0', label: '当前版本' },
          ].map((s, i) => (
            <div key={i} className="border border-zinc-800 rounded-lg p-4 bg-zinc-900/30 text-center">
              <div className="text-2xl font-bold text-zinc-100">{s.value}</div>
              <div className="text-xs text-zinc-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
