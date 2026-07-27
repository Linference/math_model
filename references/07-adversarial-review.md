# 07 — 多智能体对抗审稿协议

核心创新：多个 AI 各司其职，交叉审稿、互相挑战，用对抗机制逼出最高质量。由 `workflows/adversarial-review.js` 驱动。

## 角色
| 角色 | agentType | 立场 |
|---|---|---|
| 写作者 | mm-writer | 生成内容、执行修改、补充实验 |
| 审稿人 | mm-reviewer | 批判审稿、定位弱点（默认挑刺） |
| 验证者 | mm-verifier | 交叉验证、数值/逻辑检查、独立重算 |
| 推理者 | mm-reasoner | 深度推理、数学证明、推导审计 |

## 对抗循环
```
写作者产出草稿
  → [审稿人 ∥ 验证者 ∥ 推理者] 并行对抗打分(0-10, 五维度) + 弱点清单
  → 聚合平均分
  → 若 < 目标(默认7.5) 且 轮次 ≤ 4：
       写作者按 high→low 弱点逐条修改（needMoreExperiments 则自动补充实验）
       → 三评审复评
  → 达标或用尽 4 轮停
```

## 五评分维度（0-10）
- modeling 建模合理性
- rigor 数学严谨性
- results 结果与验证充分性
- writing 表达与图表规范
- innovation 创新性

## 自动补充实验触发
任一评审 `needMoreExperiments=true`（结果单薄、缺灵敏度/对照/验证）→ 写作者补做实验并把新图新数写进论文。

## 目标：5.0 → 7.5
基线常在 5-6（基本完成但有硬伤），经 2-4 轮对抗修到 7.5+（省一级别）。每条弱点必须**可定位、可执行修法**，复评时逐条核对。

## 调用
```
Workflow({ scriptPath: "<skill>/workflows/adversarial-review.js",
  args: { draftPath:"<slug>/paper/main.tex", lang:"zh",
          targetScore:7.5, maxRounds:4, dataContext:"<关键结果数值>" }})
```
返回：finalScore、每轮评分记录、残留 high 弱点、各评审分维度。
