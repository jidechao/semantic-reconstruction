"""Stable result models exposed by the semantic-reconstruction SDK."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

from .exceptions import OutputValidationError


@dataclass
class Evidence:
    """An auditable source fragment with an exact line mapping."""

    evidence_id: str
    document_id: str
    source_path: str
    line_start: int
    line_end: int
    heading_path: tuple[str, ...]
    block_type: str
    text: str
    raw_text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def location(self) -> str:
        return f"lines {self.line_start}-{self.line_end}"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["heading_path"] = list(self.heading_path)
        return data


@dataclass
class KnowledgeUnit:
    """A self-contained semantic unit reconstructed from source evidence."""

    unit_id: str
    business_question: str
    object: str
    conditions: list[str]
    action_or_conclusion: str
    exceptions: list[str]
    time_range: str
    self_explanation: str
    evidence: list[Evidence]
    changes: list[dict[str, str]]
    generation_mode: str
    review_status: str
    validation_findings: list[dict[str, str]] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    known_gaps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = [item.to_dict() for item in self.evidence]
        return data


@dataclass(frozen=True)
class SourceInfo:
    source_id: str
    source_path: str
    title: str
    line_count: int
    char_count: int
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    location: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReconstructionResult:
    schema_version: str
    source: SourceInfo
    units: list[KnowledgeUnit]
    diagnostics: list[Diagnostic] = field(default_factory=list)
    llm_usage: list[dict[str, Any]] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, Any]:
        return {
            "source_id": self.source.source_id,
            "unit_count": len(self.units),
            "auto_validated": sum(unit.review_status == "auto_validated" for unit in self.units),
            "pending_business_review": sum(unit.review_status == "pending_business_review" for unit in self.units),
            "blocked": sum(unit.review_status == "blocked" for unit in self.units),
            "error_count": sum(
                finding["status"] == "error"
                for unit in self.units
                for finding in unit.validation_findings
            ),
            "warning_count": sum(
                finding["status"] == "warning"
                for unit in self.units
                for finding in unit.validation_findings
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source": self.source.to_dict(),
            "summary": self.summary,
            "units": [unit.to_dict() for unit in self.units],
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "llm_usage": self.llm_usage,
        }

    def write_json(self, path: str | Path) -> Path:
        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except (OSError, TypeError, ValueError) as exc:
            raise OutputValidationError(f"写入 JSON 失败：{exc}") from exc
        return target

    def write_report(self, path: str | Path) -> Path:
        from .report import render_report

        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_report(self), encoding="utf-8")
        except OSError as exc:
            raise OutputValidationError(f"写入报告失败：{exc}") from exc
        return target


def source_info_from_text(
    text: str, source_id: str, source_path: str, title: str
) -> SourceInfo:
    return SourceInfo(
        source_id=source_id,
        source_path=source_path,
        title=title,
        line_count=text.count("\n") + (0 if text.endswith("\n") or not text else 1),
        char_count=len(text),
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )
