"""Automatic rule-based semantic reconstruction from parsed Markdown."""
from __future__ import annotations

import re
from typing import Any

from .detector import detect_risk_flags
from .markdown_parser import ParsedDocument, strip_inline_markdown
from .models import Evidence, KnowledgeUnit
from .validator import validate_knowledge_unit

_CONDITION = re.compile(r"(如果|若|当|满足|同时满足|任一|至少|需要|须|必须|只有|适用条件|前提|条件是)")
_EXCEPTION = re.compile(r"(除外|不适用|例外|但不|不过|不得|禁止)")
_TIME = re.compile(r"((?:19|20)\d{2}[-年/.]\d{1,2}(?:[-月/.]\d{1,2})?|V\d+(?:\.\d+)+|版本|有效期|生效日期|发布日期|自.{1,12}起)")
_POLICY_MODAL = re.compile(r"(必须|不得|禁止|应当|应该|须|需要|可以|可由|负责|审批|执行)")
_EXTERNAL_GAP = re.compile(r"(附件|另行规定|另行|以最新通知为准)")
_PREVIOUS_REF = re.compile(r"(上述|以上|前文|如前所述)")
_NEXT_REF = re.compile(r"(以下|如下|下图|下表|右侧|按照以下|参见以下)")
_CANDIDATE_TYPES = {"paragraph", "list", "table_row", "blockquote"}
_SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?；;])\s*")


def _sentences(text: str) -> list[str]:
    return [item.strip() for item in _SENTENCE_SPLIT.split(text) if item.strip()]


def _deduplicate_evidence(items: list[Evidence]) -> list[Evidence]:
    result: list[Evidence] = []
    seen: set[str] = set()
    for item in items:
        if item.evidence_id not in seen:
            result.append(item)
            seen.add(item.evidence_id)
    return result


