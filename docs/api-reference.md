# API 参考

## `SemanticReconstructor`

```python
SemanticReconstructor(config=None, *, llm_client=None, vision_client=None)
```

- `config`：`ReconstructionConfig`，缺省为离线 `rule` 模式
- `llm_client`：可选 OpenAI-compatible client，用于 mock、代理或私有网关
- `vision_client`：可选视觉客户端，用于 mock、代理或多模态私有网关

### `reconstruct_markdown`

```python
reconstruct_markdown(path, source_id=None) -> ReconstructionResult
```

读取一个 UTF-8 Markdown 文件并重构。`source_id` 缺省由文件名生成稳定 slug。

### `reconstruct_text`

```python
reconstruct_text(text, source_id, source_path=None) -> ReconstructionResult
```

从内存文本重构。`source_path` 只用于审计展示，不会读取文件。

### `reconstruct_files`

```python
reconstruct_files(paths) -> list[ReconstructionResult]
```

支持：

- 单个文件路径
- Markdown 目录
- 路径可迭代对象

目录遍历会跳过 `.venv`、`node_modules`、`__pycache__` 和 `.pytest_cache`。

## `ReconstructionConfig`

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---:|---|
| `mode` | `rule/hybrid/llm` | `rule` | 运行模式 |
| `api_key` | `str \| None` | `None` | 显式 key；也可来自 `DEEPSEEK_API_KEY` |
| `base_url` | `str` | DeepSeek 地址 | OpenAI-compatible base URL |
| `model` | `str` | `deepseek-v4-flash` | 模型名 |
| `reasoning_effort` | `str` | `high` | reasoning effort |
| `enable_thinking` | `bool` | `True` | DeepSeek thinking 开关 |
| `timeout_seconds` | `float` | `120.0` | 单次请求超时 |
| `max_retries` | `int` | `2` | 瞬时错误重试次数 |
| `max_document_chars` | `int` | `2000000` | 单文档字符上限 |
| `include_code_blocks` | `bool` | `True` | 代码块是否作为证据保留 |
| `include_image_references` | `bool` | `True` | 图片引用是否作为证据保留 |
| `include_chart_blocks` | `bool` | `True` | Mermaid / SVG 是否作为图表证据保留 |
| `allow_absolute_image_paths` | `bool` | `True` | 是否允许读取 Markdown 目录外的本机绝对路径和 `file:///` 图片 |
| `keep_raw_evidence` | `bool` | `True` | 是否保留原始 Markdown 片段 |
| `llm_batch_size` | `int` | `25` | 每次模型请求最多处理的知识单元数 |
| `extra_headers` | `dict` | `{}` | 传递给 provider 的额外 header |
| `image_understanding` | `off/auto/required` | `auto` | 图片理解模式 |
| `vision_api_key` | `str \| None` | `None` | 视觉模型 key；也可来自 `VISION_API_KEY` |
| `vision_base_url` | `str \| None` | `None` | 视觉模型 OpenAI-compatible base URL |
| `vision_model` | `str \| None` | `None` | 多模态模型名 |
| `vision_timeout_seconds` | `float` | `120.0` | 视觉请求超时 |
| `vision_max_retries` | `int` | `1` | 视觉请求瞬时错误重试次数 |
| `vision_max_image_bytes` | `int` | `10485760` | 单张图片大小上限 |
| `vision_min_confidence` | `float` | `0.55` | 视觉描述最低置信度 |

安全约束：

- `repr(config)` 永远显示 `api_key=<redacted>` 和 `vision_api_key=<redacted>`
- SDK 不读取 `.env`
- 只有 `hybrid/llm` 模式或启用视觉理解时才可能访问网络
- 相对路径必须落在 Markdown 目录内；本机绝对路径和 `file:///` 默认允许，可通过 `allow_absolute_image_paths=False` 关闭
- SDK 不下载 HTTP(S) 图片，视觉模型启用时把 URL 直接传给 provider

## `ReconstructionResult`

| 成员 | 说明 |
|---|---|
| `schema_version` | 当前为 `1.2` |
| `source` | 来源 ID、路径、标题、行数、字符数和 SHA-256 |
| `units` | `KnowledgeUnit` 列表 |
| `diagnostics` | 文档级诊断 |
| `llm_usage` | 模型调用摘要，不含 key 和请求原文 |
| `summary` | 单元数与状态统计 |
| `to_dict()` | 转为 JSON 兼容 dict |
| `write_json(path)` | 写入 JSON |
| `write_report(path)` | 写入中文 Markdown 报告 |

## `KnowledgeUnit`

包含：

- `unit_id`
- `business_question`
- `object`
- `conditions`
- `action_or_conclusion`
- `exceptions`
- `time_range`
- `self_explanation`
- `evidence`
- `changes`
- `generation_mode`
- `review_status`
- `validation_findings`
- `risk_flags`
- `known_gaps`

## 自定义 LLM client

注入对象需要提供：

```python
client.chat.completions.create(**kwargs)
```

返回值需兼容 OpenAI SDK `ChatCompletion` 的 `choices[0].message.content` 和 `usage` 字段。


## 自定义视觉 client

注入对象需要实现：

```python
def describe_image(request: ImageRequest) -> ImageDescription: ...
```

内置 `OpenAICompatibleVisionClient` 使用 OpenAI-compatible `image_url` 消息格式。视觉输出必须包含：

- `description`
- `visible_text`
- `chart_type`
- `objects_or_nodes`
- `relationships`
- `colors_or_legends`
- `limitations`
- `confidence`

详见 [图片与图表处理](image-and-chart-processing.md)。
