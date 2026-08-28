"""Optional OpenAI-compatible multimodal image understanding."""
from __future__ import annotations

import base64
import binascii
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Protocol

from .config import ReconstructionConfig
from .exceptions import LLMProviderError

SUPPORTED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
_DATA_URI = re.compile(r"^data:([^;,]+);base64,(.*)$", re.DOTALL)


@dataclass(frozen=True)
class ImageRequest:
    path: str
    mime_type: str
    data: bytes = field(repr=False, compare=False)
    alt: str = ""
    title: str = ""
    caption: str = ""
    heading_path: tuple[str, ...] = ()
    evidence_id: str = ""

    @property
    def data_uri(self) -> str:
        return "data:" + self.mime_type + ";base64," + base64.b64encode(self.data).decode("ascii")


@dataclass(frozen=True)
class ImageDescription:
    description: str
    visible_text: str
    chart_type: str
    objects_or_nodes: list[str]
    relationships: list[str]
    colors_or_legends: list[str]
    limitations: list[str]
    confidence: float
    model: str = ""
    usage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VisionClientProtocol(Protocol):
    def describe_image(self, request: ImageRequest) -> ImageDescription: ...


def decode_data_uri(value: str) -> tuple[str, bytes] | None:
    match = _DATA_URI.match(value.strip())
    if not match:
        return None
    mime, encoded = match.group(1), match.group(2)
    try:
        return mime, base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return None


def validate_description(value: ImageDescription, *, min_confidence: float = 0.0) -> list[str]:
    errors: list[str] = []
    required_text = (value.description, value.visible_text, value.chart_type)
    if not any(item.strip() for item in required_text):
        errors.append("视觉描述缺少 description、visible_text 或 chart_type。")
    if not isinstance(value.confidence, (int, float)) or not 0.0 <= float(value.confidence) <= 1.0:
        errors.append("视觉描述 confidence 必须位于 0 到 1。")
    elif value.confidence < min_confidence:
        errors.append(f"视觉描述置信度过低：{value.confidence} < {min_confidence}")
    if any(term in value.description.lower() for term in ("审批通过", "可以审批", "必须由")) and "可见文字" not in value.description:
        errors.append("视觉描述疑似新增业务规则。")
    if any("冲突" in item or "contradict" in item.lower() for item in value.limitations):
        errors.append("视觉描述提示与正文证据存在冲突。")
    return errors


def description_from_mapping(value: dict[str, Any], model: str = "") -> ImageDescription:
    return ImageDescription(
        description=str(value.get("description", "")),
        visible_text=str(value.get("visible_text", "")),
        chart_type=str(value.get("chart_type", "")),
        objects_or_nodes=[str(item) for item in value.get("objects_or_nodes", [])],
        relationships=[str(item) for item in value.get("relationships", [])],
        colors_or_legends=[str(item) for item in value.get("colors_or_legends", [])],
        limitations=[str(item) for item in value.get("limitations", [])],
        confidence=float(value.get("confidence", 0.0)),
        model=model,
        usage=dict(value.get("usage", {})),
    )


class OpenAICompatibleVisionClient:
    """Built-in multimodal client for OpenAI-compatible image_url APIs."""

    def __init__(self, config: ReconstructionConfig, client: Any | None = None):
        self.config = config
        self._client = client

    def __repr__(self) -> str:
        return (
            "OpenAICompatibleVisionClient("
            f"model={self.config.vision_model!r}, base_url={self.config.vision_base_url!r}, "
            "api_key=<redacted>)"
        )

    def _create_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMProviderError("openai 依赖未安装") from exc
        return OpenAI(
            api_key=self.config.vision_api_key,
            base_url=self.config.vision_base_url,
            timeout=self.config.vision_timeout_seconds,
        )

    def describe_image(self, request: ImageRequest) -> ImageDescription:
        if request.mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
            raise LLMProviderError(f"不支持的图片 MIME 类型：{request.mime_type}")
        client = self._create_client()
        context = {
            "alt": request.alt,
            "title": request.title,
            "caption": request.caption,
            "heading_path": list(request.heading_path),
        }
        instruction = (
            "你是企业知识库图片证据描述器。只描述图片可见内容，不要推断业务规则、权限、额度、"
            "例外或生效条件；无法确认的字段写“待确认”。返回 JSON，字段包括 description、"
            "visible_text、chart_type、objects_or_nodes、relationships、colors_or_legends、"
            "limitations、confidence。confidence 位于 0 到 1。"
        )
        messages = [
            {
                "role": "system",
                "content": "你是严谨的图片证据描述器，只输出 JSON。",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction + "\n上下文：" + json.dumps(context, ensure_ascii=False)},
                    {"type": "image_url", "image_url": {"url": request.data_uri}},
                ],
            },
        ]
        last_error: Exception | None = None
        for attempt in range(1, self.config.vision_max_retries + 2):
            try:
                response = client.chat.completions.create(
                    model=self.config.vision_model,
                    messages=messages,
                    stream=False,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or ""
                parsed = json.loads(content)
                if not isinstance(parsed, dict):
                    raise ValueError("视觉模型 JSON 顶层必须是对象")
                usage = getattr(response, "usage", None)
                usage_dict = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                }
                parsed["usage"] = usage_dict
                return description_from_mapping(parsed, model=str(self.config.vision_model))
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()
                retryable = any(term in message for term in ("timeout", "connection", "rate limit", "temporarily unavailable")) or getattr(exc, "status_code", None) in {408, 409, 429, *range(500, 600)}
                if not retryable or attempt > self.config.vision_max_retries:
                    raise LLMProviderError(f"视觉模型调用失败：{exc}") from exc
        raise LLMProviderError(f"视觉模型调用失败：{last_error}")
