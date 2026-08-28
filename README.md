[![CI](https://github.com/jidechao/semantic-reconstruction/actions/workflows/ci.yml/badge.svg)](https://github.com/jidechao/semantic-reconstruction/actions/workflows/ci.yml)

# Semantic Reconstruction SDK

`semantic-reconstruction` 是一个生产级 Python SDK，用于把 UTF-8 Markdown 重构为可审计、可独立理解的语义知识单元。它保留原文证据、行号、标题路径、修改记录和 12 问验收结果，适合企业知识库、RAG 前处理、制度审计和技术文档理解场景。

## 核心能力

- 解析标题、段落、列表、表格、引用、HTML、fenced code block、图片、figure、Mermaid 和 SVG
- 自动绑定对象、条件、结论、例外、时间范围和证据位置
- 识别“上述、以下、下图、附件、除外、原则上、另行”等高风险依赖
- 输出原文证据层与重构知识层
- 内置 12 问验收，缺证据时阻断而不是臆造
- 默认 `rule` 模式完全离线、确定性运行
- 可选 `hybrid` / `llm` 模式基于 DeepSeek OpenAI-compatible API，并强制越界校验
- 支持 API key 注入、密钥脱敏、可选多模态图片理解和私有 wheel 分发
- 支持相对路径、本机绝对路径、`file:///`、data URI 和 HTTP(S) URL 图片证据，并为每张图片生成独立知识单元

## 在 RAG 流程中的位置

Semantic Reconstruction 位于数据清洗之后、Embedding 与向量入库之前，负责把原始 Markdown 重构为可审计、可独立理解的 `KnowledgeUnit`。下游分片、向量检索和 RAG 生成都基于这些语义单元，而不是重新按固定字符长度切分原文。

![Semantic Reconstruction 在 RAG 流程中的位置](Semantic%20reconstruction.png)

## 安装

在项目内创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

安装私有 wheel：

```powershell
.\.venv\Scripts\python.exe -m pip install semantic_reconstruction-1.2.0-py3-none-any.whl
```

## 5 分钟集成

```python
from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor

config = ReconstructionConfig(mode="rule")
sdk = SemanticReconstructor(config)

result = sdk.reconstruct_markdown("docs/policy.md")
print(result.summary)

for unit in result.units:
    print(unit.unit_id, unit.review_status)
    print(unit.self_explanation)
    for evidence in unit.evidence:
        print(evidence.evidence_id, evidence.line_start, evidence.line_end)

result.write_json("output/policy.json")
result.write_report("output/policy.md")
```

## CLI

```powershell
semantic-reconstruction reconstruct docs/policy.md --mode rule --out output
semantic-reconstruction reconstruct docs --mode rule --out output
```

如需使用模型模式，可以通过环境变量提供密钥，或使用 `--env-file` 让 CLI 读取本地配置文件：

```powershell
$env:DEEPSEEK_API_KEY="your-api-key"
semantic-reconstruction reconstruct docs/policy.md --mode hybrid --out output-hybrid
semantic-reconstruction reconstruct docs/policy.md --mode llm --out output-llm
```

SDK Python API 不会隐式读取 `.env`。

## 三种模式

| 模式 | 网络访问 | 适用场景 | 安全行为 |
|---|---|---|---|
| `rule` | 无 | 离线批处理、回归测试、基线生成 | 确定性输出 |
| `hybrid` | DeepSeek | 需要更自然表达 | 模型只改写表达；越界自动回退规则结果 |
| `llm` | DeepSeek | 模型参与结构化生成 | 字段必须与证据锚一致；越界输出 blocked |

## 接入后续知识分片

语义重构的输出不应该再回到原始 Markdown 后按固定字符长度切块。推荐链路是：

```text
Markdown
→ SemanticReconstructor
→ ReconstructionResult.units
→ KnowledgeChunk
→ Embedding / Vector Store / Knowledge Index
```

`KnowledgeUnit` 是业务语义完整单元；`KnowledgeChunk` 是下游索引和检索单元。后续分片层只做包装、过滤、父子组织和索引，不应重新切断对象、条件、结论、例外和时间范围。

### 1. 读取重构结果

单文档：

```python
from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor

sdk = SemanticReconstructor(ReconstructionConfig(mode="rule"))
result = sdk.reconstruct_markdown("docs/policy.md")

for unit in result.units:
    print(unit.unit_id, unit.review_status)
    print(unit.self_explanation)
```

批量文档：

```python
results = sdk.reconstruct_files("docs")

for result in results:
    for unit in result.units:
        print(result.source.source_id, unit.unit_id)
```

### 2. 状态过滤规则

| 状态 | 是否进入生产索引 | 建议处理 |
|---|---:|---|
| `auto_validated` | 可以 | 进入候选索引 |
| `pending_business_review` | 暂不 | 进入人工复核队列；确认后再入生产索引 |
| `blocked` | 不可以 | 进入待处理或资料修复队列 |

人工复核状态建议存放在下游系统，不要反向改写 SDK 的原始 `KnowledgeUnit` 输出。

### 3. 最小 Chunk 适配器

下面的示例将 `KnowledgeUnit` 转换为下游可入库的 `KnowledgeChunk`：

```python
from dataclasses import asdict, dataclass
from typing import Any

from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor


@dataclass
class KnowledgeChunk:
    chunk_id: str
    parent_id: str
    document_id: str
    source_path: str
    content: str
    embedding_text: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_heading_path(unit) -> list[str]:
    if not unit.evidence:
        return []
    return list(unit.evidence[0].heading_path)


def make_parent_id(result, unit) -> str:
    heading_path = get_heading_path(unit)
    if not heading_path:
        return result.source.source_id
    return result.source.source_id + "::" + " > ".join(heading_path[-2:])


def unit_to_chunk(result, unit) -> KnowledgeChunk:
    heading_path = get_heading_path(unit)
    embedding_text = f"{unit.business_question}\n\n{unit.self_explanation}".strip()

    return KnowledgeChunk(
        chunk_id=unit.unit_id,
        parent_id=make_parent_id(result, unit),
        document_id=result.source.source_id,
        source_path=result.source.source_path,
        content=unit.self_explanation,
        embedding_text=embedding_text,
        metadata={
            "schema_version": result.schema_version,
            "source_sha256": result.source.sha256,
            "business_question": unit.business_question,
            "object": unit.object,
            "conditions": unit.conditions,
            "action_or_conclusion": unit.action_or_conclusion,
            "exceptions": unit.exceptions,
            "time_range": unit.time_range,
            "heading_path": heading_path,
            "generation_mode": unit.generation_mode,
            "review_status": unit.review_status,
            "risk_flags": unit.risk_flags,
            "known_gaps": unit.known_gaps,
            "evidence_ids": [item.evidence_id for item in unit.evidence],
            "validation_findings": unit.validation_findings,
            "changes": unit.changes,
        },
    )


def result_to_chunks(result, *, include_pending_review: bool = False) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []

    for unit in result.units:
        if unit.review_status == "blocked":
            continue
        if unit.review_status == "pending_business_review" and not include_pending_review:
            continue
        chunks.append(unit_to_chunk(result, unit))

    return chunks


sdk = SemanticReconstructor(ReconstructionConfig(mode="rule"))
results = sdk.reconstruct_files("docs")

all_chunks: list[KnowledgeChunk] = []
for result in results:
    all_chunks.extend(result_to_chunks(result))
```

`content` 和 `embedding_text` 使用 `unit.self_explanation`。业务问题可以拼入 `embedding_text` 以提升问答式检索效果；`validation_findings`、`changes` 和原文证据更适合放在 metadata 或证据层，不要全部拼入向量文本。

### 4. 保留证据映射

每个 chunk 至少保留：

```python
"evidence_ids": [item.evidence_id for item in unit.evidence]
```

原文证据建议单独存成映射：

```text
evidence_id → source_path / line_start / line_end / heading_path / text / raw_text
```

向量索引用于检索，证据层用于回答时引用、审计和回查原文。不要把大段 `raw_text` 全部混入 embedding 文本，否则会稀释主要语义。

### 5. 父子分片结构

推荐建立两层结构：

```text
Parent Chunk
  - 文档或章节上下文
  - heading path
  - 子 chunk ID 列表

Child Chunk
  - 一个 KnowledgeUnit
  - 用于向量检索
```

构建方式：

```python
from collections import defaultdict


def build_parent_chunks(results, *, include_pending_review: bool = False):
    children = []
    parents = defaultdict(lambda: {
        "document_id": "",
        "source_path": "",
        "heading_path": [],
        "child_ids": [],
        "objects": [],
        "summaries": [],
    })

    for result in results:
        for unit in result.units:
            if unit.review_status == "blocked":
                continue
            if unit.review_status == "pending_business_review" and not include_pending_review:
                continue

            child = unit_to_chunk(result, unit)
            children.append(child)

            parent = parents[child.parent_id]
            parent["document_id"] = result.source.source_id
            parent["source_path"] = result.source.source_path
            parent["child_ids"].append(child.chunk_id)

            if child.metadata["heading_path"] and not parent["heading_path"]:
                parent["heading_path"] = child.metadata["heading_path"]
            if child.metadata["object"] not in parent["objects"]:
                parent["objects"].append(child.metadata["object"])
            if child.metadata["action_or_conclusion"] not in parent["summaries"]:
                parent["summaries"].append(child.metadata["action_or_conclusion"])

    for parent in parents.values():
        parent["content"] = "\n".join([
            f"文档：{parent['source_path']}",
            f"章节：{' > '.join(parent['heading_path'])}",
            f"对象：{'；'.join(parent['objects'])}",
            "包含的知识结论：",
            *[f"- {item}" for item in parent["summaries"]],
        ])

    return children, list(parents.values())
```

检索时先命中 child，再取 parent 补充章节上下文，最后用 `evidence_ids` 回查原文行号。

### 6. 消费 CLI JSON

CLI 批量输出 `output/results.json` 时，顶层是数组：

```python
import json
from pathlib import Path

data = json.loads(Path("output/results.json").read_text(encoding="utf-8"))

for result in data:
    for unit in result["units"]:
        if unit["review_status"] == "blocked":
            continue

        evidence = unit.get("evidence", [])
        heading_path = evidence[0].get("heading_path", []) if evidence else []
        parent_id = (
            result["source"]["source_id"] + "::" + " > ".join(heading_path[-2:])
            if heading_path
            else result["source"]["source_id"]
        )

        chunk = {
            "chunk_id": unit["unit_id"],
            "parent_id": parent_id,
            "document_id": result["source"]["source_id"],
            "source_path": result["source"]["source_path"],
            "content": unit["self_explanation"],
            "embedding_text": (
                unit.get("business_question", "")
                + "\n\n"
                + unit.get("self_explanation", "")
            ).strip(),
            "metadata": {
                "object": unit.get("object", ""),
                "conditions": unit.get("conditions", []),
                "exceptions": unit.get("exceptions", []),
                "time_range": unit.get("time_range", ""),
                "review_status": unit.get("review_status", ""),
                "generation_mode": unit.get("generation_mode", ""),
                "evidence_ids": [item["evidence_id"] for item in evidence],
            },
        }
```

单文档 `write_json()` 输出的顶层是对象；CLI 批量输出顶层是数组。下游解析器应同时兼容这两种形态。

### 7. 超大 KnowledgeUnit 的保守切分

默认情况下：

```text
一个 KnowledgeUnit = 一个 KnowledgeChunk
```

只有当 `self_explanation` 超过 embedding 模型限制时才做保守切分，并遵守以下规则：

1. 每个子片继续携带 `root_unit_id`
2. 每个子片继续携带对象、条件、例外和时间范围
3. 不允许把条件切在一边、结论切在另一边
4. 子片之间可以重叠
5. 回答时通过 parent 或 root unit 重新聚合

不要为了凑长度合并不同对象、不同条件、不同例外或不同版本的知识单元。短单元应通过 parent 提供上下文，而不是硬拼成长 chunk。

### 8. 推荐入库字段

无论使用哪个向量库，建议至少保留：

```text
chunk_id
root_unit_id
parent_id
document_id
source_path
source_sha256
heading_path
object
conditions
exceptions
time_range
generation_mode
review_status
risk_flags
evidence_ids
```

生产问答时过滤 `review_status != blocked`；如果下游有人工复核流程，则检索条件通常是：

```text
review_status == auto_validated
or human_review.status == approved
```

这样知识进入向量库后，仍然可以回答：

```text
在说谁
在什么条件下成立
结论是什么
有哪些例外
适用于哪个版本或时间
证据来自哪里
```

## 更多文档

- [快速开始](docs/quickstart.md)
- [API 参考](docs/api-reference.md)
- [输入格式](docs/input-format.md)
- [输出 Schema](docs/output-schema.md)
- [错误处理](docs/error-handling.md)
- [部署指南](docs/deployment.md)
- [图片与图表处理](docs/image-and-chart-processing.md)

## License

Apache-2.0. See [LICENSE](LICENSE).

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Private integration fixtures are stored under `tests/fixtures/markdown/` and are excluded from wheel and sdist artifacts.
