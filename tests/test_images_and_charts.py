import base64
import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from semantic_reconstruction import (
    ImageDescription,
    InvalidConfigurationError,
    ReconstructionConfig,
    SemanticReconstructor,
)
from semantic_reconstruction.markdown_parser import MarkdownParser
from semantic_reconstruction.vision import ImageRequest, OpenAICompatibleVisionClient

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8AAAwAB/AL+kQAAAABJRU5ErkJggg=="
)


def write_png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PNG)
    return path


def parse(text: str, source_id: str = "demo") -> list[tuple[str, int, int, dict]]:
    document = MarkdownParser().parse_text(text, source_id=source_id)
    return [(item.block_type, item.line_start, item.line_end, item.metadata) for item in document.evidence]


def test_markdown_image_reference_and_definition(tmp_path):
    write_png(tmp_path / "assets" / "flow.png")
    text = '# 图\n\n![流程图][arch]\n\n[arch]: assets/flow.png "审批流程"\n'
    document = MarkdownParser().parse_text(text, source_id="demo", source_path=str(tmp_path / "demo.md"))
    images = [item for item in document.evidence if item.block_type == "image"]
    assert len(images) == 1
    image = images[0]
    assert image.line_start == 3
    assert image.metadata["path"] == "assets/flow.png"
    assert image.metadata["alt"] == "流程图"
    assert image.metadata["title"] == "审批流程"
    assert image.metadata["source_type"] == "local"
    assert image.metadata["exists"] is True
    assert image.metadata["sha256"]
    assert image.evidence_id.startswith("demo-b")


def test_markdown_remote_data_and_missing_images():
    data_uri = "data:image/png;base64," + base64.b64encode(PNG).decode("ascii")
    text = f'''# 图\n\n![远程](https://example.com/a.png)\n\n![内联](data_uri_placeholder)\n\n![缺失](./missing.png)\n'''.replace("data_uri_placeholder", data_uri)
    document = MarkdownParser().parse_text(text, source_id="assets")
    images = [item for item in document.evidence if item.block_type == "image"]
    assert [item.metadata["source_type"] for item in images] == ["remote", "data", "local"]
    assert images[1].metadata["_data_uri"].startswith("data:image/png;base64,")
    serialized_data = images[1].to_dict()["metadata"]["path"]
    assert serialized_data == "data:image/png;base64,<omitted>"
    assert images[2].metadata["exists"] is False


def test_html_figure_image_and_caption():
    text = '''# 图\n\n<figure>\n  <img src="./chart.png" alt="趋势图" title="趋势" width="800">\n  <figcaption>图 2：趋势</figcaption>\n</figure>\n'''
    document = MarkdownParser().parse_text(text, source_id="html")
    types = [item.block_type for item in document.evidence]
    assert ["heading", "figure", "image", "image_caption"] == types
    figure = document.evidence[1]
    image = document.evidence[2]
    caption = document.evidence[3]
    assert image.metadata["alt"] == "趋势图"
    assert image.metadata["width"] == "800"
    assert image.metadata["container_evidence_id"] == figure.evidence_id
    assert figure.metadata["caption_evidence_id"] == caption.evidence_id
    assert caption.metadata["asset_evidence_id"] == image.evidence_id


def test_html_img_missing_src_and_alt():
    text = '# 图\n\n<img alt="无来源">\n\n<img src="./x.png">\n'
    document = MarkdownParser().parse_text(text, source_id="bad-img")
    images = [item for item in document.evidence if item.block_type == "image"]
    assert len(images) == 2
    assert images[0].metadata["missing_src"] is True
    assert images[1].metadata.get("alt", "") == ""


def test_mermaid_is_chart_not_code():
    text = '''# 流程\n\n```mermaid\nflowchart TD\n  A[提交申请] --> B{负责人确认}\n  B -->|通过| C[生成任务]\n```\n'''
    document = MarkdownParser().parse_text(text, source_id="mermaid")
    charts = [item for item in document.evidence if item.block_type == "chart_code"]
    assert len(charts) == 1
    chart = charts[0]
    assert chart.metadata["chart_type"] == "flowchart"
    assert chart.metadata["direction"] == "TD"
    assert "提交申请" in chart.metadata["nodes"]
    assert any("A[提交申请]" in relation for relation in chart.metadata["relationships"])
    assert not any(item.block_type == "code_example" for item in document.evidence)


def test_fenced_and_inline_svg_do_not_execute_scripts():
    fenced = '''# 图\n\n```svg\n<svg><title>架构</title><desc>系统</desc><text>网关</text><script>alert(1)</script></svg>\n```\n'''
    document = MarkdownParser().parse_text(fenced, source_id="svg")
    chart = next(item for item in document.evidence if item.block_type == "chart_svg")
    assert chart.metadata["title"] == "架构"
    assert chart.metadata["description"] == "系统"
    assert "网关" in chart.metadata["texts"]
    assert chart.metadata["scripts_present"] is True
    assert "alert(1)" not in chart.text

    inline = '# 图\n\n<svg><title>内联</title><script>alert(2)</script></svg>\n'
    inline_document = MarkdownParser().parse_text(inline, source_id="inline-svg")
    inline_chart = next(item for item in inline_document.evidence if item.block_type == "chart_svg")
    assert inline_chart.metadata["title"] == "内联"
    assert inline_chart.metadata["scripts_present"] is True


def test_image_reference_binds_caption_and_blocks_when_missing(tmp_path):
    write_png(tmp_path / "assets" / "flow.png")
    good = '# 审批\n\n如下图展示审批流程。\n\n![流程图](assets/flow.png "流程")\n\n图 1：审批流程\n'
    markdown = tmp_path / "good.md"
    markdown.write_text(good, encoding="utf-8")
    result = SemanticReconstructor().reconstruct_markdown(markdown)
    unit = next(item for item in result.units if "如下图" in item.action_or_conclusion)
    types = [item.block_type for item in unit.evidence]
    assert "image" in types and "image_caption" in types
    assert "流程图" in unit.self_explanation

    missing = tmp_path / "missing.md"
    missing.write_text('# 审批\n\n如下图展示审批流程。\n\n![流程图](assets/missing.png)\n', encoding="utf-8")
    missing_result = SemanticReconstructor().reconstruct_markdown(missing)
    missing_unit = next(item for item in missing_result.units if "如下图" in item.action_or_conclusion)
    assert missing_unit.review_status == "blocked"
    assert any("本地图片不存在" in gap for gap in missing_unit.known_gaps)

    no_image = tmp_path / "no-image.md"
    no_image.write_text('# 审批\n\n如下图展示审批流程。\n', encoding="utf-8")
    no_image_result = SemanticReconstructor().reconstruct_markdown(no_image)
    no_image_unit = next(item for item in no_image_result.units if "如下图" in item.action_or_conclusion)
    assert no_image_unit.review_status == "blocked"
    assert any("没有可用的图片" in gap for gap in no_image_unit.known_gaps)


class RecordingVisionClient:
    def __init__(self, description: ImageDescription | Exception):
        self.description = description
        self.calls = 0

    def describe_image(self, request):
        self.calls += 1
        if isinstance(self.description, Exception):
            raise self.description
        return self.description


def make_description(confidence: float = 0.9, limitations: list[str] | None = None) -> ImageDescription:
    return ImageDescription(
        description="图中显示流程节点。",
        visible_text="提交申请",
        chart_type="flowchart",
        objects_or_nodes=["提交申请"],
        relationships=["提交申请 -> 负责人确认"],
        colors_or_legends=[],
        limitations=limitations or [],
        confidence=confidence,
        model="mock-vision",
        usage={"total_tokens": 12},
    )


def vision_setup(tmp_path, *, config=None, description=None):
    write_png(tmp_path / "assets" / "flow.png")
    markdown = tmp_path / "doc.md"
    markdown.write_text(
        '# 审批\n\n如下图展示审批流程。\n\n![流程图](assets/flow.png "流程")\n',
        encoding="utf-8",
    )
    client = RecordingVisionClient(description or make_description())
    cfg = config or ReconstructionConfig(image_understanding="required")
    sdk = SemanticReconstructor(cfg, vision_client=client)
    return sdk.reconstruct_markdown(markdown), client


