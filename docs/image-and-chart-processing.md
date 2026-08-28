# 图片与图表处理

`semantic-reconstruction` v1.1 提供两档图片和图表处理能力：

1. **引用层处理**：默认启用，离线、确定性、无需视觉模型。
2. **视觉理解**：配置多模态模型后启用，仅读取本地图片和 data URI。

## 支持格式

| 输入 | evidence 类型 | 说明 |
|---|---|---|
| Markdown 图片 `![alt](path "title")` | `image` | 提取 alt、title、路径、来源类型、行号 |
| Markdown 引用式图片 `![alt][key]` | `image` | 解析 `[key]: path "title"` 定义 |
| HTML `<img>` | `image` | 提取 src、alt、title、width、height |
| HTML `<figure>` | `figure` | 保留整块证据 |
| HTML `<figcaption>` / Markdown 图注 | `image_caption` | 与最近图片或图表双向关联 |
| Mermaid fenced code | `chart_code` | 提取图表类型、方向、节点和关系 |
| fenced SVG | `chart_svg` | 提取 title、desc、文本和基础图形 |
| 内联 `<svg>` | `chart_svg` | 不执行脚本，只保留安全文本证据 |
| `.svg` 文件引用 | `chart_svg` | 保留本地文件引用和哈希 |

## 引用层处理

默认配置：

```python
from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor

config = ReconstructionConfig(
    image_understanding="auto",
    include_image_references=True,
    include_chart_blocks=True,
)
sdk = SemanticReconstructor(config)
```

引用层会：

- 保留图片 URL 或本地路径
- 识别本地 / 远程 / data URI
- 对存在的本地文件计算 SHA-256
- 将 `如下图、下图、如图所示、见图 N` 绑定到后文资产
- 将图注绑定到最近图片或图表
- 缺少图片、路径不存在或缺少 alt / 图注时输出证据缺口

远程图片只会保留引用，不会被抓取。

## 视觉理解配置

显式配置：

```python
config = ReconstructionConfig(
    mode="rule",
    image_understanding="auto",
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
| `off` | 不调用视觉模型，只做引用层处理 |
| `auto` | 默认；配置完整时启用，未配置时走引用层 |
| `required` | 必须配置视觉模型或注入自定义客户端，否则初始化失败 |

自定义客户端：

```python
sdk = SemanticReconstructor(
    ReconstructionConfig(image_understanding="required"),
    vision_client=my_vision_client,
)
```

自定义客户端需实现：

```python
def describe_image(request) -> ImageDescription
```

## 安全边界

视觉理解仅处理：

- Markdown 文件所在目录内的本地图片
- data URI

允许 MIME：

- `image/png`
- `image/jpeg`
- `image/webp`
- `image/gif`

限制：

- 不抓取远程 HTTP / HTTPS 图片
- 不读取 Markdown 目录之外的本地路径
- 不处理 PDF、视频、音频
- 不执行 SVG 脚本
- 不把图片二进制或 data URI payload 写入 JSON
- 不记录 API key
- 超过大小限制或 MIME 不支持时回退引用层

## 输出 metadata

图片 evidence 示例：

```json
{
  "asset_type": "image",
  "source_type": "local",
  "path": "assets/flow.png",
  "resolved_path": "...",
  "exists": true,
  "mime_type": "image/png",
  "sha256": "...",
  "alt": "流程图",
  "title": "审批流程",
  "caption_evidence_id": "doc-b0005"
}
```

视觉理解成功时追加：

```json
{
  "vision": {
    "model": "your-multimodal-model",
    "description": "...",
    "visible_text": "...",
    "chart_type": "flowchart",
    "objects_or_nodes": [],
    "relationships": [],
    "colors_or_legends": [],
    "limitations": [],
    "confidence": 0.82,
    "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "total_tokens": 0
    }
  }
}
```

视觉描述只作为证据保留：

- 不新增业务规则
- 不替代原文结论
- 参与视觉理解的知识单元输出 `pending_business_review`
- 视觉输出与正文冲突时输出 `blocked`

## 失败回退

以下情况不会中断整份文档处理：

- 视觉模型超时或异常
- 输出不是合法结构化描述
- confidence 低于 `vision_min_confidence`
- 图片超过大小限制
- MIME 不支持
- 本地路径越界

系统会保留引用层 evidence，并在 `diagnostics` 中输出 warning。若视觉描述提示与正文冲突，则对应知识单元 blocked。

## 推荐写法

```markdown
### 经销商审批流程

申请提交后，系统按照下图展示的流程执行初审。

![经销商审批流程](assets/dealer-flow.png "经销商审批流程")

图 1：经销商审批流程。左侧为申请节点，右侧为审批节点。
```

推荐同时提供：

- 有意义的 `alt`
- `title`
- 独立图注
- 图注中的对象、条件和结论说明
