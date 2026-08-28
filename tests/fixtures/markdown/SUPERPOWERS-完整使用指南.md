# Superpowers 实战指南

## —— 给 AI Coding 初学者的完整工作流手册

> 作者：老季聊AI
> 
> 本指南面向初入职场的开发者和产品经理，帮你从零理解 Superpowers 的工作流，并通过一个真实案例（构建企业级智能问答助手）串联所有知识点。

---

## 一、为什么你需要 Superpowers

先说一个场景，你可能很熟悉：

你刚入职，接到了第一个需求。打开 Claude Code / Cursor / Codex，兴冲冲地输入："帮我做一个登录页面"。然后 Agent 像打了鸡血一样，噼里啪啦甩出 500 行代码。你复制粘贴，运行——报错。修了一个，又冒出三个。更糟的是，它压根没做密码强度校验，但顺手帮你加了个 OAuth 2.0 集成——你没要这个。

这就是没有流程的 AI Coding：**强大但混乱**。

AI 编程 Agent 本质上像一个能力很强但毫无经验的应届生——写代码飞快，但会跳过需求分析、不写测试、不管设计文档、一上来就埋头实现。结果呢？功能做错、代码没测、实现半拉子。

**Superpowers 解决的正是这个问题。** 它不是又一个 AI 工具，而是给你的 AI Agent 套上了一套"资深工程师级别"的工作流程：

- **先设计，后编码** —— 不允许 Agent 看到需求就直接动手
- **先测试，后实现** —— 每一行生产代码都必须有一个先失败的测试撑腰
- **先验证，后声明** —— "应该没问题了"这种话，必须用测试输出打脸
- **先审查，后合并** —— 代码必须经过规范的 Review 流程

打个比方：Superpowers 就像在你 AI Agent 的脑子里塞进了一个认真负责的技术导师。你想偷懒跳步骤？不行。你想先写代码再补测试？不行。你想不跑测试就说"搞定了"？更不行。

这不是限制你，而是保护你。尤其在刚入职场的阶段，这套流程会帮你养成受益终身的工程习惯——即使你以后不用 AI 写代码了，这些习惯也值了。

---

## 二、核心理念：5 条铁律

Superpowers 的所有技能（skill）都围绕 5 条核心哲学构建。记住这 5 条，你就掌握了 Superpowers 的灵魂。

### 铁律一：先设计，后编码

> 对应技能：`brainstorming`

AI Agent 最常见的问题是什么？**太着急。** 你刚说"做一个登录页"，它已经开始写 CSS 了。

brainstorming 技能会在 Agent 动手之前强制拦住它。Agent 会先问你一连串问题：你的登录页面向什么用户？需要支持哪些登录方式？密码规则是什么？登录成功后跳哪？只有当你确认了设计方案之后，Agent 才被允许碰代码。

**Before（没有 Superpowers）：**

```
你：帮我做一个登录页
Agent：（直接输出 500 行代码）
```

**After（有 Superpowers）：**

```
你：帮我做一个登录页
Agent：好的，我先了解一下需求。请问——
  1. 这个登录页面的目标用户是谁？（C 端消费者 / 内部员工 / 两者都有）
  2. 需要支持哪些登录方式？（手机号 / 邮箱 / 第三方登录）
  3. 有没有已有的设计稿或 UI 规范可以参考？
  ...
你：C 端消费者，手机号验证码登录，没有设计稿
Agent：明白。我推荐以下方案：...（呈现设计方案）
你：OK，就这么做
Agent：（这才开始写代码）
```

### 铁律二：先写测试，后写代码

> 对应技能：`test-driven-development`

这可能是最反直觉但最有价值的一条。TDD 的核心循环是 **Red-Green-Refactor**：

1. 🔴 **Red** —— 先写一个会失败的测试（因为功能还没实现）
2. ✅ **Green** —— 写最少量的代码让测试通过
3. 🔵 **Refactor** —— 在测试保护下重构代码

**铁律：没有失败的测试，就没有生产代码。** 如果 Agent 先写了代码再补测试，Superpowers 会要求它**删掉代码重新来过**。不是开玩笑，是真的删。

**Before：**

```
Agent：登录功能写好了！（300 行代码）
Agent：我再补一下测试...（写几个跑得过的测试）
Agent：搞定了！
结果：3 个边界情况没覆盖，空邮箱能直接登录
```

**After：**

```
Agent：我正在用 TDD 方式实现登录功能。
Agent：Step 1 - 写一个失败的测试：空邮箱应该被拒绝
  → 运行测试 → ❌ FAIL（函数还不存在）
Agent：Step 2 - 写最少的代码让测试通过
  → 运行测试 → ✅ PASS
Agent：Step 3 - 提交这个 commit
Agent：下一个测试：无效邮箱格式应该被拒绝...
```

### 铁律三：证据优先于声明

> 对应技能：`verification-before-completion`

这条规则简单粗暴：**没有跑过验证命令，就不许说"搞定了"。**

Agent 最爱说的话是"应该没问题了"、"看起来可以了"、"应该跑得通"。在 Superpowers 里，这些话必须在附上测试运行结果之后才能说。

**Before：**

```
Agent：登录功能实现完毕，应该没问题了 ✨
你：（手动测试）报错了，密码为空居然能登录？？？
```

**After：**

```
Agent：登录功能实现完毕。
Agent：（运行 npm test）
  → 34/34 tests passing ✅
  → 0 failures, 0 errors
Agent：所有测试通过，具体结果如上。
```

### 铁律四：系统化而非随意

> 对应技能：`systematic-debugging`

遇到 Bug 时，AI Agent 的本能反应是"猜一个原因，改一下试试"。这种做法的问题在于：你可能改对了，也可能改错了但恰好掩盖了症状，更可能改出新的 Bug。

Superpowers 要求 Agent 遵循 4 阶段调试流程：

1. **根因调查（Root Cause Investigation）** —— 读错误信息、稳定复现、检查最近改动（git diff）、在多组件边界加诊断日志、追踪数据流
2. **模式分析（Pattern Analysis）** —— 找类似的能正常工作的代码做对比、列出每一个差异
3. **假设与验证（Hypothesis and Testing）** —— 明确写下假设"我认为根因是 X 因为 Y"、做最小改动验证、验证通过才进下一步
4. **实施修复（Implementation）** —— 先写失败测试重现 bug、针对根因修一个地方、验证修复有效且没引入新问题

> ⚠️ **3 次修复失败 → 质疑架构**：如果连续 3 次修复尝试都失败，停下来——大概率不是代码的问题，是架构的问题。找你的搭档（或同事）聊聊，从根本上重新审视方案。

**Before：**

```
Agent：登录页白屏了，可能是样式问题，我改一下 CSS... 不行，那我改一下 JS... 还是不行...
（20 分钟后）Agent：可能是路由配置的问题？
```

**After：**

```
Agent：登录页白屏。我按 systematic-debugging 4 阶段流程排查。
Agent：Phase 1 - 根因调查：打开 /login → 白屏，控制台报 TypeError
Agent：Phase 2 - 模式分析：对比正常工作的 /dashboard 页面，发现它有空值保护而 /login 没有
Agent：Phase 3 - 假设与验证：假设"根因是 utils/format.js 第 42 行传入 undefined 导致 .trim() 报错"，做最小改动验证 → 确认
Agent：Phase 4 - 实施修复：先写失败测试重现 bug → 在调用 .trim() 前添加空值检查 → 验证修复有效 ✅
```

### 铁律五：小步快跑，频繁提交

> 对应技能：`writing-plans`

Superpowers 把所有工作拆成**原子级的小任务**，每个任务只需 2-5 分钟。一个典型的任务看起来是这样的：

```
Step 1: 写一个失败的测试（测试代码）
Step 2: 运行测试，确认它失败
Step 3: 写最少的代码让测试通过
Step 4: 运行测试，确认它通过
Step 5: 提交 commit
```

每一步都是独立、可验证、可回滚的。这背后的哲学是：**与其花 2 小时写一大坨代码然后 debug 半天，不如每 5 分钟交付一个确定能用的增量。**

---

## 三、安装与配置

Superpowers 支持主流的 AI Coding 平台。不同平台的安装方式略有差异，下面逐个说明。

### Claude Code（推荐 ⭐）

Superpowers 在 Claude Code 的官方插件市场可以直接安装：

```bash
/plugin install superpowers@claude-plugins-official
```

如果官方市场暂时不可用，也可以通过第三方市场：

```bash
# 先注册市场
/plugin marketplace add obra/superpowers-marketplace
# 再安装插件
/plugin install superpowers@superpowers-marketplace
```

> 💡 **为什么推荐 Claude Code？** 因为它的 subagent（子代理）支持最成熟，能充分发挥 Superpowers 的 subagent-driven-development 能力——可以给每个任务派一个独立的 Agent 去执行，然后自动审查。

### Cursor

在 Cursor 的 Agent 聊天窗口中输入：

```
/add-plugin superpowers
```

或者在插件市场搜索 "superpowers" 安装。

### Codex

Codex 有两种安装方式：

**Codex CLI：**

打开插件搜索界面：

```bash
/plugins
```

搜索 "superpowers" 并选择 "Install Plugin"。

或者手动安装（clone + symlink）：

```bash
# 克隆仓库
git clone https://github.com/obra/superpowers.git ~/.codex/superpowers
# 创建技能符号链接
mkdir -p ~/.agents/skills
ln -s ~/.codex/superpowers/skills ~/.agents/skills/superpowers
# 重启 Codex
```

