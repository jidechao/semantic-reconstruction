from semantic_reconstruction import ReconstructionConfig, SemanticReconstructor
from semantic_reconstruction.markdown_parser import MarkdownParser
from conftest import REAL_MARKDOWN_FILES


def test_three_real_documents_parse_with_stable_blocks():
    parser = MarkdownParser()
    seen_ids: set[str] = set()
    for path in REAL_MARKDOWN_FILES:
        first = parser.parse_file(path)
        second = parser.parse_file(path)
        assert first.evidence
        assert [item.evidence_id for item in first.evidence] == [item.evidence_id for item in second.evidence]
        assert first.source.line_count > 0
        assert first.source.sha256 == second.source.sha256
        for block in first.evidence:
            assert block.line_start >= 1
            assert block.line_end >= block.line_start
            assert isinstance(block.heading_path, tuple)
            assert block.raw_text
            assert block.evidence_id not in seen_ids
            seen_ids.add(block.evidence_id)


def test_fenced_code_does_not_pollute_heading_tree():
    parser = MarkdownParser()
    document = parser.parse_file(REAL_MARKDOWN_FILES[1])
    heading_texts = [item.text for item in document.evidence if item.block_type == "heading"]
    assert heading_texts
    assert "先注册市场" not in heading_texts
    assert "克隆仓库" not in heading_texts
    assert any(item.block_type == "code_example" for item in document.evidence)


def test_table_rows_inherit_headers_and_exact_lines():
    parser = MarkdownParser()
    document = parser.parse_file(REAL_MARKDOWN_FILES[2])
    rows = [item for item in document.evidence if item.block_type == "table_row"]
    assert rows
    for row in rows:
        assert row.metadata["table_headers"]
        assert row.line_start >= row.metadata["table_line_start"]
        assert "表头：" in row.text
        assert "当前行：" in row.text


def test_html_and_code_are_evidence_not_headings():
    parser = MarkdownParser()
    document = parser.parse_file(REAL_MARKDOWN_FILES[0])
    assert any(item.block_type == "html" for item in document.evidence)
    assert any(item.block_type == "code_example" for item in document.evidence)
    assert all("先注册市场" != item.text for item in document.evidence if item.block_type == "heading")


def test_include_code_blocks_false_removes_code_evidence_only():
    text = "# 标题\n\n正文说明。\n\n```bash\n# 注释\n```\n"
    with_code = MarkdownParser(include_code_blocks=True).parse_text(text, source_id="demo")
    without_code = MarkdownParser(include_code_blocks=False).parse_text(text, source_id="demo")
    assert any(item.block_type == "code_example" for item in with_code.evidence)
    assert not any(item.block_type == "code_example" for item in without_code.evidence)
    assert [item.evidence_id for item in without_code.evidence] == [
        item for item in [with_code.evidence[0].evidence_id, with_code.evidence[1].evidence_id]
    ]


def test_table_reference_binds_header_and_first_row():
    text = "# 表格规则\n\n符合以下条件时按审批表执行。\n\n| 对象 | 审批人 |\n|---|---|\n| 经销商 | 区域总监 |\n"
    result = SemanticReconstructor(ReconstructionConfig()).reconstruct_text(text, "table-context")
    unit = next(item for item in result.units if "审批表" in item.action_or_conclusion)
    types = [item.block_type for item in unit.evidence]
    assert "table_header" in types
    assert "table_row" in types


def test_object_heading_path_is_evidence_mapped():
    text = "# 一级对象\n\n## 二级对象\n\n申请人须满足条件：合同有效。\n"
    result = SemanticReconstructor(ReconstructionConfig()).reconstruct_text(text, "heading-evidence")
    unit = next(item for item in result.units if "合同有效" in item.action_or_conclusion)
    headings = [item.text for item in unit.evidence if item.block_type == "heading"]
    assert "一级对象" in headings
    assert "二级对象" in headings

