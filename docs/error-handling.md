# 错误处理

## 异常基类

所有 SDK 异常都继承：

```python
SemanticReconstructionError
```

推荐第三方服务捕获基类并记录稳定错误信息。

## 异常列表

| 异常 | 场景 | 建议处理 |
|---|---|---|
| `InvalidConfigurationError` | mode、key、limit 等配置非法 | 检查配置，不要重试 |
| `DocumentParseError` | 文件不存在、编码错误、输入为空 | 检查路径和 UTF-8 编码 |
| `DocumentTooLargeError` | 超过 `max_document_chars` | 拆分文档或提高上限 |
| `LLMProviderError` | provider 初始化失败或不可恢复调用失败 | 检查网络、key、模型名 |
| `OutputValidationError` | JSON 或报告写入失败 | 检查路径权限和磁盘空间 |

## 单条知识失败

单条知识单元失败不会中断整份文档：

- 证据缺失：`review_status=blocked`，写入 `known_gaps`
- 模型表达越界：`hybrid` 回退规则结果，写入 LLM warning
- 模型结构化越界：`llm` 输出 blocked，写入 LLM error
- 执行主体不明确：输出 warning，等待业务复核
- 图片缺失或图片引用无资产：输出 blocked
- 视觉模型失败、低置信度、MIME 不支持、路径越界：回退引用层并输出 warning
- 视觉描述与正文冲突：输出 blocked

## 示例

```python
from semantic_reconstruction import (
    DocumentParseError,
    DocumentTooLargeError,
    SemanticReconstructionError,
    SemanticReconstructor,
)

try:
    result = sdk.reconstruct_markdown("docs/policy.md")
except DocumentTooLargeError:
    ...
except DocumentParseError:
    ...
except SemanticReconstructionError:
    ...
```

## LLM 重试策略

只重试：

- 网络错误
- timeout
- 408、409、429
- 5xx

不重试：

- JSON 越界
- 字段缺失
- 条件、例外、数字或主体改变
- 400、401、403、404 等不可恢复错误


## 视觉处理诊断

| code | 含义 |
|---|---|
| `image_asset_missing` | 本地图片或 `file:///` 目标不存在 |
| `image_src_missing` | HTML 图片缺少 `src` |
| `image_path_escape` | 相对路径越界，或绝对路径被配置禁止 |
| `image_mime_unsupported` | 本地/data URI 图片 MIME 不支持 |
| `image_too_large` | 本地/data URI 图片超过大小限制 |
| `vision_output_rejected` | 视觉输出未通过结构化、置信度或安全校验 |
| `vision_provider_error` | 视觉模型调用失败，已回退引用层 |
