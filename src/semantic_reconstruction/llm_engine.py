"""Constrained batch engines for hybrid and LLM-backed reconstruction."""
from __future__ import annotations

import json
import re
from typing import Any

from .llm_client import DeepSeekClient, parse_json_content
from .models import KnowledgeUnit
from .validator import MODAL_TERMS, validate_knowledge_unit

_NUMBER = re.compile(r"\d+(?:\.\d+)?%?")
_ROLE_GUARDS = ("总经理", "副总经理", "大客户负责人", "区域总监", "数据管理员", "财务")


def _normalize(value: Any) -> str:
    return re.sub(r"\s+", "", str(value))


def _anchor(unit: KnowledgeUnit) -> dict[str, Any]:
    return {
        "unit_id": unit.unit_id,
        "object": unit.object,
        "conditions": unit.conditions,
        "action_or_conclusion": unit.action_or_conclusion,
        "exceptions": unit.exceptions,
        "time_range": unit.time_range,
        "evidence_ids": [item.evidence_id for item in unit.evidence],
    }


def _evidence_view(unit: KnowledgeUnit) -> list[dict[str, Any]]:
    return [
        {
            "evidence_id": item.evidence_id,
            "line_start": item.line_start,
            "line_end": item.line_end,
            "heading_path": list(item.heading_path),
            "block_type": item.block_type,
            "text": item.text,
        }
        for item in unit.evidence
    ]


def _controlled_values(unit: KnowledgeUnit) -> list[str]:
    return [unit.object, *unit.conditions, unit.action_or_conclusion, *unit.exceptions, unit.time_range]


def _validate_expression(candidate: dict[str, Any], baseline: KnowledgeUnit) -> list[str]:
    text = candidate.get("self_explanation")
    if not isinstance(text, str) or not text.strip():
        return ["self_explanation 缺失或不是字符串。"]
    normalized = _normalize(text)
    errors = [f"重构表达遗漏受控内容：{value}" for value in _controlled_values(baseline) if value and _normalize(value) not in normalized]
    evidence_text = " ".join(item.text for item in baseline.evidence)
    expected_modal = [term for term in MODAL_TERMS if term in baseline.self_explanation]
    errors.extend(f"重构表达遗漏关键逻辑词：{term}" for term in expected_modal if term not in text)
    unsupported_roles = [role for role in _ROLE_GUARDS if role in text and role not in baseline.self_explanation and role not in evidence_text]
    if unsupported_roles:
        errors.append(f"重构表达新增未支持执行主体：{unsupported_roles}")
    unsupported_numbers = sorted(set(_NUMBER.findall(text)) - set(_NUMBER.findall(baseline.self_explanation)) - set(_NUMBER.findall(evidence_text)))
    if unsupported_numbers:
        errors.append(f"重构表达新增未支持数字：{unsupported_numbers}")
    return errors


def _validate_structured(candidate: dict[str, Any], baseline: KnowledgeUnit) -> list[str]:
    required = {
        "unit_id": str,
        "object": str,
        "conditions": list,
        "action_or_conclusion": str,
        "exceptions": list,
        "time_range": str,
        "self_explanation": str,
        "evidence_ids": list,
    }
    errors = [f"字段 {field} 类型不合法或缺失。" for field, expected in required.items() if not isinstance(candidate.get(field), expected)]
    if errors:
        return errors
    if candidate["unit_id"] != baseline.unit_id:
        errors.append("unit_id 与请求中的知识单元不一致。")
    if _normalize(candidate["object"]) != _normalize(baseline.object):
        errors.append("业务对象与证据基线不一致。")
    if [_normalize(item) for item in candidate["conditions"]] != [_normalize(item) for item in baseline.conditions]:
        errors.append("适用条件与证据基线不一致。")
    if _normalize(candidate["action_or_conclusion"]) != _normalize(baseline.action_or_conclusion):
        errors.append("动作或结论与证据基线不一致。")
    if [_normalize(item) for item in candidate["exceptions"]] != [_normalize(item) for item in baseline.exceptions]:
        errors.append("例外情况与证据基线不一致。")
    if _normalize(candidate["time_range"]) != _normalize(baseline.time_range):
        errors.append("时间范围与证据基线不一致。")
    expected_ids = {item.evidence_id for item in baseline.evidence}
    if set(candidate["evidence_ids"]) != expected_ids:
        errors.append(f"证据映射不完整：应为 {sorted(expected_ids)}，实际 {sorted(set(candidate['evidence_ids']))}。")
    errors.extend(_validate_expression(candidate, baseline))
    return errors


class BaseLLMEngine:
    mode = "llm"

    def __init__(self, client: DeepSeekClient):
        self.client = client

    def _messages(self, units: list[KnowledgeUnit], expression_only: bool) -> list[dict[str, str]]:
        mode = "hybrid_expression_only" if expression_only else "structured_knowledge_units"
        if expression_only:
            requirement = "只返回 {\"units\":[{\"unit_id\":\"...\",\"self_explanation\":\"...\"}]}；self_explanation 必须逐字包含受控语义锚中的每个字符串，不得输出 evidence_id、行号或其他来源编号。"
        else:
            requirement = "返回 {\"units\":[...]}；每个对象包含 unit_id、object、conditions、action_or_conclusion、exceptions、time_range、self_explanation、evidence_ids；object、conditions、action_or_conclusion、exceptions、time_range 必须逐字复制受控语义锚，self_explanation 必须逐字复制 self_explanation_anchor。"
        system = (
            "你是企业知识库语义重构引擎。你只能使用用户给出的证据和受控语义锚，"
            "不得补充常识、猜测缺失主体、改变逻辑关系、确定性、数字、例外或时间范围。"
            "原文缺失的信息必须标记待确认。只输出 JSON，不输出解释文字。"
        )
        payload = {
            "mode": mode,
            "要求": requirement,
            "units": [
                {
                    "business_question": unit.business_question,
                    "受控语义锚": _anchor(unit),
                    "self_explanation_anchor": unit.self_explanation,
                    "必须逐字包含的字符串": _controlled_values(unit),
                    "evidence": _evidence_view(unit),
                }
                for unit in units
            ],
        }
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]

    def _call_batches(self, units: list[KnowledgeUnit], expression_only: bool) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[str]]:
        by_id: dict[str, dict[str, Any]] = {}
        usage: list[dict[str, Any]] = []
        global_errors: list[str] = []
        size = self.client.config.llm_batch_size
        for start in range(0, len(units), size):
            batch = units[start:start + size]
            result = self.client.chat(self._messages(batch, expression_only))
            batch_usage = result.usage_dict if hasattr(result, "usage_dict") else (result.usage.to_dict() if result.usage else None)
            if batch_usage:
                batch_usage["batch_size"] = len(batch)
                usage.append(batch_usage)
            if not result.ok:
                global_errors.append(f"批次 {start // size + 1} 调用失败：{result.error}")
                continue
            parsed, error = parse_json_content(result.content)
            if parsed is None or not isinstance(parsed.get("units"), list):
                global_errors.append(f"批次 {start // size + 1} 输出无效：{error or 'units 数组缺失'}")
                continue
            for item in parsed["units"]:
                if isinstance(item, dict) and isinstance(item.get("unit_id"), str):
                    by_id[item["unit_id"]] = item
        return by_id, usage, global_errors


class HybridEngine(BaseLLMEngine):
    mode = "hybrid"

    def reconstruct(self, units: list[KnowledgeUnit]) -> tuple[list[KnowledgeUnit], list[dict[str, Any]]]:
        output: list[KnowledgeUnit] = []
        if not units:
            return [], []
        candidates, usage, errors = self._call_batches(units, expression_only=True)
        for baseline in units:
            baseline.generation_mode = "hybrid"
            candidate = candidates.get(baseline.unit_id)
            validation_errors = _validate_expression(candidate, baseline) if candidate else (["模型输出缺失。"] if not errors else [])
            if candidate and not validation_errors:
                accepted = KnowledgeUnit(**{**baseline.__dict__, "self_explanation": candidate["self_explanation"]})
                accepted.generation_mode = "hybrid"
                accepted.validation_findings = validate_knowledge_unit(accepted)
                accepted.changes.append({"type": "模型表达生成", "detail": "模型仅重组受控语义表达。"})
                output.append(accepted)
            else:
                if candidate:
                    message = "模型表达越界，已回退规则结果：" + "；".join(validation_errors)
                elif errors:
                    message = "模型调用或 JSON 解析失败，已回退规则结果：" + "；".join(errors)
                else:
                    message = "模型输出缺失，已回退规则结果。"
                baseline.validation_findings.append({"check": "LLM", "status": "warning", "message": message})
                baseline.changes.append({"type": "模型表达回退", "detail": "使用规则结果作为安全输出。"})
                output.append(baseline)
        return output, usage


class LLMEngine(BaseLLMEngine):
    mode = "llm"

    def reconstruct(self, units: list[KnowledgeUnit]) -> tuple[list[KnowledgeUnit], list[dict[str, Any]]]:
        if not units:
            return [], []
        eligible = [unit for unit in units if not unit.known_gaps]
        candidates, usage, errors = self._call_batches(eligible, expression_only=False)
        output: list[KnowledgeUnit] = []
        for baseline in units:
            baseline.generation_mode = "llm"
            baseline.review_status = "blocked" if baseline.known_gaps else "pending_business_review"
            if baseline.known_gaps:
                baseline.validation_findings = validate_knowledge_unit(baseline)
                output.append(baseline)
                continue
            candidate = candidates.get(baseline.unit_id)
            validation_errors = _validate_structured(candidate, baseline) if candidate else (["模型输出缺失。"] if not errors else [])
            if candidate and not validation_errors:
                accepted = KnowledgeUnit(
                    unit_id=baseline.unit_id,
                    business_question=baseline.business_question,
                    object=candidate["object"],
                    conditions=list(candidate["conditions"]),
                    action_or_conclusion=candidate["action_or_conclusion"],
                    exceptions=list(candidate["exceptions"]),
                    time_range=candidate["time_range"],
                    self_explanation=candidate["self_explanation"],
                    evidence=baseline.evidence,
                    changes=[*baseline.changes, {"type": "模型结构化生成", "detail": "字段与证据基线一致，保留业务复核。"}],
                    generation_mode="llm",
                    review_status="pending_business_review",
                    risk_flags=baseline.risk_flags,
                    known_gaps=baseline.known_gaps,
                )
                accepted.validation_findings = validate_knowledge_unit(accepted)
                output.append(accepted)
            else:
                baseline.review_status = "blocked"
                message = "模型输出被拒绝：" + "；".join(validation_errors or errors)
                baseline.validation_findings.append({"check": "LLM", "status": "error", "message": message})
                baseline.changes.append({"type": "模型结构化输出拒绝", "detail": "保留规则语义基线并阻断发布。"})
                output.append(baseline)
        return output, usage