Windows 用户用 PowerShell 创建 junction：

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\superpowers" "$env:USERPROFILE\.codex\superpowers\skills"
```

**Codex App：**

在 Codex App 侧边栏点击 Plugins，在 Coding 分类中找到 Superpowers，点击 `+` 按钮按提示安装。

详细的配置文档可以参考项目中的 `docs/README.codex.md`。

### OpenCode

在 `opencode.json`（全局或项目级）的 `plugin` 数组中加一行：

```json
{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git"]
}
```

重启 OpenCode 即可。插件会自动安装并注册所有技能。

验证安装：问 Agent "Tell me about your superpowers"。

如需固定版本：

```json
{
  "plugin": ["superpowers@git+https://github.com/obra/superpowers.git#v5.0.7"]
}
```

详细文档见 `docs/README.opencode.md`。

### Gemini CLI

```bash
gemini extensions install https://github.com/obra/superpowers
```

更新时运行：

```bash
gemini extensions update superpowers
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add obra/superpowers-marketplace
copilot plugin install superpowers@superpowers-marketplace
```

### 验证安装

安装完成后，打开一个新的 Agent 会话，输入：

> 帮我规划一个功能

如果一切正常，Agent 应该**不会直接写代码**，而是启动 brainstorming 技能，开始向你提问、了解需求。看到 Agent 主动问问题而不是甩代码，就说明 Superpowers 已经生效了。

---

## 四、工作流全景图：你的第一次 Superpowers 之旅

好了，概念和安装都搞定了。现在让我们走一遍完整的 Superpowers 工作流。

我们用一个简单的例子：**你要做一个 Todo List 应用**。假设你已经打开了 Claude Code 并安装好了 Superpowers。

### 全局流程

```
brainstorming → using-git-worktrees → writing-plans → subagent-driven-development → finishing-a-development-branch
  (需求设计)      (创建隔离分支)       (拆分实现计划)    (逐任务执行+审查)          (合并或创建PR)
```

下面你将看到每一步在终端里长什么样。

---

### Step 1：brainstorming —— 从想法到设计

```
你：我想做一个 Todo List 应用

Agent：我正在使用 brainstorming 技能来帮你梳理需求。

先了解一下项目情况……（查看当前目录文件结构）

几个问题想确认一下：

这个 Todo List 面向什么场景？
  A. 个人待办管理（简单优先）
  B. 团队协作任务管理（需要更多功能）
  C. 学习练手项目

你：A，个人用的

Agent：明白。那再问一个——需要哪些核心功能？
  A. 增删改查 + 标记完成（最简版）
  B. A + 优先级 + 截止日期
  C. A + 标签分类 + 筛选

你：A 就行，保持简单

Agent：好，基于你的需求，我推荐以下方案：

**架构方案**
- 纯前端应用，数据存在 localStorage
- 组件：TodoInput（输入框）、TodoList（列表）、TodoItem（单条）
- 不引入状态管理库，用 React useState 够用

这个方向对吗？

你：可以

Agent：（呈现更详细的设计方案，每部分分段展示，你逐一确认）
...
Agent：设计文档已保存到 docs/superpowers/specs/2026-04-15-todo-app-design.md
Agent：请你看一下这个设计文档，确认没问题后我们开始做实现计划。
```

**你看到了什么？** Agent 没有——也**不能**——在你说"做个 Todo List"的时候直接甩代码。它被 Superpowers 的 brainstorming 技能强制拉住，一步步问清楚需求、确认设计，最后还保存了设计文档让你审阅。

---

### Step 2：using-git-worktrees —— 创建隔离工作空间

```
你：设计确认，继续

Agent：我正在使用 using-git-worktrees 技能创建隔离工作空间。

→ 检查 .worktrees/ 目录... 存在
→ 确认 .worktrees/ 已在 .gitignore 中... ✅
→ 创建 worktree: git worktree add .worktrees/todo-app -b feature/todo-app
→ 运行 npm install... 完成
→ 运行 npm test... 47/47 passing ✅

Worktree 已就绪: .worktrees/todo-app
测试基线: 47 tests passing, 0 failures
准备开始实现 Todo List 功能
```

**为什么需要这步？** Git worktree 让你的新功能在一个完全隔离的分支和目录里开发，不会影响你当前的工作目录。万一搞砸了，直接删掉这个 worktree 就行，干干净净。

---

### Step 3：writing-plans —— 拆分实现计划

```
Agent：我正在使用 writing-plans 技能创建实现计划。

（阅读设计文档，拆分为原子任务……）

计划已保存到: docs/superpowers/plans/2026-04-15-todo-app.md

计划概要:
  Task 1: 创建 TodoItem 组件 + 测试
  Task 2: 创建 TodoInput 组件 + 测试
  Task 3: 创建 TodoList 组件 + 测试
  Task 4: 整合 App 组件 + localStorage 持久化 + 测试

每个 Task 约 2-5 分钟工作量。

两种执行方式：
  1. Subagent-Driven（推荐）- 在当前会话中，每个任务派独立 Agent 执行，自动审查，全自动
  2. Inline Execution (executing-plans) - 在当前会话中持续执行，遇到阻塞时停下来确认，适合没有 subagent 支持的平台

你选哪种？

你：1，Subagent-Driven
```

**你看到了什么？** Agent 没有笼统地说"开始写代码"，而是把工作拆成了 4 个精确的小任务。每个任务都有明确的文件路径、测试代码、实现代码、验证命令。这份计划详细到"一个没见过这个项目的初级工程师也能照着做完"。

---

### Step 4：subagent-driven-development —— 逐任务执行 + 自动审查

```
Agent：我正在使用 subagent-driven-development 技能执行计划。
（提取全部 4 个任务的完整内容和上下文）

━━━ Task 1: TodoItem 组件 ━━━

→ 派遣 implementer subagent...

Implementer:
  ✅ 写了失败测试: TodoItem 显示待办文本 + 完成状态
  → 运行测试... ❌ FAIL（组件不存在）
  ✅ 实现 TodoItem 组件（最简代码）
  → 运行测试... ✅ PASS
  ✅ 自查: 发现遗漏了点击切换完成状态的交互，补充了
  ✅ 已提交 commit

→ 派遣 spec reviewer（规格审查）...
Spec Reviewer: ✅ 符合设计文档，不多不少

→ 派遣 code quality reviewer（代码质量审查）...
Code Reviewer: 
  优点: 测试覆盖好，组件简洁
  问题（重要）: 删除按钮没有 aria-label 无障碍标签

→ Implementer 修复: 添加 aria-label
→ Code Reviewer 复查: ✅ 通过

✅ Task 1 完成

━━━ Task 2: TodoInput 组件 ━━━
（同样的流程：实现 → 规格审查 → 质量审查 → 修复 → 通过）
...

━━━ Task 3: TodoList 组件 ━━━
...

━━━ Task 4: App 整合 + localStorage ━━━
...

→ 全部 4 个任务完成
→ 派遣最终代码审查 subagent...
Final Reviewer: 所有需求已实现，测试全覆盖，可以合并 ✅
```

**你看到了什么？** 整个执行过程几乎是全自动的。每个任务都经历：

1. **实现** —— 一个独立的 Agent 按计划写测试、写代码、提交
2. **规格审查** —— 另一个 Agent 检查"做得对不对"（有没有偏离设计文档）
3. **质量审查** —— 再一个 Agent 检查"做得好不好"（代码质量、边界情况）

三个 Agent 各司其职，互不干扰。你只需要在旁边看着，偶尔确认一下就行。

---

### Step 5：finishing-a-development-branch —— 收尾

```
Agent：我正在使用 finishing-a-development-branch 技能完成这次开发。

→ 运行 npm test... 62/62 passing ✅（新增 15 个测试）

实现已完成。你想怎么处理这个分支？

  1. 本地合并回 main
  2. 推送并创建 Pull Request
  3. 保留分支（稍后自己处理）
  4. 丢弃这些工作

你：2，创建 PR

Agent：
→ git push -u origin feature/todo-app
→ 创建 PR:

  Title: feat: add Todo List application
  Summary:
  - 新增 TodoItem、TodoInput、TodoList、App 四个组件
  - 实现 localStorage 持久化
  - 15 个新增测试，全部通过

→ 清理 worktree... 完成

