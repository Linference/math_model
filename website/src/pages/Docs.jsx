import CodeBlock from '../components/CodeBlock'

export default function Docs() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-16 fade-in">
        <h1 className="text-3xl font-bold text-zinc-100 mb-3">使用文档</h1>
        <p className="text-zinc-500">从零搭建环境到跑出第一篇论文的完整指南</p>
      </div>

      {/* TOC */}
      <nav className="glass rounded-xl p-5 mb-12 fade-in fade-in-1 text-sm">
        <h3 className="text-zinc-300 font-semibold mb-3">目录</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-zinc-500">
          {[
            '系统要求', '安装 Node.js', '安装 Claude Code',
            '配置 CCSwitch（国内用户必读）', '安装 Skills 包',
            '环境自检', '启动建模流水线', '流水线详解',
            '手动单步操作', '项目结构说明', '常见问题'
          ].map((item, i) => (
            <a key={i} href={`#section-${i}`} className="hover:text-zinc-300 transition-colors">
              {i + 1}. {item}
            </a>
          ))}
        </div>
      </nav>

      {/* Section 0: 系统要求 */}
      <section id="section-0" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">1. 系统要求</h2>
        <div className="glass rounded-xl p-6 space-y-3 text-sm text-zinc-400">
          <div className="flex items-start gap-3">
            <span className="text-green-400 mt-0.5">Python</span>
            <span>3.10 或更高版本。推荐 <a href="https://www.anaconda.com/" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">Anaconda</a>（含 numpy/pandas/scipy/sklearn/matplotlib）</span>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-green-400 mt-0.5">Node.js</span>
            <span>18.x 或更高版本。Claude Code CLI 的运行环境</span>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-green-400 mt-0.5">LaTeX</span>
            <span>Windows 装 <a href="https://miktex.org/" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">MiKTeX</a>，macOS/Linux 装 <a href="https://tug.org/texlive/" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">TeXLive</a>。用于编译论文 PDF，需含 xelatex</span>
          </div>
          <div className="flex items-start gap-3">
            <span className="text-green-400 mt-0.5">Git</span>
            <span>用于克隆仓库。没有的话去 <a href="https://git-scm.com/" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">git-scm.com</a> 下载</span>
          </div>
        </div>
      </section>

      {/* Section 1: 安装 Node.js */}
      <section id="section-1" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">2. 安装 Node.js</h2>
        <div className="glass rounded-xl p-6 space-y-4">
          <p className="text-sm text-zinc-400">
            打开终端，输入 <code className="text-green-400 bg-white/5 px-1.5 py-0.5 rounded text-xs">node --version</code>。如果显示 ≥ v18.0.0，跳过此步。
          </p>
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-zinc-300">Windows</h4>
            <ol className="text-sm text-zinc-400 list-decimal list-inside space-y-1">
              <li>打开 <a href="https://nodejs.org/zh-cn" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">nodejs.org/zh-cn</a></li>
              <li>点击左侧绿色 LTS 按钮下载 .msi 安装包</li>
              <li>双击运行，一路点 Next（所有选项保持默认）</li>
              <li>关闭终端重新打开，输入 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">node --version</code> 验证</li>
            </ol>
          </div>
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-zinc-300">macOS</h4>
            <CodeBlock code={`brew install node`} lang="bash" />
          </div>
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-zinc-300">Linux (Ubuntu/Debian)</h4>
            <CodeBlock code={`curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -\nsudo apt-get install -y nodejs`} lang="bash" />
          </div>
        </div>
      </section>

      {/* Section 2: 安装 Claude Code */}
      <section id="section-2" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">3. 安装 Claude Code</h2>
        <div className="glass rounded-xl p-6 space-y-3">
          <p className="text-sm text-zinc-400">打开终端，运行以下命令全局安装：</p>
          <CodeBlock code={`npm install -g @anthropic-ai/claude-code`} lang="bash" />
          <p className="text-sm text-zinc-400">验证：</p>
          <CodeBlock code={`claude --version`} lang="bash" />
          <p className="text-sm text-zinc-500 mt-3">
            VSCode 用户也可直接在扩展商店搜索 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">Claude Code</code> 安装图形界面版。
          </p>
        </div>
      </section>

      {/* Section 3: CCSwitch */}
      <section id="section-3" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">4. 配置 CCSwitch（国内用户必读）</h2>
        <div className="glass rounded-xl p-6 space-y-4">
          <div className="border border-green-500/20 bg-green-500/5 rounded-lg p-4 text-sm text-zinc-300">
            Claude Code 的 API 在国内无法直连。CCSwitch 将请求转发到 DeepSeek V4 Pro，国内可用。
          </div>

          <h4 className="text-sm font-semibold text-zinc-300">步骤 1：下载 CCSwitch</h4>
          <p className="text-sm text-zinc-400">
            打开 <a href="https://ccswitch.io" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">ccswitch.io</a>，点 Download。
            Windows 下载 .msi，macOS 下载 .dmg 或用 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">brew install --cask cc-switch</code>。
          </p>

          <h4 className="text-sm font-semibold text-zinc-300">步骤 2：获取 DeepSeek API Key</h4>
          <ol className="text-sm text-zinc-400 list-decimal list-inside space-y-1">
            <li>打开 <a href="https://platform.deepseek.com" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">platform.deepseek.com</a> 注册</li>
            <li>左侧菜单 → API Keys → 创建 Key → 复制保存</li>
          </ol>

          <h4 className="text-sm font-semibold text-zinc-300">步骤 3：配置</h4>
          <div className="glass rounded-lg p-4 text-sm text-zinc-400">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="text-left py-2 text-zinc-500 font-normal">配置项</th>
                  <th className="text-left py-2 text-zinc-500 font-normal">填什么</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-white/[0.03]">
                  <td className="py-2 text-zinc-300">提供商类型</td>
                  <td className="py-2">DeepSeek</td>
                </tr>
                <tr className="border-b border-white/[0.03]">
                  <td className="py-2 text-zinc-300">API Key</td>
                  <td className="py-2">粘贴上一步复制的 Key</td>
                </tr>
                <tr className="border-b border-white/[0.03]">
                  <td className="py-2 text-zinc-300">模型</td>
                  <td className="py-2"><code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">deepseek-chat</code> (日常) 或 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">deepseek-reasoner</code> (推理)</td>
                </tr>
                <tr>
                  <td className="py-2 text-zinc-300">Base URL</td>
                  <td className="py-2">保持默认 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">https://api.deepseek.com</code></td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-sm text-zinc-400">点「测试连接」，提示成功后设为默认后端，点「启动代理」。</p>
        </div>
      </section>

      {/* Section 4: 安装 Skills */}
      <section id="section-4" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">5. 安装 Skills 包</h2>
        <div className="glass rounded-xl p-6 space-y-4">
          <h4 className="text-sm font-semibold text-zinc-300">方法 A：Git 克隆（推荐）</h4>
          <CodeBlock code={`git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling`} lang="bash" />
          <p className="text-xs text-zinc-500">后续更新：<code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">cd ~/.claude/skills/math-modeling && git pull</code></p>

          <h4 className="text-sm font-semibold text-zinc-300">方法 B：下载 ZIP</h4>
          <p className="text-sm text-zinc-400">
            去 <a href="https://github.com/Linference/math_model/releases" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">Releases 页面</a> 下载
            <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">skill-v2.0.zip</code>，
            解压到 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">~/.claude/skills/math-modeling/</code>
          </p>
          <p className="text-xs text-zinc-500">
            Windows 路径：<code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">C:\Users\你的用户名\.claude\skills\math-modeling\</code>
          </p>
        </div>
      </section>

      {/* Section 5: 环境自检 */}
      <section id="section-5" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">6. 环境自检</h2>
        <div className="glass rounded-xl p-6 space-y-3">
          <p className="text-sm text-zinc-400">运行 doctor.py 检查所有依赖是否就绪：</p>
          <CodeBlock code={`python ~/.claude/skills/math-modeling/scripts/doctor.py`} lang="bash" />
          <p className="text-sm text-zinc-400">37 项检查全部通过后即可开始建模。</p>
          <p className="text-xs text-zinc-500">还支持 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">--json</code> 输出和 <code className="text-green-400 bg-white/5 px-1 py-0.5 rounded text-xs">--verbose</code> 详细模式。</p>
        </div>
      </section>

      {/* Section 6: 启动 */}
      <section id="section-6" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">7. 启动建模流水线</h2>
        <div className="glass rounded-xl p-6 space-y-4">
          <p className="text-sm text-zinc-400">在 Claude Code 终端中输入：</p>
          <CodeBlock code={`/math-modeling\n\n[粘贴赛题原文，或拖入 PDF 文件]`} />
          <p className="text-sm text-zinc-400">
            系统会自动按 7 阶段执行：审题 → 选方法 → 找数据 → 求解 → 画图 → 写论文编译 → 对抗审稿。
            每阶段落盘验证后才进入下一阶段，5 道 Subagent 质检门禁自动触发。
          </p>
        </div>
      </section>

      {/* Section 7: 流程详解 */}
      <section id="section-7" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">8. 流水线详解</h2>
        <div className="glass rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left py-3 px-5 text-zinc-400 font-medium w-12">阶段</th>
                <th className="text-left py-3 px-5 text-zinc-400 font-medium">内容</th>
                <th className="text-left py-3 px-5 text-zinc-400 font-medium">产出</th>
                <th className="text-left py-3 px-5 text-zinc-400 font-medium">质检</th>
              </tr>
            </thead>
            <tbody className="text-zinc-400">
              {[
                ['0', '建立工作目录', '项目骨架 + decision_log.json', '—'],
                ['1', '深度审题', '审题报告 (≥2000字)', 'M1: mm-verifier'],
                ['2', '方法选型', '建模方案表 + ML/DL决策', '—'],
                ['3', '数据获取', 'CSV文件 + SOURCES.md', '—'],
                ['4', '编程求解', 'code/solve_qN.py + 结果', 'P1→编码→P2'],
                ['5', '可视化', 'figures/*.png (300dpi)', '—'],
                ['6', '论文写作', 'main.pdf', 'W1→写作→W2'],
                ['7', '对抗审稿', '终版PDF + 评分记录', '均分≥7.5'],
              ].map((row, i) => (
                <tr key={i} className="border-b border-white/[0.03] last:border-0 hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-5">
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-white/5 text-green-400">{row[0]}</span>
                  </td>
                  <td className="py-3 px-5 text-zinc-300">{row[1]}</td>
                  <td className="py-3 px-5">{row[2]}</td>
                  <td className="py-3 px-5 text-zinc-500 font-mono text-xs">{row[3]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 8: 手动操作 */}
      <section id="section-8" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">9. 手动单步操作</h2>
        <div className="glass rounded-xl p-6 space-y-4">
          <p className="text-sm text-zinc-400">不想走自动流水线？可以手动执行每个步骤：</p>
          <CodeBlock code={`# 新建项目骨架（zh=国赛 / en=美赛）
python skill/scripts/new_project.py "2024国赛A题" --lang zh

# 联网找数据
python skill/scripts/fetch_data.py --sklearn iris
python skill/scripts/fetch_data.py --worldbank EN.ATM.CO2E.KT
python skill/scripts/fetch_data.py --search "climate energy"

# 数据质量检查
python skill/scripts/fetch_data.py --quality data/cities.csv

# 编译论文
python skill/scripts/compile.py 项目文件夹/paper/main.tex

# 交叉验证（代码 vs 论文数字）
python skill/scripts/verify_results.py 项目文件夹`} lang="bash" />
        </div>
      </section>

      {/* Section 9: 项目结构 */}
      <section id="section-9" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">10. 项目结构说明</h2>
        <div className="glass rounded-xl p-6">
          <CodeBlock code={`math_model/
├── README.md
├── samples/                    # 两个完整示例
│   ├── 2024_CUMCM_A/           # 国赛A题：板凳龙
│   └── 2025_HiMCM_Problem_B/   # HiMCM B题：超级碗选址
└── skill/                      # Skills 安装包
    ├── SKILL.md                # 主技能定义（7阶段+8Agent+5门禁）
    ├── CHANGELOG.md            # 更新日志
    ├── references/             # 15本参考手册
    │   ├── 01-10               # 审题→建模→数据→算法→可视化→写作→审稿→验证→创新→技巧
    │   ├── 11-anti-patterns.md # 反模式手册（24个常见错误）
    │   ├── 12-data-sources.md  # 数据源大全
    │   ├── 13-phrase-bank.md   # 中英句式库
    │   ├── 14-playbook-guide.md# Playbook指南
    │   ├── 15-scoring-rubric.md# 评分细则
    │   └── cookbooks/          # 6本独立算法手册
    ├── scripts/                # 6个辅助脚本
    │   ├── doctor.py           # 环境自检（37项检查）
    │   ├── new_project.py      # 新建项目
    │   ├── fetch_data.py       # 数据获取
    │   ├── plot_helpers.py     # 图表绘制（16种）
    │   ├── compile.py          # LaTeX编译
    │   └── verify_results.py   # 交叉验证
    ├── state/                  # 状态管理
    │   └── decision_log.json   # 跨阶段决策日志
    ├── templates/              # LaTeX模板
    └── workflows/              # 工作流脚本`} lang="" />
        </div>
      </section>

      {/* Section 10: FAQ */}
      <section id="section-10" className="mb-16 fade-in">
        <h2 className="text-xl font-bold text-zinc-100 mb-4">11. 常见问题</h2>
        <div className="space-y-3">
          {[
            { q: '没有 LaTeX 怎么办？', a: '如果只是建模和写代码，不需要 LaTeX。需要编译 PDF 时才装 MiKTeX (Windows) 或 TeXLive (macOS/Linux)。' },
            { q: '能用 ChatGPT 代替 Claude Code 吗？', a: '把 skill/SKILL.md 当系统提示词，手动按流水线一步步让 ChatGPT 帮你做。效果一样，但没有自动编排。' },
            { q: 'DeepSeek 够用吗？', a: 'DeepSeek V4 Pro 在数学推理和中文写作上很强，配合本 Skill 的手动流程完全够用。自动编排和 Subagent 质检需要 Claude Code。' },
            { q: '论文质量怎么样？', a: '经过三角色对抗审稿（4轮迭代，均分≥7.5/10）后，论文质量达到可提交水平。但最终需要你自己审阅和修改。' },
            { q: '支持什么竞赛？', a: '国赛 CUMCM（中文）、美赛 MCM/ICM（英文）、HiMCM 高中生数学建模。中英双版 LaTeX 模板均已就绪。' },
            { q: '数据来源可靠吗？', a: '数据猎人优先使用权威来源（World Bank/WHO/NOAA/国家统计局），所有数据来源记录在 SOURCES.md 中可追溯。模拟数据会显著标注。' },
          ].map((faq, i) => (
            <details key={i} className="glass rounded-xl group">
              <summary className="px-5 py-4 cursor-pointer text-sm font-medium text-zinc-300 hover:text-zinc-100 transition-colors select-none">
                {faq.q}
              </summary>
              <div className="px-5 pb-4 text-sm text-zinc-400 leading-relaxed">
                {faq.a}
              </div>
            </details>
          ))}
        </div>
      </section>
    </div>
  )
}
