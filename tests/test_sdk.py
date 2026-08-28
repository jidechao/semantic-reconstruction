import json

import pytest

from semantic_reconstruction import (
    DocumentTooLargeError,
    ReconstructionConfig,
    SemanticReconstructor,
)


MARKDOWN = """# 华东区域经销商临时授信

申请人同时满足以下条件：合同有效；最近三个月无逾期。

满足上述条件时，可由区域总监审批临时授信，额度最高为20万元；新签约不足90天的经销商除外。

本规则适用于2026年度试行期。
"""


def make_result():
    return SemanticReconstructor(ReconstructionConfig()).reconstruct_text(MARKDOWN, "dealer-credit")


def test_public_api_reconstructs_self_contained_unit():
    result = make_result()
    assert result.schema_version == "1.0"
    assert result.units
    assert all(len(unit.validation_findings) == 12 for unit in result.units)
    assert all(unit.evidence for unit in result.units)
    assert all(all(item.line_start and item.line_end for item in unit.evidence) for unit in result.units)
    assert any("华东区域经销商临时授信" in unit.object for unit in result.units)
    assert any("最近三个月无逾期" in unit.self_explanation for unit in result.units)
    assert any("新签约不足90天" in unit.self_explanation for unit in result.units)
    assert any("2026年度试行期" in unit.self_explanation for unit in result.units)


def test_rule_mode_is_deterministic():
    first = make_result().to_dict()
    second = make_result().to_dict()
    assert json.dumps(first, ensure_ascii=False) == json.dumps(second, ensure_ascii=False)


def test_external_reference_blocks_instead_of_inventing():
    text = "# 售后政策\n\n符合上述条件的，由区域负责人审批；特殊情况按附件二处理。\n"
    result = SemanticReconstructor().reconstruct_text(text, "after-sales")
    assert any(unit.review_status == "blocked" for unit in result.units)
    assert any("附件" in gap for unit in result.units for gap in unit.known_gaps)


def test_write_json_and_report(tmp_path):
    result = make_result()
    json_path = result.write_json(tmp_path / "nested" / "result.json")
    report_path = result.write_report(tmp_path / "nested" / "report.md")
    assert json.loads(json_path.read_text(encoding="utf-8")) == result.to_dict()
    report = report_path.read_text(encoding="utf-8")
    assert "12 问验收" in report
    assert "原文证据层" in report


def test_reconstruct_files_supports_directory(tmp_path):
    source = tmp_path / "input"
    source.mkdir()
    (source / "a.md").write_text("# A\n\nA 说明内容。\n", encoding="utf-8")
    (source / "b.md").write_text("# B\n\nB 说明内容。\n", encoding="utf-8")
    results = SemanticReconstructor().reconstruct_files(source)
    assert len(results) == 2
    assert [item.source.source_id for item in results] == ["a", "b"]


def test_document_too_large_raises(tmp_path):
    path = tmp_path / "large.md"
    path.write_text("# 大文档\n\n内容\n", encoding="utf-8")
    sdk = SemanticReconstructor(ReconstructionConfig(max_document_chars=5))
    with pytest.raises(DocumentTooLargeError):
        sdk.reconstruct_markdown(path)


def test_config_repr_redacts_api_key():
    config = ReconstructionConfig(api_key="secret-key-value")
    assert "secret-key-value" not in repr(config)
    assert "api_key=<redacted>" in repr(config)


def test_keep_raw_evidence_false_is_supported():
    config = ReconstructionConfig(keep_raw_evidence=False)
    result = SemanticReconstructor(config).reconstruct_text("# 简化流程\n\n申请人须满足条件：合同有效。\n", "no-raw")
    assert result.units
    assert all(item.raw_text == "" for unit in result.units for item in unit.evidence)


def test_blocked_unit_is_also_reported_in_diagnostics():
    text = "# 政策\n\n符合上述条件的，按附件二处理。\n"
    result = SemanticReconstructor().reconstruct_text(text, "gap")
    assert result.diagnostics
    assert any(item.code == "semantic_unit_blocked" for item in result.diagnostics)
