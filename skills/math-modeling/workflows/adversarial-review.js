export const meta = {
  name: 'mm-adversarial-review',
  description: '数学建模论文多智能体对抗审稿：写作者↔审稿人/验证者/推理者并行挑战，≤4轮，评分达7.5停',
  whenToUse: '已有一份论文草稿（paper/main.tex 或 REPORT.md 内容）需要通过对抗协作提升到国赛级别时',
  phases: [
    { title: 'Algorithm Audit', detail: '自动化算法审计：代码可运行性+公式一致性+数字可追溯' },
    { title: 'Baseline', detail: '三评审并行给出基线评分与弱点' },
    { title: 'Revise', detail: '写作者按意见修改' },
    { title: 'Re-review', detail: '三评审复评，判定是否达标' },
  ],
}

// args: { draftPath, lang, targetScore, maxRounds, dataContext, projectRoot }
const draftPath = (args && args.draftPath) || 'paper/main.tex'
const lang = (args && args.lang) || 'zh'
const TARGET = (args && args.targetScore) || 7.5
const MAX_ROUNDS = Math.min((args && args.maxRounds) || 4, 4)
const dataContext = (args && args.dataContext) || ''
const projectRoot = (args && args.projectRoot) || '.'

// 结构化打分 schema：三评审各自输出
const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    score: { type: 'number', description: '0-10 综合评分' },
    dimensions: {
      type: 'object',
      properties: {
        modeling: { type: 'number' },      // 建模合理性
        rigor: { type: 'number' },         // 数学严谨性/推导正确
        results: { type: 'number' },       // 结果与验证充分性
        writing: { type: 'number' },       // 表达与图表规范
        innovation: { type: 'number' },    // 创新性
      },
      required: ['modeling', 'rigor', 'results', 'writing', 'innovation'],
    },
    weaknesses: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          where: { type: 'string' },       // 定位：章节/公式/图
          issue: { type: 'string' },       // 问题
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          fix: { type: 'string' },         // 建议修法
        },
        required: ['where', 'issue', 'severity', 'fix'],
      },
    },
    needMoreExperiments: { type: 'boolean' }, // 是否需自动补充实验
    verdict: { type: 'string', enum: ['accept', 'revise', 'reject'] },
  },
  required: ['score', 'dimensions', 'weaknesses', 'needMoreExperiments', 'verdict'],
}

const langNote = lang === 'en' ? 'The paper is in English (MCM/ICM).'
  : '论文为中文（国赛 CUMCM），评审与建议用中文。'

function reviewPrompt(role, roleDesc, draft) {
  return `你是数学建模论文评审中的【${role}】。${roleDesc}
${langNote}

评分口径（国赛级别，7.5=省一以上，5.0=基本完成）：
- 严格、对抗性地找问题，默认草稿有缺陷，宁可挑刺也不放水。
- 从你的角色视角切入，不要泛泛而谈；每条弱点必须能定位到具体章节/公式/图/数据。

待审论文/草稿内容：
<<<
${draft.slice(0, 18000)}
>>>
${dataContext ? '\n数据与结果背景：\n' + dataContext.slice(0, 4000) : ''}

⛔ 你是只读评审：不得修改任何文件（不 Edit/Write/删除），只输出评估结果。
按 schema 输出：综合评分、五维度分、弱点清单(含定位/严重度/修法)、是否需补实验、结论。`
}

const ROLES = [
  ['审稿人', `你负责批判审稿、定位弱点：
    - 建模是否合理、假设是否牵强、逻辑链是否完整
    - 创新点是否真实且有价值（而非包装旧方法）——检查论文是否显式声明了创新且提供了创新 vs 无创新的对比
    - 表达与图表是否规范
    - 参考 innovation 评分维度：创新是否有用（9-10）、有改进但未充分证明（7-8）、声明了但缺对比（5-6）、伪创新（<5）`],
  ['验证者', `你负责交叉验证与检查：
    - 数值结果是否可复现（代码输出与论文数字是否一致）
    - 量纲/边界/单位是否正确
    - 结论与数据是否自洽
    - 有无算术或统计错误
    - 创新声明的数值支撑是否真实（改进 X% 这个数字能否复现）`],
  ['推理者', `你负责深度推理与数学证明：
    - 公式推导是否严谨、模型假设到结论的每一步是否成立
    - 是否存在未证断言、能否给出更严格论证
    - 创新策略的数学基础是否成立（如"自适应权重"的数学定义是否清晰）
    - 方法组合创新的接口是否数学上自洽`],
]

