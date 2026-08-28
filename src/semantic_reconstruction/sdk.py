"""Stable synchronous facade for third-party Python integration."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import ReconstructionConfig
from .exceptions import DocumentParseError, DocumentTooLargeError, InvalidConfigurationError
from .llm_client import ClientProtocol, DeepSeekClient
from .llm_engine import HybridEngine, LLMEngine
from .markdown_parser import MarkdownParser, _slug
from .models import Diagnostic, ReconstructionResult
from .pipeline import RuleReconstructor

SCHEMA_VERSION = "1.0"


class SemanticReconstructor:
    """Reconstruct Markdown into auditable, self-contained knowledge units."""

    def __init__(
        self,
        config: ReconstructionConfig | None = None,
        *,
        llm_client: ClientProtocol | None = None,
    ):
        self.config = config or ReconstructionConfig()
        self._injected_client = llm_client
        self.config.require_llm(has_custom_client=llm_client is not None)
        self._client = DeepSeekClient(self.config, llm_client) if llm_client is not None else (
            DeepSeekClient(self.config) if self.config.mode in {"hybrid", "llm"} else None
        )

    def _parse(self, text: str, source_id: str, source_path: str) -> ReconstructionResult:
        if len(text) > self.config.max_document_chars:
            raise DocumentTooLargeError(
                f"文档超过 max_document_chars 限制：{len(text)} > {self.config.max_document_chars}"
            )
        parser = MarkdownParser(include_code_blocks=self.config.include_code_blocks)
        parsed = parser.parse_text(text, source_id=source_id, source_path=source_path)
        units = RuleReconstructor(parsed).reconstruct()
        usage: list[dict] = []

        if self.config.mode in {"hybrid", "llm"}:
            engine = HybridEngine(self._client) if self.config.mode == "hybrid" else LLMEngine(self._client)
            units, usage = engine.reconstruct(units)

        if not self.config.keep_raw_evidence:
            for unit in units:
                for evidence in unit.evidence:
                    evidence.raw_text = ""

        diagnostics: list[Diagnostic] = []
        for unit in units:
            if unit.review_status == "blocked":
                diagnostics.append(Diagnostic(
                    code="semantic_unit_blocked",
                    severity="error",
                    message="知识单元存在证据缺口或验收错误，已阻断。",
                    location=f"{unit.unit_id}",
                ))
            for finding in unit.validation_findings:
                if finding.get("check") != "LLM" or finding.get("status") not in {"warning", "error"}:
                    continue
                diagnostics.append(Diagnostic(
                    code="llm_output_rejected" if finding["status"] == "error" else "llm_fallback",
                    severity=finding["status"],
                    message=finding["message"],
                    location=f"{unit.unit_id}",
                ))
        return ReconstructionResult(
            schema_version=SCHEMA_VERSION,
            source=parsed.source,
            units=units,
            diagnostics=diagnostics,
            llm_usage=usage,
        )

    def reconstruct_text(
        self,
        text: str,
        source_id: str,
        source_path: str | None = None,
    ) -> ReconstructionResult:
        if not source_id.strip():
            raise InvalidConfigurationError("source_id 不能为空")
        return self._parse(text, _slug(source_id), source_path or "<memory>")

    def reconstruct_markdown(
        self,
        path: str | Path,
        source_id: str | None = None,
    ) -> ReconstructionResult:
        source_path = Path(path)
        if not source_path.is_file():
            raise DocumentParseError(f"Markdown 文件不存在：{source_path}")
        try:
            text = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentParseError(f"文件不是合法 UTF-8：{source_path}") from exc
        sid = _slug(source_id or source_path.stem)
        return self._parse(text, sid, str(source_path))

    def reconstruct_files(
        self,
        paths: str | Path | Iterable[str | Path],
    ) -> list[ReconstructionResult]:
        if isinstance(paths, (str, Path)):
            root = Path(paths)
            if root.is_dir():
                files = sorted(
                    path for path in root.rglob("*.md")
                    if not any(part in {".venv", "node_modules", "__pycache__", ".pytest_cache"} or part.startswith("output") for part in path.parts)
                )
            else:
                files = [root]
        else:
            files = [Path(path) for path in paths]
        if not files:
            raise DocumentParseError("未找到可处理的 Markdown 文件")
        return [self.reconstruct_markdown(path) for path in files]

