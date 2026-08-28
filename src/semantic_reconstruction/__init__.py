"""Semantic Reconstruction production Python SDK."""

from .config import ImageUnderstandingMode, ReconstructionConfig, ReconstructionMode
from .exceptions import (
    DocumentParseError,
    DocumentTooLargeError,
    InvalidConfigurationError,
    LLMProviderError,
    OutputValidationError,
    SemanticReconstructionError,
)
from .models import Diagnostic, Evidence, KnowledgeUnit, ReconstructionResult, SourceInfo
from .sdk import SemanticReconstructor
from .vision import ImageDescription, ImageRequest, OpenAICompatibleVisionClient, VisionClientProtocol

__version__ = "1.2.0"
__all__ = [
    "SemanticReconstructor",
    "ReconstructionConfig",
    "ReconstructionMode",
    "ImageUnderstandingMode",
    "ReconstructionResult",
    "KnowledgeUnit",
    "Evidence",
    "SourceInfo",
    "Diagnostic",
    "ImageDescription",
    "ImageRequest",
    "OpenAICompatibleVisionClient",
    "VisionClientProtocol",
    "SemanticReconstructionError",
    "InvalidConfigurationError",
    "DocumentParseError",
    "DocumentTooLargeError",
    "LLMProviderError",
    "OutputValidationError",
]