✅ PR 已创建: https://github.com/your-org/your-repo/pull/42
```

**完美。** 从需求到 PR，每一步都有据可查、有测试保障、有审查把关。这就是 Superpowers 的完整工作流。

---

### 回顾一下你刚才经历了什么

| 步骤                             | Agent 做了什么         | 你做了什么       |
| ------------------------------ | ------------------ | ----------- |
| brainstorming                  | 提问 → 呈现设计 → 保存文档   | 回答问题 → 确认设计 |
| using-git-worktrees            | 创建隔离分支 → 跑基线测试     | （自动完成）      |
| writing-plans                  | 拆分 4 个原子任务 → 保存计划  | 选择执行方式      |
| subagent-driven-development    | 每个任务独立执行 + 双重审查    | （自动完成）      |
| finishing-a-development-branch | 跑全量测试 → 创建 PR → 清理 | 选择 PR 方式    |

你的实际操作就是：**回答几个问题、做几次确认、选一次执行方式、选一次合并方式**。剩下的脏活累活——写测试、写代码、跑测试、查规格、查质量、提交 commit、创建 PR——Superpowers 全帮你干了。

而且每一步都有证据。不是"应该没问题了"，而是"62/62 tests passing"。

---

## 五、14 个技能详解：什么时候触发，怎么用

上一章你已经走了一遍完整流程，对各个技能有了感性认识。这一章我们把所有 14 个技能摊开来，逐个讲清楚：它干什么、什么时候自动激活、你会看到什么、以及新手最容易踩的坑。

先按功能分个类，方便你脑子里有个框架：

- **协作类**（5 个）：brainstorming、writing-plans、subagent-driven-development、executing-plans、finishing-a-development-branch
- **测试与调试类**（3 个）：test-driven-development、systematic-debugging、verification-before-completion
- **代码评审类**（2 个）：requesting-code-review、receiving-code-review
- **工程工具类**（4 个）：using-git-worktrees、dispatching-parallel-agents、writing-skills、using-superpowers

### 协作类（设计到交付的完整流程）

这 5 个技能串联起来，就是从"我有个想法"到"PR 已创建"的完整链路。

---

#### 1. brainstorming（头脑风暴）

**一句话说明：** 在 Agent 写任何代码之前，强制它先搞清楚你要做什么。

**触发时机：** 你提出任何"做点什么"的请求时自动激活——新功能、新组件、修改行为，全都算。Agent 检测到你想要创造或修改什么东西，就会启动这个技能。

**实际操作：**

1. Agent 先偷偷看一眼项目现状（文件结构、最近提交、README 等）
2. 如果你提到的东西可能涉及 UI/视觉相关的问题，Agent 会单独问一句："我可以打开一个浏览器页面给你看效果图，要不要试试？"（这就是 Visual Companion，视觉助手——它会在本地启动一个轻量级服务器，在浏览器窗口中展示设计草图、对比方案等可视化内容，与终端对话形成双窗口协作）
3. 然后开始**一次只问一个问题**——目标用户是谁？核心场景是什么？需要什么技术栈？
4. 问完后，Agent 提出 2-3 个方案，附上各方案的优缺点和它推荐的选项
5. 你选了方案后，Agent 会分段展示设计细节，每段等你确认
6. 你确认后，设计文档保存到 `docs/superpowers/specs/` 目录
7. Agent 自己快速审查一遍文档（查缺补漏、查矛盾、查模糊），有问题当场修
8. Agent 请你审阅写好的设计文档，你确认后才进入下一步——这是硬门槛（HARD-GATE），用户必须明确批准设计文档，Agent 才能调用 writing-plans
9. 确认后自动调用 writing-plans 进入下一步

**避坑指南：**

- 🚫 **最常见的错误：** "这个需求太简单了，不用设计吧？" —— Superpowers 明确禁止这种想法。再简单的项目也有未审视的假设。"简单"恰恰是最容易翻车的地方。设计文档可以只有几句话，但必须存在。
- 🚫 **别让 Agent 一次问一堆问题。** 规则是"一次只问一个"。如果你发现 Agent 连珠炮似的甩出 5 个问题，提醒它慢下来。
- 🚫 **别急着说"开始做吧"。** brainstorming 有个硬门槛（HARD-GATE）：在你确认设计方案之前，Agent **不能**写任何代码、不能创建项目、不能做任何实现动作。如果你发现 Agent 还没问完问题就开始写代码了，这是技能没正确触发。

---

#### 2. writing-plans（编写计划）

**一句话说明：** 把确认好的设计拆成一个个 2-5 分钟能干完的原子任务。

**触发时机：** brainstorming 结束、你批准了设计方案之后，Agent 自动调用这个技能。

**实际操作：**

1. Agent 宣布"我正在使用 writing-plans 技能创建实现计划"
2. 它先定义文件结构——要创建哪些文件、修改哪些文件、每个文件负责什么
3. 然后把工作拆成一个个小任务，每个任务的格式是：

```
Task N: [组件名]
Files: 创建 xxx，修改 xxx，测试 xxx
Step 1: 写一个失败的测试    ← 完整的测试代码
Step 2: 运行测试，确认失败   ← 运行命令 + 预期输出
Step 3: 写最少代码让它通过   ← 完整的实现代码
Step 4: 运行测试，确认通过   ← 运行命令 + 预期输出
Step 5: 提交 commit         ← 完整的 git 命令
```

4. 计划保存到 `docs/superpowers/plans/YYYY-MM-DD-功能名.md`
5. Agent 自己审查一遍计划（检查有没有遗漏、有没有占位符、类型是否一致）
6. 最后问你选哪种执行方式：
   - **Subagent-Driven**（推荐）：在当前会话中，每个任务派一个独立 Agent 执行，自动做完规格审查 + 代码质量审查，全自动，你只需要看最终结果
   - **Inline Execution**（executing-plans）：在当前会话中持续执行任务，遇到阻塞（依赖缺失、测试不过、指令不清）时停下来问你，适合你的平台不支持 subagent（比如某些 AI 编程工具）的情况

**避坑指南：**

- 🚫 **计划里绝对不能有" TBD "、" TODO "、" 后面再补充 "这类占位符。** 每一步都必须包含完整的代码和命令。如果一个步骤说"添加适当的错误处理"而不给具体代码，这是计划失败。
- 🚫 **计划不能说"类似 Task N"。** 执行任务的 Agent 可能是乱序阅读的，它看不到"Task N"。所以每一步的代码必须完整写出，不引用其他步骤。
- 🚫 **别怕计划太长。** 好的计划详细到"一个不了解这个项目的初级工程师也能照着做完"。计划越长，执行越顺。

---

#### 3. subagent-driven-development（子代理驱动开发）

**一句话说明：** 给每个任务派一个独立的"小 Agent"去执行，做完自动审查，一个接一个推进。

**触发时机：** 你在 writing-plans 结束时选择了"Subagent-Driven"方式（推荐选项）。

**实际操作：**

1. 主 Agent 一次性读取计划的全部内容，提取所有任务的完整文本
2. 对每个任务：
   - 派一个 **implementer（实现者）** 子代理，给它完整的任务文本、上下文和约束
   - 实现者按 TDD 方式工作：写测试 → 验证失败 → 写代码 → 验证通过 → 提交
   - 实现者做完后，派一个 **spec reviewer（规格审查者）** 检查"做得对不对"——是否符合设计文档，有没有多做或少做
   - 规格审查通过后，再派一个 **code quality reviewer（代码质量审查者）** 检查"做得好不好"——代码质量、边界情况、命名等
   - 如果审查发现问题，实现者去修复，然后审查者复查，直到通过
3. 全部任务完成后，派一个最终审查者检查整个实现
4. 最后自动调用 finishing-a-development-branch 收尾

**避坑指南：**

- 🚫 **别让多个实现者并行工作。** 它们会修改相同的文件，互相冲突。任务必须一个接一个做。
- 🚫 **规格审查必须在代码质量审查之前。** 顺序不能反——先确认"做对了"，再确认"做好了"。
- 🚫 **子代理可能会问你问题。** 别忽略它的问题，认真回答后再让它继续。它的疑问说明计划或上下文有不足。

---

#### 4. executing-plans（执行计划）

**一句话说明：** 没有 subagent 支持时的备选方案——在当前会话里持续执行任务，遇到阻塞时停下来问你。

**触发时机：** 你选择了"Inline Execution"方式，或者你使用的平台不支持 subagent（比如某些 AI 编程工具）。

**实际操作：**

1. Agent 加载计划文件
2. 先**批判性地审查**计划——有没有疑问或顾虑？有就先提出来
3. 没问题的话，创建 TodoWrite 待办列表，然后逐个任务执行
4. 每一步严格按计划走，每步运行验证命令
5. 遇到阻塞（依赖缺失、测试不过、指令不清）时**立即停下来**，问你怎么办

**避坑指南：**

- 🚫 **如果你的平台支持 subagent，请用 subagent-driven-development 而不是这个。** subagent-driven = 每个任务派独立 Agent 全自动执行 + 自动审查；executing-plans = 持续执行 + 遇阻塞才停。前者质量高很多。
- 🚫 **Agent 不应该硬闯障碍。** "我不太确定，但让我试试改这个"——在 executing-plans 里，遇到不确定的事应该停下来问你，而不是猜。

---

#### 5. finishing-a-development-branch（完成开发分支）

**一句话说明：** 所有任务做完后，验证测试、给你选择怎么处理这个分支。

**触发时机：** subagent-driven-development 或 executing-plans 的最后一步自动调用。

**实际操作：**

1. **先跑全量测试**（硬门槛：测试不过就不继续）
2. 如果测试全过，给你呈现**恰好 4 个选项**：

| 选项                    | 说明                            |
| --------------------- | ----------------------------- |
| 1. 本地合并回 main         | 切回 main → merge → 删分支         |
| 2. 推送并创建 Pull Request | push → 用 `gh pr create` 创建 PR |
| 3. 保留分支（我自己处理）        | 什么都不做，worktree 保留             |
| 4. 丢弃这些工作             | 需要你手动输入 "discard" 确认，然后删分支    |

3. 你选择后 Agent 执行对应操作，需要的话清理 worktree

**避坑指南：**

- 🚫 **别在测试没过的时候选"合并"或"创建 PR"。** 技能会拦住你，但你要理解为什么——把测试没过的代码合并进主分支是灾难的开始。
- 🚫 **"丢弃"选项需要手动输入 "discard" 确认。** 这是故意设计的，防止误操作。不要让 Agent 跳过这个确认步骤。

### 测试与调试类

这 3 个技能确保你写出来的代码是靠谱的、修好的 bug 是真修好的。

---

#### 6. test-driven-development（测试驱动开发）

**一句话说明：** 先写一个会失败的测试，再写最少量的代码让它通过。就这么简单，就这么严格。

**触发时机：** Agent 在实现任何功能或修复任何 bug 时自动激活。

**核心流程（Red-Green-Refactor）：**

1. 🔴 **Red** — 写一个会失败的测试（因为功能还没实现）
2. 验证测试确实失败了（且失败的原因是功能缺失，不是拼写错误）
3. 🟢 **Green** — 写最少量的代码让测试通过
4. 验证测试确实通过了（且其他测试也没被搞坏）
5. 🔵 **Refactor** — 在测试保护下清理代码（不改行为）
6. 提交 commit，进入下一个测试

**铁律：没有失败的测试，就没有生产代码。** 如果你（或 Agent）先写了代码再补测试——**删掉代码，重新来过。** 不是开玩笑。

常见借口和真相（直接从技能文档搬过来的）：

| 借口              | 真相                                     |
| --------------- | -------------------------------------- |
| "太简单不用测"        | 简单的代码也会坏。测试只需 30 秒。                    |
| "我写完再测"         | 写完后测试一次就过了，说明什么都没证明。                   |
| "先探索一下再测"       | 可以探索，但探索完要丢掉，从 TDD 开始。                 |
| "删掉 X 小时的代码太浪费" | 沉没成本谬误。留着无法验证的代码才是真正的浪费。               |
| "TDD 会拖慢进度"     | TDD 比调试快。"实用主义"的捷径 = 在生产环境 debug = 更慢。 |
| "我已经手动测过了"      | 手动测试是临时的，没有记录，改了代码还得重测。                |

**避坑指南：**

- 🚫 **最常见的翻车点：** "这个逻辑我写完再补个测试就行。" —— 不行。测试后写 = 你测的是你写的，不是你该写的。测试先写 = 你定义的是需求，代码去满足需求。差别巨大。
- 🚫 **别保留"仅供参考"的代码。** 如果 Agent 说"我先写了代码，现在删掉当参考重新来"——这不行。"删掉"意味着真的删掉，不能偷看。

---

#### 7. systematic-debugging（系统化调试）

**一句话说明：** 遇到 bug 不能猜，必须找到根因才能动手修。

**触发时机：** 任何 bug、测试失败、意外行为——总之就是"该对的不对"的时候。

**铁律：不做根因调查，就不许修。** "我猜是 X 的问题，让我改一下试试"——这不是调试，这是盲猜。

**4 个阶段：**

**Phase 1 - 根因调查：**

- 仔细读错误信息（别跳过！）
- 稳定重现 bug（能每次都触发吗？）
- 检查最近的改动（git diff）
- 多组件系统？在每个边界加诊断日志
- 追踪数据流：错误的值从哪来的？

**Phase 2 - 模式分析：**

- 找到类似的、正常工作的代码
- 对比差异（每一个差异都列出来）
- 理解依赖关系

**Phase 3 - 假设与验证：**

- 明确写下假设："我认为根因是 X，因为 Y"
- 做最小改动来验证假设
- 验证通过 → 进入 Phase 4；没通过 → 新假设，不要在失败的假设上堆改动

**Phase 4 - 实现修复：**

- 先写一个失败的测试（重现 bug）
- 针对根因修一个地方
- 验证修复有效且没引入新问题
- 如果连续 3 次修复都失败 → 停下来，考虑是不是架构有问题

**避坑指南：**

- 🚫 **"我觉得问题出在这，让我改一下" — 这是最常见的错误。** 系统化调试不允许"试一下"。你必须先在 Phase 3 写下明确假设并验证，再在 Phase 4 动手修。
- 🚫 **别同时改多个地方。** 一次只改一个变量，否则你不知道哪个改动起了作用（或引入了新 bug）。
- 🚫 **连续修了 3 次都没好？** 大概率不是代码的问题，是架构的问题。停下来和你的搭档（或同事）聊聊。这就是 systematic-debugging 的"3 次修复失败→质疑架构"规则。

---

#### 8. verification-before-completion（完成前验证）

**一句话说明：** 没跑过验证命令，就不许说"搞定了"。

**触发时机：** Agent 准备声称任何成功、完成、修复、通过的时候——**每次**。

**铁律：没有新鲜的验证证据，就没有完成声明。** "新鲜的"意思是"在当前这条消息里刚跑过的"，不是"上一次跑过的"。

**验证门（Gate Function）：**

1. 确定什么命令能证明你的声明？
2. 跑这个命令（完整的、从头跑）
3. 读完整输出，检查退出码，数失败数
4. 输出确认声明了吗？确认 → 附上证据声明；不确认 → 报告实际情况
5. 然后你才能说"搞定了"

**这些话在验证之前绝对不能说：**

- "应该没问题了"
- "看起来可以了"
- "我很有信心"
- "应该能通过"
- "大概修好了"

**避坑指南：**

- 🚫 **最常见的违规：** Agent 说"修改完成，测试应该能通过"——不行，必须跑 `npm test`，看到绿色的 "X/X tests passing" 才能这么说。
- 🚫 **别拿 linter 通过当 build 通过。** Linter 只检查代码风格，不检查能不能编译。`npm test` 通过 ≠ `npm run build` 通过。
- 🚫 **Agent 说"搞定了"不等于真搞定了。** Agent 的成功报告需要独立验证。看 git diff，确认改动确实在那里。

### 代码评审类

代码写完了不等于写好了。这 2 个技能确保代码经过专业审查。

---

#### 9. requesting-code-review（请求代码评审）

**一句话说明：** 派一个专业的审查 Agent 来检查你刚做完的工作。

**触发时机：**

- 必须触发：每个任务完成后、大功能完成后、合并前
- 建议触发：卡住时（换个视角）、重构前（先记录现状）、复杂 bug 修复后

**实际操作：**

1. Agent 获取当前改动的 git SHA 范围
2. 派遣一个 code-reviewer 子代理，给它：
   - 你刚实现了什么
   - 计划/需求文档
   - 代码改动的范围
3. 审查者返回结果，按严重程度分类：

| 级别            | 说明        | 处理方式    |
| ------------- | --------- | ------- |
| Critical（关键）  | 会阻塞进展的问题  | 必须立即修复  |
| Important（重要） | 在继续之前应该修复 | 修复后再往下走 |
| Minor（次要）     | 记下来以后再说   | 可以暂不处理  |

**避坑指南：**

- 🚫 **别因为"改动很简单"就跳过审查。** 简单的改动也能引入微妙的 bug。
- 🚫 **别忽略 Important 级别的问题。** 它们不是"建议"，是"修完再继续"。
- 🚫 **审查者也可能说错。** 如果你用技术理由认为审查者是错的，可以反驳——但要拿代码和测试说话。

---

#### 10. receiving-code-review（接收代码评审）

**一句话说明：** 收到评审反馈后，先验证再执行，别无脑同意。

**触发时机：** 当你（或你的 Agent）收到代码评审反馈时。

**正确的处理流程：**

1. **读完所有反馈**，先别急着反应
2. **用自己的话复述**每条要求（或追问不清楚的地方）
3. **对照代码库验证**——反馈说得对吗？在这套代码库里适用吗？
4. **评估**技术合理性
5. **回复**（技术性确认或带理由的反驳）
6. **逐条实现**，每条都跑测试

**绝对禁止的回复：**

- ❌ "你说得对！"
- ❌ "好建议！"
- ❌ "我马上实现"（在验证之前）
- ❌ 任何感恩戴德的客套话

不是说不礼貌，而是这些话是**表演性同意**——嘴上说好，脑袋还没转过弯。正确的做法是：要么直接动手修（行动胜于言辞），要么用技术理由反驳。

**YAGNI 检查：** 如果审查者建议你"好好实现一下这个功能"，先搜一下代码库里有没有人用——没人用就别加。"你不需要它"（You Aren't Gonna Need It）。

**避坑指南：**

- 🚫 **反馈有不清楚的地方？别猜，先问清楚。** 如果有 6 条反馈你只看懂了 4 条，不要先实现 4 条再问剩下 2 条——它们可能是关联的，部分理解 = 错误实现。
- 🚫 **外部审查者的建议不是命令。** 验证它、质疑它、然后决定做不做。技术正确性高于社交舒适度。

### 工程工具类

这 4 个技能提供基础设施支持——工作空间、并行执行、技能创建、技能发现。

---

#### 11. using-git-worktrees（使用 Git 工作树）

**一句话说明：** 在新分支上创建一个独立的开发目录，不影响你当前的工作。

**触发时机：** brainstorming 完成、准备开始写代码时自动调用。

**实际操作：**

1. Agent 检查项目中是否已有 `.worktrees/` 目录（优先用它）
2. 如果没有，检查 CLAUDE.md 里有没有偏好设置
3. 如果都没有，问你："放在 `.worktrees/` 还是 `~/.config/superpowers/worktrees/`？"
4. 创建 worktree 之前，确认目录已被 `.gitignore` 忽略（防止误提交 worktree 内容）
5. 在 worktree 里自动检测并运行项目设置：有 `package.json` 就 `npm install`，有 `Cargo.toml` 就 `cargo build`，以此类推
6. 跑一遍测试，确认干净的基线
7. 报告："Worktree 就绪，X 个测试全过，准备开工"

**避坑指南：**

- 🚫 **别跳过 `.gitignore` 检查。** 如果 `.worktrees/` 没被忽略，worktree 里的文件会被 git 追踪，污染你的仓库。
- 🚫 **别跳过基线测试。** 如果一开始就有测试不过，后面你就分不清是新引入的 bug 还是老问题。
- 🚫 **别假设目录位置。** 按优先级来：已有目录 > CLAUDE.md 偏好 > 问用户。

---

#### 12. dispatching-parallel-agents（并行派发代理）

**一句话说明：** 多个互不相关的问题？同时派多个 Agent 分头调查，快 3 倍。

**触发时机：** 你有 2 个以上互相独立的任务，且它们之间没有共享状态或顺序依赖。

**使用条件：**

- ✅ 多个测试文件失败，且失败原因互不相关
- ✅ 多个子系统独立出问题
- ✅ 每个问题不需要其他问题的上下文就能理解
- ❌ 失败是关联的（修一个可能修好另一个）
- ❌ 需要理解整个系统状态
- ❌ Agent 会互相干扰（编辑相同的文件）

**实际操作：**

1. 把问题按独立域分组
2. 每个 Agent 获得精确的指令：范围、目标、约束、期望输出
3. 同时派遣，并行工作
4. 全部回来后：读每个摘要 → 检查冲突 → 跑全量测试 → 合并

**避坑指南：**

- 🚫 **别给一个 Agent 太宽的范围。** "修复所有测试"——它会迷路。应该"修复 `agent-tool-abort.test.ts` 的 3 个失败"——它才能集中火力。
- 🚫 **别让并行 Agent 编辑相同的文件。** 这是冲突的温床。确保每个 Agent 的文件范围不重叠。
- 🚫 **别在探索性调试时用并行。** 如果你连哪里坏了都不知道，先自己调查，定位清楚后再并行。

---

#### 13. writing-skills（编写技能）

**一句话说明：** "编写技能就是测试驱动开发应用于流程文档。"

**触发时机：** 创建新技能或修改已有技能时。

**核心理念：** 编写技能的过程和 TDD 一模一样：

| TDD 概念       | 技能创建对应              |
| ------------ | ------------------- |
| 测试用例         | 压力场景（用子代理模拟）        |
| 生产代码         | 技能文档（SKILL.md）      |
| 测试失败（Red）    | Agent 没有技能时违反规则（基线） |
| 测试通过（Green）  | Agent 有了技能后遵守规则     |
| 重构（Refactor） | 堵住新发现的漏洞            |

**实际操作：**

1. **Red：** 不写技能，先跑压力场景，记录 Agent 的违规行为和借口（原话记下来）
2. **Green：** 针对那些具体违规写技能文档
3. **Refactor：** Agent 找到新借口？加针对性的反制措施，重新测试

技能文档的 frontmatter（YAML 头）有讲究：

- `name` 只用字母、数字和连字符
- `description` 以 "Use when..." 开头，只描述触发条件，**不总结流程**（否则 Agent 会只看描述不看正文，偷工减料）

**避坑指南：**

- 🚫 **description 里别写技能的流程！** 测试发现，如果 description 里写了流程摘要，Agent 会直接按摘要做而跳过正文。比如写"每个任务后做代码审查"会导致只做一次审查，而技能正文明明要求做两次（规格审查 + 质量审查）。
- 🚫 **别一次批量创建多个技能。** 每个技能都要单独测试验证后才能做下一个。
- 🚫 **别觉得"这个技能写得很清楚了不用测"。** 对你清楚不等于对 Agent 清楚。15 分钟测试省下几小时的线上事故。

---

#### 14. using-superpowers（使用 Superpowers）

**一句话说明：** 教 Agent 如何发现和使用其他技能的"元技能"——会话启动时首先加载。

**触发时机：** 每次新会话开始时。Agent 首先加载这个技能来了解整个技能体系。

**核心规则：如果你觉得某个技能哪怕只有 1% 的可能性适用，你就必须调用它。** 这不是建议，是强制要求。

**指令优先级：**

1. 用户指令（CLAUDE.md、直接要求）→ 最高优先级
2. Superpowers 技能 → 覆盖默认系统行为
3. 默认系统提示 → 最低优先级

也就是说：如果你在 CLAUDE.md 里写了"不用 TDD"，而技能说"必须 TDD"，听你的。

**技能优先级（多个技能可能适用时）：**

1. 先用流程类技能（brainstorming、debugging）——决定"怎么做事"
2. 再用实现类技能——指导"做具体什么"

**避坑指南：**

- 🚫 **别觉得"这就是个简单问题，不用查技能"。** 问题简单不等于没有适用的技能。
- 🚫 **别"先探索一下代码库再说"。** 技能会告诉你**怎么**探索。先查技能，再动手。
- 🚫 **别凭记忆使用技能。** 技能会更新，你记得的可能是旧版本。每次都重新读取。

---

### 速查表：技能触发场景

| 你在做什么      | 应该触发的技能                                                                           |
| ---------- | --------------------------------------------------------------------------------- |
| 开始一个新功能    | brainstorming                                                                     |
| 设计已批准，准备开发 | using-git-worktrees → writing-plans                                               |
| 有计划了，准备执行  | subagent-driven-development（推荐：全自动，每个任务派独立 Agent）或 executing-plans（备选：持续执行，遇阻塞才停） |
| 正在写功能代码    | test-driven-development                                                           |
| 遇到 bug     | systematic-debugging                                                              |
| 准备说"完成了"   | verification-before-completion                                                    |
| 任务完成，要检查   | requesting-code-review                                                            |
| 收到评审反馈     | receiving-code-review                                                             |
| 所有任务完成     | finishing-a-development-branch                                                    |
| 多个独立问题要解决  | dispatching-parallel-agents                                                       |
| 想创建新技能     | writing-skills                                                                    |
| 刚打开新会话     | using-superpowers（自动加载）                                                           |

---

## 六、最佳实践：用 Superpowers 构建「企业级智能问答助手」

好了，理论讲完了，技能也过了一遍。现在我们来做一个**真正的项目**——从零开始，完整走一遍 Superpowers 工作流，让你看到每一步在真实场景中长什么样。

### 场景说明

假设你是一家中型公司的初级开发者或产品经理。公司有大量内部文档——产品文档、HR 政策、技术 Wiki、会议纪要——散落在 Confluence、Google Drive 和本地文件里。老板找到你说：

> "能不能做一个智能问答系统，让员工直接问问题，AI 从内部文档里找答案？"

好，需求来了。让我们用 Superpowers 的完整流程，从零开始做这个**基于内部知识库的企业级智能问答助手**。

---

### Phase 1：头脑风暴 — 理清需求（brainstorming 技能）

```
你：帮我做一个企业内部知识库问答系统