// 读取草稿（用一个只读 agent 取回内容，避免脚本直接读文件）
async function loadDraft() {
  const txt = await agent(
    `读取文件 ${draftPath} 的完整文本内容并原样返回（不要总结、不要加解释）。若文件不存在，返回字符串 "MISSING"。`,
    { label: 'load-draft', phase: 'Baseline', agentType: 'mm-verifier' }
  )
  return txt || 'MISSING'
}

function panelReview(draft, phase) {
  return parallel(ROLES.map(([role, desc]) => () =>
    agent(reviewPrompt(role, desc, draft),
      { label: `review:${role}`, phase, schema: REVIEW_SCHEMA, agentType: 'mm-reviewer' })
      .then(r => { if (r) r._role = role; return r })
  ))
}

// 角色×维度权重矩阵（来自 07-adversarial-review.md §1.3 + 15-scoring-rubric.md §4.1）
const ROLE_WEIGHTS = {
  '审稿人':   { modeling: 0.50, rigor: 0.20, results: 0.20, writing: 0.70, innovation: 0.60 },
  '验证者':   { modeling: 0.20, rigor: 0.30, results: 0.60, writing: 0.10, innovation: 0.10 },
  '推理者':   { modeling: 0.30, rigor: 0.50, results: 0.20, writing: 0.20, innovation: 0.30 },
}
const DIM_WEIGHTS = { modeling: 0.25, rigor: 0.25, results: 0.25, writing: 0.15, innovation: 0.10 }
const DIM_NAMES = ['modeling', 'rigor', 'results', 'writing', 'innovation']

// 聚合规则（来自 15-scoring-rubric.md §4.1–4.3）：
//   步骤 1：每个维度按角色权重加权聚合
//   步骤 2：维度加权得综合分
//   步骤 3：应用硬上限规则
//   步骤 4：离群值仲裁（极差 ≥ 4.0 → 中位数）
function aggregate(reviews) {
  const valid = reviews.filter(Boolean)
  if (!valid.length) return { avg: 0, dimScores: {}, reviews: [], allWeak: [], needExp: false, arbitrated: false }

  // 步骤 1：维度级加权聚合
  const dimScores = {}
  for (const dim of DIM_NAMES) {
    let weightedSum = 0, weightSum = 0
    const dimVals = []
    for (const r of valid) {
      if (r.dimensions && typeof r.dimensions[dim] === 'number') {
        // 根据角色名匹配权重；若 agent 角色名未在 ROLE_WEIGHTS 中 → 回退为等权
        const roleKey = Object.keys(ROLE_WEIGHTS).find(k => r._role && r._role.includes(k))
        const w = roleKey ? (ROLE_WEIGHTS[roleKey][dim] || 1/3) : 1/3
        weightedSum += r.dimensions[dim] * w
        weightSum += w
        dimVals.push(r.dimensions[dim])
      }
    }
    // 离群值仲裁：极差 ≥ 4.0 → 中位数
    if (dimVals.length >= 2) {
      const range = Math.max(...dimVals) - Math.min(...dimVals)
      if (range >= 4.0) {
        dimVals.sort((a, b) => a - b)
        const mid = Math.floor(dimVals.length / 2)
        dimScores[dim] = dimVals.length % 2 ? dimVals[mid] : (dimVals[mid - 1] + dimVals[mid]) / 2
        dimScores._arbitrated = dimScores._arbitrated || []
        dimScores._arbitrated.push(dim)
        continue
      }
    }
    dimScores[dim] = weightSum > 0 ? weightedSum / weightSum : 0
  }

  // 步骤 2：维度加权 → 综合分
  let composite = 0
  for (const dim of DIM_NAMES) {
    composite += (dimScores[dim] || 0) * (DIM_WEIGHTS[dim] || 0)
  }

  // 步骤 3：硬上限规则（来自 15-scoring-rubric.md §4.2）
  const caps = []
  if (dimScores.rigor < 5)                     caps.push({ cap: 6.0, reason: 'rigor < 5 → 综合分 ≤ 6.0' })
  if (dimScores.results < 5)                   caps.push({ cap: 5.5, reason: 'results < 5 → 综合分 ≤ 5.5' })
  if (dimScores.modeling < 3)                  caps.push({ cap: 4.0, reason: 'modeling < 3 → 综合分 ≤ 4.0' })
  if (DIM_NAMES.some(d => dimScores[d] < 3))   caps.push({ cap: 4.0, reason: '任一维度 < 3 → 综合分 ≤ 4.0' })
  if (DIM_NAMES.filter(d => dimScores[d] < 5).length >= 2)
    caps.push({ cap: 5.0, reason: '两个及以上维度 < 5 → 综合分 ≤ 5.0' })

  for (const c of caps) {
    if (composite > c.cap) { composite = c.cap }
  }
  const effectiveCap = caps.length ? Math.min(...caps.map(c => c.cap)) : 10
  composite = Math.min(composite, effectiveCap)

  const avg = Math.round(composite * 100) / 100
  const allWeak = valid.flatMap(r => r.weaknesses || [])
  const needExp = valid.some(r => r.needMoreExperiments)
  const arbitrated = !!dimScores._arbitrated

  return { avg, dimScores, reviews: valid, allWeak, needExp, arbitrated, hardCaps: caps }
}

