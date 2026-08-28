"""Deterministic Markdown parser with exact source mappings."""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Any

from .exceptions import DocumentParseError
from .models import Evidence, SourceInfo, source_info_from_text

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_LIST = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*(.*)$")
_TABLE = re.compile(r"^\s*\|.*\|\s*$")
_HTML = re.compile(r"^\s*<[^>]+>\s*$")
_IMAGE_ONLY = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")


@dataclass
class ParsedDocument:
    source: SourceInfo
    evidence: list[Evidence]
    document_title: str
    heading_tree: list[dict[str, Any]] = field(default_factory=list)


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", value).strip("-")
    return cleaned[:48] or "document"


def strip_inline_markdown(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"[图片：\1]", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"<https?://[^>]+>", "", value)
    value = re.sub(r"[*_`]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


class MarkdownParser:
    """Parse Markdown without interpreting fenced code as real Markdown."""

    def __init__(self, *, include_code_blocks: bool = True):
        self.include_code_blocks = include_code_blocks

    def parse_file(self, path: str | Path, source_id: str | None = None) -> ParsedDocument:
        source_path = Path(path)
        if not source_path.is_file():
            raise DocumentParseError(f"Markdown 文件不存在：{source_path}")
        try:
            text = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentParseError(f"文件不是合法 UTF-8：{source_path}") from exc
        sid = source_id or _slug(source_path.stem)
        return self.parse_text(text, source_id=sid, source_path=str(source_path))

    def parse_text(
        self,
        text: str,
        *,
        source_id: str,
        source_path: str = "<memory>",
    ) -> ParsedDocument:
        if not text.strip():
            raise DocumentParseError("Markdown 输入为空")
        lines = text.splitlines()
        evidence: list[Evidence] = []
        heading_tree: list[dict[str, Any]] = []
        heading_stack: list[tuple[int, str]] = []
        document_title = source_id
        index = 0
        block_number = 0

        def heading_path() -> tuple[str, ...]:
            return tuple(name for _, name in heading_stack)

        def append_block(
            start: int,
            end: int,
            block_type: str,
            raw: str,
            text_value: str | None = None,
            metadata: dict[str, Any] | None = None,
        ) -> None:
            nonlocal block_number
            if not raw.strip():
                return
            block_number += 1
            evidence.append(Evidence(
                evidence_id=f"{source_id}-b{block_number:04d}",
                document_id=source_id,
                source_path=source_path,
                line_start=start + 1,
                line_end=end + 1,
                heading_path=heading_path(),
                block_type=block_type,
                text=text_value if text_value is not None else strip_inline_markdown(raw),
                raw_text=raw,
                metadata=metadata or {},
            ))

        while index < len(lines):
            line = lines[index]
            fence_match = _FENCE.match(line)
            if fence_match:
                marker = fence_match.group(1)[0] * 3
                start = index
                index += 1
                while index < len(lines) and not _FENCE.match(lines[index]):
                    index += 1
                # A valid closing fence uses the same character and enough length.
                if index < len(lines):
                    closing = _FENCE.match(lines[index])
                    if closing and closing.group(1)[0] == marker[0]:
                        index += 1
                raw = "\n".join(lines[start:index])
                if self.include_code_blocks:
                    append_block(start, index - 1, "code_example", raw)
                continue

            heading_match = _HEADING.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                title = strip_inline_markdown(heading_match.group(2))
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, title))
                if not heading_tree:
                    document_title = title
                append_block(index, index, "heading", line, title)
                node: dict[str, Any] = {"level": level, "title": title, "line": index + 1, "children": []}
                parents = [heading_tree]
                for _, parent_title in heading_stack[:-1]:
                    found = next(
                        (child for child in parents[-1] if child["title"] == parent_title),
                        None,
                    )
                    if found is None:
                        found = {"level": level, "title": parent_title, "line": index + 1, "children": []}
                        parents[-1].append(found)
                    parents.append(found["children"])
                parents[-1].append(node)
                index += 1
                continue

            if _TABLE.match(line):
                start = index
                while index < len(lines) and _TABLE.match(lines[index]):
                    index += 1
                table_lines = lines[start:index]
                headers = [
                    strip_inline_markdown(part.strip())
                    for part in table_lines[0].strip().strip("|").split("|")
                ]
                append_block(start, start, "table_header", table_lines[0], "；".join(headers), {"table_headers": headers})
                for row_index, row in enumerate(table_lines[1:], start=start + 1):
                    if re.match(r"^\s*\|?[\s:|-]+\|?\s*$", row):
                        continue
                    values = [strip_inline_markdown(part.strip()) for part in row.strip().strip("|").split("|")]
                    row_text = "；".join(
                        f"{header or f'列{position}'}={value}"
                        for position, (header, value) in enumerate(zip(headers, values), 1)
                    )
                    append_block(
                        row_index,
                        row_index,
                        "table_row",
                        row,
                        f"表头：{'；'.join(headers)}。当前行：{row_text}",
                        {"table_headers": headers, "row_values": values, "table_line_start": start + 1},
                    )
                continue

            if _LIST.match(line):
                start = index
                while index < len(lines) and (_LIST.match(lines[index]) or (lines[index].startswith((" ", "\t")) and lines[index].strip() and not _HEADING.match(lines[index]))):
                    index += 1
                raw = "\n".join(lines[start:index]).rstrip()
                append_block(start, index - 1, "list", raw)
                continue

            if line.startswith(">"):
                start = index
                while index < len(lines) and lines[index].startswith(">"):
                    index += 1
                raw = "\n".join(lines[start:index])
                append_block(start, index - 1, "blockquote", raw)
                continue

            if _HTML.match(line):
                start = index
                while index < len(lines) and lines[index].strip() and not _HEADING.match(lines[index]) and not _FENCE.match(lines[index]):
                    if index > start and _HTML.match(lines[index]):
                        # Extend HTML blocks only across contiguous markup or blank continuation lines.
                        if not (_HTML.match(lines[index]) or not lines[index].strip()):
                            break
                    index += 1
                raw = "\n".join(lines[start:index]).rstrip()
                append_block(start, index - 1, "html", raw)
                continue

            if not line.strip():
                index += 1
                continue

            start = index
            while index < len(lines) and lines[index].strip() and not (
                _HEADING.match(lines[index])
                or _FENCE.match(lines[index])
                or _TABLE.match(lines[index])
                or _LIST.match(lines[index])
                or lines[index].startswith(">")
                or _HTML.match(lines[index])
            ):
                index += 1
            raw = "\n".join(lines[start:index])
            append_block(start, index - 1, "paragraph", raw)

        if not document_title or document_title == source_id:
            for item in evidence:
                if item.block_type == "heading":
                    document_title = item.text
                    break
        source = source_info_from_text(text, source_id, source_path, document_title)
        return ParsedDocument(source=source, evidence=evidence, document_title=document_title, heading_tree=heading_tree)