Agent：我正在使用 brainstorming 技能来帮你梳理需求。

先看看当前项目的情况……（扫描目录结构）
→ 这是一个全新的项目，没有已有代码。

好，让我一步步了解你的需求：

这个系统主要给谁用？
  A. 全公司所有员工
  B. 特定部门（比如客服、技术支持）
  C. 管理层

你：先做 A，全公司都能用

Agent：明白。知识源有哪些？文档格式是什么？
  - PDF？
  - Word (.docx)？
  - Markdown？
  - Confluence 页面？
  - 还是有其他的？

你：主要是 PDF 和 Confluence，还有一些 Word 文档

Agent：好。期望的响应速度？
  A. 实时（1 秒内）
  B. 快速（3-5 秒可接受）
  C. 不急（10 秒内都行）

你：B，几秒钟能接受

Agent：安全要求呢？需要权限控制吗？
  - 不同部门看到不同内容？
  - 还是所有人看所有文档？

你：第一版先不做权限，所有人看所有内容

Agent：最后一个问题——预计文档量级？
  A. 几百篇
  B. 几千篇
  C. 上万篇以上

你：先从几百篇开始，但后续会增长到几千篇

Agent：好，需求明确了。基于你的回答，我整理了 3 个技术方案供你选择：

---

**方案对比：**

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A. RAG（检索增强生成） | 向量检索 + LLM 生成回答 | 易维护、可增量更新、成本可控 | 需要向量化服务 |
| B. Fine-tuned Model | 针对内部文档微调模型 | 回答更精准 | 成本高、更新慢、维护难 |
| C. 混合方案 | 简单问题关键词检索，复杂问题走 RAG | 兼顾速度和质量 | 架构复杂 |

