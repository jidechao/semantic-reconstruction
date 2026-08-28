"""Human-readable Markdown report renderer."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .models import KnowledgeUnit, ReconstructionResult

_STATUS = {
    "auto_validated": "自动验收通过",
    "pending_business_review": "待业务复核",
    "blocked": "阻断",
}


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _bullets(values: Iterable[str]) -> str:
    items = list(values)
    return "\n".join(f"- {item}" for item in items) if items else "- 无"


def _findings_table(findings: list[dict[str, str]]) -> str:
    rows = ["| 检查 | 结果 | 说明 |", "|---|---|---|"]
    for item in findings:
        if item.get("check") == "LLM":
            label = {"warning": "警告", "error": "错误", "pass": "通过"}.get(item["status"], item["status"])
            rows.append(f"| LLM | {label} | {_escape(item['message'])} |")
        else:
            label = {"pass": "通过", "warning": "警告", "error": "错误"}.get(item["status"], item["status"])
            rows.append(f"| {item['check']} | {label} | {_escape(item['message'])} |")
    return "\n".join(rows)


def _unit_section(unit: KnowledgeUnit) -> list[str]:
    lines = [
        f"### {unit.unit_id}",
        "",
        f"业务问题：{unit.business_question}",
        "",
        f"状态：**{_STATUS.get(unit.review_status, unit.review_status)}**；生成模式：`{unit.generation_mode}`。",
        "",
        "#### 原文证据层",
        "",
    ]
    lines.extend(
        f"- `{item.evidence_id}`｜{item.document_id}｜{item.source_path}:{item.line_start}-{item.line_end}｜"
        f"{' > '.join(item.heading_path) or '文档根路径'}｜{item.block_type}：{item.text}"
        for item in unit.evidence
    )
    evidence_by_id = {item.evidence_id: item for item in unit.evidence}
    image_items = [item for item in unit.evidence if item.block_type == "image"]
    if image_items:
        lines.extend(["", "#### 图片与视觉证据层", ""])
        for item in image_items:
            metadata = item.metadata
            vision = metadata.get("vision")
            caption_id = str(metadata.get("caption_evidence_id", ""))
            caption = evidence_by_id.get(caption_id)
            lines.append(f"##### 图片 `{item.evidence_id}`")
            lines.extend([
                f"- 来源：`{_escape(metadata.get('path', '未知来源'))}`",
                f"- Alt：{_escape(metadata.get('alt') or '待确认')}",
                f"- Title：{_escape(metadata.get('title') or '待确认')}",
                f"- 图注：{_escape(caption.text if caption else '待确认')}",
            ])
            if not vision:
                lines.append("- 视觉描述：未生成，图片内容需人工复核。")
                lines.append("")
                continue
            usage = vision.get("usage", {})
            limitations = vision.get("limitations") or []
            lines.extend([
                f"- 视觉模型：`{_escape(vision.get('model', 'unknown'))}`",
                f"- 图表类型：{_escape(vision.get('chart_type') or '待确认')}",
                f"- 置信度：{vision.get('confidence', 0)}",
                f"- 图片描述：{_escape(vision.get('description') or '待确认')}",
                f"- 可见文字：{_escape(vision.get('visible_text') or '无')}",
                f"- 限制说明：{_escape('；'.join(str(value) for value in limitations) or '无')}",
                f"- Token usage：prompt {_escape(usage.get('prompt_tokens', 'N/A'))}；completion {_escape(usage.get('completion_tokens', 'N/A'))}；total {_escape(usage.get('total_tokens', 'N/A'))}.",
                "",
            ])
    lines.extend([
        "",
        "#### 重构知识层",
        "",
        f"- 对象：{unit.object}",
        f"- 适用条件：{'；'.join(unit.conditions) or '无'}",
        f"- 动作或结论：{unit.action_or_conclusion}",
        f"- 例外情况：{'；'.join(unit.exceptions) or '无'}",
        f"- 时间范围：{unit.time_range}",
        "",
        "#### 可独立理解表达",
        "",
        unit.self_explanation,
        "",
        "#### 修改记录",
        "",
        _bullets(f"{item.get('type', '变更')}：{item.get('detail', '')}" for item in unit.changes),
        "",
        "#### 高风险依赖与证据缺口",
        "",
        _bullets([*unit.risk_flags, *unit.known_gaps]),
        "",
        "#### 12 问验收",
        "",
        _findings_table(unit.validation_findings),
        "",
    ])
    return lines


def render_report(result: ReconstructionResult) -> str:
    counts = Counter(unit.review_status for unit in result.units)
    lines = [
        "# 语义重构 SDK 报告",
        "",
        f"- 来源：`{result.source.source_path}`",
        f"- 文档标识：`{result.source.source_id}`",
        f"- Schema 版本：`{result.schema_version}`",
        f"- 知识单元：{len(result.units)} 条",
        f"- 自动验收通过：{counts.get('auto_validated', 0)} 条",
        f"- 待业务复核：{counts.get('pending_business_review', 0)} 条",
        f"- 阻断：{counts.get('blocked', 0)} 条",
        "",
        "## 知识单元明细",
        "",
    ]
    for unit in result.units:
        lines.extend(_unit_section(unit))
    if result.llm_usage:
        lines.extend(["## 模型调用摘要", ""])
        lines.extend(
            f"- 模型 `{item.get('model', 'unknown')}`；模式 `{item.get('mode', 'unknown')}`；"
            f"批量 {item.get('batch_size', 'N/A')} 条；第 {item.get('attempt', 'N/A')} 次尝试；"
            f"耗时 {item.get('elapsed_ms', 0)} ms；total tokens {item.get('total_tokens', 'N/A')}。"
            for item in result.llm_usage
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_batch_report(results: list[ReconstructionResult]) -> str:
    if len(results) == 1:
        return render_report(results[0])
    lines = ["# 语义重构 SDK 批量报告", "", f"- 文档数：{len(results)}", ""]
    total = Counter()
    for result in results:
        total.update(result.summary)
        lines.append(f"- {result.source.source_path}：{len(result.units)} 条；自动验收 {result.summary['auto_validated']}；待复核 {result.summary['pending_business_review']}；阻断 {result.summary['blocked']}。")
    lines.extend(["", "## 文档报告", ""])
    for result in results:
        lines.extend([f"## {result.source.source_id}", ""])
        lines.extend(render_report(result).splitlines()[2:])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
