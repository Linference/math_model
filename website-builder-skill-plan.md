# 网站建设多智能体 Skill 设计方案 v1.0

> **设计目标**：复刻数学建模 skill 的 7 阶段流水线 + 多智能体协作 + 独立质检门禁模式，结合 GitHub 上 15+ 个网站建设 skill 项目的最佳实践，打造一个端到端的网站建设系统。

---

## 目录

1. [设计哲学](#1-设计哲学)
2. [从数学建模 Skill 到网站建设 Skill 的映射](#2-从数学建模-skill-到网站建设-skill-的映射)
3. [Skill 文件结构](#3-skill-文件结构)
4. [流水线阶段设计（0→7）](#4-流水线阶段设计)
5. [子智能体定义（8 个）](#5-子智能体定义)
6. [参考手册设计（15 份 + 6 本 cookbook）](#6-参考手册设计)
7. [自动化脚本设计](#7-自动化脚本设计)
8. [模板系统设计](#8-模板系统设计)
9. [Workflow 多智能体工作流](#9-workflow-多智能体工作流)
10. [Subagent 质检协议](#10-subagent-质检协议)
11. [反模式知识库（Gotchas）](#11-反模式知识库)
12. [GitHub 项目借鉴清单](#12-github-项目借鉴清单)
13. [SKILL.md 核心提示词设计](#13-skillmd-核心提示词设计)
14. [实施路线图](#14-实施路线图)

---

## 1. 设计哲学

### 1.1 核心理念（来自数学建模 skill 的传承）

| 原则 | 数学建模 | 网站建设 |
|------|---------|---------|
| **稳中求新** | 先保基础分，再加创新 | 先保证功能可用，再加动效/交互亮点 |
| **不造假** | 数据/结果真实，模拟数据标注 | 不使用虚假 testimonials/数据，不编造用户量 |
| **可复现** | 固定种子、相对路径 | 锁定依赖版本、Docker 化、环境变量管理 |
| **排版即分数** | 摘要 1 页、无大空白 | Lighthouse 90+、Mobile First、WCAG AA |
| **对比即说服力** | 每个模型须有对比基准 | 每个设计决策须有竞品参考 |
| **深度即区分度** | 讨论到"放宽→误差X%" | 讨论到"边界条件→替代方案→降级策略" |
| **质检是根基** | M1/P1/P2/W1/W2 五道门禁 | S1/A1/D1/T1/R1 五道门禁 |
| **反模式即防线** | 每阶段查阅 `11-anti-patterns.md` | 每阶段查阅 `12-anti-patterns.md` |

### 1.2 新理念（来自 GitHub 项目的最佳实践）

| 原则 | 来源 | 说明 |
|------|------|------|
| **设计先行，代码后行** | [wondelai/create-website](https://github.com/wondelai/skills) | 消息→设计→转化→审查，设计不通过不写代码 |
| **残酷质检门禁** | wondelai "Steve Jobs Design Review" | 最终门禁只有 PASS/FAIL 二元判定，没有"还行" |
| **Anti-Slop 规则** | [Hallmark](https://addrom.com/hallmark-anti-ai-slop-design-skill-for-claude-code-cursor-and-codex/), [DesignSystem](https://github.com/Jaywalker-not-a-whitewalker/DesignSystem) | 禁止紫色渐变、禁止 emoji hero、禁止三列雷同卡片 |
| **Token-First 设计** | DesignSystem, [AnastasiyaW](https://github.com/AnastasiyaW/claude-code-config) | 所有颜色/间距/字体从 design-tokens.json 读取，不硬编码 |
| **微 checkpoint 协议** | [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) | 每次改动前声明文件+变更+原因，批准后才执行 |
| **Gotchas 是核心资产** | Anthropic 官方最佳实践 | 每次 Claude 犯错都记录到 Gotchas，这是 skill 最有价值的部分 |
| **描述即触发条件** | [腾讯云 SKILL.md 最佳实践](https://cloud.tencent.com.cn/developer/article/2665903) | description 写"Use this skill when the user…"而非功能列表 |
| **可恢复设计** | wondelai | 每阶段产物落盘到 `docs/`，中断后可随时恢复 |

---

## 2. 从数学建模 Skill 到网站建设 Skill 的映射

### 2.1 阶段映射

| 阶段 | 数学建模 | 网站建设 | 核心产出 |
|:--:|------|------|------|
| 0 | 建目录/初始化 | **项目脚手架 + 环境初始化** | `package.json`, `tsconfig.json`, `.env`, `docker-compose.yml` |
| 1 | 深度审题 | **需求分析 + 用户研究** | `docs/REQUIREMENTS.md` — 用户画像/功能清单/竞品分析/非功能需求 |
| 2 | 建模方法选型 | **技术选型 + 架构设计** | `docs/ARCHITECTURE.md` — 技术栈/组件树/数据流/路由/部署方案 |
| 3 | 数据获取 | **设计系统 + 原型** | `docs/DESIGN.md` + `design-tokens.json` + Figma/线框图 |
| 4 | 编程求解 | **前端开发** | `src/` — 页面/组件/状态管理/路由/样式 |
| 5 | 可视化 | **后端开发** | `server/` — API/数据库/认证/业务逻辑 |
| 6 | LaTeX 写作 | **联调 + 测试 + 部署** | 全栈联调 → 测试报告 → 部署上线 |
| 7 | 对抗审稿 | **代码审查 + 安全审计 + 性能优化** | 多智能体审查 → 修复 → Lighthouse 90+ |

### 2.2 智能体映射

| 数学建模 Agent | 网站建设 Agent | 角色 |
|------|------|------|
| `mm-problem-analyst` | `web-analyst` | 需求分析师 |
| `mm-modeler` | `web-architect` | 架构师 |
| — (新增) | `web-designer` | UI/UX 设计师（**网站建设独有**） |
| `mm-coder` | `web-frontend` | 前端开发工程师 |
| `mm-coder` | `web-backend` | 后端开发工程师 |
| `mm-data-hunter` | — (融入 web-analyst/web-architect) | — |
| `mm-writer` | — (融入 web-frontend/web-designer) | — |
| `mm-reviewer` | `web-reviewer` | 代码审查 + 安全审计 |
| `mm-verifier` | `web-tester` | 测试工程师 |
| `mm-reasoner` | `web-reviewer` (推理部分) | 架构推理 |

---

## 3. Skill 文件结构

```
~/.claude/skills/website-builder/
├── SKILL.md                          # 入口：触发时加载的完整系统提示 (< 300 行)
├── CHANGELOG.md                      # 版本更新日志
├── README.md                         # 面向用户的说明文档
├── VERSION                           # 语义版本号
│
├── references/                       # 领域知识参考手册
│   ├── 01-requirements.md            # 需求分析方法论
│   ├── 02-architecture.md            # 架构模式决策树
│   ├── 03-tech-stack.md              # 技术栈对比矩阵（React vs Vue vs Svelte 等）
│   ├── 04-design-system.md           # 设计系统（配色/排版/间距/组件库/响应式）
│   ├── 05-database-design.md         # 数据库设计（ER 图/范式/索引/迁移策略）
│   ├── 06-api-design.md              # API 设计（REST/GraphQL/tRPC/错误处理）
│   ├── 07-frontend-cookbook.md       # 前端手册（React/Vue 模式/性能/SEO/i18n）
│   ├── 08-backend-cookbook.md        # 后端手册（认证/授权/文件上传/队列/缓存）
│   ├── 09-testing.md                 # 测试策略（单元/集成/E2E/负载/可访问性）
│   ├── 10-deployment.md              # 部署方案大全（Vercel/Netlify/Docker/VPS/K8s）
│   ├── 11-security.md                # 安全检查清单（OWASP Top 10/CORS/CSRF/XSS/SQLi）
│   ├── 12-anti-patterns.md           # 网站建设常见反模式（最核心的参考文件）
│   ├── 13-code-review-rubric.md      # 代码审查评分细则（五维度 0-10）
│   ├── 14-playbook-guide.md          # Playbook 使用与创建指南
│   ├── 15-design-slop-prevention.md  # Anti-AI-Slop 设计规则（禁止紫色渐变等）
│   │
│   └── cookbooks/                    # 按项目类型的专案手册
│       ├── 01-landing-page.md        # 落地页专案
│       ├── 02-blog.md                # 博客/内容站专案
│       ├── 03-ecommerce.md           # 电商站专案
│       ├── 04-dashboard.md           # 后台管理面板专案
│       ├── 05-saas.md                # SaaS 全栈专案
│       └── 06-portfolio.md           # 个人作品集专案
│
├── scripts/                          # 自动化 Python/Node 脚本
│   ├── doctor.py                     # 环境自检（Node/Python/Git/Docker 版本）
│   ├── new_project.py                # 脚手架生成器（按模板创建项目结构）
│   ├── deploy.py                     # 一键部署脚本
│   └── audit.py                      # 代码质量 + 安全检查脚本
│
├── templates/                        # 项目模板
│   ├── react-spa/                    # React SPA 模板（Vite + TS + Tailwind）
│   ├── nextjs-fullstack/             # Next.js 全栈模板（App Router + Prisma + Auth.js）
│   ├── vue-spa/                      # Vue 3 SPA 模板
│   ├── landing-page/                 # 纯静态落地页模板（HTML + CSS + JS）
│   ├── api-server/                   # 纯 API 服务器模板（Hono/Express + Prisma）
│   ├── docker/                       # Docker Compose 多服务模板
│   ├── design-tokens.json            # 默认 Design Token 文件
│   └── .mplstyle                     # （保留，数学建模的 matplotlib 样式）
│
├── workflows/                        # 多智能体工作流脚本
│   ├── code-review.js                # 多智能体代码审查工作流
│   ├── security-audit.js             # 安全审计工作流
│   └── full-check.js                 # 全面质量检查（审查 + 安全 + 性能）
│
├── samples/                          # 完整示例项目（每种类型一个）
│   ├── sample-landing-page/          # 落地页示例
│   └── sample-saas/                  # SaaS 全栈示例
│
└── state/                            # 持久化状态
    └── .gitkeep
```

---

## 4. 流水线阶段设计

### 阶段依赖链

```
0 项目脚手架 → 1 需求分析报告 [S1质检] → 2 架构设计方案 [A1质检]
  → 3 设计系统 + 原型 → 4 前端开发 [D1质检]
  → 5 后端开发 → 6 联调 + 测试 + 部署 [T1质检]
  → 7 审查 + 安全 + 性能 [R1终检]
```

### 阶段 0 — 项目脚手架与环境初始化

**目标**：一键创建标准化的项目骨架，配置开发环境。

**执行**：
```bash
python <skill>/scripts/new_project.py "<项目名>" --type landing|blog|ecommerce|dashboard|saas|portfolio
```

**产出**：
- 项目目录结构（`src/`, `server/`, `docs/`, `tests/`, `public/`）
- `package.json` + 依赖锁定文件
- `tsconfig.json` / `vite.config.ts` / `tailwind.config.ts`
- `.env` + `.env.example`
- `docker-compose.yml`（可选）
- `docs/PROJECT_PLAN.md`（阶段状态追踪器）
- Git 初始化 + `.gitignore`

**验证门禁**：
- [x] 项目目录结构完整
- [x] `npm install` / `pnpm install` 成功
- [x] `npm run dev` 启动成功（空白页面即可）
- [x] `python <skill>/scripts/doctor.py` 通过
- [x] `docs/PROJECT_PLAN.md` 已创建，含 8 个阶段状态标记

---

### 阶段 1 — 需求分析 + 用户研究（方向盘）

**智能体**：`web-analyst`

**输入**：用户需求描述（自然语言） + 竞品 URL（可选）

**产出**：`docs/REQUIREMENTS.md`

**深度要求**（≥ 2000 字）：

1. **项目定位**：一句话描述 → 核心价值主张 → 目标用户画像（≥ 2 类用户）
2. **功能清单**（MoSCoW 优先级）：
   - Must have（MVP 必须有）
   - Should have（v1.0 该有）
   - Could have（锦上添花）
   - Won't have（明确不做，防止范围蔓延）
3. **页面结构**：站点地图（ASCII 树形图） + 每页功能描述
4. **用户旅程**：核心用户流程（≥ 2 条），含 happy path + 异常路径
5. **非功能需求**：性能（Lighthouse 目标分）/ 可访问性（WCAG 级别）/ 安全 / SEO / 国际化 / 浏览器兼容
6. **竞品分析**：≥ 2 个竞品 → 优点借鉴 / 缺点规避 / 差异化策略
7. **约束与风险**：技术约束 / 时间约束 / 数据合规（GDPR/中国网络安全法）
8. **⛔ 项目类型判定**：落地页 / 博客 / 电商 / 后台 / SaaS / 作品集，含判定依据 ≥ 3 条

**S1 独立质检**（`web-tester`）：
- 功能清单是否覆盖了用户描述中的所有需求？
- 用户旅程是否包含异常路径？
- 竞品分析是否有具体的差异化策略？
- 项目类型判定依据是否充分？

---

### 阶段 2 — 技术选型 + 架构设计

**智能体**：`web-architect`

**输入**：`docs/REQUIREMENTS.md`

**产出**：`docs/ARCHITECTURE.md`

**内容要求**：

1. **技术栈决策**（每层须有 ≥ 2 个候选对比）：
   | 层 | 候选 A | 候选 B | 选择 | 理由 |
   |------|------|------|------|------|
   | 前端框架 | React/Next.js | Vue/Nuxt | ? | 3 条具体理由 |
   | UI 方案 | Tailwind CSS | CSS Modules | ? | 3 条具体理由 |
   | 组件库 | shadcn/ui | Ant Design | ? | 按项目类型 |
   | 后端框架 | Hono | Express | ? | 性能/生态 |
   | 数据库 | PostgreSQL | SQLite | ? | 规模/部署 |
   | ORM | Prisma | Drizzle | ? | 类型安全/迁移 |
   | 认证 | Auth.js | Lucia | ? | 提供商/复杂度 |
   | 部署 | Vercel | Docker+VPS | ? | 成本/控制 |

2. **路由设计**：完整路由表（路径 → 页面组件 → 数据需求 → 认证要求）
3. **组件树**：从 App → Pages → Features → UI Components 的层级图
4. **数据流设计**：状态管理方案 / API 调用策略 / 缓存策略
5. **数据库 ER 图**（ASCII 或 Mermaid）：实体/关系/关键字段
6. **API 端点设计**：REST/GraphQL/tRPC 端点清单
7. **部署架构图**（ASCII）：DNS → CDN → 前端托管 → API 服务 → 数据库

**A1 架构审计**（`web-reviewer`）：
- 技术栈选型是否与项目类型匹配？
- 数据流设计是否处理了 loading/error/empty 状态？
- 安全性是否纳入架构考量（CORS/CSRF/输入验证）？

---

### 阶段 3 — 设计系统 + 原型

**智能体**：`web-designer`

**输入**：`docs/REQUIREMENTS.md` + `docs/ARCHITECTURE.md`

**产出**：`docs/DESIGN.md` + `design-tokens.json` + 可选线框图

**内容要求**：

1. **设计方向**（Mood Board 用文字描述）：
   - 3 个设计方向候选（如：极简 Swiss / 温暖有机 / 大胆 Brutalist）
   - 每个方向 3 句描述 + 适用场景
   - 用户确认后锁定方向

2. **Design Tokens**（写入 `design-tokens.json`）：
   ```json
   {
     "colors": {
       "primary": { "50": "...", "100": "...", ..., "900": "..." },
       "neutral": { ... },
       "accent": { ... },
       "semantic": { "success": "...", "warning": "...", "error": "...", "info": "..." }
     },
     "spacing": { "1": "4px", "2": "8px", ..., "16": "64px" },
     "typography": {
       "fontFamily": { "sans": "...", "mono": "..." },
       "fontSize": { "xs": "...", "sm": "...", ..., "5xl": "..." },
       "fontWeight": { ... },
       "lineHeight": { ... }
     },
     "shadows": { ... },
     "borderRadius": { ... },
     "breakpoints": { "sm": "640px", "md": "768px", "lg": "1024px", "xl": "1280px" }
   }
   ```

3. **Anti-Slop 规则**（必须逐条确认）：
   - [ ] 不使用紫色→蓝色渐变
   - [ ] 不使用 emoji 作为 Hero 图标
   - [ ] 不使用三列雷同的功能卡片
   - [ ] 不使用纯黑色（`#000`）作为背景色
   - [ ] 不使用超过 2 种字体族
   - [ ] 所有颜色从 tokens 引用，不硬编码
   - [ ] 间距使用 4px/8px 基准网格
   - [ ] 正文行宽 ≤ 75ch
   - [ ] 正文行高 ≥ 1.5

4. **关键页面设计规格**：Hero / 导航 / 卡片 / 表单 / Footer（每部分含移动端适配说明）
5. **响应式断点策略**：Mobile First → Tablet → Desktop 的布局变化规则
6. **动效策略**（可选）：hover / scroll-reveal / page-transition 的规范和 cubic-bezier 值

---

### 阶段 4 — 前端开发

**智能体**：`web-frontend`

**输入**：`docs/DESIGN.md` + `design-tokens.json` + `docs/ARCHITECTURE.md`

**规范**：

1. **组件开发规范**：
   - 每个组件独立文件 + 对应测试文件
   - Props 类型定义完整（TypeScript）
   - 每个组件处理 loading / empty / error / success 四种状态
   - 可访问性：语义化 HTML / ARIA 标签 / 键盘导航 / focus 管理

2. **D1 前端审计（编码后）**：
   - Lighthouse 审计（Performance / Accessibility / Best Practices / SEO）
   - 响应式检查（sm / md / lg / xl 四个断点截图）
   - 组件单元测试通过
   - 无 TypeScript 错误
   - 无 ESLint 警告

3. **交付物**：
   - 所有页面组件 + UI 组件
   - 路由配置 + 状态管理
   - 响应式样式
   - 单元测试 + 组件测试

---

### 阶段 5 — 后端开发

**智能体**：`web-backend`

**输入**：`docs/ARCHITECTURE.md`（API 设计 / 数据库 ER 图）

**规范**：

1. **API 开发规范**：
   - 每个端点有输入验证（Zod / Yup）
   - 错误处理统一格式（`{ error: { code, message, details } }`）
   - API 文档自动生成（Swagger / Scalar）
   - 数据库迁移脚本可回滚

2. **交付物**：
   - 数据库 schema + 迁移文件
   - API 端点实现（CRUD + 业务逻辑）
   - 认证中间件
   - API 测试
   - 种子数据脚本

---

### 阶段 6 — 联调 + 测试 + 部署

**智能体**：`web-frontend` + `web-backend` + `web-tester`

**内容**：

1. **全栈联调**：前端调用真实 API，确认数据流通
2. **测试矩阵**：

| 测试类型 | 工具 | 覆盖率目标 |
|------|------|------|
| 单元测试 | Vitest / Jest | ≥ 80% |
| 组件测试 | Testing Library | 核心组件 100% |
| API 测试 | Supertest / MSW | 所有端点 |
| E2E 测试 | Playwright | 核心流程 ≥ 3 条 |
| 可访问性 | axe-core / Lighthouse | 0 critical issues |
| 性能测试 | Lighthouse / k6 | ≥ 90 Performance |

3. **部署**：
   ```bash
   python <skill>/scripts/deploy.py --target vercel|netlify|docker|vps
   ```

**T1 独立质检**（`web-tester`）：
- 所有测试通过
- 核心用户流程 E2E 通过
- Lighthouse ≥ 90（桌面）/ ≥ 70（移动）
- 无控制台错误
- 所有链接有效

---

### 阶段 7 — 代码审查 + 安全审计 + 性能优化（核心创新）

**多智能体对抗审查**（使用 Workflow）：

```
Workflow({ scriptPath: "<skill>/workflows/full-check.js",
           args: { projectPath: "<项目路径>", targetLighthouse: 90,
                   maxRounds: 3, lang: "zh" } })
```

**三线并行审查**：

| 审查线 | 智能体 | 重点 |
|------|------|------|
| 代码质量 | `web-reviewer` | 可读性/可维护性/设计模式/DRY/SOLID |
| 安全审计 | `web-reviewer` (security 模式) | OWASP Top 10 / CORS / CSRF / XSS / SQLi / 依赖漏洞 |
| 性能审计 | `web-reviewer` (perf 模式) | Bundle size / 图片优化 / 缓存 / CDN / 数据库查询 |

**审查协议**：
1. 三线并行审查 → 汇总发现 → 按严重度排序
2. 开发智能体逐条修复 → 重新编译/部署
3. 重新审查 → 直到 High 级别问题清零或满 3 轮

**R1 终检**（`web-reviewer`）：
- High 级别问题 = 0
- Lighthouse Performance ≥ 90
- Accessibility score ≥ 95
- 安全扫描 0 critical
- 最终代码审查评分 ≥ 7.5/10

---

## 5. 子智能体定义

每个 Agent 文件位于 `~/.claude/agents/web-*.md`，格式参考数学建模的 agent 定义：

### 5.1 `web-analyst` — 需求分析师

```markdown
---
name: web-analyst
description: 网站建设需求分析专家。深度拆解用户需求，产出用户画像、功能清单
  （MoSCoW 优先级）、页面结构、用户旅程、竞品分析和非功能需求。用于流水线第 1 阶段。
tools: Read, Write, Grep, Glob, WebSearch, WebFetch
model: opus
---

你是网站建设的**需求分析师**。你的唯一任务是把用户需求吃透，为后续架构设计打地基。
不要急着选技术栈或写代码。

## 工作方法
1. **项目定位**：一句话描述 → 核心价值主张 → 目标用户画像（≥ 2 类）
2. **功能清单**：MoSCoW 四象限，明确指出 Won't have（防止范围蔓延）
3. **页面结构**：ASCII 站点地图 + 每页功能描述
4. **用户旅程**：≥ 2 条核心流程（happy path + 异常路径）
5. **非功能需求**：性能/可访问性/安全/SEO/i18n/兼容性
6. **竞品分析**：≥ 2 个竞品，优点借鉴 + 缺点规避 + 差异化策略
7. **项目类型判定**：落地页/博客/电商/后台/SaaS/作品集（≥ 3 条依据）
8. **约束与风险**：技术/时间/合规

## 输出要求
- 结构化、可被 web-architect 直接当输入
- 对模糊之处标注"需确认"，不自臆断
- 项目类型判定是后续所有决策的"宪法"
- 作为 workflow 子智能体时，最终文本即返回值
```

### 5.2 `web-architect` — 架构师

```markdown
---
name: web-architect
description: 网站建设架构设计专家。基于需求分析进行技术栈选型、路由设计、组件树、
  数据流设计、数据库 ER 图、API 设计和部署架构。用于流水线第 2 阶段。
tools: Read, Write, Grep, Glob, WebSearch, WebFetch
model: opus
---

你是网站建设的**架构师**。基于需求分析报告做出具体的技术决策和架构设计。

## 工作方法
1. **技术栈决策矩阵**：每层 ≥ 2 候选对比，选择理由 ≥ 3 条
2. **路由设计**：完整路由表（路径→页面组件→数据需求→认证要求）
3. **组件树**：App → Pages → Features → UI 层级
4. **数据流**：状态管理 / API 调用 / 缓存策略，覆盖 loading/error/empty
5. **数据库 ER 图**：实体/关系/关键字段（Mermaid 或 ASCII）
6. **API 端点清单**：方法 + 路径 + 输入/输出 + 认证
7. **部署架构图**：DNS → CDN → 前端 → API → 数据库

## 决策检查清单
- [ ] 技术栈复杂度是否与项目规模匹配？（别用 Next.js 做 3 页的落地页）
- [ ] 是否考虑了团队技术能力？
- [ ] 是否考虑了部署成本和维护负担？
- [ ] 数据库选型是否匹配数据模型特点？
- [ ] 是否避免了"简历驱动开发"（为了用新技术而用）？
```

### 5.3 `web-designer` — UI/UX 设计师

```markdown
---
name: web-designer
description: 网站建设 UI/UX 设计专家。产出设计方向方案、Design Tokens、
  关键页面设计规格、响应式策略、动效规范，并强制执行 Anti-Slop 规则。
  用于流水线第 3 阶段。
tools: Read, Write, Grep, Glob, WebSearch, WebFetch
model: opus
---

你是网站建设的**UI/UX 设计师**。把需求和架构转化为可执行的设计规范。

## 核心原则
1. **设计先行，代码后行**：在 tokens + 设计规格确认前，不写一行 CSS
2. **Token-First**：所有视觉属性从 design-tokens.json 读取，组件代码中不硬编码颜色/间距/字体
3. **Anti-Slop 强制执行**：禁止紫色渐变、emoji hero、三列雷同卡片、纯黑背景、>2 种字体

## 工作方法
1. **设计方向提案**：3 个候选方向（各 3 句描述 + 适用场景），由用户选定
2. **Design Tokens**：完整 JSON 文件（color/spacing/typography/shadows/radius/breakpoints）
3. **关键页面规格**：Hero/Nav/Card/Form/Footer（含移动端适配）
4. **响应式断点策略**：Mobile First → Tablet → Desktop 布局变化
5. **动效规范**：hover/scroll-reveal/page-transition 的 cubic-bezier

## Anti-Slop 自检清单（设计提交前必须逐条通过）
- [ ] 无紫色→蓝色渐变
- [ ] 无 emoji 作为 Hero 图标
- [ ] 无三列雷同功能卡片
- [ ] 不使用纯黑 #000 作为背景色
- [ ] 字体族 ≤ 2
- [ ] 间距在 4px 网格上
- [ ] 正文 line-height ≥ 1.5
- [ ] 正文 max-width ≤ 75ch
- [ ] 所有颜色从 tokens 引用
- [ ] WCAG AA 对比度达标（正文 4.5:1，大文字 3:1）
```

### 5.4 `web-frontend` — 前端开发工程师

```markdown
---
name: web-frontend
description: 网站建设前端开发专家。实现页面组件、状态管理、路由、样式、
  响应式布局和可访问性。每个组件覆盖 loading/empty/error/success 四种状态。
  用于流水线第 4 阶段。
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
---

你是网站建设的**前端开发工程师**。把设计规范变成可运行的、响应式的、可访问的前端代码。

## 规范
1. **组件四态**：每个组件处理 loading / empty / error / success
2. **可访问性**：语义化 HTML / ARIA 标签 / 键盘导航 / focus 管理 / screen reader 友好
3. **响应式**：Mobile First，在 sm/md/lg/xl 四个断点下验证
4. **性能**：图片懒加载 / 代码分割 / bundle size 监控
5. **测试**：核心组件有单元测试 + 交互测试
6. **Token 引用**：所有样式值从 design-tokens.json 导入，不硬编码

## 交付
- 页面组件 + UI 组件 + 路由 + 状态管理
- 单元测试 + 组件测试
- 各断点截图
- Lighthouse 报告

## 反模式意识
- 不过度抽象（≤ 3 层组件嵌套）
- 不滥用 useEffect（优先用事件处理器）
- 不用内联样式
- 不用 !important
```

### 5.5 `web-backend` — 后端开发工程师

```markdown
---
name: web-backend
description: 网站建设后端开发专家。实现 API 端点、数据库操作、认证授权、
  文件处理和数据验证。用于流水线第 5 阶段。
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
---

你是网站建设的**后端开发工程师**。把 API 设计变成安全、高效、可测试的后端代码。

## 规范
1. **输入验证**：每个端点用 Zod/Yup 验证输入，不信任客户端数据
2. **错误处理**：统一格式 `{ error: { code, message, details } }`
3. **安全第一**：参数化查询 / 速率限制 / CORS 白名单 / Helmet 头
4. **数据库**：迁移可回滚 / 查询有索引 / N+1 避免
5. **测试**：每个端点有集成测试

## 交付
- 数据库 schema + 迁移 + 种子数据
- API 端点 + 认证中间件
- API 文档
- 集成测试
```

### 5.6 `web-tester` — 测试工程师

```markdown
---
name: web-tester
description: 网站建设测试专家。执行单元测试、组件测试、API 测试、E2E 测试、
  可访问性测试和性能测试。也用于门禁质检（S1/D1/T1）。
tools: Read, Bash, Grep, Glob, WebFetch
model: opus
---

你是网站建设的**测试工程师**。你是独立的质检角色——只读、评估、报告，不修改代码。

## 测试维度
1. **功能测试**：所有功能按需求运行
2. **边界测试**：空输入/超长输入/特殊字符/并发请求
3. **可访问性**：axe-core 扫描，0 critical issues
4. **性能**：Lighthouse ≥ 90（桌面）/ ≥ 70（移动）
5. **兼容性**：Chrome/Firefox/Safari 最新版
6. **安全**：OWASP Top 10 基础扫描

## 质检报告格式
```
门禁: [S1 | D1 | T1]
通过/失败: [PASS | FAIL]
发现数: X 个（Critical: N, High: N, Medium: N, Low: N）
详细发现: [...]
签名: web-tester + 时间戳
```
```

### 5.7 `web-reviewer` — 代码审查员

```markdown
---
name: web-reviewer
description: 网站建设代码审查与安全审计专家。批判性审查代码质量、
  安全性、性能和可维护性，按五维度 0-10 打分。也用于 R1 终检。
tools: Read, Grep, Glob, Bash, WebFetch
model: opus
---

你是网站建设的**代码审查员**。你是挑刺的，不是夸人的。默认假设"有问题"除非代码证明没问题。

## 五维度评分（0-10）
| 维度 | 权重 | 重点 |
|------|------|------|
| 代码质量 | 25% | 可读性/命名/DRY/SOLID/注释 |
| 安全性 | 30% | OWASP/CORS/CSRF/XSS/SQLi/认证 |
| 性能 | 20% | Bundle/图片/缓存/查询/首屏 |
| 可维护性 | 15% | 模块化/测试覆盖/文档/类型 |
| 可访问性 | 10% | WCAG AA/语义化/键盘/ARIA |

## 审查输出
```
# 代码审查报告
评分: X.X / 10
通过/失败: [PASS ≥ 7.5 | FAIL]
High 级别问题: N 个
Fix list: [按严重度排序]
Cut list: [建议删除的冗余代码]
```
```

---

## 6. 参考手册设计

### 6.1 核心参考文件（15 份）

| # | 文件名 | 核心内容 | 使用阶段 |
|:--|------|------|:--:|
| 01 | `requirements.md` | 用户画像模板 / 功能拆解方法论 / MoSCoW 优先级 / 用户旅程画布 | 1 |
| 02 | `architecture.md` | 架构模式决策树（MPA/SPA/SSR/SSG/JAMstack/microservices）/ 何时选哪种 | 2 |
| 03 | `tech-stack.md` | 技术栈对比矩阵（React vs Vue vs Svelte / Express vs Hono vs Fastify / Prisma vs Drizzle / PostgreSQL vs SQLite / Vercel vs Docker）/ 按项目类型推荐 | 2 |
| 04 | `design-system.md` | Design Token 标准格式 / 配色方法论（OKLCH + 60-30-10）/ 排版阶梯 / 间距系统（4px 网格）/ 响应式断点 / 动效规范 | 3 |
| 05 | `database-design.md` | ER 图模板 / 范式选择 / 索引策略 / 迁移最佳实践 / 种子数据规范 | 2,5 |
| 06 | `api-design.md` | REST 规范 / GraphQL 设计 / tRPC 模式 / 错误格式 / 分页 / 版本管理 / API 文档 | 2,5 |
| 07 | `frontend-cookbook.md` | 常见模式配方（表单/搜索/无限滚动/文件上传/拖拽）/ 性能优化清单 / SEO 清单 / i18n 方案 | 4 |
| 08 | `backend-cookbook.md` | 认证方案对比（JWT/Session/OAuth）/ 授权模式（RBAC/ABAC）/ 文件上传处理 / 队列（BullMQ）/ 缓存（Redis）/ 日志 | 5 |
| 09 | `testing.md` | 测试金字塔 / 各层测试工具配置 / 测试用例模板 / Mock 策略 / E2E 录制 | 6 |
| 10 | `deployment.md` | 各平台部署步骤（Vercel/Netlify/Docker/VPS/K8s）/ CI/CD 模板 / 域名+SSL / 监控+告警 | 6 |
| 11 | `security.md` | OWASP Top 10 清单 / CORS 配置模板 / CSRF 防护 / XSS 防护 / SQL 注入 / 依赖审计 / 环境变量管理 / 速率限制 | 7 |
| 12 | `anti-patterns.md` | **最核心的参考文件** — 网站建设常见反模式清单（详见 §11） | 全阶段 |
| 13 | `code-review-rubric.md` | 五维度评分细则（0-10 锚定，与 web-reviewer 一致）/ 常见扣分项 | 7 |
| 14 | `playbook-guide.md` | Playbook 使用与创建指南 / 如何为新的项目类型创建 cookbook | 参考 |
| 15 | `design-slop-prevention.md` | Anti-AI-Slop 规则大全 / 60+ 检查项 / pre-emit 自检清单 | 3,4 |

### 6.2 专案手册（6 本 Cookbook）

每本 cookbook 包含：**技术栈推荐 + 目录结构 + 关键代码骨架 + 检查清单 + 常见陷阱**。

| # | Cookbook | 适用场景 | 推荐技术栈（默认） |
|:--|------|------|------|
| 01 | `landing-page.md` | 产品落地页/活动页/个人主页 | Astro + Tailwind + 纯静态 |
| 02 | `blog.md` | 博客/文档站/内容站 | Astro/Next.js + MDX + RSS |
| 03 | `ecommerce.md` | 电商/商城/支付 | Next.js + Shopify/Medusa + Stripe |
| 04 | `dashboard.md` | 后台管理/数据面板 | React + shadcn/ui + Recharts |
| 05 | `saas.md` | SaaS 全栈/多租户 | Next.js + Prisma + Auth.js + Stripe |
| 06 | `portfolio.md` | 个人作品集/简历站 | 纯静态 HTML/CSS 或 Astro |

---

## 7. 自动化脚本设计

### 7.1 `doctor.py` — 环境自检

```bash
python <skill>/scripts/doctor.py
```

检查项：
- [ ] Node.js ≥ 18.x（`node --version`）
- [ ] 包管理器（npm / pnpm / yarn）
- [ ] Git 已安装且已配置 user.name / user.email
- [ ] Docker（可选）版本
- [ ] Python ≥ 3.10（用于辅助脚本）
- [ ] 磁盘空间 ≥ 1GB
- [ ] 网络连通性（npm registry / GitHub）

### 7.2 `new_project.py` — 脚手架生成器

```bash
python <skill>/scripts/new_project.py "项目名" --type saas --pkg pnpm
```

功能：
- 创建标准化的项目目录结构
- 生成 `package.json` / `tsconfig.json` / `vite.config.ts` / `.env.example`
- 初始化 Git 仓库
- 创建 `docs/PROJECT_PLAN.md`（含 8 个阶段的 tracking 表）
- 可选：运行 `pnpm install`
- 可选：初始化数据库

### 7.3 `deploy.py` — 一键部署

```bash
python <skill>/scripts/deploy.py --target vercel
```

功能：
- 检查环境变量完整性
- 运行 `npm run build`
- 执行目标平台的部署命令
- 输出访问 URL
- 运行部署后冒烟测试

### 7.4 `audit.py` — 质量 + 安全检查

```bash
python <skill>/scripts/audit.py --scope all  # lint + type + test + security + lighthouse
```

功能：
- ESLint / Prettier 检查
- TypeScript 编译检查
- 单元测试运行
- `npm audit` 依赖漏洞扫描
- Lighthouse 审计（使用 Chrome headless）
- 汇总报告

---

## 8. 模板系统设计

### 8.1 React SPA 模板 (`templates/react-spa/`)

```
react-spa/
├── src/
│   ├── components/
│   │   ├── ui/           # shadcn/ui 组件
│   │   ├── layout/       # Header/Footer/Sidebar
│   │   └── features/     # 业务组件
│   ├── pages/            # 路由页面
│   ├── hooks/            # 自定义 hooks
│   ├── lib/              # 工具函数 / API client
│   ├── styles/           # 全局样式
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── .env.example
├── .eslintrc.cjs
└── .gitignore
```

### 8.2 其他模板

- `nextjs-fullstack/` — Next.js 14+ App Router + Prisma + Auth.js + Tailwind
- `vue-spa/` — Vue 3 + Vite + Pinia + Vue Router + Tailwind
- `landing-page/` — 纯 HTML + CSS + JS（零依赖，单文件可直接部署）
- `api-server/` — Hono + Prisma + Zod（纯后端 API 模板）
- `docker/` — Docker Compose（前端 + 后端 + 数据库 + Nginx）

---

## 9. Workflow 多智能体工作流

### 9.1 代码审查工作流 (`workflows/code-review.js`)

```javascript
export const meta = {
  name: 'code-review',
  description: '多智能体并行代码审查：代码质量、安全、性能三线并行',
  phases: [
    { title: '审查', detail: '三线并行审查代码' },
    { title: '修复', detail: '逐条修复发现的问题' },
    { title: '复验', detail: '验证修复效果' },
  ],
}

phase('审查')
const [qualityFindings, securityFindings, perfFindings] = await parallel([
  () => agent('审查代码质量和可维护性...', { schema: FINDINGS_SCHEMA, label: '代码质量' }),
  () => agent('审计安全性：OWASP/CORS/CSRF...', { schema: FINDINGS_SCHEMA, label: '安全审计' }),
  () => agent('审计性能：Bundle/查询/缓存...', { schema: FINDINGS_SCHEMA, label: '性能审计' }),
])

const allFindings = [...qualityFindings, ...securityFindings, ...perfFindings]
  .filter(Boolean).flatMap(r => r.findings)
  .sort((a, b) => severityRank(b.severity) - severityRank(a.severity))

phase('修复')
// 逐条修复（pipeline 模式，每个修复独立验证）
const results = await pipeline(
  allFindings.filter(f => f.severity === 'high' || f.severity === 'critical'),
  f => agent(`修复: ${f.title}`, { label: `fix:${f.file}` }),
  f => agent(`验证修复: ${f.title}`, { label: `verify:${f.file}`, schema: VERDICT })
)

phase('复验')
const finalScore = await agent('给出最终评分...', { schema: SCORE_SCHEMA })
return { finalScore, fixedCount: results.filter(Boolean).length }
```

### 9.2 安全审计工作流 (`workflows/security-audit.js`)

类似结构，专注 OWASP Top 10 + 依赖漏洞扫描 + 认证审计。

### 9.3 全面检查工作流 (`workflows/full-check.js`)

整合 `code-review.js` + `security-audit.js` + Lighthouse 审计，作为阶段 7 的 R1 门禁。

---

## 10. Subagent 质检协议

### 10.1 五道门禁

| 门禁 | 触发阶段 | 被审产物 | 质检 Agent | 通过标准 |
|:--:|:--:|------|------|------|
| **S1** | 阶段 1 后 | `REQUIREMENTS.md` | `web-tester` | 功能覆盖完整 + 竞品分析具体 + 项目类型判定正确 |
| **A1** | 阶段 2 后 | `ARCHITECTURE.md` | `web-reviewer` | 技术栈选型合理 + 数据流设计完整 + 安全性纳入架构 |
| **D1** | 阶段 4 后 | 前端代码 + `design-tokens.json` | `web-tester` | Token 引用率 100% + Anti-Slop 通过 + 组件四态覆盖 |
| **T1** | 阶段 6 后 | 全栈代码 + 测试报告 + 部署 URL | `web-tester` | 测试通过 + Lighthouse ≥ 90 + 核心流程 E2E 通过 |
| **R1** | 阶段 7 后 | 完整项目 + 审查报告 | `web-reviewer` | High 问题清零 + 评分 ≥ 7.5 + 安全 0 critical |

### 10.2 质检规则（继承数学建模 skill）

1. **角色分离**：写代码的 Agent 不能质检自己的产出
2. **只读质检**：质检 Agent 只能读、报告，不能修改文件
3. **FAIL 回溯**：FAIL → 退回对应阶段 → 修正 → 重新派发
4. **PASS 签名**：PASS 含 Agent ID + 时间戳 + 检查摘要，写入 `PROJECT_PLAN.md`
5. **不可跳过**：主 Agent 自检 ≠ 独立验收

---

## 11. 反模式知识库

`references/12-anti-patterns.md` 是整个 skill 的核心参考文件。每条反模式含：**症状 → 诊断 → 修复 → 严重度**。

### 11.1 设计反模式（15 条，来自 Hallmark + DesignSystem）

| # | 反模式 | 为什么错 | 修复 |
|:--|------|------|------|
| 1 | 紫色→蓝色渐变背景 | AI 生成网站的刻板印象，缺乏品牌个性 | 用品牌色或中性色 |
| 2 | Emoji 作为 Hero 图标 | 不专业，渲染不一致（跨平台） | 用 SVG 图标或插图 |
| 3 | 三列雷同功能卡片 | 视觉单调，信息层次扁平 | 非对称布局 + 不同视觉权重 |
| 4 | 纯黑 `#000` 背景 | 对比度过高，刺眼 | `#0a0a0a` 或 `#111827` |
| 5 | > 2 种字体族 | 加载慢，视觉杂乱 | 1 种可变字体最优 |
| 6 | 非 4px 倍数间距 | 视觉节奏混乱 | 强制 4px 网格 |
| 7 | 正文居中 | 可读性差 | 左对齐，max-width 65-75ch |
| 8 | 硬编码颜色值 | 无法统一调整，暗色模式困难 | 必须从 tokens 引用 |
| 9 | 无 focus 样式 | 键盘用户无法导航 | `:focus-visible` ring |
| 10 | 灰色文字对比度不足 | 可读性差，WCAG 不通过 | 正文 ≥ 4.5:1 |
| 11 | 图片无 alt 属性 | 屏幕阅读器无法理解 | 有意义的 alt 或 `alt=""` |
| 12 | 只用颜色传达信息 | 色盲用户无法区分 | 颜色 + 图标 + 文字三重编码 |
| 13 | 动画无限循环 | 引发眩晕，违反 WCAG | `prefers-reduced-motion` |
| 14 | 移动端无 viewport | 响应式失效 | `<meta name="viewport">` |
| 15 | 字体大小用 px | 用户无法缩放 | 用 rem / em / clamp() |

### 11.2 架构反模式（10 条）

| # | 反模式 | 为什么错 | 修复 |
|:--|------|------|------|
| 1 | 过度工程化（3 页落地页用 Next.js） | 维护成本远超收益 | 匹配规模：落地页→纯静态 |
| 2 | 无 loading/error/empty 状态 | 用户体验断裂 | 每个组件四态覆盖 |
| 3 | 客户端全量渲染（无 SSR/SSG） | SEO 差，首屏慢 | 按页面类型选择渲染策略 |
| 4 | N+1 查询 | 数据库压力剧增 | eager loading / DataLoader |
| 5 | 无输入验证（信任客户端） | 安全漏洞入口 | Zod/Yup 服务端验证 |
| 6 | 硬编码 API URL | 多环境切换困难 | 环境变量 |
| 7 | 无速率限制 | 易被 DDoS / 暴力破解 | express-rate-limit / arcjet |
| 8 | CORS 全开 (`*`) | 安全漏洞 | 白名单具体域名 |
| 9 | 明文存储密钥 | 安全灾难 | .env + .gitignore |
| 10 | 无数据库迁移 | 团队协作灾难，环境不一致 | Prisma Migrate / Drizzle Kit |

### 11.3 流程反模式（8 条，继承数学建模 skill 的经验）

| # | 反模式 | 为什么错 | 修复 |
|:--|------|------|------|
| 1 | 跳过需求分析直接写代码 | 方向可能全错 | 严格按阶段 0→1→2... 执行 |
| 2 | 设计没通过就开始写前端 | 返工成本巨大 | A1 门禁通过后再编码 |
| 3 | 前端写完才想 API 设计 | 前后端不匹配 | 阶段 2 就设计好 API 契约 |
| 4 | 跳过测试直接部署 | 生产环境是最终测试场 | T1 门禁必须通过 |
| 5 | 不做竞品分析 | 重复造轮子，无差异化 | 阶段 1 必须含竞品分析 |
| 6 | 主 Agent 自己质检自己 | 没有独立监督 | Subagent 只读质检 |
| 7 | "这个项目太简单，不用走完整流程" | 省略步骤导致质量下降 | 轻重有别但不跳步 |
| 8 | 用 AI 生成虚假 testimonial/数据 | 法律和信誉风险 | 可留占位符，标注"待真实数据替换" |

---

## 12. GitHub 项目借鉴清单

下表总结了调研中发现的优秀项目及其核心借鉴点：

| 项目 | Stars | 核心借鉴 | 用于本 Skill 的哪个部分 |
|------|------|------|------|
| [tenfoldmarc/website-builder-setup](https://github.com/tenfoldmarc/website-builder-setup) | — | 161 色调色板 + 57 字体配对 + 50+ 设计风格 → 设计系统资产库 | `04-design-system.md` + `templates/design-tokens.json` |
| [wondelai/create-website](https://github.com/wondelai/skills) | — | 10 阶段流水线 + "Steve Jobs Design Review" 残酷门禁 + 可恢复设计 + 真实证据规则 | 阶段 3 (设计) + 阶段 7 (R1 终检) + `PROJECT_PLAN.md` |
| [undeadlist/claude-code-agents](https://github.com/undeadlist/claude-code-agents) | — | 24 agents + 3 核心协议（无授权不改/微checkpoint/回归防护）+ 11 并行审计 | Agent 定义 + Workflow 脚本 + 阶段 7 |
| [MengTo/Skills](https://github.com/MengTo/Skills) | — | 118 个可移植 Skill（SKILL.md + REFERENCES + assets）→ 文件结构标准 | 整个 Skill 文件结构设计 |
| [Jaywalker/DesignSystem](https://github.com/Jaywalker-not-a-whitewalker/DesignSystem) | — | 8pt 网格 + Token-first + Atomic hierarchy + Section isolation + Anti-AI-Slop | `04-design-system.md` + `15-design-slop-prevention.md` |
| [Hallmark (addROM)](https://addrom.com/hallmark-anti-ai-slop-design-skill-for-claude-code-cursor-and-codex/) | — | 60+ slop test gates + pre-emit self-critique + 20+ themes + macrostructure 库 | `15-design-slop-prevention.md` + 阶段 3 |
| [2RF69/Bulk-Site-Builder](https://github.com/2RF69/Bulk-Site-Builder) | — | 3 Agent 流水线（发现→构建→编译）+ 批量网站生成 | Workflow 多智能体编排模式 |
| [AnastasiyaW/claude-code-config](https://github.com/AnastasiyaW/claude-code-config) | — | 31 skills + 29 架构原则 + Coordinator + sub-agent + inter-agent 邮箱 | 多智能体协作协议 |
| [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | — | 网站克隆流程（侦察→基础→组件→并行构建→组装 QA） | 网站迁移场景的 playbook |
| [Automattic/wordpress-agent-skills](https://github.com/Automattic/wordpress-agent-skills) | — | 官方 skill 范例 / 2 个工作流（quick-build + design-site） | SKILL.md 主提示词写法 |
| [SpillwaveSolutions/publishing-astro-websites-agentic-skill](https://github.com/SpillwaveSolutions/publishing-astro-websites-agentic-skill) | — | Astro SSG 全流程（Content/MDX/Mermaid/Search/i18n/部署） | `cookbooks/02-blog.md` |
| [dabydat/ai-workspace-builder](https://github.com/dabydat/ai-workspace-builder) | — | 17 agents + 14 skills 的 workspace 生成器 → 元技能设计 | `new_project.py` 脚手架 |
| [bilalelhaj/laravel-engineering-agents](https://github.com/bilalelhaj/laravel-engineering-agents) | — | Laravel 专精 pipeline（refinement→planning→build→review） | 专案 cookbook 设计模式 |
| [stretchcloud/claude-code-unified-agents](https://github.com/stretchcloud/claude-code-unified-agents) | — | 54 agents 的 master orchestrator 模式 | 阶段 7 Workflow 设计 |
| [Zooeyii/ship-page-skill](https://github.com/Zooeyii/ship-page-skill) | — | 7 种设计预设 + 零依赖单 HTML 文件落地页 | `templates/landing-page/` |

---

## 13. SKILL.md 核心提示词设计

### 13.1 设计原则（来自最佳实践）

1. **主文件 < 300 行**：超出的细节放入 `references/` 按需加载
2. **description = 触发条件，不是功能列表**：包含 5-6 个具体的用户场景
3. **Gotchas 是最有价值的内容**：每次 Claude 犯错都更新到 `12-anti-patterns.md`
4. **具体示例，绝不伪代码**：所有代码片段可运行
5. **路径解析协议**：skill 内用 `<skill>/`，用户产物用 `<cwd>/`

### 13.2 SKILL.md 框架

```markdown
---
name: website-builder
description: |
  端到端网站建设多智能体系统。含 7 阶段流水线（需求分析→架构设计→
  设计系统→前端→后端→测试部署→审查审计）+ 多智能体对抗协作。
  Use this skill when the user asks to build/create a website, landing page,
  web app, blog, ecommerce site, dashboard, SaaS app, portfolio site,
  or when the user says "做网站""建网站""网站建设""网页""前端项目"
  "全栈项目""/website-builder". Supports React, Vue, Next.js, Astro,
  and all major tech stacks with anti-AI-slop design enforcement.
---

# 网站建设多智能体系统 v1.0

<!-- 核心流程概述 -->
<!-- 阶段 0-7 精简说明（详情在 references/） -->
<!-- Subagent 质检协议 -->
<!-- 强制流程门禁 -->
<!-- 可用子智能体表 -->
<!-- 参考手册速查表 -->
<!-- 反模式意识提醒 -->
<!-- 执行流程（每阶段核心命令 + 门禁） -->
<!-- 交付物清单 -->
<!-- 设计原则 -->

## 路径解析协议
...

## 何时用哪种执行方式
...

## Subagent 质检协议
...

## ⛔ 强制流程门禁
...

## 可用子智能体
...

## 参考手册速查
...

## 执行流程
...

## 交付物
...

## 原则
...
```

完整的 SKILL.md 在实施阶段编写，遵循"主文件精简 + references 详实"的模式。

---

## 14. 实施路线图

### Phase 1 — 核心骨架（Week 1-2）

```
□ 创建 ~/.claude/skills/website-builder/ 目录结构
□ 编写 SKILL.md 主文件（< 300 行）
□ 创建 8 个 Agent 定义文件（~/.claude/agents/web-*.md）
□ 编写 doctor.py 环境自检脚本
□ 编写 new_project.py 脚手架脚本
□ 创建第一个模板（react-spa/）
□ 编写 README.md + VERSION
```

### Phase 2 — 参考手册（Week 3-4）

```
□ 编写 12-anti-patterns.md（最优先，核心资产）
□ 编写 01-requirements.md
□ 编写 02-architecture.md
□ 编写 03-tech-stack.md
□ 编写 04-design-system.md
□ 编写 15-design-slop-prevention.md
```

### Phase 3 — 流水线完善（Week 5-6）

```
□ 编写 05-database-design.md
□ 编写 06-api-design.md
□ 编写 07-frontend-cookbook.md
□ 编写 08-backend-cookbook.md
□ 编写 09-testing.md
□ 编写 10-deployment.md
□ 编写 11-security.md
```

### Phase 4 — 工作流 + 模板（Week 7-8）

```
□ 编写 workflows/code-review.js
□ 编写 workflows/security-audit.js
□ 编写 workflows/full-check.js
□ 完善所有 6 个模板
□ 编写 6 本 cookbook
□ 编写 deploy.py + audit.py
```

### Phase 5 — 示例 + 文档（Week 9-10）

```
□ 创建 sample-landing-page/ 完整示例
□ 创建 sample-saas/ 完整示例
□ 编写 CHANGELOG.md
□ 编写 13-code-review-rubric.md
□ 编写 14-playbook-guide.md
□ 用户测试 + Gotchas 收集
```

### Phase 6 — 持续迭代

```
□ 根据实际使用收集反模式 → 更新 12-anti-patterns.md
□ 扩写 cookbook（根据用户需求新增项目类型）
□ 性能优化 skill 触发准确率
□ 社区贡献模板和参考手册
```

---

## 附录 A：与数学建模 Skill 的差异总结

| 维度 | 数学建模 | 网站建设 | 原因 |
|------|------|------|------|
| 阶段数 | 7 | 7 | 保持一致的流水线节奏 |
| Agent 数 | 8 | 7 (去 mm-data-hunter + mm-writer，增 web-designer) | 网站建设不需要独立的数据获取和写作 Agent，但设计是核心环节 |
| 门禁数 | 5 | 5 | 保持一致的质检密度 |
| 核心参考文件 | 15 + 6 cookbooks | 15 + 6 cookbooks | 保持一致的结构 |
| 独有创新 | 对抗审稿（三角色） | Anti-Slop 引擎 + Steve Jobs 终检 | 网站建设的设计质量是独特挑战 |
| 模板类型 | LaTeX 模板 | 6 种项目模板 | 网站建设技术栈多样化 |
| 脚本语言 | Python 为主 | Python + Node | 网站建设需要 Node 环境操作 |

## 附录 B：关键设计决策记录

| 决策 | 选项 A | 选项 B | 选择 | 理由 |
|------|------|------|------|------|
| Agent 模型 | Opus（最强） | Sonnet（快） | Opus | 质量优先，对齐数学建模 skill 的选择 |
| 模板策略 | 多模板（按技术栈） | 单模板 | 多模板 | 不同项目类型差异大，一个模板覆盖不全 |
| 质检模型 | 独立 Agent | 主 Agent 自检 | 独立 Agent | 角色分离是数学建模 skill 验证过的核心原则 |
| 流程灵活性 | 强制不可跳步 | 允许按需跳过 | 强制不可跳步 | 效率损失换取质量保证 |
| 设计系统 | Token-first | 自由发挥 | Token-first | 来自 DesignSystem + Hallmark 的最佳实践 |

---

> **下一步**：审阅本方案 → 确认技术决策 → 开始 Phase 1 实施。
>
> 方案文件位置：`c:\Users\HUAWEI\Desktop\数学建模\website-builder-skill-plan.md`