**我推荐方案 A（RAG）**，原因：
1. 你的文档会持续更新，RAG 支持增量添加，不用重新训练
2. 几百到几千篇文档的量级，RAG 完全能胜任
3. 成本可控——按 API 调用付费，不用 GPU 训练
4. 架构简单，容易维护

你觉得怎么样？

你：A 可以，用 RAG

Agent：好，那我来分段呈现设计方案。每一段请你看完告诉我 OK 还是有修改意见。

---

**系统架构**
```

文档导入层 → 向量化层 → 检索层 → 生成层 → 前端交互层

```
5 层架构：
- 文档导入层：支持 PDF、Word、Confluence 导入，统一转换为纯文本
- 向量化层：文本分块 + 生成 embedding 向量
- 检索层：基于向量相似度的语义检索
- 生成层：LLM 基于检索到的文档片段生成自然语言回答
- 前端交互层：Web 界面，支持提问、查看回答、显示引用来源

这个方向对吗？

你：OK

---

**核心组件**

1. **Document Processor** — 文档解析和文本分块
2. **Embedding Service** — 调用 embedding 模型生成向量
3. **Vector Store** — 向量存储和相似度检索
4. **LLM Service** — 调用大模型生成回答
5. **API Server** — RESTful API（上传文档、提问）
6. **Web Frontend** — React 聊天界面

---

**数据流**
```

上传文档 → 解析文本 → 分块(200-500字/块) → 向量化 → 存入向量库

用户提问 → 问题向量化 → 检索 Top-K 相关片段 → 拼接 Prompt → LLM 生成回答 → 返回前端

```
---

**技术选型建议**

| 组件 | 推荐方案 | 备选 |
|------|---------|------|
| Backend | Python (FastAPI) | Node.js (Express) |
| Vector Store | ChromaDB（开发）/ Milvus（生产） | Pinecone, Weaviate |
| Embedding | OpenAI text-embedding-3-small | 本地模型 (all-MiniLM-L6-v2) |
| LLM | GPT-4o-mini | Claude Haiku |
| Frontend | React + TypeScript | Vue 3 |
| 部署 | Docker Compose | K8s |

你：技术选型没问题，就用推荐的

Agent：设计文档已保存到 `docs/superpowers/specs/2026-04-15-enterprise-qa-design.md`

文档包含以下内容：
```

# 企业内部知识库问答系统 - 设计文档

## 1. 项目背景与目标

- 业务背景、目标用户、成功指标

## 2. 用户故事

- 作为员工，我想输入自然语言问题并获得基于文档的回答
- 作为管理员，我想上传新文档并自动更新知识库
- 作为员工，我想看到回答的引用来源

## 3. 系统架构

- 5 层架构图、组件交互图

## 4. 核心组件设计

- 每个组件的职责、接口、数据结构

## 5. 数据流设计

- 文档导入流、查询流

## 6. API 接口定义

- POST /upload、POST /query、GET /documents

## 7. 技术选型及理由

- 每个选型的 why

## 8. 非功能性需求

- 性能（P95 < 3s）、安全、扩展性
  
  ```
  
  ```

请你看一下设计文档，确认没问题后我们开始做实现计划。

```
**到这里，Phase 1 完成。** 你花了大约 10 分钟回答了几轮问题，换来了一份完整的设计文档。这份文档不只是给你看的——后续所有 Agent 都会参照这份文档来工作。

> 💡 **关键洞察**：注意 Agent 是怎么工作的——它**一次只问一个问题**，不会一口气甩出 10 个问题让你头大。而且问完之后不是直接动手，而是先提出 2-3 个方案让你选，再分段展示设计细节让你逐步确认。这种渐进式的需求探索和分段呈现，是 brainstorming 技能的核心设计。

---

### Phase 2：创建工作区（using-git-worktrees 技能）
```

你：设计确认，继续

Agent：我正在使用 using-git-worktrees 技能创建隔离工作空间。

→ 检查 .worktrees/ 目录... 不存在
→ 请问你希望 worktree 放在哪里？
    A. .worktrees/（推荐，已被 .gitignore 忽略）
    B. 自定义路径

你：用 .worktrees/ 吧

Agent：
→ 添加 .worktrees/ 到 .gitignore ✅
→ 创建 worktree: git worktree add .worktrees/enterprise-qa -b feature/enterprise-qa
→ 安装项目依赖... 完成
→ 验证基线: 项目无已有测试（新项目），仓库干净 ✅

Worktree 已就绪: .worktrees/enterprise-qa
准备开始实现企业级智能问答助手功能

```
**为什么这步很重要？** 因为从现在开始，你的所有代码改动都在 `.worktrees/enterprise-qa` 这个隔离目录里进行。主分支完全不受影响。万一后面发现方案走错了，直接删掉这个 worktree，一切回到原点，干干净净。就像画画先打草稿一样——草稿不满意，撕掉重来，不伤画布。

---

### Phase 3：编写实施计划（writing-plans 技能）
```

Agent：我正在使用 writing-plans 技能创建实现计划。

（阅读设计文档，拆分为原子任务……）

计划已保存到: docs/superpowers/plans/2026-04-15-enterprise-qa.md

计划概要（8 个任务）：

━━━ Task 1: 项目初始化与基础配置 ━━━

- 创建项目目录结构
- 初始化 FastAPI 应用
- 配置 requirements.txt
- 验证: uvicorn 能正常启动

━━━ Task 2: 文档处理模块 ━━━
  文件: src/document_processor.py
  测试: tests/test_document_processor.py
  TDD 步骤:
    - [ ] Step 1: 写失败测试 — 文本分块应遵守最大长度
    - [ ] Step 2: 运行测试，确认失败
    - [ ] Step 3: 实现 chunk_text 函数
    - [ ] Step 4: 运行测试，确认通过
    - [ ] Step 5: 写失败测试 — 分块应有 overlap 重叠
    - [ ] Step 6: 运行测试，确认失败
    - [ ] Step 7: 添加 overlap 支持
    - [ ] Step 8: 运行测试，确认通过
    - [ ] Step 9: 写失败测试 — PDF 文件解析为纯文本
    - [ ] Step 10: 运行测试，确认失败
    - [ ] Step 11: 实现 PDF 解析
    - [ ] Step 12: 运行测试，确认通过
    - [ ] Step 13: 提交 commit

━━━ Task 3: 向量化服务 ━━━
  文件: src/embedding_service.py
  测试: tests/test_embedding_service.py
  TDD 步骤:
    - [ ] Step 1: 写失败测试 — 单文本 embedding 生成
    - [ ] Step 2: 运行测试，确认失败
    - [ ] Step 3: 实现 embedding 生成
    - [ ] Step 4: 运行测试，确认通过
    - [ ] Step 5: 写失败测试 — 批量 embedding 处理
    - [ ] Step 6: 运行测试，确认失败
    - [ ] Step 7: 实现批量处理
    - [ ] Step 8: 运行测试，确认通过
    - [ ] Step 9: 提交 commit

━━━ Task 4: 向量存储与检索 ━━━
  文件: src/vector_store.py
  测试: tests/test_vector_store.py
  TDD 步骤:
    - [ ] Step 1: 写失败测试 — 存储向量
    - [ ] Step 2: 运行测试，确认失败
    - [ ] Step 3: 实现向量存储
    - [ ] Step 4: 运行测试，确认通过
    - [ ] Step 5: 写失败测试 — 相似度检索 Top-K
    - [ ] Step 6: 运行测试，确认失败
    - [ ] Step 7: 实现相似度检索
    - [ ] Step 8: 运行测试，确认通过
    - [ ] Step 9: 提交 commit

━━━ Task 5: LLM 问答服务 ━━━
  文件: src/qa_service.py
  测试: tests/test_qa_service.py
  TDD 步骤:
    - [ ] Step 1: 写失败测试 — 基于上下文生成回答
    - [ ] Step 2: 运行测试，确认失败
    - [ ] Step 3: 实现 QA 逻辑
    - [ ] Step 4: 运行测试，确认通过
    - [ ] Step 5: 写失败测试 — 回答包含引用来源
    - [ ] Step 6: 运行测试，确认失败
    - [ ] Step 7: 添加引用来源
    - [ ] Step 8: 运行测试，确认通过
    - [ ] Step 9: 提交 commit

━━━ Task 6: API 路由 ━━━
  文件: src/api/routes.py
  测试: tests/test_api.py
  TDD 步骤:
    - [ ] Step 1: 写失败测试 — POST /upload 上传文档
    - [ ] Step 2: 运行测试，确认失败
    - [ ] Step 3: 实现上传接口
    - [ ] Step 4: 运行测试，确认通过
    - [ ] Step 5: 写失败测试 — POST /query 提问接口
    - [ ] Step 6: 运行测试，确认失败
    - [ ] Step 7: 实现查询接口
    - [ ] Step 8: 运行测试，确认通过
    - [ ] Step 9: 提交 commit

━━━ Task 7: 前端界面 ━━━
  文件: frontend/src/App.tsx

- 聊天界面组件（输入框 + 对话历史）
- 文档上传组件
- 回答展示组件（含引用来源高亮）

━━━ Task 8: 集成测试与部署配置 ━━━

- 端到端测试（上传文档 → 提问 → 验证回答）
- Docker Compose 配置
- README 文档

每个 Task 预计 10-20 分钟。
总计约 2-3 小时完整实现。

两种执行方式：

1. Subagent-Driven（推荐）- 在当前会话中，每个任务派独立 Agent 执行，自动双重审查，全自动
2. Inline Execution (executing-plans) - 在当前会话中持续执行，遇到阻塞时停下来确认，适合没有 subagent 支持的平台

你选哪种？

你：1，Subagent-Driven

```
**你看到了什么？** 8 个任务，每个任务都精确到了具体的文件路径、测试代码和 TDD 步骤。不是"先做个文档处理"这种模糊描述，而是"先写测试 X、确认失败、实现 Y、确认通过、提交"这种机器人都能执行的指令。

> 💡 **TDD 到底长什么样？** 让我用 Task 2（文档处理模块）给你展示一个真实的 TDD 循环，这是实际代码，不是演示：

**🔴 RED（写失败测试）：**

```python
# tests/test_document_processor.py

def test_chunk_text_respects_max_length():
    """文本分块后，每块长度不应超过 max_length"""
    text = "这是一段很长的文本。" * 500  # 模拟长文档，约 5000 字
    chunks = chunk_text(text, max_length=200)
    assert all(len(c) <= 200 for c in chunks), "存在超过 max_length 的分块"
    assert len(chunks) > 1, "长文本应被分为多个分块"

def test_chunk_text_preserves_content():
    """分块不应丢失原文内容"""
    text = "第一段内容。" + "第二段内容。" + "第三段内容。"
    chunks = chunk_text(text, max_length=20)
    # 所有分块的内容都应来自原文
    for chunk in chunks:
        assert chunk.strip() in text, f"分块内容不在原文中: {chunk}"
```

运行测试：`pytest tests/test_document_processor.py -v`
结果：❌ **FAIL** — `NameError: name 'chunk_text' is not defined`

> 好！测试如预期地失败了。因为 `chunk_text` 函数还不存在——这正是我们要的。

**✅ GREEN（写最少代码让测试通过）：**

```python
# src/document_processor.py

def chunk_text(text: str, max_length: int = 200, overlap: int = 50) -> list[str]:
    """将长文本分块，支持重叠区域"""
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks
```

运行测试：`pytest tests/test_document_processor.py -v`
结果：✅ **PASS** — 2 tests passed

**提交：**

```bash
git commit -m "feat: add text chunking with overlap support"
```

这就是一个完整的 TDD 循环。先定义"正确长什么样"（测试），再让代码去满足这个定义（实现），最后提交。接下来继续写下一个失败测试（比如测试 PDF 解析），再实现，再通过，再提交。每个循环只关注一个小功能，一步一步推进。

---

### Phase 4：子代理驱动执行（subagent-driven-development 技能）

计划就绪，开始自动执行。

```
Agent：我正在使用 subagent-driven-development 技能执行计划。
（提取全部 8 个任务的完整内容和上下文）

━━━ Task 1: 项目初始化与基础配置 ━━━

→ 派遣 implementer subagent...

Implementer:
  ✅ 创建项目目录结构 (src/, tests/, frontend/)
  ✅ 初始化 FastAPI 应用 (src/main.py)
  ✅ 配置 requirements.txt (fastapi, uvicorn, chromadb, openai, pytest)
  ✅ 启动验证: uvicorn src.main:app --reload → 正常启动
  ✅ 已提交 commit

→ 派遣 spec reviewer（规格审查）...
Spec Reviewer: ✅ 符合设计文档

→ 派遣 code quality reviewer（代码质量审查）...
Code Reviewer: ✅ 通过

✅ Task 1 完成

━━━ Task 2: 文档处理模块 ━━━

→ 派遣 implementer subagent...

Implementer:
  ✅ RED: 写失败测试 chunk_text → 运行 → ❌ FAIL
  ✅ GREEN: 实现 chunk_text → 运行 → ✅ PASS
  ✅ RED: 写失败测试 PDF 解析 → 运行 → ❌ FAIL
  ✅ GREEN: 实现 PDF 解析 → 运行 → ✅ PASS
  ✅ 已提交 commit

→ 派遣 spec reviewer（规格审查）...
Spec Reviewer: ✅ 符合设计文档

→ 派遣 code quality reviewer（代码质量审查）...

[Code Reviewer Subagent Report]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task 2: 文档处理模块

Strengths（优点）:
  ✅ 职责分离清晰——解析和分块是独立函数
  ✅ 测试覆盖好——覆盖了正常和边界情况
  ✅ 有完整的 type hints

Issues（问题）:
  🔴 Important: chunk_text 空字符串输入需明确处理
     → 当 text="" 时返回空列表 []
     → 行为正确，但应补充测试用例显式验证

  🟡 Minor: max_length=200 是魔法数字
     → 建议提取为配置常量 CHUNK_MAX_LENGTH

Assessment: Important 问题建议补充测试，Minor 建议修复，均不阻塞。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

→ Implementer 处理: 补充空字符串测试 + 提取 CHUNK_MAX_LENGTH 常量
→ Code Reviewer 复查: ✅ 通过

✅ Task 2 完成

━━━ Task 3: 向量化服务 ━━━
（同样流程：实现 → 规格审查 → 质量审查 → 修复 → 通过）

━━━ Task 4: 向量存储与检索 ━━━
（这里遇到了一个 Bug，详见 Phase 5）

━━━ Task 5-7: （逐个完成）━━━

━━━ Task 8: 集成测试与部署配置 ━━━
...
```

**关键点：双重审查机制。** 每个任务完成后，不是只有一轮审查，而是两轮：

1. **Spec Reviewer（规格审查）**：你做的东西和设计文档一致吗？有没有多做或少做？——检查"做得对不对"
2. **Code Quality Reviewer（代码质量审查）**：代码写得好不好？有没有 bug、安全隐患、性能问题？——检查"做得好不好"

两轮审查都通过，才进入下一个任务。这就是为什么 Superpowers 能保证质量——不是靠运气，而是靠流程。

---

### Phase 5：遇到 Bug 怎么办（systematic-debugging 技能）

真实开发中不可能一帆风顺。让我们看看 Superpowers 怎么处理 Bug。

在 Task 4（向量存储与检索）的执行过程中，一个测试失败了：

```
FAILED tests/test_vector_store.py::test_similarity_search_returns_top_k
AssertionError: Expected 5 results, got 0
```

Agent 没有"猜一下改改试试"，而是启动 `systematic-debugging` 技能：

```
Agent：检测到测试失败。启动 systematic-debugging 技能。

━━━ Phase 1: 根因调查（Root Cause Investigation） ━━━
→ 仔细读错误信息：Expected 5 results, got 0 — 是检索返回空
→ 运行失败的测试... ❌ 复现成功（每次都返回 0 结果，100% 复现率）
→ 测试意图：存入 10 个向量 → 用一个查询向量检索 Top-5 → 期望返回 5 个结果
→ 实际结果：返回 0 个结果
→ 检查最近改动（git diff）... 刚新增了向量存储模块

━━━ Phase 2: 模式分析（Pattern Analysis） ━━━
问题出在"存"还是"取"？

→ 单独测试存储：存入 10 个向量，检查数据库中向量数量 → 10 ✅
  结论：存储没问题

→ 单独测试检索：直接用查询向量检索 → 返回 0 结果 ❌
  结论：检索有问题

继续缩小范围——找类似的能正常工作的代码做对比：
→ 检查查询向量的维度... 1536 维（OpenAI text-embedding-3-small）
→ 检查存储向量的维度... 384 维（本地模型 all-MiniLM-L6-v2）
→ 列出差异：唯一的差异就是 embedding 模型不同
→ ⚡ 找到根因了！

━━━ Phase 3: 假设与验证（Hypothesis and Testing） ━━━
→ 明确写下假设："我认为根因是 embedding 维度不匹配——存储用 384 维模型，查询用 1536 维模型，导致相似度计算返回空结果"
→ 做最小改动验证：修改查询接口使用同一个 384 维模型
→ 验证：运行失败测试 → ✅ PASS（返回 5 个结果）
→ 假设验证通过 → 进入 Phase 4

根本原因：Embedding 维度不匹配！
  - 存储文档时用的 embedding 模型输出 384 维
  - 查询时用的 embedding 模型输出 1536 维
  - 向量库计算相似度时维度不匹配，返回空结果

━━━ Phase 4: 实施修复（Implementation） ━━━
→ 先写一个失败测试重现 bug：测试不同 embedding 模型混用时应抛出明确错误 → ❌ FAIL
→ 针对 root cause 修复：修改 EmbeddingService，确保文档 embedding 和查询 embedding 使用同一个模型
→ 添加维度一致性检查：在存储前验证 embedding 维度与数据库配置匹配
→ 运行失败测试... ✅ PASS
→ 运行全部测试... ✅ 28/28 passing
→ 提交 commit: "fix: ensure consistent embedding model for docs and queries"
```

**你看到了什么？** Agent 没有瞎猜，而是系统地走了一遍：根因调查 → 模式分析 → 假设与验证 → 实施修复。每一步都有明确的目标和方法，不是"试试看"而是"先证明再动手"。整个过程只用了大约 3 分钟，但如果是人工"猜测式调试"，可能要花 30 分钟甚至更久——因为你可能会先怀疑向量库配置、然后怀疑检索算法、接着怀疑数据格式……在每个错误方向上浪费时间。

> ⚠️ **3 次修复失败规则**：如果 Agent 连续 3 次尝试修复都没解决，systematic-debugging 会要求它停下来——大概率不是代码层面的问题，而是架构设计有缺陷。此时应该退回到 brainstorming 重新审视方案，而不是继续在错误的方向上蛮干。

> 💡 **调试的本质**：不是"改代码让报错消失"，而是"找到为什么错了，然后针对性地修"。systematic-debugging 技能强制 Agent 遵循这个原则，避免了"改了 A、B 坏了、改了 B、C 又坏了"的死循环。

---

### Phase 6：完成交付（finishing-a-development-branch 技能）

所有 8 个任务完成，进入收尾阶段。

```
Agent：所有任务已完成。我正在使用 finishing-a-development-branch 技能。

→ 运行全量测试...
  pytest tests/ -v → 47/47 passing ✅
  （从 0 个测试增长到 47 个，每个都有对应的实现代码）

→ 代码统计:
  - 新增文件: 12 个
  - 新增代码: ~1,200 行
  - 测试覆盖率: 89%

实现已完成。你想怎么处理这个分支？

  1. 本地合并回 main — 适合个人项目或你有 main 的写权限
  2. 推送并创建 Pull Request — 适合团队协作（推荐）
  3. 保留分支（稍后自己处理） — 你想自己决定什么时候合并
  4. 丢弃这些工作 — 需要手动输入 "discard" 确认

你：2，创建 PR

Agent：
→ 推送代码: git push -u origin feature/enterprise-qa
→ 创建 Pull Request:

  Title: feat: 企业内部知识库问答系统 (RAG)

  Summary:
  - 文档处理：支持 PDF、Word 解析 + 智能分块（overlap 支持）
  - 向量服务：OpenAI Embedding 集成 + 批量处理
  - 向量存储：ChromaDB 集成 + 相似度检索 Top-K
  - 问答服务：RAG 管线 + 引用来源追踪
  - API：FastAPI 文档上传 + 查询接口
  - 前端：React + TypeScript 聊天界面
  - 部署：Docker Compose 一键启动

  Tests: 47/47 passing | Coverage: 89%

→ 清理 worktree... 完成

✅ PR 已创建: https://github.com/your-org/enterprise-qa/pull/1
```

**交付完成！** 从老板说"能不能做一个智能问答系统"到你创建 PR，整个过程大约 2-3 小时（大部分是 Agent 在自动执行）。你实际参与的时间大概 30 分钟——回答需求问题、确认设计方案、偶尔看看中间产物。

---

### 回顾：完整流程一张图

```
老板的一句话需求
       ↓
Phase 1: brainstorming（~10 分钟）
  → Agent 逐个提问 → 你回答 → 方案对比 → 分段确认 → 设计文档
       ↓
Phase 2: using-git-worktrees（~1 分钟）
  → 隔离工作区创建 → 基线验证
       ↓
Phase 3: writing-plans（~5 分钟）
  → 8 个原子任务 → 每个都有完整 TDD 步骤 → 选择执行方式
       ↓
Phase 4: subagent-driven-development（~1.5-2 小时）
  → 逐任务执行 → 实现者写测试写代码 → 规格审查 → 质量审查 → 修复 → 通过
       ↓
Phase 5: systematic-debugging（如需要，~3-5 分钟/次）
  → 系统化定位和修复 Bug（不是瞎猜！）
       ↓
Phase 6: finishing-a-development-branch（~3 分钟）
  → 跑全量测试 → 创建 PR → 清理 worktree
       ↓
✅ 交付完成：47 个测试、89% 覆盖率、完整功能
```

**你的实际参与时间：约 30 分钟。Agent 工作时间：约 2 小时。质量保障：双重审查 + TDD + 系统化调试。** 这就是 Superpowers 的价值。

