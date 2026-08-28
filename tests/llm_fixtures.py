from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor
from semantic_reconstruction.llm_engine import _anchor


TEXT = """# 简化流程

申请人同时满足以下条件：合同有效；无逾期记录。

满足上述条件时，可由部门负责人审批并按简化流程办理；定制项目除外。
"""


def make_units():
    result = SemanticReconstructor(ReconstructionConfig()).reconstruct_text(TEXT, "process")
    return result.units
