"""Deterministic Markdown parser with exact source and asset mappings."""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import re
from typing import Any
from urllib.parse import urlparse

from .exceptions import DocumentParseError
from .models import Evidence, SourceInfo, source_info_from_text

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_LIST = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*(.*)$")
_TABLE = re.compile(r"^\s*\|.*\|\s*$")
_HTML_LINE = re.compile(r"^\s*<[^>]+>?\s*$", re.IGNORECASE)
_CAPTION = re.compile(r"^\s*((?:图|Figure|Fig\.)\s*\d+|图示|图表|架构图|流程图)\s*[:：]\s*(.+)$", re.IGNORECASE)
_IMAGE_INLINE = re.compile(r"!\[([^\]]*)\]\(\s*([^)\s]+)(?:\s+\"([^\"]*)\")?\s*\)")
_IMAGE_REFERENCE = re.compile(r"!\[([^\]]*)\]\[([^\]]+)\]")
_IMAGE_DEFINITION = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s+(\S+)(?:\s+\"([^\"]*)\")?\s*$")
_ASSET_BLOCK_TYPES = {"image", "figure", "chart_code", "chart_svg"}
_CHART_LANGUAGES = {"mermaid", "mmd", "svg"}
_GRAPH_SHAPES = {"circle", "ellipse", "line", "path", "polygon", "polyline", "rect", "text", "tspan", "g", "defs", "marker", "arrow"}


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


def _safe_asset_display(value: str) -> str:
    if value.startswith("data:"):
        return value.split(",", 1)[0] + ",<omitted>"
    return value


def _source_type(path: str) -> str:
    if path.startswith("data:"):
        return "data"
    if urlparse(path).scheme in {"http", "https"}:
        return "remote"
    return "local"


def _mime_from_path(path: str) -> str:
    suffix = Path(urlparse(path).path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
    }.get(suffix, "")


def _asset_metadata(path: str, base_dir: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "asset_type": "chart" if _mime_from_path(path) == "image/svg+xml" else "image",
        "source_type": _source_type(path),
        "path": path if path.startswith("data:") else _safe_asset_display(path),
    }
    if path.startswith("data:"):
        header = path.split(",", 1)[0]
        metadata["path"] = header + ",<omitted>"
        metadata["mime_type"] = header[5:].split(";", 1)[0] or ""
        metadata["_data_uri"] = path
        try:
            import base64
            payload = path.split(",", 1)[1]
            metadata["sha256"] = hashlib.sha256(base64.b64decode(payload, validate=False)).hexdigest()
        except Exception:
            metadata["sha256"] = ""
        return metadata
    if _source_type(path) == "local":
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        try:
            resolved = candidate.resolve()
            metadata["resolved_path"] = str(resolved)
            metadata["exists"] = resolved.is_file()
            if resolved.is_file():
                metadata["mime_type"] = _mime_from_path(str(resolved))
                metadata["sha256"] = hashlib.sha256(resolved.read_bytes()).hexdigest()
        except OSError:
            metadata["exists"] = False
    else:
        metadata["mime_type"] = _mime_from_path(path)
    return metadata


def _parse_mermaid(raw_code: str, language: str) -> dict[str, Any]:
    lines = [line.strip() for line in raw_code.splitlines() if line.strip()]
    first = lines[0].split() if lines else []
    chart_type = first[0] if first else "unknown"
    direction = first[1] if len(first) > 1 and chart_type in {"flowchart", "graph"} else ""
    node_labels: list[str] = []
    for match in re.findall(r"[\[\(\{<]([^\[\]\(\)\{\}<>]+)[\]\)\}\>]", raw_code):
        label = match.strip().strip('"\'' )
        if label and label not in node_labels and label not in {direction, chart_type}:
            node_labels.append(label)
    relationships = [
        line for line in lines
        if re.search(r"-->|-->|->>|---|--|-\.-|==>", line)
    ]
    return {
        "chart_format": language,
        "chart_type": chart_type,
        "direction": direction,
        "nodes": node_labels,
        "relationships": relationships,
        "script_present": any("<script" in line.lower() for line in lines),
    }


