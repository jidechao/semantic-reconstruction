# Taste Skill 使用指南：让 AI 写出不像 AI 的前端界面

> 作者：老季聊AI
> 
> 本指南面向会用 Cursor、Claude Code、Codex 等 AI 编码工具的开发者和产品经理。

---

## 一、Taste Skill 是什么？解决什么问题？

### AI 写的界面为什么都长得一样？

你肯定见过这种现象——不管你让 AI 生成什么着陆页，出来都是那几样：

- 居中大标题 + 副标题 + 按钮，万年不变的「英雄区」
- 左边文字右边图片的固定布局
- 到处都是半透明毛玻璃卡片
- 破折号（em-dash）被滥用成灾
- 每个 section 都有编号（"01"、"02"、"03"……）
- 滚动提示箭头、装饰性色带、假的产品截图

社区给这种现象取了个名字叫 **"slop"**——就是 AI 吐出来的那种看起来没毛病、但就是没有灵魂的模板界面。它不是「丑」，而是「平庸」。每一个元素单独看都还行，放在一起就是没有设计师做的感觉。

### Taste Skill 的定位

**Taste Skill** 是一个 **Anti-Slop（反模板化）前端技能库**。它不是框架，不是组件库，而是一组给 AI Agent 看的「设计准则」——告诉 AI 怎么写前端才不像流水线出品。

打个比方：普通的 AI 写界面就像用 PPT 模板做汇报，换换文字就交了。Taste Skill 做的事相当于请了一个有审美的高级设计师站在 AI 后面，每写一行代码都提醒它：「别用那个布局，太俗了。」

### 一句话概括

**13 个独立的 skill，每个解决一个特定的前端设计问题。** 你不需要全装，按需选择就好。

---

## 二、三种安装方式