def test_auto_without_vision_config_does_not_call_provider(tmp_path):
    write_png(tmp_path / "assets" / "flow.png")
    markdown = tmp_path / "doc.md"
    markdown.write_text('# 审批\n\n如下图展示审批流程和责任边界。\\n\n![流程图](assets/flow.png)\n', encoding="utf-8")
    result = SemanticReconstructor().reconstruct_markdown(markdown)
    assert not result.llm_usage
    assert all("vision" not in item.metadata for unit in result.units for item in unit.evidence)


def test_required_missing_vision_configuration_raises():
    with pytest.raises(InvalidConfigurationError):
        SemanticReconstructor(ReconstructionConfig(image_understanding="required"))


def test_vision_description_is_evidence_and_requires_review(tmp_path):
    result, client = vision_setup(tmp_path)
    assert client.calls == 1
    image = next(item for unit in result.units for item in unit.evidence if item.block_type == "image")
    assert image.metadata["vision"]["model"] == "mock-vision"
    unit = next(unit for unit in result.units if image in unit.evidence)
    assert unit.review_status == "pending_business_review"
    assert any(change["type"] == "视觉描述生成" for change in unit.changes)
    assert result.llm_usage[0]["mode"] == "vision"
    serialized = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "base64" not in serialized and "mock-api-key" not in serialized


def test_vision_remote_url_is_not_fetched(tmp_path):
    markdown = tmp_path / "remote.md"
    markdown.write_text('# 图\n\n如下图。\n\n![远程](https://example.com/image.png)\n', encoding="utf-8")
    client = RecordingVisionClient(make_description())
    sdk = SemanticReconstructor(
        ReconstructionConfig(image_understanding="required"),
        vision_client=client,
    )
    result = sdk.reconstruct_markdown(markdown)
    assert client.calls == 0
    assert any(item.code == "image_understanding_skipped" for item in result.diagnostics)


def test_vision_rejects_unsupported_mime_size_and_path_escape(tmp_path):
    unsupported = tmp_path / "unsupported.png"
    unsupported.write_bytes(PNG)
    markdown = tmp_path / "unsupported.md"
    markdown.write_text('# 图\n\n如下图。\n\n![图](unsupported.png)\n', encoding="utf-8")
    # Rename after parser metadata is built is not possible; use extension mismatch directly.
    unsupported.unlink()
    unsupported = tmp_path / "unsupported.txt"
    unsupported.write_bytes(PNG)
    markdown.write_text('# 图\n\n如下图。\n\n![图](unsupported.txt)\n', encoding="utf-8")
    client = RecordingVisionClient(make_description())
    sdk = SemanticReconstructor(ReconstructionConfig(image_understanding="required"), vision_client=client)
    result = sdk.reconstruct_markdown(markdown)
    assert client.calls == 0
    assert any("MIME" in item.message for item in result.diagnostics)

    write_png(tmp_path / "assets" / "large.png")
    large = tmp_path / "large.md"
    large.write_text('# 图\n\n如下图。\n\n![图](assets/large.png)\n', encoding="utf-8")
    client = RecordingVisionClient(make_description())
    sdk = SemanticReconstructor(
        ReconstructionConfig(image_understanding="required", vision_max_image_bytes=1),
        vision_client=client,
    )
    result = sdk.reconstruct_markdown(large)
    assert client.calls == 0
    assert any("大小限制" in item.message for item in result.diagnostics)

    outside = tmp_path.parent / "semantic-reconstruction-outside.png"
    write_png(outside)
    escape = tmp_path / "escape.md"
    escape.write_text('# 图\n\n如下图。\n\n![图](../semantic-reconstruction-outside.png)\n', encoding="utf-8")
    client = RecordingVisionClient(make_description())
    sdk = SemanticReconstructor(ReconstructionConfig(image_understanding="required"), vision_client=client)
    result = sdk.reconstruct_markdown(escape)
    assert client.calls == 0
    assert any("路径越界" in item.message for item in result.diagnostics)