class _SVGParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.texts: list[str] = []
        self.shapes: list[str] = []
        self.scripts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "foreignobject"}:
            self._skip_depth += 1
            if tag == "script":
                self.scripts.append(tag)
            return
        if self._skip_depth:
            return
        if tag == "title":
            self._in_title = True
        if tag == "desc":
            self._in_desc = True
        if tag in _GRAPH_SHAPES:
            self.shapes.append(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "foreignobject"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag == "desc":
            self._in_desc = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        value = " ".join(data.split())
        if not value:
            return
        if getattr(self, "_in_title", False):
            self.title = value
        elif getattr(self, "_in_desc", False):
            self.description = value
        else:
            self.texts.append(value)


def _parse_svg(raw: str) -> dict[str, Any]:
    parser = _SVGParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception:
        # SVG evidence remains auditable even when malformed; never execute it.
        pass
    return {
        "chart_format": "svg",
        "chart_type": "svg",
        "title": parser.title,
        "description": parser.description,
        "texts": parser.texts,
        "shapes": parser.shapes,
        "scripts_present": bool(parser.scripts),
    }


class _HTMLAssetParser(HTMLParser):
    def __init__(self, block_offset: int, lines: list[str]):
        super().__init__(convert_charrefs=True)
        self.block_offset = block_offset
        self.lines = lines
        self.events: list[dict[str, Any]] = []
        self._figure_depth = 0
        self._caption_depth = 0
        self._caption_parts: list[str] = []
        self._caption_line = 1

    def _line(self) -> int:
        line, _ = self.getpos()
        return line

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "figure":
            self._figure_depth += 1
            self.events.append({"type": "figure", "line": self._line()})
        elif tag == "img":
            self.events.append({"type": "image", "line": self._line(), "attrs": values})
        elif tag == "figcaption":
            self._caption_depth += 1
            self._caption_parts = []
            self._caption_line = self._line()
        elif tag == "svg":
            self.events.append({"type": "svg", "line": self._line(), "attrs": values})

    def handle_data(self, data: str) -> None:
        if self._caption_depth and data.strip():
            self._caption_parts.append(" ".join(data.split()))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "figure" and self._figure_depth:
            self._figure_depth -= 1
        elif tag == "figcaption" and self._caption_depth:
            self._caption_depth -= 1
            self.events.append({
                "type": "caption",
                "line": self._caption_line,
                "text": " ".join(self._caption_parts).strip(),
            })


@dataclass
class ParsedDocument:
    source: SourceInfo
    evidence: list[Evidence]
    document_title: str
    heading_tree: list[dict[str, Any]] = field(default_factory=list)


class MarkdownParser:
    """Parse Markdown without interpreting fenced code as real Markdown."""

    def __init__(
        self,
        *,
        include_code_blocks: bool = True,
        include_image_references: bool = True,
        include_chart_blocks: bool = True,
    ):
        self.include_code_blocks = include_code_blocks
        self.include_image_references = include_image_references
        self.include_chart_blocks = include_chart_blocks

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
        base_dir = Path(source_path).parent if source_path != "<memory>" else Path.cwd()
        definitions = self._scan_image_definitions(lines)
        evidence: list[Evidence] = []
        heading_tree: list[dict[str, Any]] = []
        heading_stack: list[tuple[int, str]] = []
        document_title = source_id
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
        ) -> Evidence:
            nonlocal block_number
            block_number += 1
            item = Evidence(
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
            )
            evidence.append(item)
            return item

        def append_asset_from_token(
            line_index: int, alt: str, path: str, title: str = ""
        ) -> Evidence | None:
            if not self.include_image_references:
                return None
            metadata = _asset_metadata(path, base_dir)
            metadata.update({"alt": alt, "title": title})
            is_svg = metadata.get("mime_type") == "image/svg+xml"
            block_type = "chart_svg" if is_svg else "image"
            label = "SVG图表" if is_svg else "图片"
            return append_block(
                line_index,
                line_index,
                block_type,
                f"![{alt}]({_safe_asset_display(path)})",
                f"[{label}：{alt or '待确认'}；来源：{_safe_asset_display(path)}]",
                metadata,
            )

        while index_value := 0:
            break

        index = 0
        while index < len(lines):
            line = lines[index]
            fence_match = _FENCE.match(line)
            if fence_match:
                marker = fence_match.group(1)[0] * 3
                language = fence_match.group(2).strip().lower()
                start = index
                index += 1
                while index < len(lines) and not _FENCE.match(lines[index]):
                    index += 1
                if index < len(lines):
                    closing = _FENCE.match(lines[index])
                    if closing and closing.group(1)[0] == marker[0]:
                        index += 1
                raw = "\n".join(lines[start:index])
                raw_code = "\n".join(lines[start + 1:index - 1]) if index > start + 1 else ""
                if language in {"mermaid", "mmd"} and self.include_chart_blocks:
                    metadata = _parse_mermaid(raw_code, language)
                    append_block(start, index - 1, "chart_code", raw, raw_code, metadata)
                elif language == "svg" and self.include_chart_blocks:
                    metadata = _parse_svg(raw_code)
                    svg_text = "；".join(filter(None, [metadata.get("title"), metadata.get("description"), *metadata.get("texts", [])]))
                    append_block(start, index - 1, "chart_svg", raw, svg_text, metadata)
                elif self.include_code_blocks:
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
                    found = next((child for child in parents[-1] if child["title"] == parent_title), None)
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
                headers = [strip_inline_markdown(part.strip()) for part in table_lines[0].strip().strip("|").split("|")]
                append_block(start, start, "table_header", table_lines[0], "；".join(headers), {"table_headers": headers})
                for row_index, row in enumerate(table_lines[1:], start=start + 1):
                    if re.match(r"^\s*\|?[\s:|-]+\|?\s*$", row):
                        continue
                    values = [strip_inline_markdown(part.strip()) for part in row.strip().strip("|").split("|")]
                    row_text = "；".join(f"{header or f'列{position}'}={value}" for position, (header, value) in enumerate(zip(headers, values), 1))
                    append_block(row_index, row_index, "table_row", row, f"表头：{'；'.join(headers)}。当前行：{row_text}", {"table_headers": headers, "row_values": values, "table_line_start": start + 1})
                continue

            if _IMAGE_DEFINITION.match(line):
                index += 1
                continue

            caption_match = _CAPTION.match(line)
            if caption_match and self.include_image_references:
                append_block(index, index, "image_caption", line, f"{caption_match.group(1)}：{caption_match.group(2)}")
                index += 1
                continue

            if _LIST.match(line):
                start = index
                while index < len(lines) and (_LIST.match(lines[index]) or (lines[index].startswith((" ", "\t")) and lines[index].strip() and not _HEADING.match(lines[index]))):
                    index += 1
                raw = "\n".join(lines[start:index]).rstrip()
                block = append_block(start, index - 1, "list", raw)
                self._append_inline_assets(block, raw, index - 1, append_asset_from_token)
                continue

            if line.startswith(">"):
                start = index
                while index < len(lines) and lines[index].startswith(">"):
                    index += 1
                raw = "\n".join(lines[start:index])
                block = append_block(start, index - 1, "blockquote", raw)
                self._append_inline_assets(block, raw, index - 1, append_asset_from_token)
                continue

            if line.lstrip().startswith(("<img", "<figure", "<svg")) or _HTML_LINE.match(line):
                start = index
                while index < len(lines) and lines[index].strip() and not (
                    _HEADING.match(lines[index]) or _FENCE.match(lines[index]) or _TABLE.match(lines[index]) or _LIST.match(lines[index])
                ):
                    index += 1
                raw = "\n".join(lines[start:index]).rstrip()
                self._parse_html_block(raw, start, index - 1, base_dir, append_block)
                continue

            if not line.strip():
                index += 1
                continue

            start = index
            while index < len(lines) and lines[index].strip() and not (
                _HEADING.match(lines[index]) or _FENCE.match(lines[index]) or _TABLE.match(lines[index])
                or _LIST.match(lines[index]) or lines[index].startswith(">") or _HTML_LINE.match(lines[index])
            ):
                index += 1
            raw = "\n".join(lines[start:index])
            inline_assets = self._inline_assets(raw, definitions)
            without_assets = _IMAGE_REFERENCE.sub("", _IMAGE_INLINE.sub("", raw)).strip()
            if inline_assets and not without_assets:
                for item in inline_assets:
                    append_asset_from_token(start, item[0], item[1], item[2])
            else:
                block = append_block(start, index - 1, "paragraph", raw)
                self._append_inline_assets(block, raw, index - 1, append_asset_from_token, definitions)

        self._resolve_reference_images(evidence, definitions, append_asset_from_token)
        self._associate_captions(evidence)
        if not document_title or document_title == source_id:
            for item in evidence:
                if item.block_type == "heading":
                    document_title = item.text
                    break
        source = source_info_from_text(text, source_id, source_path, document_title)
        return ParsedDocument(source=source, evidence=evidence, document_title=document_title, heading_tree=heading_tree)

    @staticmethod
    def _scan_image_definitions(lines: list[str]) -> dict[str, tuple[str, str]]:
        result: dict[str, tuple[str, str]] = {}
        for line in lines:
            match = _IMAGE_DEFINITION.match(line)
            if match:
                result[match.group(1).lower()] = (match.group(2), match.group(3) or "")
        return result

    @staticmethod
    def _inline_assets(raw: str, definitions: dict[str, tuple[str, str]]) -> list[tuple[str, str, str]]:
        assets: list[tuple[str, str, str]] = []
        for match in _IMAGE_INLINE.finditer(raw):
            assets.append((match.group(1), match.group(2), match.group(3) or ""))
        for match in _IMAGE_REFERENCE.finditer(raw):
            definition = definitions.get(match.group(2).lower())
            if definition:
                assets.append((match.group(1), definition[0], definition[1]))
        return assets

    def _append_inline_assets(
        self,
        block: Evidence,
        raw: str,
        end_index: int,
        append_asset,
        definitions: dict[str, tuple[str, str]] | None = None,
    ) -> None:
        definitions = definitions or {}
        for alt, path, title in self._inline_assets(raw, definitions):
            asset = append_asset(end_index, alt, path, title)
            if asset:
                block.metadata.setdefault("asset_evidence_ids", []).append(asset.evidence_id)
                asset.metadata["container_evidence_id"] = block.evidence_id

    def _resolve_reference_images(self, evidence: list[Evidence], definitions: dict[str, tuple[str, str]], append_asset) -> None:
        # Reference-style images already carry definition paths; no extra evidence is needed here.
        return

    def _parse_html_block(self, raw: str, start: int, end: int, base_dir: Path, append_block) -> None:
        lines = raw.splitlines()
        parser = _HTMLAssetParser(start, lines)
        try:
            parser.feed(raw)
            parser.close()
        except Exception:
            pass
        is_figure = raw.lstrip().lower().startswith("<figure")
        generic = append_block(start, end, "figure" if is_figure else "html", raw)
        child_ids: list[str] = []
        for event in sorted(parser.events, key=lambda item: item["line"]):
            absolute_line = start + event["line"] - 1
            if event["type"] == "image":
                attrs = event["attrs"]
                src = attrs.get("src", "")
                metadata = _asset_metadata(src, base_dir) if src else {"asset_type": "image", "source_type": "unknown", "path": "", "exists": False}
                metadata.update({
                    "alt": attrs.get("alt", ""),
                    "title": attrs.get("title", ""),
                    "width": attrs.get("width", ""),
                    "height": attrs.get("height", ""),
                    "html_tag": "img",
                    "missing_src": not bool(src),
                })
                block_type = "chart_svg" if metadata.get("mime_type") == "image/svg+xml" else "image"
                item = append_block(absolute_line, absolute_line, block_type, lines[event["line"] - 1], f"[HTML图片：{metadata['alt'] or '待确认'}；来源：{_safe_asset_display(src) or '缺失'}]", metadata)
                item.metadata["container_evidence_id"] = generic.evidence_id
                child_ids.append(item.evidence_id)
            elif event["type"] == "svg":
                metadata = _parse_svg(raw)
                metadata.update({"html_tag": "svg", "asset_type": "chart", "source_type": "inline"})
                item = append_block(absolute_line, end, "chart_svg", raw, "；".join(filter(None, [metadata.get("title"), metadata.get("description"), *metadata.get("texts", [])])), metadata)
                item.metadata["container_evidence_id"] = generic.evidence_id
                child_ids.append(item.evidence_id)
            elif event["type"] == "caption":
                item = append_block(absolute_line, absolute_line, "image_caption", lines[event["line"] - 1], event["text"])
                item.metadata["container_evidence_id"] = generic.evidence_id
                child_ids.append(item.evidence_id)
        if child_ids:
            generic.metadata["asset_evidence_ids"] = child_ids

    @staticmethod
    def _associate_captions(evidence: list[Evidence]) -> None:
        captions = [item for item in evidence if item.block_type == "image_caption"]
        assets = [item for item in evidence if item.block_type in _ASSET_BLOCK_TYPES]
        for caption in captions:
            candidates = [asset for asset in assets if abs(asset.line_start - caption.line_start) <= 3 and asset.evidence_id != caption.evidence_id]
            if not candidates:
                continue
            asset = min(candidates, key=lambda item: (abs(item.line_start - caption.line_start), 1 if item.line_start >= caption.line_start else 0))
            asset.metadata["caption_evidence_id"] = caption.evidence_id
            caption.metadata["asset_evidence_id"] = asset.evidence_id
            if asset.metadata.get("container_evidence_id"):
                container = next((item for item in evidence if item.evidence_id == asset.metadata["container_evidence_id"]), None)
                if container:
                    container.metadata["caption_evidence_id"] = caption.evidence_id