Taste Skill 的安装依赖 [Vercel 的 `npx skills add` 工具](https://github.com/vercel-labs/agent-skills)，当然你也可以手动使用。

### 方式一：全量安装（一次装完 13 个 skill）

```bash
npx skills add https://github.com/Leonxlnx/taste-skill
```

这会把仓库里 `skills/` 目录下的所有 13 个 skill 都安装到你的项目中。如果你不确定需要哪些，或者你想都试试，就用这个命令。

### 方式二：指定安装单个 skill（推荐）

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

**⚠️ 重要提醒**：`--skill` 后面的名字是 SKILL.md 文件里 YAML frontmatter 中的 `name:` 字段值，**不是文件夹名**。

举个例子你就明白了：

- 文件夹名是 `taste-skill/`，但安装名是 `design-taste-frontend`
- 文件夹名是 `gpt-tasteskill/`，但安装名是 `gpt-taste`
- 文件夹名是 `soft-skill/`，但安装名是 `high-end-visual-design`

本文后面每个 skill 的介绍里都会列出准确的安装命令，直接复制就行。

### 方式三：手动复制 SKILL.md

如果你不想用命令行，或者你的工具不支持 `npx skills add`，可以直接把对应 skill 文件夹里的 `SKILL.md` 文件：

- 复制到你的项目根目录
- 或者直接粘贴到 ChatGPT / Codex 的对话里

这种方式最灵活，但需要你自己管理更新。

### 更新已有的 skill

如果你之前安装过 v1 版本，重新运行安装命令就会自动升级到 v2：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

安装名没变，所以你之前的脚本不需要改。如果你需要锁定在 v1，用 `design-taste-frontend-v1` 这个安装名。

---

## 三、两大类 Skill 总览

13 个 skill 分成两类，区别在于**输出的是什么**：

### 实现类（输出代码）—— 10 个

这类 skill 会让 AI 直接输出前端代码。装了之后，AI 生成的 HTML/CSS/JS/React 代码质量会有质的飞跃。

| Skill            | 安装名                          | 一句话说明                         |
| ---------------- | ---------------------------- | ----------------------------- |
| taste-skill      | `design-taste-frontend`      | 主力 skill，通用型，适配绝大多数场景         |
| taste-skill-v1   | `design-taste-frontend-v1`   | 老版本，仅在你依赖 v1 的行为时使用           |
| gpt-taste        | `gpt-taste`                  | 为 GPT/Codex 优化，更强的反重复机制       |
| image-to-code    | `image-to-code`              | 先生成设计图再写代码，图→分析→实现            |
| redesign-skill   | `redesign-existing-projects` | 改造已有项目，不重写，只优化                |
| soft-skill       | `high-end-visual-design`     | 高端奢华风，冷静优雅，像奢侈品网站             |
| output-skill     | `full-output-enforcement`    | 专治 AI 偷懒截断输出                  |
| minimalist-skill | `minimalist-ui`              | Notion/Linear 风的极简编辑风格        |
| brutalist-skill  | `industrial-brutalist-ui`    | 粗野主义 + 瑞士印刷风，硬核工业感            |
| stitch-skill     | `stitch-design-taste`        | Google Stitch 专用，输出 DESIGN.md |

### 图片生成类（输出设计稿图片）—— 3 个

这类 skill **不写代码**，只输出设计参考图。适合跟 ChatGPT Images 等图片生成工具配合使用。

| Skill                    | 安装名                        | 一句话说明                     |
| ------------------------ | -------------------------- | ------------------------- |
| imagegen-frontend-web    | `imagegen-frontend-web`    | 网页设计参考图（着陆页、营销页等）         |
| imagegen-frontend-mobile | `imagegen-frontend-mobile` | 移动端 App 屏幕设计参考图           |
| brandkit                 | `brandkit`                 | 品牌视觉系统（Logo、配色、字体、Mockup） |

---

## 四、逐个 Skill 详细介绍

### 4.1 taste-skill（主力 skill）

**安装名**：`design-taste-frontend`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

#### 一句话说明

这是整个项目的**核心 skill**（v2 实验版，1206 行），让 AI 先读懂你的需求、推断设计方向、再写代码，出来的界面不会像模板。

#### 适用场景

- 做一个新的 SaaS 着陆页
- 做设计师/开发者个人作品集网站
- 对现有页面进行重新设计
- 任何「不想让 AI 写得千篇一律」的前端页面

**不适合**（§13 明确排除的场景）：

- 后台管理系统 / 仪表盘 / Admin 面板
- 数据表格（请用 TanStack Table 或 AG Grid）
- 多步骤表单 / 向导式流程
- 代码编辑器（请用 Monaco / CodeMirror）
- 原生移动端（请用 Apple HIG / Material Design）
- 实时协作 UI（如光标同步、OT 等）

#### 谁适合用

开发者 + 产品经理都可以。开发者直接在编码工具里用，产品经理可以用它来生成高质量的设计参考。

#### 三大旋钮（Dials）

这是 taste-skill 最核心的配置机制，三个 1-10 的旋钮控制设计的三个维度：

| 旋钮                   | 含义          | 低值（1-3）       | 高值（8-10）      |
| -------------------- | ----------- | ------------- | ------------- |
| **DESIGN_VARIANCE**  | 设计偏离标准模板的程度 | 保守、居中、传统      | 大胆、非对称、实验性    |
| **MOTION_INTENSITY** | 动画和运动感      | 静态、仅 hover 效果 | 滚动动画、磁性跟随、电影感 |
| **VISUAL_DENSITY**   | 每屏的视觉信息密度   | 留白多、像画廊       | 紧凑、信息密集       |

**默认值：8/6/4**（有创意但不疯狂、适度动效、干净留白）

不同场景的推荐预设：

| 场景       | DESIGN_VARIANCE | MOTION_INTENSITY | VISUAL_DENSITY |
| -------- | --------------- | ---------------- | -------------- |
| SaaS 着陆页 | 7               | 6                | 4              |
| 创意代理商    | 9               | 8                | 3              |
| 设计师作品集   | 8               | 7                | 3              |
| 政府/公共服务  | 3               | 2                | 5              |
| 极简主义     | 5-6             | 3-4              | 2-3            |
| 活泼有趣     | 9-10            | 8-10             | 3-4            |

你可以在 prompt 里直接写「把 DESIGN_VARIANCE 调到 9，MOTION 到 8」来调整。

#### 核心特性

1. **Brief Inference（需求推断）**：AI 在写代码之前先「读懂你的意图」——页面类型、调性关键词、目标受众、参考资料，然后输出一行「设计读取」描述。比如：*"读取为：面向技术买家的 B2B SaaS 着陆页，采用 Linear 风格极简语言，偏向 Tailwind + Geist + 克制动效。"*

2. **Design System Map（设计系统映射）**：会自动匹配到真实的设计系统（Material Design、Fluent、Carbon、shadcn 等），以及原生 CSS 美学风格（玻璃拟态、Bento、粗野主义等）。

3. **Anti-AI-Tells（反 AI 特征清单）**：一个详尽的「禁用清单」，包括：禁用 em-dash 破折号、禁用 section 编号、禁用假产品 UI 截图、禁用装饰性文字条、禁用滚动提示箭头等。

4. **GSAP 动效模式**：内置三种经典 GSAP 代码骨架——Sticky-Stack（粘性堆叠）、Horizontal-Pan（水平平移）、Scroll-Reveal Stagger（滚动揭示交错）。

5. **Pre-Flight Check（起飞前检查）**（§14）：代码输出前的**硬性检查矩阵**——这不是可选项。包含 50+ 项逐项检查，从「零 em-dash 容忍」到「Core Web Vitals 达标（LCP < 2.5s, INP < 200ms, CLS < 0.1）」，任何一项不通过就不算完成。这是 taste-skill 区别于其他 skill 的核心质量门控。

6. **暗色模式协议**（§8）：默认支持明暗双模式。不只是简单的颜色反转，而是要求定义 token 策略、确保对比度和视觉层级在两种模式下保持一致、并对 `prefers-reduced-transparency` 提供回退方案。

7. **重设计协议**：三种模式——Greenfield（全新设计）、Preserve（保留现有风格）、Overhaul（完全翻新）。
   
   > **💡 Hero 区硬性规则**（§4.7，这是用户最常犯错的地方）：
   > 
   > - 标题最多 2 行，副标题最多 20 词且最多 4 行
   > - CTA 必须无需滚动即可看到
   > - Hero 最多 4 个文本元素（eyebrow 或品牌条、标题、副标题、CTA）
   > - 顶部内边距上限 `pt-24`
   > - "Used by / Trusted by" Logo 墙放在 Hero 下方，不在 Hero 内部
   > - 导航必须单行，高度 ≤ 80px

8. **Block Library（区块库）**：内置 hero、feature、social-proof、pricing、cta、footer、portfolio、transition、navigation 等区块模板。

#### 使用提示

在 prompt 里提到「landing page」「portfolio」「redesign」等关键词就会自动触发。你也可以在 prompt 中指定旋钮值，比如：

> 用 taste-skill 做一个创意代理商着陆页，DESIGN_VARIANCE 调到 9，MOTION_INTENSITY 调到 8，走暗色系。

---

### 4.2 taste-skill-v1（经典老版本）

**安装名**：`design-taste-frontend-v1`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend-v1"
```

#### 一句话说明

最初版本的 taste-skill，已被冻结（永不修改），仅在你依赖 v1 的特定行为时才需要用它。

#### 适用场景

- 你之前的项目用 v1 做的，升级到 v2 后某些地方出了问题
- 你的工作流中某些自定义配置跟 v2 有冲突
- 你需要一个更简单、更可预测的 skill（v1 没有 Brief Inference 和 Pre-Flight Check）

#### 谁适合用

已经在使用 v1 并且不想冒险升级的老用户。**新用户请直接用 v2。**

#### 核心特性

1. 同样有三个旋钮（DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY），默认值 8/6/4
2. 确定性的排版规则——字体大小、行高、字间距都有硬性规定
3. 颜色校准——不会出现 AI 常见的「彩虹配色」问题
4. 布局多样化——防止 AI 总是用居中布局
5. 反卡片滥用——不让 AI 把所有内容都塞进卡片里
6. **创意主动实现**（§4）：磁性微物理交互（按钮跟随鼠标）、永久微交互（脉冲、打字机、浮动、微光效果）、弹簧物理动效、Framer Motion 布局过渡、交错编排的瀑布式揭示。

技术栈默认：React/Next.js + Tailwind + framer-motion + Phosphor/Radix 图标。

#### 使用提示

只有在你明确需要 v1 时才安装。日常使用请直接选 `design-taste-frontend`（v2）。

---

### 4.3 gpt-taste（GPT/Codex 专版）

**安装名**：`gpt-taste`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "gpt-taste"
```

#### 一句话说明

专为 GPT/Codex 系列 Agent 设计的加强版 skill，通过 Python 随机模拟打破 AI 的默认重复行为。

#### 适用场景

- 你使用 ChatGPT、Codex 或基于 GPT 系列模型的编码工具
- 你发现 AI 总是输出一模一样的布局（左边文字右边图片、卡片排列……）
- 你需要 Awwwards 级别的高级动效

#### 谁适合用

主要面向使用 GPT 系列模型的开发者。

#### 核心特性

1. **Python 驱动的真随机化**：AI 在生成之前会模拟 `random.choice()` 来选择布局、字体、组件和 GSAP 动效模式——防止模型每次都默认选第一个选项。

2. **AIDA 页面结构**：遵循经典的营销文案结构——Attention（吸引注意）→ Interest（激发兴趣）→ Desire（唤起欲望）→ Action（促成行动），section 之间留大间距（`py-32` 到 `py-48`）。

3. **Hero 区双行铁律**：大标题（H1）绝不能超过 2-3 行，使用超宽容器确保文字不换行。

4. **无缝 Bento Grid**：使用 `grid-flow-dense`，数学验证 `col-span`/`row-span`，确保没有丑陋的空隙。

5. **高级 GSAP 动效**：滚动固定、图片缩放渐变、文字擦除、卡片堆叠等专业动效。

6. **组件武器库**：内联排版图片、水平手风琴、无限滚动跑马灯、证言轮播等。

7. **强制 Pre-Flight `<design_plan>`**：在写任何代码之前，AI 必须输出一个设计计划块，包含：Python 随机执行结果、AIDA 结构检查、Hero 数学验证（确认 H1 行数）、Bento 网格密度验证（数学证明无空格）、标签清扫和按钮对比度检查。只有这个计划通过后才开始写代码。

8. **Meta-Label 永久禁令**：禁止使用 "SECTION 01"、"QUESTION 05"、"ABOUT US" 等元标签——它们看起来廉价且不专业。

#### 使用提示

在 prompt 中明确使用 AIDA 结构，比如：

> 用 gpt-taste 做一个 SaaS 产品着陆页，遵循 AIDA 结构，使用 GSAP ScrollTrigger 做滚动固定动效。

---

### 4.4 image-to-code（图→代码流水线）

**安装名**：`image-to-code`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "image-to-code"
```

#### 一句话说明

先让 AI 生成设计参考图，再分析图片，最后写出匹配的前端代码——完整的「图→分析→实现」流水线。

#### 适用场景

- 你想要一个高质量着陆页，但不想让 AI 直接盲写代码
- 你希望先看到设计方向，确认后再让它写代码
- 你在做 hero section、营销页面或作品集的视觉化流程

#### 谁适合用

开发者（主要）。这个 skill 需要你用的工具支持图片生成能力。

#### 核心特性

1. **强制工作流顺序**：图片生成 → 图片分析 → 代码实现，绝不能跳过第一步。
2. **逐 section 生成图片**：每个区块一张独立图片（不是一整张压缩的大图），8 个 section = 8 张图。
3. **9 个可调参数**：DESIGN_VARIANCE（8）、VISUAL_DENSITY（3）、ART_DIRECTION（8）、IMPLEMENTATION_CLARITY（9）、IMAGE_USAGE_PRIORITY（9）、SPACING_GENEROSITY（9）、ANALYSIS_PRECISION（10，深度提取设计细节）、IMAGE_GENERATION_EAGERNESS（10，尽可能多生成图片）、UI_SIMPLICITY_DISCIPLINE（9，极简去噪）。
4. **绝不偷懒**：有能力生成图片时必须生成，绝不跳过。

#### 使用提示

在 prompt 中明确说明工作流：

> 用 image-to-code skill 做一个着陆页。先生成设计图，再分析，最后写代码。

---

### 4.5 redesign-skill（改造已有项目）

**安装名**：`redesign-existing-projects`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "redesign-existing-projects"
```

#### 一句话说明

不重写，只优化——扫描现有项目的 UI 问题，诊断，然后针对性地修复。

#### 适用场景

- 你有一个已经写好的网站，看起来「还行但不够好」
- 你之前的 AI 生成的页面太模板化了，想提升一下
- 你的老项目需要视觉升级，但不能影响功能

#### 谁适合用

开发者（主要）。产品经理可以用它来了解现有 UI 的问题清单。

#### 核心特性

1. **三步流程**：Scan（扫描代码库）→ Diagnose（诊断问题）→ Fix（修复）。先看清楚再动手，不会一上来就大改。

2. **全面的审计清单**：覆盖 9 个维度——排版、颜色/表面、布局、交互/状态、内容、组件模式、图标、代码质量、战略性省略。

3. **固定优先级**：字体替换 → 颜色清理 → hover 状态 → 布局调整 → 组件替换 → 添加状态 → 打磨细节。先改效果最大的，不改影响最小的。

4. **尊重现有技术栈**：不管你用的是 Tailwind、vanilla CSS 还是 styled-components，都在现有基础上改，不会强制换成别的。

5. **不破坏功能**：绝不重写、不打破现有交互、保持所有改动可 review。

6. **具体的升级技巧**：
   
   - **排版升级**：可变字体动画（滚动时插值字重）、轮廓到填充过渡、文字遮罩揭示（大字作为视频窗口）
   - **布局升级**：破碎网格 / 非对称、最大化留白、视差卡堆叠、分屏反向滚动
   - **动效升级**：弹簧物理、交错入场、滚动驱动的遮罩揭示和 SVG 绘制
   - **表面升级**：真正的毛玻璃（带内边框和内阴影模拟折射）、聚光灯边框（鼠标跟随发光）、噪点纹理叠加、带色调的彩色阴影

#### 使用提示

把这个 skill 指向你的项目根目录：

> 用 redesign-skill 审计并优化这个项目的 UI，保持现有功能不变。

---

### 4.6 soft-skill（高端视觉设计）

**安装名**：`high-end-visual-design`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "high-end-visual-design"
```

#### 一句话说明

让 AI 设计出看起来很贵的界面——冷静、优雅、充满高级感，像 15 万美金设计公司的出品。

#### 适用场景

- 做奢侈品/高端品牌的数字体验
- 需要「Apple 风」或「Linear 风」的精致 UI
- 产品需要传达「高级感」和「信赖感」

#### 谁适合用

开发者和产品经理都适合。产品经理可以用它来传达「我们想要高端感」这个模糊需求。

#### 核心特性

1. **三种氛围原型**：
   
   - **Ethereal Glass**（空灵玻璃）—— 暗色科技风
   - **Editorial Luxury**（编辑奢华）—— 温暖奶白色调
   - **Soft Structuralism**（柔和结构）—— 清新白色系

2. **三种布局原型**：
   
   - **非对称 Bento**（Asymmetrical Bento）
   - **Z 轴层叠**（Z-Axis Cascade）
   - **编辑式分栏**（Editorial Split）

3. **「双框」嵌套架构**：外框容器 + 内框核心，创造纵深层次感。

4. **弹簧物理动效**：所有动画使用弹簧物理参数，拒绝线性缓动。包括流体岛导航栏、汉堡按钮变形等精心编排的微交互。

5. **禁用清单**：Inter/Roboto 字体、Lucide/FontAwesome 图标、通用阴影、线性缓动——全部禁用。

#### 使用提示

在 prompt 中指定你想要的氛围：

> 用 high-end-visual-design skill，走 Ethereal Glass 风格，做一个暗色系科技产品着陆页。

---

### 4.7 output-skill（完整输出强制）

**安装名**：`full-output-enforcement`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "full-output-enforcement"
```

#### 一句话说明

专治 AI 偷懒——防止它截断输出、写 `// TODO`、省略代码块。

#### 适用场景

- AI 总是写到一半就停了，留下 `// ...` 或 `// TODO: 其余代码`
- 你要求 5 个组件，AI 只写了 2 个就开始偷懒
- 输出的代码里有「为了简洁省略」之类的注释

#### 谁适合用

所有被 AI 偷懒行为困扰的开发者。

#### 核心特性

1. **硬性禁用模式**：`// ...`、`// TODO`、`"for brevity"`、`"rest follows same pattern"`、裸 `...` 等偷懒写法，全部禁止。

2. **三步执行流程**：
   
   - **Scope**（范围）：先清点要交付的内容数量
   - **Build**（构建）：全部生成
   - **Cross-check**（交叉检查）：对照范围清单逐项验证

3. **长输出处理**：当代码太长可能被截断时，写到干净断点处停下，输出 `"[PAUSED — X of Y complete]"`，下次接着写。不会在函数中间断掉。

4. **最终检查**：无禁用模式、所有请求项都在、代码可运行。

#### 使用提示

这个 skill 通常和其他 skill 组合使用。在 prompt 里强调：

> 用 taste-skill 做这个页面，同时应用 full-output-enforcement，确保完整输出所有代码。

---

### 4.8 minimalist-skill（极简编辑风格）

**安装名**：`minimalist-ui`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "minimalist-ui"
```

#### 一句话说明

Notion / Linear 风格的极简编辑式 UI——温暖单色调、克制配色、扁平 Bento 网格。

#### 适用场景

- 做一个像 Notion 或 Linear 那样的产品型网站
- 你需要干净、专业、「工具感」的界面
- 想要极简但不无聊的设计

#### 谁适合用

开发者和产品经理都适合。特别适合做工具型产品的团队。

#### 核心特性

1. **温暖单色调配色**：
   
   - 画布色：`#FFFFFF` / `#F7F6F3`
   - 边框色：`#EAEAEA`
   - 强调色：柔和的粉红、粉蓝、粉绿、粉黄等淡彩色

2. **精选字体**：
   
   - 无衬线：SF Pro Display / Geist
   - 衬线：Newsreader / Playfair
   - 等宽：Geist Mono

3. **组件系统**：Bento Box 网格、纯黑 CTA 按钮、药丸标签、无边框手风琴、按键微 UI 等。

4. **禁用清单**：Inter/Roboto、渐变、霓虹色、毛玻璃效果、全圆角容器、emoji——全部禁止。

#### 使用提示

明确描述你想要的风格：

> 用 minimalist-ui skill 做一个类似 Linear 的产品着陆页，温暖极简风格。

---

### 4.9 brutalist-skill（工业粗野主义）

**安装名**：`industrial-brutalist-ui`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "industrial-brutalist-ui"
```

#### 一句话说明

融合瑞士印刷风和军事终端美学的硬核工业界面——极端字号对比、刚性网格、模拟衰减效果。

#### 适用场景

- 做一个看起来像「机密蓝图」或「军用仪表盘」的数据密集型界面
- 你需要强烈视觉冲击力的作品集或编辑型网站
- 想要一种「反消费级 UI」的实验性设计

#### 谁适合用

有明确视觉方向的开发者。这个风格比较极端，不适合所有项目。

#### 核心特性

1. **双视觉模式**（每个项目只选一个，不能混用）：
   
   - **Swiss Industrial Print**（瑞士工业印刷）—— 浅色新闻纸背景 `#F4F4F0`、碳黑墨水、危险红强调色
   - **Tactical Telemetry / CRT Terminal**（战术遥测 / CRT 终端）—— 暗色 `#0A0A0A`、终端绿 `#4AF626`（可选，仅用于单个特定 UI 元素）、全面等宽字体

2. **极端字号对比**：超大号大写标题 + 极小等宽元数据，形成强烈的视觉张力。

3. **纹理干扰效果**：半色调、扫描线、CRT 辉光、位图抖动——模拟模拟信号的衰减和噪声。

4. **禁用清单**：渐变、柔和阴影、半透明效果、现代消费级 UI 模式——全部禁止。

#### 使用提示

先确定你要用哪个视觉模式：

> 用 industrial-brutalist-ui skill，走 Swiss Industrial Print 模式，做一个编辑型作品集网站。

---

### 4.10 stitch-skill（Google Stitch 专用）

**安装名**：`stitch-design-taste`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "stitch-design-taste"
```

#### 一句话说明

专门为 Google Stitch（labs.google.com/stitch）设计的 skill，输出 DESIGN.md 文件作为设计唯一真实来源。

#### 适用场景

- 你在使用 Google Stitch 生成 UI
- 你需要一个结构化的设计规范文件来指导 AI 生成一致的界面
- 你想在 Stitch、Cursor、Gemini CLI 之间保持设计一致性

#### 谁适合用

使用 Google Stitch 的开发者和设计师。

#### 核心特性

1. **DESIGN.md 单一来源**：生成一个 7 大部分的设计规范文件，作为所有生成的唯一参考。

2. **四个旋钮**：Creativity（创意）、Density（密度）、Variance（多样性）、Motion Intent（动效意图），默认 8/4/8/6。
   
   > **注意**：stitch-skill 的四旋钮系统（Creativity / Density / Variance / Motion Intent）和 taste-skill 的三旋钮系统（DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY）是**不同的配置体系**，名字和默认值都不一样。如果你同时使用两个 skill，注意区分。

3. **DESIGN.md 的 7 个部分**：
   
   - Visual Theme（视觉主题）
   - Color Palette（调色板）
   - Typography（字体）
   - Components（组件）
   - Layout（布局）
   - Motion（动效）
   - Anti-Patterns（反模式）

4. **配套模板文件**：包含一个 DESIGN.md 模板，可以直接拿来填。

5. **MCP 集成**：可通过 Stitch MCP Server 与 Cursor、Gemini CLI 等工具集成。

#### 使用提示

配合 Google Stitch 使用：

> 用 stitch-design-taste skill 生成 DESIGN.md，用于 Google Stitch 生成 SaaS 产品着陆页。

---

### 4.11 imagegen-frontend-web（网页设计参考图）

**安装名**：`imagegen-frontend-web`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "imagegen-frontend-web"
```

#### 一句话说明

**只生成图片，不写代码。** 为网页设计生成高质量参考图，每个 section 一张独立图片。

#### 适用场景

- 你需要网页设计的视觉参考图（着陆页、营销页的 section 设计）
- 你想先确定设计方向，再交给编码 agent 实现
- 你在使用 ChatGPT Images 等图片生成工具

#### 谁适合用

开发者和产品经理都适合。产品经理可以用它来快速生成设计方向供团队讨论。

#### 核心特性

1. **硬规则：每个 section 一张图**：8 个 section = 8 张图片，绝不压缩成一张大图。这一点非常重要——很多 AI 喜欢把所有内容塞进一张图里，这个 skill 禁止这种行为。

2. **8 个可调参数**：DESIGN_VARIANCE（设计方差，默认 8）、VISUAL_DENSITY（视觉密度，默认 4）、ART_DIRECTION（艺术方向，默认 8）、IMPLEMENTATION_CLARITY（实现清晰度，默认 9）、IMAGE_USAGE_PRIORITY（图片使用优先级，默认 9）、SPACING_GENEROSITY（间距宽裕度，默认 8）、LAYOUT_VARIATION（布局变化度，默认 8）、CONVERSION_DISCIPLINE（转化纪律，默认 8）。

3. **Hero 构图多样化**：不会总是用「左边文字右边图片」的固定构图，内置 9+ 种替代方案。

4. **统一的调色板**：所有图片使用同一个配色方案，确保整体一致性。

5. **叙事概念主线**：设计不是随机的，而是有一条视觉叙事线，还包含「第二眼发现」的细节设计。

#### 使用提示

在 prompt 中说明你要什么类型的页面和多少个 section：

> 用 imagegen-frontend-web skill 生成一个 SaaS 着陆页的设计参考图，6 个 section，每个 section 一张独立图片。

然后你可以把这些图片交给编码 agent（配合 `image-to-code` skill）来实现。

---

### 4.12 imagegen-frontend-mobile（移动端设计参考图）

**安装名**：`imagegen-frontend-mobile`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "imagegen-frontend-mobile"
```

#### 一句话说明

**只生成图片，不写代码。** 专为移动端 App 屏幕设计生成高质量参考图，自带手机 Mockup 框架。

#### 适用场景

- 设计移动 App 的界面（iOS / Android / 跨平台）
- 需要一组风格统一的 App 屏幕设计参考
- 做用户引导流程、登录注册、首页、设置等常见页面的设计探索

#### 谁适合用

开发者和产品经理都适合。特别适合移动端产品的早期设计探索。

#### 核心特性

1. **丰富的屏幕类型**：支持引导页、登录注册、首页、个人中心、设置、聊天、电商、金融、健康、效率工具、社交等各种类型的移动端界面。

2. **手机 Mockup 框架**：默认在高端 iPhone Mockup 框架内展示，让设计图看起来更专业。

3. **多屏幕一致性**：同一组设计图中，所有屏幕保持一致的配色、字体和视觉语言。

4. **图片主导的构图**：不是简单的色块 + 文字，而是以图片为主角的构图方式。

5. **不适用于**：网站、着陆页、桌面仪表盘、代码生成——这些场景请选其他 skill。

#### 使用提示

在 prompt 中明确你要的屏幕类型：

> 用 imagegen-frontend-mobile skill 生成一个健身 App 的设计参考图，包括引导页、首页、训练详情、个人中心 4 个屏幕。

---

### 4.13 brandkit（品牌视觉系统）

**安装名**：`brandkit`
**安装命令**：

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "brandkit"
```

#### 一句话说明

**只生成图片，不写代码。** 生成专业的品牌视觉系统图——Logo 方向、配色方案、字体系统、Mockup 等全套品牌物料。

#### 适用场景

- 新项目需要一套完整的品牌视觉定义
- 你需要 Logo 方向探索（多方案对比）
- 你要做品牌展示、品牌手册、视觉世界演示

#### 谁适合用

开发者和产品经理都适合。特别适合需要从头建立品牌视觉的早期项目。

#### 核心特性

1. **深色画布 + 网格布局**：在深灰色画布上以网格方式呈现品牌物料，看起来像专业设计公司的出品。

2. **支持 10 种品牌风格**：极简、电影感、编辑风、暗色科技、奢华、文化、安全、游戏、开发工具、消费级 App——总有一种适合你的项目。

3. **完整的品牌物料**：Logo 概念、构图、字体、Mockup、艺术指导的图片——一个品牌需要的视觉元素全覆盖。

4. **一板一核心理念**：每张品牌板聚焦一个强有力的品牌概念，不会把所有东西塞进一张图里。

#### 使用提示

在 prompt 中描述你的品牌调性：

> 用 brandkit skill 生成一组品牌视觉系统图，科技初创公司风格，暗色系，极简方向，需要包含 Logo 概念、配色方案和 Mockup。

---

## 五、Skill 选择决策树

不知道该用哪个？跟着这个流程走：

```
你要做什么？
│
├─ 做一个全新的网页/着陆页
│  └─ taste-skill（主力通用）或 gpt-taste（GPT 专版）
│
├─ 改进已有的项目
│  └─ redesign-skill
│
├─ 确定了视觉风格
│  ├─ 要极简 Notion/Linear 风 → minimalist-skill
│  ├─ 要高端奢华感 → soft-skill
│  ├─ 要硬核工业风 → brutalist-skill
│  └─ 要用 Google Stitch → stitch-skill
│
├─ AI 总是偷懒/截断输出
│  └─ output-skill（通常跟其他 skill 组合用）
│
├─ 需要设计参考图（不写代码）
│  ├─ 网页设计 → imagegen-frontend-web
│  ├─ 移动 App → imagegen-frontend-mobile
│  └─ 品牌视觉 → brandkit
│
├─ 想先看设计图再写代码
│  └─ image-to-code（图→分析→代码 完整流水线）
│
└─ 在用 v1 且不想升级
   └─ taste-skill-v1
```

简单记法：

- **新项目** → `design-taste-frontend`
- **老项目** → `redesign-existing-projects`
- **看图再做** → `image-to-code`
- **只要图** → `imagegen-frontend-web` / `imagegen-frontend-mobile` / `brandkit`
- **偷懒问题** → `full-output-enforcement`

---

## 六、常见问题 FAQ

### Q：Taste Skill 和其他 AI 设计技能有什么不同？

市面上有不少 AI 设计工具和 prompt，但它们大多只解决一个问题。Taste Skill 的核心不同在于：

1. **13 个专精 skill，不是一个大而全的方案**。每个 skill 只做一件事，做到位。
2. **可调节的旋钮系统**（不是简单的 on/off），让你精确控制设计方向。
3. **基于研究驱动的 Anti-Slop 规则**，不是拍脑袋定的禁止清单。
4. **框架无关**——React、Vue、Svelte 都能用，规则针对设计意图而非特定 API。

### Q：支持 React / Vue / Svelte 吗？

**都支持。** Taste Skill 的规则针对的是设计意图（排版、配色、布局、动效），不是某个框架的 API。不管你用的是 React、Vue、Svelte 还是纯 HTML/CSS，都能用。

不过，默认的技术栈推荐是：

- CSS：Tailwind v4（如果项目需要 v3 也可以）
- React 动效：`motion/react`（新版包名）
- 滚动动画：GSAP
- 图标：Phosphor → HugeIcons → Radix → Tabler（按优先级）

### Q：v1 和 v2 怎么选？

**新项目直接用 v2**（安装名 `design-taste-frontend`）。

v2 相比 v1 增加了：

- Brief Inference（需求推断，写代码前先读懂你的意图）
- Design System Map（设计系统映射）
- Anti-AI-Tells（反 AI 特征的完整禁用清单）
- GSAP 代码骨架（三种经典动效模式的即用代码）
- Pre-Flight Check（交付前硬性检查清单）
- Redesign Protocol（重设计的三种模式）
- Block Library（内置区块模板）

v1 已经冻结不再修改。只有在你之前的项目依赖 v1 的行为、且升级 v2 后出了问题时，才需要用 v1。

### Q：图片生成 skill 能写代码吗？

**不能，也不应该。** 三个图片生成 skill（`imagegen-frontend-web`、`imagegen-frontend-mobile`、`brandkit`）只输出设计参考图。这是有意为之的设计——先确定视觉方向，再写代码。

工作流建议：

1. 用图片生成 skill 生成设计参考图
2. 确认设计方向
3. 把图片交给编码 agent（配合 `image-to-code` 或 `taste-skill`）来实现

### Q：怎么配合 ChatGPT Images 使用？

直接把图片生成 skill 的 SKILL.md 文件粘贴到 ChatGPT 对话里，然后描述你要什么：

1. 复制 `imagegen-frontend-web/SKILL.md` 的内容
2. 粘贴到 ChatGPT 对话
3. 告诉它：「按照这个 skill 的规则，生成一个 SaaS 着陆页的设计参考图」
4. 把生成的图片保存下来
5. 在 Cursor / Claude Code / Codex 中配合 `taste-skill` 或 `image-to-code` 来实现代码

### Q：不写代码的产品经理能用吗？

**能用，而且很有价值。** 特别是：

- **imagegen-frontend-web**：生成网页设计参考图，可以拿去跟设计师或开发沟通
- **imagegen-frontend-mobile**：生成移动端设计参考图
- **brandkit**：生成品牌视觉系统，用于品牌方向讨论

这三个 skill 不需要你写任何代码。你只需要能跟 ChatGPT（或其他支持图片生成的 AI）对话就行。

---

## 七、实用小贴士

### 怎么在 prompt 里写才能发挥最大效果

Taste Skill 在 prompt 越具体的时候效果越好。以下是几个技巧：

**1. 提到你的目标受众**

不要只说「做一个着陆页」，而是说：

> 做一个面向技术买家的 B2B SaaS 着陆页，受众是 CTO 和技术负责人。

**2. 给出参考风格**

> 想要类似 Linear.so 那种极简科技感。

或者：

> 参考 Apple 产品页的高级感和大留白。

**3. 指定旋钮值**

> DESIGN_VARIANCE 调到 9，MOTION 到 8，DENSITY 保持 4。

**4. 说明暗色还是亮色**

> 走暗色系，支持暗色模式。

**5. 说明你不需要什么**

> 不要卡片式布局，不要破折号分隔线，不要 section 编号。

### 多个 skill 可以组合使用吗？

**可以，而且推荐组合使用。** 最常见的组合：

| 组合                                        | 适用场景           |
| ----------------------------------------- | -------------- |
| `taste-skill` + `output-skill`            | 做着陆页 + 防 AI 偷懒 |
| `imagegen-frontend-web` + `image-to-code` | 先生成设计图，再写代码    |
| `soft-skill` + `output-skill`             | 高端风格 + 完整输出    |
| `minimalist-skill` + `output-skill`       | 极简风格 + 完整输出    |
| `brutalist-skill` + `output-skill`        | 工业风 + 完整输出     |

`output-skill` 是个百搭组合件——任何 skill 都可以跟它组合，确保 AI 不会偷懒。

### 怎么调整三旋钮

三旋钮是 `taste-skill`（v2）和 `taste-skill-v1` 的核心机制。调整方式：

**在 prompt 中直接指定**：

> 把 DESIGN_VARIANCE 设为 5，MOTION_INTENSITY 设为 3，VISUAL_DENSITY 设为 2。

**用氛围关键词间接调整**：

v2 内置了一个「氛围词→旋钮值」的映射表：

| 氛围词             | DESIGN_VARIANCE | MOTION_INTENSITY | VISUAL_DENSITY |
| --------------- | --------------- | ---------------- | -------------- |
| 极简（minimalist）  | 5-6             | 3-4              | 2-3            |
| 活泼（playful）     | 9-10            | 8-10             | 3-4            |
| 高端（premium）     | 7-8             | 5-6              | 2-3            |
| 大胆（bold）        | 9-10            | 7-8              | 4-5            |
| 严肃 B2B（serious） | 4-5             | 2-3              | 4-5            |
| 暗色科技（dark tech） | 8-9             | 7-8              | 3-4            |

所以在 prompt 里说「我想要活泼的风格」和「把 DESIGN_VARIANCE 设到 9-10」效果是一样的。

### 技术栈约定速查

Taste Skill 全系列共同遵守的技术栈约定：

| 方面       | 推荐                                    | 不推荐                    |
| -------- | ------------------------------------- | ---------------------- |
| CSS 框架   | Tailwind v4（v3 如项目需要）                 | —                      |
| React 动效 | `motion/react`                        | `framer-motion`（旧包名）   |
| 滚动动画     | GSAP（固定/擦除场景）                         | —                      |
| 图标库      | Phosphor → HugeIcons → Radix → Tabler | Lucide（不推荐）；手写 SVG（禁止） |
| 动画缓动     | 弹簧物理（spring physics）                  | 线性缓动（永远不要用）            |

---

## 八、快速上手：30 秒开始使用

如果你不想看完上面的所有内容，这里是最快的上手方式：

**第一步**：安装主力 skill

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"
```

**第二步**：在你的 AI 编码工具里写 prompt

> 用 taste-skill 做一个 SaaS 产品着陆页，暗色系，包含 hero、功能介绍、定价、CTA 四个 section，走 Linear 风格的极简科技感。

**第三步**：看效果，然后根据需要调整

- 太保守？把 DESIGN_VARIANCE 调高
- 太花哨？把 MOTION_INTENSITY 调低
- 太空旷？把 VISUAL_DENSITY 调高

就这样。不需要配置文件，不需要安装依赖，不需要改代码。把 SKILL.md 放到 AI 能看到的地方，它就知道怎么做了。

---

> **Taste Skill** · MIT License · [github.com/Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) · [tasteskill.dev](https://tasteskill.dev)
