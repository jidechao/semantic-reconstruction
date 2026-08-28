from pathlib import Path
import json
import uuid

from semantic_reconstruction.cli import main


def test_cli_reconstruct_directory(tmp_path, capsys):
    source = tmp_path / "docs"
    source.mkdir()
    (source / "sample.md").write_text(
        "# 简化流程\n\n申请人同时满足以下条件：合同有效。\n\n满足时，可由部门负责人审批。\n",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    code = main(["reconstruct", str(source), "--mode", "rule", "--out", str(output)])
    assert code == 0
    captured = capsys.readouterr().out
    assert "语义重构完成" in captured
    assert (output / "results.json").read_text(encoding="utf-8").startswith("[")
    assert "12 问验收" in (output / "report.md").read_text(encoding="utf-8")


def test_cli_missing_path_fails(tmp_path, capsys):
    code = main(["reconstruct", str(tmp_path / "missing.md"), "--mode", "rule", "--out", str(tmp_path / "out")])
    assert code == 2
    assert "执行失败" in capsys.readouterr().err



def test_cli_controls_absolute_image_paths(tmp_path):
    outside = tmp_path.parent / f"semantic-reconstruction-cli-image-{uuid.uuid4().hex}.png"
    outside.write_bytes(b"png-bytes")
    source = tmp_path / "docs"
    source.mkdir()
    markdown = source / "absolute.md"
    markdown.write_text(f"# 图\n\n![外部图]({outside})\n", encoding="utf-8")

    default_out = tmp_path / "default-output"
    assert main(["reconstruct", str(markdown), "--mode", "rule", "--image-understanding", "off", "--out", str(default_out)]) == 0
    default_result = json.loads((default_out / "results.json").read_text(encoding="utf-8"))[0]
    assert not any(item["code"] == "image_path_escape" for item in default_result["diagnostics"])
    assert any(unit["generation_mode"] == "image_evidence" for unit in default_result["units"])

    restricted_out = tmp_path / "restricted-output"
    assert main([
        "reconstruct", str(markdown), "--mode", "rule", "--image-understanding", "off",
        "--no-absolute-image-paths", "--out", str(restricted_out),
    ]) == 0
    restricted_result = json.loads((restricted_out / "results.json").read_text(encoding="utf-8"))[0]
    assert any(item["code"] == "image_path_escape" for item in restricted_result["diagnostics"])
    assert "图片与视觉证据层" in (restricted_out / "report.md").read_text(encoding="utf-8")
