"""Twelve-question acceptance validation for reconstructed knowledge units."""
from __future__ import annotations

import re

from .detector import has_explicit_role
from .models import KnowledgeUnit

MODAL_TERMS = ("同时满足", "任一", "至少", "不得", "除外", "原则上", "仅限", "可以", "必须", "应该", "应当")
VAGUE_OBJECTS = ("本产品", "该客户", "上述情况", "本办法", "这种情况")
_NUMBER = re.compile(r"\d+(?:\.\d+)?%?")
_CONDITION_HINT = re.compile(r"(如果|若|当|满足|条件|前提|须|必须|需要)")


def _normalize(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _numbers(value: str) -> set[str]:
    return set(_NUMBER.findall(value))


def _finding(check: int | str, status: str, message: str) -> dict[str, str]:
    return {"check": str(check), "status": status, "message": message}


def validate_knowledge_unit(unit: KnowledgeUnit) -> list[dict[str, str]]:
    image_unit = unit.generation_mode == "image_evidence"
    vision_text: list[str] = []
    for item in unit.evidence:
        vision = item.metadata.get("vision") if item.block_type == "image" else None
        if not vision:
            continue
        vision_text.extend([
            str(vision.get("description", "")),
            str(vision.get("visible_text", "")),
            str(vision.get("chart_type", "")),
            str(vision.get("confidence", "")),
            f"{float(vision.get('confidence', 0.0)):.2f}",
            " ".join(str(value) for value in vision.get("objects_or_nodes", [])),
            " ".join(str(value) for value in vision.get("relationships", [])),
            " ".join(str(value) for value in vision.get("colors_or_legends", [])),
            " ".join(str(value) for value in vision.get("limitations", [])),
        ])
    evidence_text = " ".join([*[item.text for item in unit.evidence], *vision_text])
    combined = " ".join([
        unit.object, *unit.conditions, unit.action_or_conclusion, *unit.exceptions, unit.time_range,
    ])
    structural = combined
    findings: list[dict[str, str]] = []

    vague = not unit.object.strip() or any(term in unit.object for term in VAGUE_OBJECTS)
    findings.append(_finding(1, "error" if vague else "pass", "业务对象明确。" if not vague else "业务对象仍依赖上下文。"))

    condition_evidence_text = " ".join(item.text for item in unit.evidence if item.block_type != "heading")
    if image_unit:
        findings.append(_finding(2, "pass", "图片证据不推断业务前置条件。"))
    elif unit.conditions:
        missing = [item for item in unit.conditions if _normalize(item) not in _normalize(structural)]
        findings.append(_finding(2, "error" if missing else "pass", "前置条件与结论共同保留。" if not missing else f"前置条件遗漏：{missing}"))
    elif _CONDITION_HINT.search(condition_evidence_text):
        findings.append(_finding(2, "error", "证据显示存在条件语义，但重构结果未保留前置条件。"))
    else:
        findings.append(_finding(2, "pass", "该知识不需要独立前置条件。"))

    if image_unit:
        findings.append(_finding(3, "pass", "图片可见文字不升级为业务规则。"))
    else:
        expected_modal = [term for term in MODAL_TERMS if term in evidence_text]
        missing_modal = [term for term in expected_modal if term not in combined]
        findings.append(_finding(3, "error" if missing_modal else "pass", "关键逻辑词保持原意。" if not missing_modal else f"关键逻辑词遗漏：{missing_modal}"))

    if image_unit:
        findings.append(_finding(4, "pass", "图片可见例外文字不升级为业务规则。"))
    elif any(_EXCEPTION_HINT.search(item.text) for item in unit.evidence):
        missing = [item for item in unit.exceptions if _normalize(item) not in _normalize(structural)]
        # Exceptions were extracted from the same candidate in rule mode; LLM mode is additionally checked against its anchor.
        findings.append(_finding(4, "pass" if unit.exceptions else "error", "一般规则与例外完整绑定。" if unit.exceptions else "证据包含例外语义但重构结果遗漏。"))
    else:
        findings.append(_finding(4, "pass", "原文未识别出例外情况。"))

    cross_source = len(unit.evidence) > 1 or len({item.line_start for item in unit.evidence}) > 1
    findings.append(_finding(5, "pass" if cross_source else "warning", "跨位置上下文已关联。" if cross_source else "未绑定标题或上下文证据。"))

    action_text = unit.action_or_conclusion + unit.self_explanation
    role_ok = has_explicit_role(action_text)
    findings.append(_finding(6, "pass" if role_ok else "warning", "执行主体明确。" if role_ok else "执行主体未明确，需要业务确认。"))

    if unit.time_range and unit.time_range != "原文未单独标注时间或版本范围":
        findings.append(_finding(7, "pass", "时间、日期或版本信息已随知识携带。"))
    else:
        findings.append(_finding(7, "pass", "原文未标注独立时间或版本范围。"))

    unsupported_numbers = sorted(_numbers(unit.self_explanation) - _numbers(evidence_text) - _numbers(unit.object))
    findings.append(_finding(8, "error" if unsupported_numbers else "pass", "未新增原文不支持的数字。" if not unsupported_numbers else f"新增未支持数字：{unsupported_numbers}"))

    unsupported_terms = [term for term in ("总经理", "一律", "必须") if term in unit.self_explanation and term not in evidence_text]
    findings.append(_finding(9, "error" if unsupported_terms else "pass", "未改变示例、建议或可能性的确定性。" if not unsupported_terms else f"确定性或主体越界：{unsupported_terms}"))

    evidence_ok = bool(unit.evidence) and not unit.known_gaps
    findings.append(_finding(10, "pass" if evidence_ok else "error", "关键结论可指回完整原文证据。" if evidence_ok else "缺少证据映射或存在未补齐的证据缺口。"))

    dual_ok = bool(unit.evidence and unit.changes)
    findings.append(_finding(11, "pass" if dual_ok else "error", "原文证据、修改记录和状态已双层保留。" if dual_ok else "缺少原文证据或修改记录。"))

    errors = [item["message"] for item in findings if item["status"] == "error"]
    findings.append(_finding(12, "error" if errors else "pass", "业务人员可在不猜测上下文的情况下理解。" if not errors else "仍需上下文才能执行：" + "；".join(errors)))
    return findings


_EXCEPTION_HINT = re.compile(r"(除外|不适用|例外|但不|不得|禁止)")

