# 输出 Schema

当前 `schema_version` 为 `1.2`。

## 顶层结构

```json
{
  "schema_version": "1.2",
  "source": {
    "source_id": "policy",
    "source_path": "docs/policy.md",
    "title": "华东区域经销商临时授信",
    "line_count": 12,
    "char_count": 320,
    "sha256": "..."
  },
  "summary": {
    "source_id": "policy",
    "unit_count": 3,
    "auto_validated": 2,
    "pending_business_review": 1,
    "blocked": 0,
    "error_count": 0,
    "warning_count": 2
  },
  "units": [],
  "diagnostics": [],
  "llm_usage": []
}
```

## KnowledgeUnit

```json
{
  "unit_id": "policy-u0001",
  "business_question": "关于对象，当条件满足时应如何理解或执行？",
  "object": "文档标题 > 当前章节",
  "conditions": ["申请人同时满足以下条件：..."],
  "action_or_conclusion": "可由区域总监审批...",
  "exceptions": ["新签约不足90天的经销商除外。"],
  "time_range": "本规则适用于2026年度试行期。",
  "self_explanation": "对象：...；适用条件：...；动作或结论：...",
  "evidence": [],
  "changes": [],
  "generation_mode": "rule",
  "review_status": "auto_validated",
  "validation_findings": [],
  "risk_flags": [],
  "known_gaps": []
}
```

## Evidence

```json
{
  "evidence_id": "policy-b0003",
  "document_id": "policy",
  "source_path": "docs/policy.md",
  "line_start": 7,
  "line_end": 7,
  "heading_path": ["华东区域经销商临时授信", "审批规则"],
  "block_type": "paragraph",
  "text": "清洗后的文本",
  "raw_text": "原始 Markdown 片段",
  "metadata": {}
}
```

图片或图表 evidence 的 `block_type` 可能是：

- `image`
- `figure`
- `image_caption`
- `chart_code`
- `chart_svg`

示例 metadata：

```json
{
  "asset_type": "image",
  "source_type": "local",
  "path": "assets/flow.png",
  "exists": true,
  "mime_type": "image/png",
  "sha256": "...",
  "alt": "流程图",
  "title": "审批流程",
  "caption_evidence_id": "policy-b0005",
  "vision": {}
}
```

## review_status

| 状态 | 含义 |
|---|---|
| `auto_validated` | 规则模式验收无错误 |
| `pending_business_review` | 高风险或模型参与，需业务复核 |
| `blocked` | 证据缺失、模型越界或验收错误，禁止直接入库 |

## 12 问验收

每个 unit 的 `validation_findings` 包含 12 项检查：

1. 业务对象是否明确
2. 前置条件是否保留
3. 关键逻辑词是否保持原意
4. 例外是否绑定
5. 跨位置上下文是否关联
6. 执行主体是否明确
7. 时间或版本是否携带
8. 是否新增未支持数字
9. 是否改变确定性
10. 是否可指回完整证据
11. 原文、修改记录和状态是否双层保留
12. 是否可以脱离原文理解

每项 `status` 为 `pass`、`warning` 或 `error`。


## 图片与图表 metadata

引用层会输出路径、alt、title、图注、来源类型、本地文件哈希、Mermaid 节点和 SVG 文本。每张图片都会生成独立的 `generation_mode="image_evidence"` 知识单元。视觉理解成功时，`metadata.vision` 包含结构化描述、confidence 和 token 用量，并渲染到报告的“图片与视觉证据层”。

输出中不包含图片二进制；data URI payload 会自动替换为 `<omitted>`。
