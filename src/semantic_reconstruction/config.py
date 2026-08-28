"""Public configuration object for the semantic-reconstruction SDK."""
from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Literal

from .exceptions import InvalidConfigurationError

ReconstructionMode = Literal["rule", "hybrid", "llm"]
_VALID_MODES = {"rule", "hybrid", "llm"}


@dataclass
class ReconstructionConfig:
    """Configuration for deterministic and optional LLM-backed reconstruction.

    The SDK never reads ``.env`` implicitly. An API key is accepted only from
    an explicit argument or from the current process environment.
    """

    mode: ReconstructionMode = "rule"
    api_key: str | None = None
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-flash"
    reasoning_effort: str = "high"
    enable_thinking: bool = True
    timeout_seconds: float = 120.0
    max_retries: int = 2
    max_document_chars: int = 2_000_000
    include_code_blocks: bool = True
    keep_raw_evidence: bool = True
    llm_batch_size: int = 25
    extra_headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.mode not in _VALID_MODES:
            raise InvalidConfigurationError(
                f"mode 必须是 rule、hybrid 或 llm，当前为 {self.mode!r}"
            )
        if self.mode in {"hybrid", "llm"}:
            self.api_key = self.api_key or os.environ.get("DEEPSEEK_API_KEY")
        if self.timeout_seconds <= 0:
            raise InvalidConfigurationError("timeout_seconds 必须大于 0")
        if not 0 <= self.max_retries <= 5:
            raise InvalidConfigurationError("max_retries 必须在 0 到 5 之间")
        if self.max_document_chars <= 0:
            raise InvalidConfigurationError("max_document_chars 必须大于 0")
        if not 1 <= self.llm_batch_size <= 25:
            raise InvalidConfigurationError("llm_batch_size 必须在 1 到 25 之间")

    def __repr__(self) -> str:
        return (
            "ReconstructionConfig("
            f"mode={self.mode!r}, api_key=<redacted>, base_url={self.base_url!r}, "
            f"model={self.model!r}, reasoning_effort={self.reasoning_effort!r}, "
            f"enable_thinking={self.enable_thinking!r}, timeout_seconds={self.timeout_seconds!r}, "
            f"max_retries={self.max_retries!r}, max_document_chars={self.max_document_chars!r}, "
            f"include_code_blocks={self.include_code_blocks!r}, keep_raw_evidence={self.keep_raw_evidence!r}, "
            f"llm_batch_size={self.llm_batch_size!r}, extra_headers={list(self.extra_headers)!r})"
        )

    def require_llm(self, *, has_custom_client: bool = False) -> None:
        if self.mode not in {"hybrid", "llm"}:
            return
        if not self.base_url or not self.model:
            raise InvalidConfigurationError("hybrid/llm 模式必须配置 base_url 和 model")
        if not has_custom_client and not self.api_key:
            raise InvalidConfigurationError(
                "hybrid/llm 模式缺少 API key；请显式传入 api_key 或设置 DEEPSEEK_API_KEY"
            )


