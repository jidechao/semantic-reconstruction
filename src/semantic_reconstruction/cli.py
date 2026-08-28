"""Command-line interface built on the public SDK API."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence

from . import __version__
from .config import ReconstructionConfig
from .exceptions import SemanticReconstructionError
from .report import render_batch_report
from .sdk import SemanticReconstructor


def _load_env_file(path: str | None) -> None:
    if not path:
        return
    env_path = Path(path)
    if not env_path.exists():
        raise SemanticReconstructionError(f".env 文件不存在：{env_path}")
    for raw in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="semantic-reconstruction",
        description="将 Markdown 重构为可审计、可独立理解的语义知识单元。",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    reconstruct = subparsers.add_parser("reconstruct", help="重构一个 Markdown 文件或目录")
    reconstruct.add_argument("path", help="Markdown 文件或目录")
    reconstruct.add_argument("--mode", choices=["rule", "hybrid", "llm"], default="rule")
    reconstruct.add_argument("--out", default="output", help="输出目录")
    reconstruct.add_argument("--env-file", default=None, help="可选 .env 文件；仅 CLI 使用，SDK API 不隐式读取")
    reconstruct.add_argument("--max-document-chars", type=int, default=2_000_000)
    reconstruct.add_argument("--include-code-blocks", action=argparse.BooleanOptionalAction, default=True)
    reconstruct.add_argument("--llm-batch-size", type=int, default=25)
    reconstruct.add_argument("--no-api-key", action="store_true", help="占位参数，用于防止密钥出现在命令行")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _load_env_file(args.env_file)
        config = ReconstructionConfig(
            mode=args.mode,
            max_document_chars=args.max_document_chars,
            include_code_blocks=args.include_code_blocks,
            llm_batch_size=args.llm_batch_size,
        )
        sdk = SemanticReconstructor(config)
        results = sdk.reconstruct_files(args.path)
        output = Path(args.out)
        output.mkdir(parents=True, exist_ok=True)
        json_path = output / "results.json"
        report_path = output / "report.md"
        json_path.write_text(
            json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report_path.write_text(render_batch_report(results), encoding="utf-8")
        total_units = sum(len(result.units) for result in results)
        passed = sum(result.summary["auto_validated"] for result in results)
        pending = sum(result.summary["pending_business_review"] for result in results)
        blocked = sum(result.summary["blocked"] for result in results)
        print(
            f"语义重构完成：文档 {len(results)} 份；知识单元 {total_units} 条；"
            f"自动验收 {passed}；待业务复核 {pending}；阻断 {blocked}。"
        )
        print(f"JSON：{json_path.resolve()}")
        print(f"报告：{report_path.resolve()}")
        return 0
    except SemanticReconstructionError as exc:
        print(f"执行失败：{exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"执行失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


