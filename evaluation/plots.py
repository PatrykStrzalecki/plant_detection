from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from .results import load_results


DEFAULT_COLORS = ["#5B9BD5", "#ED7D31", "#70AD47", "#FF6B6B"]


def plot_detection_comparison(
    results: str | Path | list[str | Path],
    output_path: str | Path,
) -> Path:
    """Plot mAP, precision, recall and F1 for all result JSON files."""
    loaded = load_results(results)
    names = list(loaded)
    metrics = ["map50", "map50_95", "precision", "recall", "f1"]
    values = [[float(loaded[name].get("metrics", {}).get(metric, 0.0)) for name in names] for metric in metrics]
    figure, axes = plt.subplots(1, len(metrics), figsize=(18, 5))
    for axis, metric, series in zip(axes, metrics, values):
        bars = axis.bar(names, series, color=DEFAULT_COLORS[: len(names)])
        axis.set_title(metric.replace("_", " ").upper())
        axis.set_ylim(0, 1)
        axis.grid(axis="y", alpha=0.3)
        axis.tick_params(axis="x", rotation=35)
        for bar, value in zip(bars, series):
            axis.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.3f}", ha="center")
    figure.tight_layout()
    return _save_figure(figure, output_path)


def plot_precision_recall(
    results: str | Path | list[str | Path],
    output_path: str | Path,
) -> Path:
    """Plot the precision-recall curves stored in the common JSON format."""
    loaded = load_results(results)
    figure, axis = plt.subplots(figsize=(10, 7))
    for index, (name, data) in enumerate(loaded.items()):
        curve = data.get("curves", {}).get("precision_recall", {})
        recall = curve.get("recall", [])
        precision = curve.get("precision", [])
        if recall and precision:
            axis.plot(recall, precision, label=name, color=DEFAULT_COLORS[index % len(DEFAULT_COLORS)])
    axis.set(title="Precision-Recall comparison", xlabel="Recall", ylabel="Precision", xlim=(0, 1), ylim=(0, 1))
    axis.grid(alpha=0.3)
    axis.legend()
    return _save_figure(figure, output_path)


def plot_timing_comparison(
    results: str | Path | list[str | Path],
    output_path: str | Path,
) -> Path:
    """Plot mean/std, FPS, distribution and min/max timing from JSON files."""
    loaded = {
        name: data
        for name, data in load_results(results).items()
        if data.get("timing", {}).get("samples_ms")
    }
    if not loaded:
        raise ValueError("The supplied JSON files do not contain timing.samples_ms.")
    names = list(loaded)
    timing = [data.get("timing", {}) for data in loaded.values()]
    figure, axes = plt.subplots(2, 2, figsize=(16, 11))
    means = [float(item.get("mean_ms", 0.0)) for item in timing]
    stds = [float(item.get("std_ms", 0.0)) for item in timing]
    axes[0, 0].bar(names, means, yerr=stds, capsize=5, color=DEFAULT_COLORS[: len(names)])
    axes[0, 0].set(title="Mean inference time", ylabel="Milliseconds")
    axes[0, 1].bar(names, [1000 / mean if mean else 0 for mean in means], color=DEFAULT_COLORS[: len(names)])
    axes[0, 1].set(title="Throughput", ylabel="FPS")
    samples = [item.get("samples_ms", []) for item in timing]
    axes[1, 0].boxplot(samples, labels=names)
    axes[1, 0].set(title="Inference-time distribution", ylabel="Milliseconds")
    positions = np.arange(len(names))
    width = 0.35
    axes[1, 1].bar(positions - width / 2, [item.get("min_ms", 0) for item in timing], width, label="min")
    axes[1, 1].bar(positions + width / 2, [item.get("max_ms", 0) for item in timing], width, label="max")
    axes[1, 1].set(title="Minimum and maximum", ylabel="Milliseconds", xticks=positions, xticklabels=names)
    axes[1, 1].legend()
    for axis in axes.flat:
        axis.grid(axis="y", alpha=0.3)
    figure.tight_layout()
    return _save_figure(figure, output_path)


def _save_figure(figure: Any, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(figure)
    return path
