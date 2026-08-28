# 输入格式

## 支持范围

- 编码：UTF-8
- 输入：Markdown 文本或 `.md` 文件
- 大小：默认单文档 2,000,000 字符，可通过 `max_document_chars` 调整

## 解析结构

SDK 会解析：

- ATX 标题：`#` 到 `######`
- 段落
- 有序和无序列表
- Markdown 表格
- 引用块
- HTML 块
- fenced code block：``` 或 ~~~
- Markdown 图片和引用式图片
- HTML `<img>`、`<figure>`、`<figcaption>`
- Mermaid fenced code
- fenced SVG 和内联 SVG

## 关键规则

### 1. 代码块不会污染标题树

代码块中的 `#`、表格和伪 Markdown 只作为 `code_example` 证据保留。

### 2. 表格行继承表头

表格每一行都会携带：

- 原表头
- 当前行值
- 原表起始行
- 当前行精确行号

### 3. HTML 不生成业务结论

HTML 导航、按钮、图片和外链会保留为 evidence，用于审计，但不会被提升为规则。

### 4. 图片和图表默认走引用层

SDK 会提取：

- alt
- title
- 本地路径 / 远程 URL / data URI
- 精确行号
- heading path
- 本地文件 SHA-256
- 图注
- Mermaid 图表类型、节点和关系
- SVG title、desc 和文本

相对路径按 Markdown 所在目录解析；本机绝对路径和 `file:///` 默认可读；HTTP(S) URL 不会被 SDK 下载，配置视觉模型后会原样传给模型。

### 5. 证据必须可回溯

每个 evidence block 包含：

- 稳定 ID
- 文档 ID
- 源路径
- 起止行号
- heading path
- block 类型
- 清洗后的文本
- 原始 Markdown 或 HTML
- asset / chart / vision metadata

### 6. 外部引用会阻断

如果文本依赖“附件、另行规定、以最新通知为准”但当前 Markdown 没有该证据，SDK 会输出 `blocked` 和 `known_gaps`，不会猜测内容。

## 推荐写法

- 用标题表达对象和章节边界
- 条件、动作、例外尽量放在相邻段落
- 表格保持标准 Markdown 格式
- 图片提供有意义 alt 和 title
- 图片下方提供 `图 N：...` 图注
- 版本和生效时间写在靠近规则的段落或标题下
- 引用附件时同时提供附件内容
