from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor
from semantic_reconstruction.validator import validate_knowledge_unit


def test_twelve_acceptance_questions_are_complete():
    text = "# 简化流程\n\n申请人同时满足以下条件：合同有效。\n\n满足时，可由部门负责人审批；定制项目除外。\n"
    result = SemanticReconstructor(ReconstructionConfig()).reconstruct_text(text, "process")
    unit = next(item for item in result.units if item.exceptions)
    checks = {item["check"] for item in validate_knowledge_unit(unit)}
    assert checks == {str(index) for index in range(1, 13)}
    assert all(unit.evidence for unit in result.units)
