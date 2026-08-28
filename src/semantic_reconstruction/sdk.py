"""Stable synchronous facade for third-party Python integration."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import ReconstructionConfig
from .detector import detect_risk_flags
from .exceptions import DocumentParseError, DocumentTooLargeError, InvalidConfigurationError
from .llm_client import ClientProtocol, DeepSeekClient
from .llm_engine import HybridEngine, LLMEngine
from .markdown_parser import MarkdownParser, _slug
from .models import Diagnostic, Evidence, KnowledgeUnit, ReconstructionResult
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
from .validator import validate_knowledge_unit

SCHEMA_VERSION = "1.2"


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

    def _append_image_units(self, parsed, units: list) -> list:
        image_evidence = [item for item in parsed.evidence if item.block_type == "image"]
        evidence_index = {item.evidence_id: item for item in parsed.evidence}
        for image in image_evidence:
            metadata = image.metadata
            heading = next((
                item for item in reversed(parsed.evidence)
                if item.block_type == "heading" and item.line_end <= image.line_start
            ), None)
            caption = evidence_index.get(metadata.get("caption_evidence_id", ""), None)
            container = evidence_index.get(metadata.get("container_evidence_id", ""), None)
            bound_evidence = [item for item in [heading, image, caption, container] if item is not None]
            known_gaps: list[str] = []
            if metadata.get("missing_src") or metadata.get("source_type") in {"", "unknown"}:
                known_gaps.append("HTML 图片缺少 src，无法定位图片证据。")
            if metadata.get("source_type") == "local" and not metadata.get("exists", False):
                known_gaps.append(f"引用的本地图片不存在：{metadata.get('path', '未知路径')}")
            if metadata.get("mime_type") not in {"", "image/png", "image/jpeg", "image/webp", "image/gif"}:
                known_gaps.append(f"不支持的图片 MIME 类型：{metadata.get('mime_type') or '未知'}")

            source_label = metadata.get("path", "未知来源")
            object_text = " > ".join(image.heading_path[-2:]) or parsed.document_title
            action = image.text or f"[图片证据：{source_label}]"
            explanation = (
                f"图片证据待人工复核：来源 {source_label}；"
                "该单元只记录图片引用和可见内容，不把图片内容升级为业务规则。"
            )
            changes: list[dict[str, str]] = [
                {"type": "图片证据绑定", "detail": "为每个图片引用生成独立证据单元。"}
            ]
            if heading is not None:
                changes.append({"type": "章节证据", "detail": f"绑定标题证据 {heading.evidence_id}。"})
            if caption is not None:
                changes.append({"type": "图注绑定", "detail": f"绑定图注证据 {caption.evidence_id}。"})
            if container is not None:
                changes.append({"type": "容器绑定", "detail": f"绑定 HTML 容器证据 {container.evidence_id}。"})

            unit = KnowledgeUnit(
                unit_id=f"{parsed.source.source_id}-u{len(units) + 1:04d}",
                business_question=f"{object_text} 中图片 {image.evidence_id} 的可见内容是什么？",
                object=object_text,
                conditions=[],
                action_or_conclusion=action,
                exceptions=[],
                time_range="原文未单独标注时间或版本范围",
                self_explanation=explanation,
                evidence=bound_evidence,
                changes=changes,
                generation_mode="image_evidence",
                review_status="blocked" if known_gaps else "pending_business_review",
                risk_flags=detect_risk_flags(bound_evidence),
                known_gaps=known_gaps,
            )
            unit.validation_findings = validate_knowledge_unit(unit)
            if any(item["status"] == "error" for item in unit.validation_findings):
                unit.review_status = "blocked"
            units.append(unit)
        return units

    @staticmethod
    def _mark_image_invalid(units: list, evidence: Evidence, reason: str) -> None:
        for unit in units:
            if not any(item.evidence_id == evidence.evidence_id for item in unit.evidence):
                continue
            if reason not in unit.known_gaps:
                unit.known_gaps.append(reason)
            unit.review_status = "blocked"
            unit.validation_findings = validate_knowledge_unit(unit)

    def _prepare_image_assets(self, parsed, units: list) -> tuple[dict[str, ImageRequest], list[Diagnostic]]:
        requests: dict[str, ImageRequest] = {}
        diagnostics: list[Diagnostic] = []
        if parsed.source.source_path == "<memory>":
            source_root = Path.cwd().resolve()
        else:
            source_root = Path(parsed.source.source_path).parent.resolve()
        def invalid(evidence: Evidence, code: str, message: str) -> None:
            diagnostics.append(Diagnostic(code=code, severity="error", message=message, location=evidence.evidence_id))
            self._mark_image_invalid(units, evidence, message)

        for evidence in (item for item in parsed.evidence if item.block_type == "image"):
            metadata = evidence.metadata
            if metadata.get("missing_src") or metadata.get("source_type") in {"", "unknown"}:
                invalid(evidence, "image_src_missing", "HTML 图片缺少 src，无法定位图片证据。")
                continue

            source_type = metadata.get("source_type")
            path = str(metadata.get("path", ""))
            common = {
                "path": path,
                "alt": str(metadata.get("alt", "")),
                "title": str(metadata.get("title", "")),
                "caption": str(metadata.get("caption_evidence_id", "")),
                "heading_path": evidence.heading_path,
                "evidence_id": evidence.evidence_id,
            }
            if source_type == "remote":
                requests[evidence.evidence_id] = ImageRequest(
                    mime_type=str(metadata.get("mime_type", "")),
                    data=b"",
                    source_url=path,
                    **common,
                )
                continue

            if source_type == "data":
                decoded = decode_data_uri(str(metadata.get("_data_uri", "")))
                if decoded is None:
                    invalid(evidence, "image_asset_missing", "data URI 图片无法解码。")
                    continue
                mime, data = decoded
                if mime not in SUPPORTED_IMAGE_MIME_TYPES:
                    invalid(evidence, "image_mime_unsupported", f"不支持的图片 MIME 类型：{mime}")
                    continue
                if len(data) > self.config.vision_max_image_bytes:
                    invalid(evidence, "image_too_large", f"图片超过大小限制：{len(data)} > {self.config.vision_max_image_bytes}")
                    continue
                requests[evidence.evidence_id] = ImageRequest(mime_type=mime, data=data, **common)
                continue

            if source_type != "local":
                invalid(evidence, "image_asset_missing", f"未知图片来源类型：{source_type}")
                continue

            resolved = Path(str(metadata.get("resolved_path", "")))
            try:
                resolved.relative_to(source_root)
                inside_root = True
            except (OSError, ValueError):
                inside_root = False
            location_kind = str(metadata.get("location_kind", "relative_path"))
            if not inside_root and location_kind == "relative_path":
                invalid(evidence, "image_path_escape", f"相对图片路径越界，拒绝读取：{resolved}")
                continue
            if not inside_root and location_kind in {"absolute_path", "file_uri"} and not self.config.allow_absolute_image_paths:
                invalid(evidence, "image_path_escape", f"本地图片路径越界，拒绝读取：{resolved}")
                continue
            if not resolved.is_file():
                invalid(evidence, "image_asset_missing", f"引用的本地图片不存在：{path or resolved}")
                continue

            mime = str(metadata.get("mime_type", ""))
            if mime not in SUPPORTED_IMAGE_MIME_TYPES:
                invalid(evidence, "image_mime_unsupported", f"不支持的图片 MIME 类型：{mime or '未知'}")
                continue
            try:
                data = resolved.read_bytes()
            except OSError as exc:
                invalid(evidence, "image_asset_missing", f"本地图片读取失败：{exc}")
                continue
            if len(data) > self.config.vision_max_image_bytes:
                invalid(evidence, "image_too_large", f"图片超过大小限制：{len(data)} > {self.config.vision_max_image_bytes}")
                continue
            requests[evidence.evidence_id] = ImageRequest(mime_type=mime, data=data, **common)

        return requests, diagnostics

    def _apply_vision(self, parsed, units: list, requests: dict[str, ImageRequest]) -> tuple[list[Diagnostic], list[dict]]:
        if not self._vision_enabled:
            return [], []
        diagnostics: list[Diagnostic] = []
        usage: list[dict] = []
        for evidence in (item for item in parsed.evidence if item.block_type == "image"):
            request = requests.get(evidence.evidence_id)
            if request is None:
                continue
            try:
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
                    for unit in units:
                        if any(item.evidence_id == evidence.evidence_id for item in unit.evidence):
                            if has_conflict:
                                unit.review_status = "blocked"
                                gap = "视觉描述与正文证据存在冲突，需人工复核。"
                                if gap not in unit.known_gaps:
                                    unit.known_gaps.append(gap)
                            unit.changes.append({
                                "type": "视觉描述未采纳",
                                "detail": "视觉输出未通过安全校验，保留图片引用层并需人工复核。",
                            })
                            unit.validation_findings = validate_knowledge_unit(unit)
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
                limitations = "；".join(description.limitations) or "无"
                visible_text = description.visible_text or "无"
                vision_explanation = (
                    f"图片可见内容：{description.description}；可见文字：{visible_text}；"
                    f"图表类型：{description.chart_type or '待确认'}；置信度：{description.confidence:.2f}；"
                    f"限制说明：{limitations}。图片描述仅作为证据保留，不升级为业务规则。"
                )
                for unit in units:
                    if not any(item.evidence_id == evidence.evidence_id for item in unit.evidence):
                        continue
                    if unit.review_status != "blocked":
                        unit.review_status = "pending_business_review"
                    if unit.generation_mode == "image_evidence":
                        unit.self_explanation = vision_explanation
                    unit.changes.append({
                        "type": "视觉描述生成",
                        "detail": "图片内容描述仅作为证据保留，需业务复核。",
                    })
                    unit.validation_findings = validate_knowledge_unit(unit)
            except Exception as exc:
                diagnostics.append(Diagnostic(
                    code="vision_provider_error",
                    severity="warning",
                    message=f"视觉模型调用失败，已回退引用层：{exc}",
                    location=evidence.evidence_id,
                ))
                for unit in units:
                    if any(item.evidence_id == evidence.evidence_id for item in unit.evidence):
                        unit.changes.append({
                            "type": "视觉描述回退",
                            "detail": "视觉模型不可用或调用失败，图片内容需人工复核。",
                        })
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
        units = self._append_image_units(parsed, units)
        image_requests, image_diagnostics = self._prepare_image_assets(parsed, units)
        vision_diagnostics, vision_usage = self._apply_vision(parsed, units, image_requests)
        usage: list[dict] = list(vision_usage)

        if self.config.mode in {"hybrid", "llm"}:
            engine = HybridEngine(self._client) if self.config.mode == "hybrid" else LLMEngine(self._client)
            units, usage = engine.reconstruct(units)

        if not self.config.keep_raw_evidence:
            for unit in units:
                for evidence in unit.evidence:
                    evidence.raw_text = ""

        diagnostics: list[Diagnostic] = [*image_diagnostics, *vision_diagnostics]
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

