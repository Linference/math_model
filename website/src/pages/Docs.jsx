import CodeBlock from '../components/CodeBlock'

const sections = [
  {
    id: 'requirements',
    title: '1. 系统要求',
    content: (
      <div className="space-y-3 text-sm text-slate-500">
        {[
          ['Python', '3.10 或更高版本。推荐 Anaconda（含 numpy/pandas/scipy/sklearn/matplotlib）'],
          ['Node.js', '18.x 或更高版本。Claude Code CLI 的运行环境'],
          ['LaTeX', 'Windows 装 MiKTeX，macOS/Linux 装 TeXLive。需含 xelatex'],
          ['Git', '用于克隆仓库。去 git-scm.com 下载'],
        ].map(([k, v]) => (
          <div key={k} className="flex items-start gap-3">
            <span className="text-green-600 font-medium shrink-0 w-20">{k}</span>
            <span>{v}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'nodejs',
    title: '2. 安装 Node.js',
    content: (
      <div className="space-y-4 text-sm text-slate-500">
        <p>打开终端，输入 <code className="text-green-600 bg-green-50 px-1.5 py-0.5 rounded text-xs font-mono">node --version</code>。≥ v18.0.0 则跳过。</p>
        <h4 className="font-semibold text-slate-700">Windows</h4>
        <ol className="list-decimal list-inside space-y-1">
          <li>打开 <a href="https://nodejs.org/zh-cn" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:underline">nodejs.org/zh-cn</a></li>
          <li>点击左侧绿色 LTS 按钮下载 .msi</li>
          <li>双击运行，一路 Next（保持默认选项）</li>
          <li>关闭终端重新打开，验证 <code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">node --version</code></li>
        </ol>
        <h4 className="font-semibold text-slate-700">macOS</h4>
        <CodeBlock code="brew install node" lang="bash" />
        <h4 className="font-semibold text-slate-700">Linux (Ubuntu/Debian)</h4>
        <CodeBlock code={`curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -\nsudo apt-get install -y nodejs`} lang="bash" />
      </div>
    ),
  },
  {
    id: 'claude-code',
    title: '3. 安装 Claude Code',
    content: (
      <div className="space-y-3 text-sm text-slate-500">
        <p>终端运行：</p>
        <CodeBlock code="npm install -g @anthropic-ai/claude-code" lang="bash" />
        <p>验证：</p>
        <CodeBlock code="claude --version" lang="bash" />
        <p>VSCode 用户也可在扩展商店搜索 <code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">Claude Code</code> 安装图形界面版。</p>
      </div>
    ),
  },
  {
    id: 'ccswitch',
    title: '4. 配置 CCSwitch（国内用户必读）',
    content: (
      <div className="space-y-4 text-sm">
        <div className="border border-green-200 bg-green-50 rounded-lg p-4 text-slate-600">
          Claude Code 的 API 在国内无法直连。CCSwitch 将请求转发到 DeepSeek V4 Pro。
        </div>

        <h4 className="font-semibold text-slate-700">步骤 1：下载 CCSwitch</h4>
        <p className="text-slate-500">打开 <a href="https://ccswitch.io" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:underline">ccswitch.io</a> → Download。Windows 下载 .msi，macOS 下载 .dmg 或用 <code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">brew install --cask cc-switch</code>。</p>

        <h4 className="font-semibold text-slate-700">步骤 2：获取 DeepSeek API Key</h4>
        <ol className="list-decimal list-inside space-y-1 text-slate-500">
          <li>打开 <a href="https://platform.deepseek.com" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:underline">platform.deepseek.com</a> 注册</li>
          <li>API Keys → 创建 Key → 复制保存</li>
        </ol>

        <h4 className="font-semibold text-slate-700">步骤 3：配置 CCSwitch</h4>
        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                <th className="text-left py-2.5 px-4 text-slate-500 font-medium">配置项</th>
                <th className="text-left py-2.5 px-4 text-slate-500 font-medium">填什么</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['提供商类型', 'DeepSeek'],
                ['API Key', '粘贴上一步复制的 Key'],
                ['模型', 'deepseek-chat（日常）/ deepseek-reasoner（推理）'],
                ['Base URL', '保持默认 https://api.deepseek.com'],
              ].map(([k, v], i) => (
                <tr key={i} className="border-b border-slate-50 last:border-0">
                  <td className="py-2.5 px-4 text-slate-700">{k}</td>
                  <td className="py-2.5 px-4 text-slate-500 font-mono text-xs">{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-slate-500">点「测试连接」→ 设为默认后端 →「启动代理」。</p>
      </div>
    ),
  },
  {
    id: 'install-skill',
    title: '5. 安装 Skills 包',
    content: (
      <div className="space-y-4 text-sm">
        <h4 className="font-semibold text-slate-700">方法 A：Git 克隆（推荐）</h4>
        <CodeBlock code="git clone https://github.com/Linference/math_model.git ~/.claude/skills/math-modeling" lang="bash" />
        <p className="text-xs text-slate-400">更新：<code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">cd ~/.claude/skills/math-modeling && git pull</code></p>

        <h4 className="font-semibold text-slate-700">方法 B：下载 ZIP</h4>
        <p className="text-slate-500">
          去 <a href="https://github.com/Linference/math_model/releases" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:underline">Releases</a> 下载 skill-v2.0.zip，
          解压到 <code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">~/.claude/skills/math-modeling/</code>
        </p>
        <p className="text-xs text-slate-400">Windows 路径：<code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">C:\Users\你的用户名\.claude\skills\math-modeling\</code></p>
      </div>
    ),
  },
  {
    id: 'doctor',
    title: '6. 环境自检',
    content: (
      <div className="space-y-3 text-sm text-slate-500">
        <p>运行 doctor.py 检查所有依赖：</p>
        <CodeBlock code="python ~/.claude/skills/math-modeling/scripts/doctor.py" lang="bash" />
        <p>37 项检查全部通过后即可开始。还支持 <code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">--json</code> 和 <code className="text-green-600 bg-green-50 px-1 py-0.5 rounded text-xs font-mono">--verbose</code>。</p>
      </div>
    ),
  },
  {
    id: 'start',
    title: '7. 启动建模流水线',
    content: (
      <div className="space-y-3 text-sm text-slate-500">
        <p>在 Claude Code 中输入：</p>
        <CodeBlock code={`/math-modeling\n\n[粘贴赛题原文，或拖入 PDF 文件]`} />
        <p>系统自动按 7 阶段执行，每阶段落盘验证后才进入下一阶段，5 道 Subagent 质检自动触发。</p>
      </div>
    ),
  },
  {
    id: 'pipeline',
    title: '8. 流水线详解',
    content: (
      <div className="border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <th className="text-left py-3 px-5 text-slate-500 font-medium w-12">阶段</th>
              <th className="text-left py-3 px-5 text-slate-500 font-medium">内容</th>
              <th className="text-left py-3 px-5 text-slate-500 font-medium">产出</th>
              <th className="text-left py-3 px-5 text-slate-500 font-medium">质检</th>
            </tr>
          </thead>
          <tbody className="text-slate-500">
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
              <tr key={i} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/50 transition-colors">
                <td className="py-3 px-5">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-green-50 text-green-600 font-medium">{row[0]}</span>
                </td>
                <td className="py-3 px-5 text-slate-700">{row[1]}</td>
                <td className="py-3 px-5">{row[2]}</td>
                <td className="py-3 px-5 text-slate-400 font-mono text-xs">{row[3]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    ),
  },
  {
    id: 'manual',
    title: '9. 手动单步操作',
    content: (
      <div className="space-y-3 text-sm text-slate-500">
        <p>不想走自动流水线？手动执行每个步骤：</p>
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
    ),
  },
  {
    id: 'structure',
    title: '10. 项目结构说明',
    content: (
      <CodeBlock code={`math_model/
├── README.md
├── samples/                    # 两个完整示例
│   ├── 2024_CUMCM_A/           # 国赛A题：板凳龙
│   └── 2025_HiMCM_Problem_B/   # HiMCM B题：超级碗选址
└── skill/                      # Skills 安装包
    ├── SKILL.md                # 主技能定义
    ├── CHANGELOG.md            # 更新日志
    ├── references/             # 15本参考手册
    │   ├── 01-05 审题/建模/数据/算法/可视化
    │   ├── 06-10 写作/审稿/验证/创新/技巧
    │   ├── 11-anti-patterns.md # 反模式手册
    │   ├── 12-data-sources.md  # 数据源大全
    │   ├── 13-phrase-bank.md   # 中英句式库
    │   ├── 14-playbook-guide.md
    │   ├── 15-scoring-rubric.md# 评分细则
    │   └── cookbooks/          # 6本独立算法手册
    ├── scripts/                # 6个辅助脚本
    │   ├── doctor.py           # 环境自检
    │   ├── new_project.py      # 新建项目
    │   ├── fetch_data.py       # 数据获取
    │   ├── plot_helpers.py     # 图表绘制
    │   ├── compile.py          # LaTeX编译
    │   └── verify_results.py   # 交叉验证
    ├── state/                  # 状态管理
    ├── templates/              # LaTeX模板
    └── workflows/              # 工作流脚本`} />
    ),
  },
  {
    id: 'faq',
    title: '11. 常见问题',
    content: (
      <div className="space-y-3">
        {[
          { q: '没有 LaTeX 怎么办？', a: '建模和写代码不需要 LaTeX。需要编译 PDF 时才装 MiKTeX (Windows) 或 TeXLive。' },
          { q: '能用 ChatGPT 代替 Claude Code 吗？', a: '把 skill/SKILL.md 当系统提示词，手动按流水线一步步让 ChatGPT 帮你做。效果一样，但没有自动编排。' },
          { q: 'DeepSeek 够用吗？', a: 'DeepSeek V4 Pro 在数学推理和中文写作上很强，配合本 Skill 的手动流程完全够用。自动编排和 Subagent 质检需要 Claude Code。' },
          { q: '论文质量怎么样？', a: '经过三角色对抗审稿（4轮迭代，均分≥7.5/10）后，论文质量达到可提交水平。最终需要你自己审阅修改。' },
          { q: '支持什么竞赛？', a: '国赛 CUMCM（中文）、美赛 MCM/ICM（英文）、HiMCM 高中生建模。中英双版 LaTeX 模板已就绪。' },
          { q: '数据来源可靠吗？', a: '数据猎人优先使用权威来源（World Bank/WHO/NOAA/国家统计局），所有来源记录在 SOURCES.md。模拟数据显著标注。' },
        ].map((faq, i) => (
          <details key={i} className="border border-slate-200 rounded-xl bg-white/80 backdrop-blur-sm group">
            <summary className="px-5 py-4 cursor-pointer text-sm font-medium text-slate-700 hover:text-slate-900 transition-colors select-none">
              {faq.q}
            </summary>
            <div className="px-5 pb-4 text-sm text-slate-500 leading-relaxed border-t border-slate-100 pt-3">
              {faq.a}
            </div>
          </details>
        ))}
      </div>
    ),
  },
]

export default function Docs() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-16 fade-in">
        <h1 className="text-3xl font-bold text-slate-900 mb-3">使用文档</h1>
        <p className="text-slate-500">从零搭建环境到跑出第一篇论文的完整指南</p>
      </div>

      {/* Quick nav */}
      <nav className="border border-slate-200 rounded-xl p-5 mb-16 fade-in fade-in-1 text-sm bg-white/80 backdrop-blur-sm">
        <h3 className="text-slate-700 font-semibold mb-3">目录</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-500">
          {sections.map((s, i) => (
            <a key={s.id} href={`#${s.id}`} className="hover:text-slate-700 transition-colors">
              {s.title}
            </a>
          ))}
        </div>
      </nav>

      {/* Sections */}
      <div className="space-y-16">
        {sections.map((s, i) => (
          <section key={s.id} id={s.id} className={`fade-in fade-in-${Math.min((i % 4) + 1, 4)}`}>
            <h2 className="text-xl font-bold text-slate-800 mb-4">{s.title}</h2>
            <div className="border border-slate-200 rounded-xl p-6 bg-white/80 backdrop-blur-sm">
              {s.content}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
