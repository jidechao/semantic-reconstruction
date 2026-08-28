"""OpenAI-compatible DeepSeek client with structured transient retries."""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .config import ReconstructionConfig
from .exceptions import LLMProviderError


@dataclass(frozen=True)
class LLMUsage:
    model: str
    mode: str
    batch_size: int
    elapsed_ms: int
    attempt: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LLMResult:
    ok: bool
    content: str = ""
    usage: LLMUsage | None = None
    error: str = ""


class ChatCompletionsProtocol(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class ChatNamespaceProtocol(Protocol):
    completions: ChatCompletionsProtocol


class ClientProtocol(Protocol):
    chat: ChatNamespaceProtocol


def _retryable(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None)
    if status in {408, 409, 429} or (isinstance(status, int) and status >= 500):
        return True
    message = str(exc).lower()
    return any(term in message for term in ("timeout", "timed out", "connection", "temporarily unavailable", "rate limit"))


class DeepSeekClient:
    """Built-in DeepSeek client; callers may inject an equivalent client."""

    def __init__(self, config: ReconstructionConfig, client: ClientProtocol | None = None):
        self.config = config
        self._client = client

    def chat(self, messages: list[dict[str, str]], *, json_mode: bool = True) -> LLMResult:
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise LLMProviderError("openai 依赖未安装") from exc
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
                default_headers=self.config.extra_headers or None,
            )

        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
        }
        if self.config.reasoning_effort:
            kwargs["reasoning_effort"] = self.config.reasoning_effort
        if self.config.enable_thinking:
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 2):
            started = time.perf_counter()
            try:
                response = self._client.chat.completions.create(**kwargs)
                choice = response.choices[0] if getattr(response, "choices", None) else None
                content = getattr(getattr(choice, "message", None), "content", "") or ""
                raw_usage = getattr(response, "usage", None)
                usage = LLMUsage(
                    model=self.config.model,
                    mode="ok",
                    batch_size=0,
                    elapsed_ms=int((time.perf_counter() - started) * 1000),
                    attempt=attempt,
                    prompt_tokens=getattr(raw_usage, "prompt_tokens", None),
                    completion_tokens=getattr(raw_usage, "completion_tokens", None),
                    total_tokens=getattr(raw_usage, "total_tokens", None),
                )
                if not content.strip():
                    return LLMResult(False, usage=usage, error="模型返回内容为空")
                return LLMResult(True, content=content, usage=usage)
            except Exception as exc:
                last_error = exc
                usage = LLMUsage(
                    model=self.config.model,
                    mode="error",
                    batch_size=0,
                    elapsed_ms=int((time.perf_counter() - started) * 1000),
                    attempt=attempt,
                )
                if not _retryable(exc) or attempt > self.config.max_retries:
                    return LLMResult(False, usage=usage, error=str(exc))
                time.sleep(min(2.0, 0.25 * (2 ** (attempt - 1))))
        raise LLMProviderError(f"LLM 调用失败：{last_error}")


def parse_json_content(content: str) -> tuple[dict[str, Any] | None, str]:
    text = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None, "模型输出不是合法 JSON。"
        try:
            value = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            return None, f"模型输出 JSON 解析失败：{exc}"
    if not isinstance(value, dict):
        return None, "模型 JSON 顶层必须是对象。"
    return value, ""
