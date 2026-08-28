"""Third-party service integration example."""
from pathlib import Path

from semantic_reconstruction import (
    DocumentParseError,
    DocumentTooLargeError,
    ReconstructionConfig,
    SemanticReconstructionError,
    SemanticReconstructor,
)


def run(path: str) -> dict:
    try:
        # Start fully offline. Switch mode to "hybrid" or "llm" only when needed.
        sdk = SemanticReconstructor(ReconstructionConfig(mode="rule"))
        result = sdk.reconstruct_markdown(Path(path))
        result.write_json("output/results.json")
        result.write_report("output/report.md")
        return result.summary
    except DocumentTooLargeError as exc:
        return {"error": "document_too_large", "message": str(exc)}
    except DocumentParseError as exc:
        return {"error": "document_parse_error", "message": str(exc)}
    except SemanticReconstructionError as exc:
        return {"error": "semantic_reconstruction_error", "message": str(exc)}


if __name__ == "__main__":
    print(run("docs/example.md"))
