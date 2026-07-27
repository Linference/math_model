export const meta = {
  name: 'mm-adversarial-review',
  description: '数学建模论文多智能体对抗审稿：写作者↔审稿人/验证者/推理者并行挑战，≤4轮，评分达7.5停',
  whenToUse: '已有一份论文草稿（paper/main.tex 或 REPORT.md 内容）需要通过对抗协作提升到国赛级别时',
  phases: [
    { title: 'Baseline', detail: '三评审并行给出基线评分与弱点' },
    { title: 'Revise', detail: '写作者按意见修改' },
    { title: 'Re-review', detail: '三评审复评，判定是否达标' },
  ],
}

// args: { draftPath, lang, targetScore, maxRounds, dataContext }
const draftPath = (args && args.draftPath) || 'paper/main.tex'
const lang = (args && args.lang) || 'zh'
const TARGET = (args && args.targetScore) || 7.5
const MAX_ROUNDS = Math.min((args && args.maxRounds) || 4, 4)
const dataContext = (args && args.dataContext) || ''

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

按 schema 输出：综合评分、五维度分、弱点清单(含定位/严重度/修法)、是否需补实验、结论。`
}

const ROLES = [
  ['审稿人', '你负责批判审稿、定位弱点：建模是否合理、假设是否牵强、逻辑链是否完整、表达与图表是否规范、创新点是否真实。'],
  ['验证者', '你负责交叉验证与检查：数值结果是否可复现、量纲/边界/单位是否正确、结论与数据是否自洽、有无算术或统计错误。'],
  ['推理者', '你负责深度推理与数学证明：公式推导是否严谨、模型假设到结论的每一步是否成立、是否存在未证断言、能否给出更严格论证。'],
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
  ))
}

function aggregate(reviews) {
  const valid = reviews.filter(Boolean)
  if (!valid.length) return { avg: 0, reviews: [], allWeak: [], needExp: false }
  const avg = valid.reduce((s, r) => s + r.score, 0) / valid.length
  const allWeak = valid.flatMap(r => r.weaknesses || [])
  const needExp = valid.some(r => r.needMoreExperiments)
  return { avg, reviews: valid, allWeak, needExp }
}

// ---- 主流程 ----
let draft = await loadDraft()
if (draft === 'MISSING' || draft.length < 50) {
  log(`⚠️ 未找到有效草稿于 ${draftPath}，请先生成论文草稿再运行对抗审稿。`)
  return { error: 'no draft', draftPath }
}

phase('Baseline')
let agg = aggregate(await panelReview(draft, 'Baseline'))
log(`基线评分: ${agg.avg.toFixed(2)} / 10  （弱点 ${agg.allWeak.length} 条${agg.needExp ? '，需补实验' : ''}）`)

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
完成后用一段话总结你改了什么、对应哪些弱点。`,
    { label: `revise:r${round}`, phase: 'Revise', agentType: 'mm-writer' })
  log(`第 ${round} 轮修改完成: ${(revised || '').slice(0, 160)}`)

  // 重新载入 + 复评
  draft = await loadDraft()
  phase('Re-review')
  agg = aggregate(await panelReview(draft, 'Re-review'))
  history.push({ round, score: agg.avg, weaknesses: agg.allWeak.length })
  log(`第 ${round} 轮复评: ${agg.avg.toFixed(2)} / 10`)
}

const passed = agg.avg >= TARGET
log(passed ? `✅ 达标：${agg.avg.toFixed(2)} ≥ ${TARGET}` : `⏹ 用尽 ${MAX_ROUNDS} 轮，当前 ${agg.avg.toFixed(2)}`)

return {
  finalScore: Number(agg.avg.toFixed(2)),
  target: TARGET,
  passed,
  rounds: history,
  remainingWeaknesses: agg.allWeak.filter(w => w.severity === 'high'),
  perReviewer: agg.reviews.map(r => ({ score: r.score, verdict: r.verdict, dims: r.dimensions })),
}
