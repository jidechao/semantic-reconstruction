# Changelog

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
