from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "markdown"
REAL_MARKDOWN_FILES = [
    FIXTURE_ROOT / "README_CN.md",
    FIXTURE_ROOT / "SUPERPOWERS-完整使用指南.md",
    FIXTURE_ROOT / "taste-skill-使用指南.md",
]
