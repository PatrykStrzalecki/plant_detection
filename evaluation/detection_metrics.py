from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import numpy as np


def _iou(first: list[float], second: list[float]) -> float:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_first = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
    area_second = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
    union = area_first + area_second - intersection
    return intersection / union if union else 0.0


def detection_summary(
    samples: Iterable[dict[str, Any]],
    class_names: list[str],
    iou_thresholds: tuple[float, ...] = (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95),
) -> dict[str, Any]:
    """Calculate threshold-independent detection metrics from JSON-friendly samples.

    A sample contains ``ground_truth`` and ``predictions`` lists. Boxes use
    ``[x1, y1, x2, y2]`` and predictions additionally contain ``score``.
    """
    samples = list(samples)
    per_iou: dict[float, dict[str, float]] = {}
    best_curve: dict[str, list[float]] = {"precision": [], "recall": []}

    for iou_threshold in iou_thresholds:
        true_positive = false_positive = false_negative = 0
        by_class: dict[int, list[tuple[float, int]]] = defaultdict(list)
        for sample in samples:
            truths = sample.get("ground_truth", [])
            predictions = sorted(
                sample.get("predictions", []),
                key=lambda item: float(item.get("score", 0.0)),
                reverse=True,
            )
            used: set[int] = set()
            for prediction in predictions:
                matches = [
                    (index, truth)
                    for index, truth in enumerate(truths)
                    if index not in used
                    and int(truth["class_id"]) == int(prediction["class_id"])
                    and _iou(truth["box"], prediction["box"]) >= iou_threshold
                ]
                if matches:
                    index, _ = max(matches, key=lambda item: _iou(item[1]["box"], prediction["box"]))
                    used.add(index)
                    true_positive += 1
                    by_class[int(prediction["class_id"])].append(
                        (float(prediction.get("score", 0.0)), 1)
                    )
                else:
                    false_positive += 1
                    by_class[int(prediction["class_id"])].append(
                        (float(prediction.get("score", 0.0)), 0)
                    )
            false_negative += len(truths) - len(used)

        precision = true_positive / max(true_positive + false_positive, 1)
        recall = true_positive / max(true_positive + false_negative, 1)
        curve = _curve_from_pairs(
            (pair for values in by_class.values() for pair in values),
            sum(len(sample.get("ground_truth", [])) for sample in samples),
        )
        per_iou[iou_threshold] = {
            "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / max(precision + recall, 1e-12),
            "average_precision": _average_precision(curve["recall"], curve["precision"]),
        }
        if iou_threshold == 0.5:
            best_curve = curve

    map50 = per_iou[0.5]["average_precision"]
    map50_95 = float(np.mean([values["average_precision"] for values in per_iou.values()]))
    return {
        "metrics": {
            "precision": per_iou[0.5]["precision"],
            "recall": per_iou[0.5]["recall"],
            "f1": per_iou[0.5]["f1"],
            "map50": map50,
            "map50_95": map50_95,
        },
        "curves": {"precision_recall": best_curve},
        "iou_metrics": {str(key): value for key, value in per_iou.items()},
    }


def _curve_from_pairs(pairs: Iterable[tuple[float, int]], total_truths: int) -> dict[str, list[float]]:
    ordered = sorted(pairs, key=lambda pair: pair[0], reverse=True)
    if not ordered:
        return {"recall": [], "precision": []}
    cumulative_tp = np.cumsum([pair[1] for pair in ordered])
    cumulative_fp = np.cumsum([1 - pair[1] for pair in ordered])
    return {
        "recall": (cumulative_tp / max(total_truths, 1)).tolist(),
        "precision": (cumulative_tp / np.maximum(cumulative_tp + cumulative_fp, 1)).tolist(),
    }


def _average_precision(recall: list[float], precision: list[float]) -> float:
    if not recall:
        return 0.0
    recall_array = np.asarray([0.0, *recall, 1.0])
    precision_array = np.asarray([0.0, *precision, 0.0])
    for index in range(len(precision_array) - 2, -1, -1):
        precision_array[index] = max(precision_array[index], precision_array[index + 1])
    changes = np.where(recall_array[1:] != recall_array[:-1])[0]
    return float(np.sum((recall_array[changes + 1] - recall_array[changes]) * precision_array[changes + 1]))
