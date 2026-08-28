# Contributing

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Before submitting

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m build --outdir dist-ci
```

Requirements:

- All tests pass.
- Do not commit `.env`, API keys, generated output, virtual environments, or build artifacts.
- Keep public API changes backward-compatible within a minor version.
- Add tests for parser, validation, SDK, CLI, and LLM safety changes.
- LLM tests must use mocks and must not call external APIs.

## Commit style

Use concise imperative commit messages, for example:

```text
Add markdown table context binding
Fix LLM output validation for unsupported roles