def test_vision_invalid_low_confidence_failure_and_conflict_fallback(tmp_path):
    result, client = vision_setup(tmp_path, description=make_description(confidence=0.1))
    assert client.calls == 1
    assert any(item.code == "vision_output_rejected" for item in result.diagnostics)
    assert not any("vision" in item.metadata for unit in result.units for item in unit.evidence)

    result, client = vision_setup(tmp_path, description=make_description(limitations=["与正文证据存在冲突"]))
    assert client.calls == 1
    assert any(item.severity == "error" for item in result.diagnostics)
    assert any(unit.review_status == "blocked" for unit in result.units)

    failure = RuntimeError("provider unavailable")
    result, client = vision_setup(tmp_path, description=failure)
    assert client.calls == 1
    assert any(item.code == "vision_provider_error" for item in result.diagnostics)




class FakeVisionCompletions:
    def create(self, **kwargs):
        payload = {
            "description": "图中显示流程节点。",
            "visible_text": "提交申请",
            "chart_type": "flowchart",
            "objects_or_nodes": ["提交申请"],
            "relationships": ["提交申请 -> 负责人确认"],
            "colors_or_legends": [],
            "limitations": [],
            "confidence": 0.91,
        }
        content = json.dumps(payload, ensure_ascii=False)
        usage = SimpleNamespace(prompt_tokens=5, completion_tokens=7, total_tokens=12)
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice], usage=usage)


class FakeOpenAIVisionClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=FakeVisionCompletions())


def test_openai_compatible_vision_client_parses_structured_output():
    config = ReconstructionConfig(
        image_understanding="required",
        vision_api_key="mock-vision-key",
        vision_base_url="https://vision.example.com/v1",
        vision_model="mock-multimodal",
    )
    assert "mock-vision-key" not in repr(config)
    client = OpenAICompatibleVisionClient(config, FakeOpenAIVisionClient())
    assert "mock-vision-key" not in repr(client)
    request = ImageRequest(
        path="inline",
        mime_type="image/png",
        data=PNG,
        alt="流程图",
        title="流程",
        caption="图 1",
        heading_path=("审批",),
    )
    description = client.describe_image(request)
    assert description.model == "mock-multimodal"
    assert description.chart_type == "flowchart"
    assert description.usage["total_tokens"] == 12


def test_html_figure_vision_marks_child_image_unit_for_review(tmp_path):
    write_png(tmp_path / "assets" / "chart.png")
    markdown = tmp_path / "figure.md"
    markdown.write_text(
        '# 返利\n\n如下图展示返利趋势。\n\n<figure>\n  <img src="assets/chart.png" alt="趋势图" title="趋势">\n  <figcaption>图 1：返利趋势</figcaption>\n</figure>\n',
        encoding="utf-8",
    )
    client = RecordingVisionClient(make_description())
    sdk = SemanticReconstructor(
        ReconstructionConfig(image_understanding="required"),
        vision_client=client,
    )
    result = sdk.reconstruct_markdown(markdown)
    assert client.calls == 1
    unit = next(item for item in result.units if "如下图" in item.action_or_conclusion)
    assert unit.review_status == "pending_business_review"
    assert any(item.block_type == "image" for item in unit.evidence)
    assert any(item.block_type == "figure" for item in unit.evidence)


def test_html_image_missing_src_blocks_referencing_unit(tmp_path):
    markdown = tmp_path / "missing-src.md"
    markdown.write_text('# 审批\n\n如下图展示审批流程和责任边界。\\n\n<img alt="流程图">\n', encoding="utf-8")
    result = SemanticReconstructor().reconstruct_markdown(markdown)
    unit = next(item for item in result.units if "如下图" in item.action_or_conclusion)
    assert unit.review_status == "blocked"
    assert any("缺少 src" in gap for gap in unit.known_gaps)
