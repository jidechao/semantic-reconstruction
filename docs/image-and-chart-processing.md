# 图片与图表处理

`semantic-reconstruction` v1.2 提供两层图片和图表处理能力：

1. **引用层处理**：默认启用，离线、确定性、无需视觉模型，会为每张图片生成独立证据知识单元。
2. **视觉理解**：配置多模态模型后启用，支持本地/data URI 图片字节输入，也支持把 HTTP(S) URL 直接传给模型。

## 支持格式

| 输入 | evidence 类型 | 说明 |
|---|---|---|
| Markdown 图片 `![alt](path "title")` | `image` | 提取 alt、title、路径、来源类型、行号 |
| Markdown 图片 `![alt](<path with spaces>)` | `image` | 支持带空格的本地路径或 URL |
| Markdown 引用式图片 `![alt][key]` | `image` | 解析 `[key]: path "title"` 定义 |
| HTML `<img>` | `image` | 提取 src、alt、title、width、height |
| HTML `<figure>` | `figure` | 保留整块证据 |
| HTML `<figcaption>` / Markdown 图注 | `image_caption` | 与最近图片或图表双向关联 |
| Mermaid fenced code | `chart_code` | 提取图表类型、方向、节点和关系 |
| fenced SVG | `chart_svg` | 提取 title、desc、文本和基础图形 |
| 内联 `<svg>` | `chart_svg` | 不执行脚本，只保留安全文本证据 |
| `.svg` 文件引用 | `chart_svg` | 保留本地文件引用和哈希 |

## 图片来源解析

| 来源 | `source_type` | `location_kind` | 行为 |
|---|---|---|---|
| `assets/flow.png` | `local` | `relative_path` | 相对 Markdown 文件所在目录解析 |
| `C:\images\flow.png` | `local` | `absolute_path` | 默认允许读取；可配置禁止 |
| `file:///C:/images/flow.png` | `local` | `file_uri` | 解码为本机路径后读取 |
| `https://example.com/flow.png` | `remote` | `remote_url` | SDK 不下载，视觉模型启用时直接传 URL |
| `data:image/png;base64,...` | `data` | `data_uri` | 解码后校验 MIME 和大小 |

默认配置：

```python
from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor

config = ReconstructionConfig(
    image_understanding="auto",
    include_image_references=True,
    include_chart_blocks=True,
    allow_absolute_image_paths=True,
)
sdk = SemanticReconstructor(config)
```

引用层会：

- 保留图片 URL 或本地路径
- 标记 `source_type` 与 `location_kind`
- 对存在的本地文件计算 SHA-256
- 将 `如下图、下图、如图所示、见图 N` 绑定到后文资产
- 将图注绑定到最近图片或图表
- 为每张图片生成独立 `generation_mode="image_evidence"` 知识单元
- 对缺失 `src`、本地文件不存在、MIME 不支持、路径越界和大小超限输出诊断

## 视觉理解配置

```python
config = ReconstructionConfig(
    mode="rule",
    image_understanding="auto",
    allow_absolute_image_paths=True,
    vision_api_key="your-vision-api-key",
    vision_base_url="https://api.example.com/v1",
    vision_model="your-multimodal-model",
    vision_timeout_seconds=120.0,
    vision_max_retries=1,
    vision_max_image_bytes=10 * 1024 * 1024,
    vision_min_confidence=0.55,
)
```

也可以通过进程环境变量提供：

```text
VISION_API_KEY
VISION_BASE_URL
VISION_MODEL
```

模式：

| 模式 | 行为 |
|---|---|
| `off` | 不调用视觉模型，只做引用层处理和图片诊断 |
| `auto` | 默认；配置完整时启用，未配置时走引用层 |
| `required` | 必须配置视觉模型或注入自定义客户端，否则初始化失败 |

自定义客户端需实现：

```python
def describe_image(request) -> ImageDescription
```

`ImageRequest` 对本地/data URI 图片携带字节数据；对 HTTP(S) 图片携带 `source_url` 且 `data` 为空。

## 安全边界

允许 MIME：

- `image/png`
- `image/jpeg`
- `image/webp`
- `image/gif`

限制：

- 相对路径解析后必须位于 Markdown 文件所在目录内
- 本机绝对路径与 `file:///` 默认允许；企业环境可用 `allow_absolute_image_paths=False` 关闭
- SDK 不下载 HTTP(S) 图片；远程 URL 直接传给视觉 provider
- 远程图片不适用 SDK 侧大小上限
- 不处理 PDF、视频、音频
- 不执行 SVG 脚本
- 不把图片二进制或 data URI payload 写入 JSON
- 不记录 API key
- 本地/data URI 超过大小限制或 MIME 不支持时回退引用层

## 独立图片知识单元与报告

每张图片都会生成一个图片证据知识单元，并绑定最近标题、图注和 HTML 容器。视觉理解成功后：

- 单元状态为 `pending_business_review`
- `self_explanation` 包含描述、可见文字、图表类型、置信度和限制
- evidence metadata 追加 `vision`
- 报告输出“图片与视觉证据层”
- 模型调用摘要记录 `mode="vision"` 和 token 用量

视觉模型未配置、调用失败或输出被拒绝时，图片单元保留引用层并标记待人工复核。图片缺失或路径无效时，图片单元阻断，并在顶层 `diagnostics` 输出对应 code。

视觉描述只作为可见内容证据，不新增业务规则；与正文证据冲突时对应单元阻断。

## 推荐写法

```markdown
### 经销商审批流程

申请提交后，系统按照下图展示的流程执行初审。

![经销商审批流程](assets/dealer-flow.png "经销商审批流程")

图 1：经销商审批流程。左侧为申请节点，右侧为审批节点。
```

推荐同时提供有意义的 `alt`、`title` 和独立图注。对跨目录资产，优先使用相对路径并确保资产随 Markdown 一起分发；确需引用本机绝对路径时，明确其可移植性风险。
