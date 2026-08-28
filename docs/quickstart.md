# 快速开始

## 1. 安装

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## 2. 准备 Markdown

输入必须是 UTF-8 文本。推荐使用真实标题结构：

```markdown
# 华东区域经销商临时授信

## 适用条件

申请人同时满足以下条件：合同仍在有效期内；最近三个月无逾期记录。

## 审批规则

满足上述条件时，可由区域总监审批临时授信，额度最高为20万元；新签约不足90天的经销商除外。

本规则适用于2026年度试行期。
```

## 3. 离线运行

```python
from pathlib import Path

from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor

sdk = SemanticReconstructor(ReconstructionConfig(mode="rule"))
result = sdk.reconstruct_markdown(Path("docs") / "policy.md")

print(result.summary)
print(result.units[0].self_explanation)
print(result.units[0].evidence[0].line_start, result.units[0].evidence[0].line_end)
```

## 4. 输出

```python
result.write_json("output/policy.json")
result.write_report("output/policy.md")
```

## 5. 使用模型模式

显式传入 key：

```python
config = ReconstructionConfig(
    mode="hybrid",
    api_key="your-api-key",
)
```

或通过进程环境变量提供：

```powershell
$env:DEEPSEEK_API_KEY="your-api-key"
```

```python
config = ReconstructionConfig(mode="hybrid")
```

## 6. 批量处理

```python
results = sdk.reconstruct_files("docs")

for result in results:
    result.write_json(f"output/{result.source.source_id}.json")
```

## 7. 下一步

阅读 [API 参考](api-reference.md) 和 [输出 Schema](output-schema.md)。

## 8. 启用图片理解

默认只做离线引用层处理。配置多模态模型后，SDK 会自动理解本地图片和 data URI：

```python
config = ReconstructionConfig(
    mode="rule",
    image_understanding="auto",
    vision_api_key="your-vision-api-key",
    vision_base_url="https://api.example.com/v1",
    vision_model="your-multimodal-model",
)
```

远程图片只保留 URL 引用，不会被抓取。详见 [图片与图表处理](image-and-chart-processing.md)。
