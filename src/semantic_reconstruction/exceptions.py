"""Stable exception hierarchy for semantic-reconstruction SDK."""


class SemanticReconstructionError(Exception):
    """Base exception for all SDK errors."""


class InvalidConfigurationError(SemanticReconstructionError):
    """Raised when runtime configuration is invalid."""


class DocumentParseError(SemanticReconstructionError):
    """Raised when a Markdown document cannot be parsed."""


class DocumentTooLargeError(SemanticReconstructionError):
    """Raised when input exceeds the configured size limit."""


class LLMProviderError(SemanticReconstructionError):
    """Raised when an LLM provider fails after configured retries."""


class OutputValidationError(SemanticReconstructionError):
    """Raised when result serialization or output writing fails."""