// ---- 主流程 ----
let draft = await loadDraft()
if (draft === 'MISSING' || draft.length < 50) {
  log(`⚠️ 未找到有效草稿于 ${draftPath}，请先生成论文草稿再运行对抗审稿。`)
  return { error: 'no draft', draftPath }
}

// 算法审计结构化输出 schema
const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    codeRunnable: { type: 'boolean' },
    randomSeedFixed: { type: 'boolean' },
    formulaConsistency: { type: 'boolean' },
    numberTraceable: { type: 'boolean' },
    unitConsistency: { type: 'boolean' },
    auditPassed: { type: 'boolean' },
    failedItems: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          check: { type: 'string' },
          file: { type: 'string' },
          detail: { type: 'string' },
        },
        required: ['check', 'detail'],
      },
    },
    summary: { type: 'string' },
  },
  required: ['codeRunnable', 'randomSeedFixed', 'formulaConsistency', 'numberTraceable', 'unitConsistency', 'auditPassed'],
}

// ⛔ 阶段 A：算法审计（审稿前必须执行的自动化验证）
phase('Algorithm Audit')
log('🔍 执行算法审计：代码可运行性 + 公式一致性 + 数字可追溯...')
const auditResult = await agent(
  `你是数学建模的【验证者】。在正式审稿之前，先执行自动化算法审计。

请在终端依次运行以下命令，并报告结果：
1. python ${projectRoot}/scripts/verify_results.py . --stage 4
   （验证：代码可运行、随机种子、量纲一致性、关键数字可追溯）

审计重点：
- 每个 solve_q*.py 是否都能跑通？
- 代码中的公式实现是否与 REPORT.md §2 方案表一致？
- 论文中引用的关键数字是否能在代码输出中找到对应来源？
- 有无量纲混用（如 kgCO2e 和 tCO2e 混用）？

按 schema 输出审计报告，auditPassed 仅在所有检查项全部通过时才为 true。
若任何一项 FAIL，auditPassed 必须为 false，并在 failedItems 中逐条列出。`,
  { label: 'audit:algorithm', phase: 'Algorithm Audit', agentType: 'mm-verifier', schema: AUDIT_SCHEMA }
)
log(`算法审计: ${auditResult?.auditPassed ? '✅ PASS' : '❌ FAIL'} — ${(auditResult?.summary || '').slice(0, 200)}`)
if (auditResult?.failedItems?.length) {
  for (const f of auditResult.failedItems) {
    log(`  ❌ ${f.check}: ${f.file || ''} — ${f.detail}`)
  }
}

// 使用结构化字段判定（替代原先脆弱的字符串匹配）
const auditFailed = !auditResult || !auditResult.auditPassed
if (auditFailed) {
  log('⛔ 算法审计未通过，中止审稿。请先修复代码问题后重新运行。')
  return { error: 'algorithm audit failed', auditResult }
}

phase('Baseline')
// 基线编译并留存版本
log('编译基线 PDF 并留存版本...')
await agent(
  `在终端运行: python ${projectRoot}/scripts/compile.py ${draftPath}
编译完成后确认 PDF 是否生成成功。不要修改任何文件，只运行编译命令并报告结果。`,
  { label: 'compile:baseline', phase: 'Baseline', agentType: 'mm-writer' }
)

