# Changelog

## 1.1.0 - 2026-08-28

### Added

- Markdown image and reference-definition parsing.
- HTML `<img>`, `<figure>`, and `<figcaption>` evidence.
- Mermaid and SVG chart evidence with deterministic text extraction.
- Image/chart caption and reference binding.
- Optional OpenAI-compatible multimodal image understanding.
- Local-file and data-URI security boundaries for vision requests.
- Vision metadata, usage reporting, diagnostics, and safe fallback.
- CLI options for image/chart handling and vision size limits.

### Changed

- Package version upgraded to 1.1.0.
- Output schema version upgraded to 1.1.
- Mermaid blocks are now `chart_code` instead of generic `code_example`.
- Data URI payloads are redacted from serialized output.


## 1.0.0 - 2026-08-28

### Added

- Stable Python SDK API: `SemanticReconstructor`, `ReconstructionConfig`, `ReconstructionResult`.
- UTF-8 Markdown parser with exact evidence line mappings.
- Deterministic offline `rule` reconstruction mode.
- Optional DeepSeek-backed `hybrid` and `llm` modes with strict evidence validation.
- Twelve-question acceptance validation and auditable change records.
- Production CLI: `semantic-reconstruction reconstruct`.
- Chinese integration documentation and third-party example.
- Apache-2.0 license.
- GitHub Actions CI for Python 3.11 and 3.12 on Linux and Windows.

### Security

- SDK API does not implicitly read `.env`.
- API keys are excluded from logs and package artifacts.
- Missing external evidence blocks knowledge units instead of allowing model invention.