---

## 七、产品经理视角：如何与 AI 协作

这一节专门写给产品经理。如果你是开发者，可以跳过——但如果你和 PM 共事，强烈推荐让他们也看看。

### PM 在 Superpowers 工作流中的角色

Superpowers 不是让 PM 变成程序员，而是让 PM 能**在正确的时机参与正确的决策**。整个流程中 PM 需要做的事情不多，但每一件都很关键：

**1. 需求定义阶段（brainstorming）—— 这是你最重要的 15 分钟**

Agent 会问你问题。你的回答质量直接决定了最终产品的方向。这个阶段的投入产出比极高——多花 10 分钟描述清楚需求，能省掉后面 2 小时的返工。

- ❌ 别说"你看着办"、"差不多就行"、"参考 XX 产品做一个"
- ✅ 要说具体的用户场景、使用目标和成功标准

好需求 vs 差需求的对比：

> ❌ "做一个类似 ChatGPT 的问答系统"——太模糊了，Agent 不知道给谁用、解决什么问题
> 
> ✅ "我们的客服团队每天要手动回答 200+ 个重复问题，主要是退货政策、物流查询和产品规格。希望做一个系统，员工输入问题后，AI 从公司内部文档（PDF 和 Confluence）里找到答案并给出引用来源。目标是减少 50% 的人工咨询量。"

你看，第二种描述给出了：用户是谁（客服）、痛点是什么（重复问题多）、文档来源是什么（PDF 和 Confluence）、期望效果是什么（减少 50%）。Agent 收到这种需求，做出来的东西才会对。

**2. 设计评审阶段 —— 你要审阅设计文档**

Agent 会分段呈现设计方案。PM 要重点看这些：

- **用户故事**：这真的是用户想要的流程吗？
- **交互流程**：用户操作步骤合理吗？够简单吗？客服能学会用吗？
- **边界情况**：文档格式不对怎么办？没找到答案怎么办？AI 编了一个看起来对但实际错的答案怎么办？

不要只看架构图和技术选型——那些给开发者看。PM 应该站在用户角度，问自己"如果我是客服，我会用这个吗？"

**3. 执行阶段 —— 做 checkpoint 检查**

你不需要盯着每行代码，但每个 Task 完成后会有审查报告。扫一眼就好：

- 规格审查有没有说"不符合设计"？有的话赶紧沟通，越早改成本越低
- 质量审查有没有标红的严重问题？

如果 Agent 在执行过程中问你问题（比如"这里的交互应该怎样"），及时回答——它会等你，你不回答它就不继续。

**4. 验收阶段 —— 用真实数据测试**

看测试报告说"47/47 passing"是好事，但不够。PM 应该：

- 用真实的业务问题测试（比如拿一个客服实际被问过的问题去试）
- 关注边界情况：输入很模糊的问题、问文档里没有的内容、上传格式错误的文件
- 看回答质量：引用来源准不准？回答是不是编的（hallucination）？
- 不要只测 happy path（正常情况），专门测异常情况——这才是 AI 容易翻车的地方

### PM 常见误区

| 误区                    | 为什么错                              | 正确做法                   |
| --------------------- | --------------------------------- | ---------------------- |
| 给一个模糊的需求，等 Agent 做完再看 | Agent 会按自己的理解做，大概率不是你要的           | brainstorming 阶段就给详细需求 |
| 不参与设计评审，只看最终结果        | 设计阶段是修正方向的最佳时机，越晚改越贵              | 每个设计 section 都给反馈      |
| 觉得 AI 写的代码不需要人看       | AI 也会犯低级错误，尤其边界情况                 | PR 阶段让有经验的开发者 review   |
| 只测 happy path         | 用户不会按你设想的方式用产品                    | 专门测异常和边界情况             |
| 需求变了好几次，不好意思说         | 越早说成本越低，brainstorming 阶段改需求几乎是免费的 | 有变化立即说，别攒到最后           |

> 💡 **PM 的黄金法则**：在 brainstorming 阶段多花 10 分钟描述清楚需求，能省掉后面 2 小时的返工。这不是浪费时间，这是最高效的时间投入。

---

## 八、常见问题 FAQ

**Q1: Superpowers 和直接用 Claude Code 有什么区别？**

A: 没有 Superpowers 的 Claude Code 就像一个没有导师的天才实习生——能力很强但没有纪律。它会跳过设计直接写代码、不写测试就声称完成、遇到 Bug 瞎猜乱改。"帮做一个登录页"，它 3 秒钟就甩出 500 行代码，但可能连密码校验都忘了做。

Superpowers 不是增强了它的能力，而是给它套上了"资深工程师级别"的流程约束。能力 × 纪律 = 质量产出。没有纪律的天才，产出可能还不如有纪律的普通人。

---

**Q2: 我必须用 Claude Code 吗？**

A: 不是。Superpowers 支持 Cursor、Codex、OpenCode、Gemini CLI 等多个平台。但 Claude Code 的 subagent（子代理）支持最成熟，能实现"每个任务派一个独立 Agent 执行"的自动化流程，效果最好。如果你用的是其他平台，可以用 `executing-plans` 技能的 Inline Execution 模式，在当前会话中逐步执行，效果也不错，只是自动化程度低一些。

---

**Q3: 技能可以自定义吗？**

A: 可以。Superpowers 提供了 `writing-skills` 技能，帮你创建自己的技能。比如你们团队有自己的代码规范、部署流程、审查清单，都可以做成技能。但核心技能（brainstorming、writing-plans、TDD 等）经过大量实战测试和调优，不建议随意修改。更好的做法是：在 CLAUDE.md 中添加项目级别的自定义指令，比如"对于小改动，跳过 brainstorming 直接实现"。你的指令优先级高于技能默认行为。

---

**Q4: 如果我觉得某个技能的流程太重了怎么办？**

A: Superpowers 的核心理念是"宁可多花 10 分钟设计，也不要浪费 2 小时返工"。但这是建议，不是法律。你可以通过 CLAUDE.md 覆盖任何技能的行为。比如加一句"对于 CSS 样式调整，跳过 brainstorming 直接实现"，你的指令优先级高于技能。

不过建议你先完整跑一遍流程，理解每个技能为什么存在，然后再决定哪些可以简化。就好比学开车——你得先学会在所有路况下安全驾驶，然后再决定哪些路可以开快一点。没学会就跳步骤，那叫危险驾驶。

---

**Q5: TDD 真的有必要吗？AI 写的代码也需要测试驱动吗？**

A: **特别需要。** 这可能是整个 FAQ 中最重要的一条。

AI 生成的代码有一个特点：**看起来正确，但常常有微妙的边界 bug。** 比如空字符串处理、并发问题、类型转换错误、off-by-one 错误——这些在"正常情况"下不会出现，但在生产环境中迟早会炸。

TDD 的价值不只是"有测试代码"，更在于"在写代码之前想清楚它应该做什么"。测试先行的过程本身就是一种思考方式——你被迫定义"正确"长什么样，然后才动手写实现。这个"先定义后实现"的过程，比测试代码本身更有价值。

---

**Q6: 可以跳过某些技能吗？**

A: 你的项目你做主。但建议先完整跑一遍流程，理解每个技能的价值，然后再决定哪些可以简化。没有经历过痛点，很难理解规则为什么存在。就好比你问一个老程序员"为什么要写测试"，他会给你讲一堆道理，但只有你经历过"凌晨 3 点被叫起来修线上 bug"的痛，才会真正理解。

先完整跑一遍，感受每个环节的价值，然后你才有资格决定哪些可以简化。

---

## 九、总结：你的下一步

恭喜你读到了这里。如果你跟着走完了前面的内容，你现在应该理解了：

- Superpowers **不是**一个 AI 工具，而是一套工作流程——给它加上"先设计后编码、先测试后实现、证据优先于声明"的纪律
- 它的 14 个技能覆盖了从需求到交付的完整链路，每个技能都有明确的触发时机和使用规则
- 从需求到交付，每个步骤都有对应的技能保障质量，不是靠运气，而是靠流程
- 你（人类）的角色是**做决策**——回答需求问题、确认设计方案、验收最终成果
- Agent 负责执行——写测试、写代码、跑测试、做审查、提交代码、创建 PR

**下一步做什么？**

1. **安装 Superpowers**（选你最熟悉的平台，推荐 Claude Code）
2. **选一个小功能练手**——不要上来就做生产项目，先用一个简单的功能体验完整流程（比如一个 Todo List、一个计数器组件、一个简单的 API）
3. **用 brainstorming 技能设计**——感受一下"Agent 不直接写代码，而是先问你问题"的体验
4. **完整走一遍 brainstorming → plan → execute → finish 流程**
5. **关注 TDD 和系统化调试带来的质量提升**——这是 Superpowers 价值最大的两个环节
6. 逐步尝试更复杂的项目

Superpowers 的核心不是某个具体的技能，而是一种**工作方式**：尊重流程、小步快跑、证据驱动。这种工作方式不仅适用于 AI 编程，也是优秀软件工程的基础。即使有一天你不再用 AI 写代码，这些习惯也会让你受益——因为它们不是 AI 时代的产物，而是软件工程几十年沉淀下来的最佳实践，只是 Superpowers 让它们变得更容易坚持。

**有用的链接：**

- 项目仓库：https://github.com/obra/superpowers
- Discord 社区：https://discord.gg/35wsABTejz
- 博客介绍：https://blog.fsck.com/2025/10/09/superpowers/

---

> 🎯 **记住：最好的学习方式是动手做。** 读完了就去开一个 Agent 会话，说"帮我规划一个功能"，然后让 Superpowers 带你飞。第一次可能有点不习惯——Agent 居然不直接写代码，而是先问你一堆问题——但这正是 Superpowers 的精髓。试一次，你就回不去了。
