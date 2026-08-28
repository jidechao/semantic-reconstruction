[![CI](https://github.com/jidechao/semantic-reconstruction/actions/workflows/ci.yml/badge.svg)](https://github.com/jidechao/semantic-reconstruction/actions/workflows/ci.yml)

# Semantic Reconstruction SDK

`semantic-reconstruction` 是一个生产级 Python SDK，用于把 UTF-8 Markdown 重构为可审计、可独立理解的语义知识单元。它保留原文证据、行号、标题路径、修改记录和 12 问验收结果，适合企业知识库、RAG 前处理、制度审计和技术文档理解场景。

## 核心能力

- 解析标题、段落、列表、表格、引用、HTML 和 fenced code block
- 自动绑定对象、条件、结论、例外、时间范围和证据位置
- 识别“上述、以下、附件、除外、原则上、另行”等高风险依赖
- 输出原文证据层与重构知识层
- 内置 12 问验收，缺证据时阻断而不是臆造
- 默认 `rule` 模式完全离线、确定性运行
- 可选 `hybrid` / `llm` 模式基于 DeepSeek OpenAI-compatible API，并强制越界校验
- 支持 API key 注入、密钥脱敏和私有 wheel 分发

## 安装

在项目内创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

安装私有 wheel：

```powershell
.\.venv\Scripts\python.exe -m pip install semantic_reconstruction-1.0.0-py3-none-any.whl
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

## 更多文档

- [快速开始](docs/quickstart.md)
- [API 参考](docs/api-reference.md)
- [输入格式](docs/input-format.md)
- [输出 Schema](docs/output-schema.md)
- [错误处理](docs/error-handling.md)
- [部署指南](docs/deployment.md)

## License

Apache-2.0. See [LICENSE](LICENSE).

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Private integration fixtures are stored under `tests/fixtures/markdown/` and are excluded from wheel and sdist artifacts.