let agg = aggregate(await panelReview(draft, 'Baseline'))
log(`基线评分: ${agg.avg.toFixed(2)} / 10（弱点 ${agg.allWeak.length} 条${agg.needExp ? '，需补实验' : ''}${agg.arbitrated ? ' ⚠️ 触发仲裁' : ''}）`)
if (agg.dimScores && !agg.dimScores._arbitrated) {
  log(`  维度: M=${agg.dimScores.modeling?.toFixed(1)} R=${agg.dimScores.rigor?.toFixed(1)} Res=${agg.dimScores.results?.toFixed(1)} W=${agg.dimScores.writing?.toFixed(1)} I=${agg.dimScores.innovation?.toFixed(1)}`)
}
if (agg.hardCaps?.length) {
  for (const c of agg.hardCaps) log(`  ⚠️ 硬上限触发: ${c.reason}`)
}
if (agg.arbitrated) {
  log(`  ⚠️ 仲裁维度: ${(agg.dimScores._arbitrated || []).join(', ')}（极差≥4.0，取中位数）`)
}

const history = [{ round: 0, score: agg.avg, weaknesses: agg.allWeak.length }]

for (let round = 1; round <= MAX_ROUNDS && agg.avg < TARGET; round++) {
  phase('Revise')
  // 高优先级弱点优先修
  const sorted = agg.allWeak.slice().sort((a, b) =>
    ({ high: 0, medium: 1, low: 2 }[a.severity] - { high: 0, medium: 1, low: 2 }[b.severity]))
  const punch = sorted.slice(0, 12).map((w, i) =>
    `${i + 1}. [${w.severity}] ${w.where} — ${w.issue}\n   修法: ${w.fix}`).join('\n')

  const expNote = agg.needExp
    ? '\n【自动补充实验】评审认为结果不足，请补充：灵敏度分析/对照实验/更多情形，并把新结果写入论文与图表。'
    : ''

  const revised = await agent(
`你是数学建模论文的【写作者】。这是第 ${round} 轮修改。
${langNote}
根据以下评审意见，直接修改论文文件 ${draftPath}（用 Edit/Write 落盘），并同步更新相关图表/代码：
${punch}${expNote}

修改要求：
- 逐条回应弱点，不要遗漏 high 严重度项；
- 涉及公式/推导错误必须改对；涉及结果不足按补充实验要求补齐；
- 保持 LaTeX 可编译（中文用 xelatex/ctex）。

⛔ 修改完成后，必须执行编译并留存版本 PDF：
  在终端运行: python ${projectRoot}/scripts/compile.py ${draftPath}
  编译成功后会自劬保存版本到 paper/versions/main_vXXX.pdf

完成后用一段话总结你改了什么、对应哪些弱点，并确认编译是否通过。`,
    { label: `revise:r${round}`, phase: 'Revise', agentType: 'mm-writer' })
  log(`第 ${round} 轮修改完成: ${(revised || '').slice(0, 160)}`)

  // 重新载入 + 复评
  draft = await loadDraft()
  phase('Re-review')
  agg = aggregate(await panelReview(draft, 'Re-review'))
  history.push({ round, score: agg.avg, weaknesses: agg.allWeak.length })
  log(`第 ${round} 轮复评: ${agg.avg.toFixed(2)} / 10${agg.arbitrated ? ' (仲裁)' : ''}  M=${agg.dimScores.modeling?.toFixed(1)} R=${agg.dimScores.rigor?.toFixed(1)} Res=${agg.dimScores.results?.toFixed(1)} W=${agg.dimScores.writing?.toFixed(1)} I=${agg.dimScores.innovation?.toFixed(1)}`)
}

const passed = agg.avg >= TARGET
log(passed ? `✅ 达标：${agg.avg.toFixed(2)} ≥ ${TARGET}` : `⏹ 用尽 ${MAX_ROUNDS} 轮，当前 ${agg.avg.toFixed(2)}`)

// 终版编译 + 版本留存
log('编译终版 PDF...')
await agent(
  `在终端运行: python ${projectRoot}/scripts/compile.py ${draftPath}
编译完成后确认 PDF 已生成，版本已自动保存到 paper/versions/ 目录。`,
  { label: 'compile:final', agentType: 'mm-writer' }
)

return {
  finalScore: Number(agg.avg.toFixed(2)),
  target: TARGET,
  passed,
  rounds: history,
  dimScores: agg.dimScores,
  remainingWeaknesses: agg.allWeak.filter(w => w.severity === 'high'),
  perReviewer: agg.reviews.map(r => ({ role: r._role, score: r.score, verdict: r.verdict, dims: r.dimensions })),
  hardCaps: agg.hardCaps || [],
  arbitrated: agg.arbitrated || false,
}
