from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"


def new_result(
    model: str,
    weights: str | Path,
    dataset: str | Path,
) -> dict[str, Any]:
    """Create the common result envelope used by every model pipeline."""
    return {
        "schema_version": SCHEMA_VERSION,
        "model": model,
        "weights": str(weights),
        "dataset": str(dataset),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {},
        "curves": {},
        "confusion_matrix": {},
        "timing": {},
    }


def save_result(result: dict[str, Any], output_path: str | Path) -> Path:
    """Write a result JSON and create its parent directory when necessary."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    return path


def load_results(paths: str | Path | list[str | Path]) -> dict[str, dict[str, Any]]:
    """Load one result file or a directory of result JSON files by model name."""
    candidates = [paths] if isinstance(paths, (str, Path)) else paths
    files: list[Path] = []
    for candidate in candidates:
        path = Path(candidate)
        files.extend(sorted(path.glob("*.json")) if path.is_dir() else [path])
    if not files:
        raise FileNotFoundError("No result JSON files were found.")

    loaded: dict[str, dict[str, Any]] = {}
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "model" not in data:
            raise ValueError(f"{path} is not a valid evaluation result.")
        loaded[str(data["model"])] = data
    return loaded
