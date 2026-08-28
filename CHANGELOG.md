# Changelog

## 1.2.0 - 2026-08-28

### Added

- Markdown angle-bracket image targets and `location_kind` asset metadata.
- Relative-path, Windows/POSIX absolute-path, `file:///`, data-URI, and direct HTTP(S) URL image handling.
- `allow_absolute_image_paths` configuration and `--absolute-image-paths / --no-absolute-image-paths` CLI controls.
- Standalone image-evidence knowledge units for every parsed image.
- Always-on diagnostics for missing images, missing `src`, unsupported MIME, excessive size, and path escapes.
- Vision requests now pass remote URLs directly to OpenAI-compatible multimodal providers without downloading.
- Markdown report rendering for image sources, visual descriptions, confidence, limitations, and token usage.

### Changed

- Package version upgraded to 1.2.0.
- Output schema version upgraded to 1.2.
- Local absolute paths and `file:///` images are allowed by default; setting `allow_absolute_image_paths=False` restores the document-root boundary.

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
