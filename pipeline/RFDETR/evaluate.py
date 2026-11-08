from __future__ import annotations

import argparse
from pathlib import Path

from evaluation.dataset import load_coco_samples
from evaluation.detection_metrics import detection_summary
from evaluation.results import new_result, save_result
from evaluation.timing import measure_inference, save_timing_result


def test_rfdetr(
    weights_path: str | Path,
    image_dir: str | Path,
    annotation_file: str | Path,
    output_path: str | Path,
    score_threshold: float = 0.05,
) -> Path:
    """Evaluate an RF-DETR checkpoint and save the shared result JSON."""
    try:
        from PIL import Image
        from rfdetr import RFDETRNano
    except ImportError as error:
        raise ImportError("Install pipeline/RFDETR/requirements.txt in the RF-DETR environment.") from error

    samples, class_names = load_coco_samples(image_dir, annotation_file)
    model = RFDETRNano(pretrain_weights=str(weights_path))
    if hasattr(model, "optimize_for_inference"):
        model.optimize_for_inference()
    for sample in samples:
        detections = model.predict(Image.open(sample["path"]).convert("RGB"), threshold=score_threshold)
        sample["predictions"] = _detections_to_predictions(detections)
    result = new_result("RF-DETR", weights_path, annotation_file)
    result.update(detection_summary(samples, class_names))
    result["dataset"] = str(image_dir)
    result["class_names"] = class_names
    return save_result(result, output_path)


def measure_rfdetr_time(
    weights_path: str | Path,
    image_dir: str | Path,
    output_path: str | Path,
    limit: int | None = 100,
    warmup: int = 10,
) -> Path:
    """Measure RF-DETR inference time and save all samples to JSON."""
    from PIL import Image
    from rfdetr import RFDETRNano

    images = sorted(
        path for path in Path(image_dir).iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    )
    if limit is not None:
        images = images[:limit]
    model = RFDETRNano(pretrain_weights=str(weights_path))
    if hasattr(model, "optimize_for_inference"):
        model.optimize_for_inference()
    synchronize = None
    try:
        import torch
        synchronize = torch.cuda.synchronize if torch.cuda.is_available() else None
    except ImportError:
        pass
    timing = measure_inference(
        lambda path: model.predict(Image.open(path).convert("RGB"), threshold=0.05),
        images,
        warmup,
        synchronize,
    )
    return save_timing_result("RF-DETR", timing, output_path)


def _detections_to_predictions(detections: object) -> list[dict[str, object]]:
    boxes = getattr(detections, "xyxy", [])
    scores = getattr(detections, "confidence", [])
    labels = getattr(detections, "class_id", [])
    return [
        {"box": [float(value) for value in box], "score": float(score), "class_id": int(label)}
        for box, score, label in zip(boxes, scores, labels)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RF-DETR on a COCO test split.")
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.05)
    args = parser.parse_args()
    test_rfdetr(args.weights, args.images, args.annotations, args.output, args.threshold)


if __name__ == "__main__":
    main()
