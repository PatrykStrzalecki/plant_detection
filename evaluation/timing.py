from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np


def measure_inference(
    predict: Callable[[Any], Any],
    inputs: Iterable[Any],
    warmup: int = 10,
    synchronize: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Measure a callable and return JSON-serializable timing statistics."""
    values = list(inputs)
    if not values:
        raise ValueError("At least one input is required for timing.")
    for item in values[:warmup]:
        predict(item)
    if synchronize:
        synchronize()
    samples = []
    for item in values:
        if synchronize:
            synchronize()
        start = time.perf_counter()
        predict(item)
        if synchronize:
            synchronize()
        samples.append((time.perf_counter() - start) * 1000)
    array = np.asarray(samples, dtype=float)
    return {
        "mean_ms": float(array.mean()),
        "std_ms": float(array.std()),
        "median_ms": float(np.median(array)),
        "min_ms": float(array.min()),
        "max_ms": float(array.max()),
        "fps": float(1000 / array.mean()),
        "samples_ms": array.tolist(),
        "sample_count": len(samples),
        "warmup_count": min(warmup, len(values)),
    }


def save_timing_result(model: str, timing: dict[str, Any], output_path: str | Path) -> Path:
    """Save timing data using the same top-level envelope as detection results."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": "1.0", "model": model, "timing": timing}, indent=2),
        encoding="utf-8",
    )
    return path
