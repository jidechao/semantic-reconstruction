from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor
from semantic_reconstruction.pipeline import RuleReconstructor
from semantic_reconstruction.validator import validate_knowledge_unit


TEXT = """# 经销商授信

申请人同时满足以下条件：合同有效；最近三个月无逾期。

满足上述条件时，可由区域总监审批，额度最高为20万元；新签约不足90天除外。

本规则适用于2026年度试行期。
"""


def test_rule_pipeline_binds_heading_condition_exception_and_time():
    result = SemanticReconstructor(ReconstructionConfig()).reconstruct_text(TEXT, "credit")
    assert result.units
    joined = "\n".join(unit.self_explanation for unit in result.units)
    assert "经销商授信" in joined
    assert "最近三个月无逾期" in joined
    assert "新签约不足90天" in joined
    assert "2026年度试行期" in joined


def test_validator_returns_twelve_checks_and_detects_missing_condition():
    result = SemanticReconstructor().reconstruct_text(TEXT, "credit")
    unit = next(item for item in result.units if item.exceptions)
    assert len(validate_knowledge_unit(unit)) == 12
    baseline_conditions = unit.conditions[:]
    unit.conditions = []
    findings = validate_knowledge_unit(unit)
    assert any(item["check"] == "2" and item["status"] == "error" for item in findings)


def test_high_risk_terms_are_detected():
    text = "# 政策\n\n符合上述条件的，按附件二处理；原则上三个工作日内完成，A类客户除外。\n"
    result = SemanticReconstructor().reconstruct_text(text, "policy")
    flags = [flag for unit in result.units for flag in unit.risk_flags]
    assert any("前文指代" in flag for flag in flags)
    assert any("附件引用" in flag for flag in flags)
    assert any("确定性约束" in flag for flag in flags)