class RuleReconstructor:
    """Build self-contained units with the minimum necessary local context."""

    def __init__(self, parsed: ParsedDocument):
        self.parsed = parsed
        self.evidence = parsed.evidence

    def _nearest_heading(self, block: Evidence) -> Evidence | None:
        for item in reversed(self.evidence):
            if item.block_type == "heading" and item.line_end <= block.line_start:
                return item
        return None

    def _previous_context(self, position: int) -> Evidence | None:
        for item in reversed(self.evidence[:position]):
            if item.block_type in _CANDIDATE_TYPES | {"code_example"}:
                return item
        return None

    def _next_context(self, position: int) -> Evidence | None:
        for item in self.evidence[position + 1:]:
            if item.block_type in _CANDIDATE_TYPES | {"code_example", "table_header"}:
                return item
        return None

    def _heading_path_evidence(self, block: Evidence) -> list[Evidence]:
        result: list[Evidence] = []
        for title in block.heading_path:
            candidates = [
                item for item in self.evidence
                if item.block_type == "heading" and item.text == title and item.line_start <= block.line_start
            ]
            if candidates:
                result.append(candidates[-1])
        return result

    def _object_for(self, block: Evidence) -> str:
        path = block.heading_path
        if not path:
            return self.parsed.document_title
        if len(path) == 1:
            return path[0]
        return " > ".join(path[-2:])

    def reconstruct(self) -> list[KnowledgeUnit]:
        units: list[KnowledgeUnit] = []
        sequence = 0
        for position, block in enumerate(self.evidence):
            if block.block_type not in _CANDIDATE_TYPES or len(block.text) < 10:
                continue
            # HTML-style navigation and image-only text are evidence, not business conclusions.
            if strip_inline_markdown(block.text).replace("[图片：]", "").strip().startswith("<"):
                continue

            sequence += 1
            heading = self._nearest_heading(block)
            previous = self._previous_context(position)
            next_block = self._next_context(position)
            context_evidence: list[Evidence] = []
            known_gaps: list[str] = []

            if _PREVIOUS_REF.search(block.text):
                if previous:
                    context_evidence.append(previous)
                else:
                    known_gaps.append("前文指代未包含在当前证据集中")
            if _NEXT_REF.search(block.text):
                if next_block:
                    context_evidence.extend([next_block])
                    if next_block.block_type == "table_header":
                        row_position = self.evidence.index(next_block) + 1
                        if row_position < len(self.evidence) and self.evidence[row_position].block_type == "table_row":
                            context_evidence.append(self.evidence[row_position])
                else:
                    known_gaps.append("后文、表格、图片或代码引用未包含在当前证据集中")
            if _EXTERNAL_GAP.search(block.text):
                known_gaps.append("外部附件或另行发布的规则未随当前 Markdown 提供")

            intro_context = previous and previous.block_type == "paragraph" and previous.text.rstrip().endswith(("：", ":"))
            if previous and _CONDITION.search(previous.text) and not _CONDITION.search(block.text):
                context_evidence.append(previous)
            if intro_context:
                context_evidence.append(previous)

            heading_evidence = self._heading_path_evidence(block)
            local_evidence = [item for item in [block, *heading_evidence, *context_evidence] if item is not None]
            candidate_conditions: list[str] = []
            condition_sources: list[Evidence] = []
            for item in [block, *context_evidence]:
                if _CONDITION.search(item.text):
                    # Keep the complete source statement: semicolons often separate
                    # multiple conditions that must remain together.
                    candidate_conditions.append(item.text)
                    condition_sources.append(item)

            exceptions = [s for s in _sentences(block.text) if _EXCEPTION.search(s)]
            time_sentences = [s for s in _sentences(block.text) if _TIME.search(s)]
            if not time_sentences:
                for prior in reversed(self.evidence[max(0, position - 12):position]):
                    if prior.block_type in {"paragraph", "heading", "list", "blockquote", "table_row"} and _TIME.search(prior.text):
                        time_sentences = [s for s in _sentences(prior.text) if _TIME.search(s)]
                        local_evidence.append(prior)
                        break

            object_text = self._object_for(block)
            action = block.text
            if block.block_type == "table_row":
                action = block.text
            time_range = "；".join(time_sentences) if time_sentences else "原文未单独标注时间或版本范围"

            evidence = _deduplicate_evidence([*local_evidence, *condition_sources])
            risk_flags = detect_risk_flags(evidence)
            if not candidate_conditions:
                condition_text = "无独立前置条件"
            else:
                condition_text = "；".join(candidate_conditions)

            explanation_parts = [f"对象：{object_text}"]
            if candidate_conditions:
                explanation_parts.append(f"适用条件：{condition_text}")
            explanation_parts.append(f"动作或结论：{action}")
            if exceptions:
                explanation_parts.append(f"例外情况：{'；'.join(exceptions)}")
            explanation_parts.append(f"时间范围：{time_range}")
            self_explanation = "；".join(explanation_parts)

            changes: list[dict[str, str]] = [{"type": "上下文绑定", "detail": "将 heading path 中的对象与候选知识块共同保留。"}]
            if heading:
                changes.append({"type": "章节证据", "detail": f"绑定标题证据 {heading.evidence_id}。"})
            if context_evidence:
                changes.append({"type": "指代补全", "detail": "绑定前后文、表格或代码证据。"})
            if condition_sources:
                changes.append({"type": "条件绑定", "detail": "将前置条件与动作或结论共同携带。"})
            if exceptions:
                changes.append({"type": "例外绑定", "detail": "保留影响结论成立的例外表述。"})
            if time_sentences:
                changes.append({"type": "时间版本绑定", "detail": "将时间或版本信息随结论携带。"})
            if block.block_type == "table_row":
                changes.append({"type": "表头绑定", "detail": "表格行继承原表头上下文。"})
            if block.block_type == "code_example":
                changes.append({"type": "代码示例保留", "detail": "保留代码证据但不升级为强制规则。"})

            if known_gaps:
                review_status = "blocked"
            elif (_POLICY_MODAL.search(action) and (candidate_conditions or exceptions or time_sentences or risk_flags)):
                review_status = "pending_business_review"
            else:
                review_status = "auto_validated"

            first_condition = candidate_conditions[0] if candidate_conditions else action[:48]
            business_question = f"关于{object_text}，当“{first_condition[:64]}”时应如何理解或执行？"
            unit = KnowledgeUnit(
                unit_id=f"{self.parsed.source.source_id}-u{sequence:04d}",
                business_question=business_question,
                object=object_text,
                conditions=candidate_conditions,
                action_or_conclusion=action,
                exceptions=exceptions,
                time_range=time_range,
                self_explanation=self_explanation,
                evidence=evidence,
                changes=changes,
                generation_mode="rule",
                review_status=review_status,
                risk_flags=risk_flags,
                known_gaps=known_gaps,
            )
            unit.validation_findings = validate_knowledge_unit(unit)
            if any(item["status"] == "error" for item in unit.validation_findings) and review_status != "blocked":
                unit.review_status = "blocked"
            units.append(unit)
        return units

