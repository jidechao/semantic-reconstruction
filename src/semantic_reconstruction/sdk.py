"""Stable synchronous facade for third-party Python integration."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import ReconstructionConfig
from .exceptions import DocumentParseError, DocumentTooLargeError, InvalidConfigurationError
from .llm_client import ClientProtocol, DeepSeekClient
from .llm_engine import HybridEngine, LLMEngine
from .markdown_parser import MarkdownParser, _slug
from .models import Diagnostic, Evidence, ReconstructionResult
from .vision import (
    ImageDescription,
    ImageRequest,
    OpenAICompatibleVisionClient,
    SUPPORTED_IMAGE_MIME_TYPES,
    VisionClientProtocol,
    decode_data_uri,
    validate_description,
)
from .pipeline import RuleReconstructor

SCHEMA_VERSION = "1.1"


class SemanticReconstructor:
    """Reconstruct Markdown into auditable, self-contained knowledge units."""

    def __init__(
        self,
        config: ReconstructionConfig | None = None,
        *,
        llm_client: ClientProtocol | None = None,
        vision_client: VisionClientProtocol | None = None,
    ):
        self.config = config or ReconstructionConfig()
        self._injected_client = llm_client
        self._injected_vision_client = vision_client
        self.config.require_llm(has_custom_client=llm_client is not None)
        self.config.require_vision(has_custom_client=vision_client is not None)
        self._client = DeepSeekClient(self.config, llm_client) if llm_client is not None else (
            DeepSeekClient(self.config) if self.config.mode in {"hybrid", "llm"} else None
        )
        self._vision_client = vision_client
        if (
            self._vision_client is None
            and self.config.image_understanding != "off"
            and self.config.vision_configured
        ):
            self._vision_client = OpenAICompatibleVisionClient(self.config)

    @property
    def _vision_enabled(self) -> bool:
        return self.config.image_understanding != "off" and self._vision_client is not None

    def _load_image_request(self, evidence: Evidence, source_root) -> ImageRequest | None:
        metadata = evidence.metadata
        source_type = metadata.get("source_type")
        data: bytes | None = None
        mime = metadata.get("mime_type", "")
        path = metadata.get("path", "")
        if source_type == "local":
            resolved = Path(metadata.get("resolved_path", ""))
            root = Path(source_root).resolve()
            try:
                resolved = resolved.resolve()
                resolved.relative_to(root)
            except (OSError, ValueError):
                raise ValueError(f"本地图片路径越界，拒绝读取：{resolved}")
            if not resolved.is_file():
                return None
            data = resolved.read_bytes()
        elif source_type == "data":
            decoded = decode_data_uri(metadata.get("_data_uri", ""))
            if decoded is None:
                return None
            mime, data = decoded
        else:
            return None
        if mime not in SUPPORTED_IMAGE_MIME_TYPES:
            raise ValueError(f"不支持的图片 MIME 类型：{mime}")
        if len(data) > self.config.vision_max_image_bytes:
            raise ValueError(f"图片超过大小限制：{len(data)} > {self.config.vision_max_image_bytes}")
        caption_id = metadata.get("caption_evidence_id")
        return ImageRequest(
            path=path,
            mime_type=mime,
            data=data,
            alt=metadata.get("alt", ""),
            title=metadata.get("title", ""),
            caption=caption_id or "",
            heading_path=evidence.heading_path,
            evidence_id=evidence.evidence_id,
        )

    def _apply_vision(self, parsed, units: list) -> tuple[list[Diagnostic], list[dict]]:
        if not self._vision_enabled:
            return [], []
        diagnostics: list[Diagnostic] = []
        usage: list[dict] = []
        source_root = Path(parsed.source.source_path).parent if parsed.source.source_path != "<memory>" else Path.cwd()
        image_evidence = [item for item in parsed.evidence if item.block_type == "image"]
        evidence_index = {item.evidence_id: item for item in parsed.evidence}
        for evidence in image_evidence:
            if evidence.metadata.get("source_type") == "remote":
                diagnostics.append(Diagnostic(
                    code="image_understanding_skipped",
                    severity="warning",
                    message="远程图片只保留引用，不主动抓取。",
                    location=evidence.evidence_id,
                ))
                continue
            try:
                request = self._load_image_request(evidence, source_root)
                if request is None:
                    continue
                description = self._vision_client.describe_image(request)
                errors = validate_description(
                    description,
                    min_confidence=self.config.vision_min_confidence,
                )
                if errors:
                    has_conflict = any("冲突" in error for error in errors)
                    diagnostics.append(Diagnostic(
                        code="vision_output_rejected",
                        severity="error" if has_conflict else "warning",
                        message="视觉输出未通过安全校验，已回退引用层：" + "；".join(errors),
                        location=evidence.evidence_id,
                    ))
                    if has_conflict:
                        for unit in units:
                            if any(item.evidence_id == evidence.evidence_id for item in unit.evidence):
                                unit.review_status = "blocked"
                                unit.known_gaps.append("视觉描述与正文证据存在冲突，需人工复核。")
                    continue
                vision_data = description.to_dict()
                usage_entry = dict(vision_data.get("usage", {}))
                usage_entry.update({
                    "model": description.model,
                    "mode": "vision",
                    "evidence_id": evidence.evidence_id,
                })
                usage.append(usage_entry)
                evidence.metadata["vision"] = vision_data
                for unit in units:
                    if not any(item.evidence_id == evidence.evidence_id for item in unit.evidence):
                        continue
                    unit.review_status = "pending_business_review"
                    unit.changes.append({
                        "type": "视觉描述生成",
                        "detail": "图片内容描述仅作为证据保留，需业务复核。",
                    })
            except Exception as exc:
                diagnostics.append(Diagnostic(
                    code="vision_provider_error",
                    severity="warning",
                    message=f"视觉模型调用失败，已回退引用层：{exc}",
                    location=evidence.evidence_id,
                ))
        return diagnostics, usage

    def _parse(self, text: str, source_id: str, source_path: str) -> ReconstructionResult:
        if len(text) > self.config.max_document_chars:
            raise DocumentTooLargeError(
                f"文档超过 max_document_chars 限制：{len(text)} > {self.config.max_document_chars}"
            )
        parser = MarkdownParser(
            include_code_blocks=self.config.include_code_blocks,
            include_image_references=self.config.include_image_references,
            include_chart_blocks=self.config.include_chart_blocks,
        )
        parsed = parser.parse_text(text, source_id=source_id, source_path=source_path)
        units = RuleReconstructor(parsed).reconstruct()
        vision_diagnostics, vision_usage = self._apply_vision(parsed, units)
        usage: list[dict] = list(vision_usage)

        if self.config.mode in {"hybrid", "llm"}:
            engine = HybridEngine(self._client) if self.config.mode == "hybrid" else LLMEngine(self._client)
            units, usage = engine.reconstruct(units)

        if not self.config.keep_raw_evidence:
            for unit in units:
                for evidence in unit.evidence:
                    evidence.raw_text = ""

        diagnostics: list[Diagnostic] = list(vision_diagnostics)
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

