from pathlib import Path

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

