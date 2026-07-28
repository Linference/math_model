export default function Setup() {
  return (
    <section id="setup" className="py-24 px-6 border-t border-zinc-800/50">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-zinc-100">安装</h2>
          <p className="mt-3 text-zinc-500">三步跑起来</p>
        </div>

        <div className="space-y-8">
          <div className="border border-zinc-800 rounded-lg p-6 bg-zinc-900/30">
            <div className="flex items-center gap-3 mb-4">
              <span className="flex items-center justify-center w-7 h-7 rounded bg-zinc-800 text-zinc-300 text-xs font-mono font-bold">1</span>
              <h3 className="text-sm font-semibold text-zinc-200">安装 CCSwitch + Claude Code</h3>
            </div>
            <p className="text-sm text-zinc-500 mb-3">
              国内用户用 CCSwitch 将 Claude Code 请求转发到 DeepSeek，直连可用。
              先去 <a href="https://ccswitch.io" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">ccswitch.io</a> 下载 CCSwitch，
              配置 DeepSeek API Key（<a href="https://platform.deepseek.com" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">platform.deepseek.com</a> 注册获取）。
            </p>
            <pre className="bg-zinc-950 border border-zinc-800 rounded-md p-4 text-sm text-zinc-300 overflow-x-auto">
              <code>{`npm install -g @anthropic-ai/claude-code    # 安装 Claude Code
claude --version                                # 验证安装`}</code>
            </pre>
            <p className="mt-2 text-xs text-zinc-600">需要 Node.js ≥ 18.x — <a href="https://nodejs.org/zh-cn" target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-zinc-300">nodejs.org/zh-cn</a></p>
          </div>

          <div className="border border-zinc-800 rounded-lg p-6 bg-zinc-900/30">
            <div className="flex items-center gap-3 mb-4">
              <span className="flex items-center justify-center w-7 h-7 rounded bg-zinc-800 text-zinc-300 text-xs font-mono font-bold">2</span>
              <h3 className="text-sm font-semibold text-zinc-200">安装 Skills 包</h3>
            </div>
            <pre className="bg-zinc-950 border border-zinc-800 rounded-md p-4 text-sm text-zinc-300 overflow-x-auto">
              <code>{`git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling`}</code>
            </pre>
            <p className="mt-2 text-xs text-zinc-500">
              或去 <a href="#download" className="text-green-400 hover:underline">下载页面</a> 下载 ZIP，解压到 <span className="font-mono text-zinc-400">~/.claude/skills/math-modeling/</span>
            </p>
          </div>

          <div className="border border-zinc-800 rounded-lg p-6 bg-zinc-900/30">
            <div className="flex items-center gap-3 mb-4">
              <span className="flex items-center justify-center w-7 h-7 rounded bg-zinc-800 text-zinc-300 text-xs font-mono font-bold">3</span>
              <h3 className="text-sm font-semibold text-zinc-200">启动建模</h3>
            </div>
            <p className="text-sm text-zinc-500 mb-3">在 Claude Code 中输入以下内容，粘贴赛题原文即可：</p>
            <pre className="bg-zinc-950 border border-zinc-800 rounded-md p-4 text-sm text-zinc-300 overflow-x-auto">
              <code>{`/math-modeling

[粘贴赛题原文或拖入 PDF 文件]`}</code>
            </pre>
            <p className="mt-2 text-xs text-zinc-500">系统自动按 7 阶段执行，每阶段落盘验证后才进入下一阶段。</p>
          </div>
        </div>
      </div>
    </section>
  )
}
