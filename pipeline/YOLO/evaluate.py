from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from evaluation.results import new_result, save_result
from evaluation.timing import measure_inference, save_timing_result


def evaluate_yolo(
    weights_path: str | Path,
    dataset_path: str | Path,
    model_name: str,
    output_path: str | Path,
) -> Path:
    """Evaluate one Ultralytics model and save the common JSON result."""
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise ImportError("Install pipeline/YOLO/requirements.txt in the YOLO environment.") from error

    model = YOLO(str(weights_path))
    validation = model.val(
        data=str(dataset_path),
        split="test",
        save_json=True,
        plots=False,
        verbose=True,
    )
    result = new_result(model_name, weights_path, dataset_path)
    result["metrics"] = {
        "precision": _json_value(validation.box.mp),
        "recall": _json_value(validation.box.mr),
        "f1": _json_value(validation.box.f1),
        "map50": _json_value(validation.box.map50),
        "map50_95": _json_value(validation.box.map),
    }
    curves = getattr(validation, "curves_results", [])
    if curves:
        result["curves"]["precision_recall"] = {
            "recall": _json_list(curves[0][0]),
            "precision": _json_list(curves[0][1][0]),
        }
    confusion = getattr(getattr(validation, "confusion_matrix", None), "matrix", None)
    if confusion is not None:
        result["confusion_matrix"] = {"matrix": _json_list(confusion)}
    return save_result(result, output_path)


def measure_yolo_time(
    weights_path: str | Path,
    image_dir: str | Path,
    output_path: str | Path,
    model_name: str,
    limit: int | None = 100,
    warmup: int = 10,
) -> Path:
    """Measure per-image inference time and save it as a timing JSON."""
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise ImportError("Install pipeline/YOLO/requirements.txt in the YOLO environment.") from error
    model = YOLO(str(weights_path))
    images = sorted(
        path for path in Path(image_dir).iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    )
    if limit is not None:
        images = images[:limit]
    synchronize = None
    try:
        import torch
        synchronize = torch.cuda.synchronize if torch.cuda.is_available() else None
    except ImportError:
        pass
    timing = measure_inference(lambda path: model(str(path), verbose=False), images, warmup, synchronize)
    return save_timing_result(model_name, timing, output_path)


def test_yolov11(weights_path: str | Path, dataset_path: str | Path, output_path: str | Path) -> Path:
    return evaluate_yolo(weights_path, dataset_path, "YOLOv11n", output_path)


def test_yolov12(weights_path: str | Path, dataset_path: str | Path, output_path: str | Path) -> Path:
    return evaluate_yolo(weights_path, dataset_path, "YOLOv12n", output_path)


def _json_value(value: Any) -> float:
    return float(value.item() if hasattr(value, "item") else value)


def _json_list(value: Any) -> list:
    values = value.tolist() if hasattr(value, "tolist") else list(value)
    return _json_compatible(values)


def _json_compatible(value: Any) -> Any:
    if isinstance(value, list):
        return [_json_compatible(item) for item in value]
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate YOLOv11n or YOLOv12n.")
    parser.add_argument("--model", choices=("yolov11", "yolov12"), required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    function = test_yolov11 if args.model == "yolov11" else test_yolov12
    function(args.weights, args.dataset, args.output)


if __name__ == "__main__":
    main()
