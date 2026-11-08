from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from evaluation.dataset import load_coco_samples
from evaluation.detection_metrics import detection_summary
from evaluation.results import new_result, save_result
from evaluation.timing import measure_inference, save_timing_result


def test_ssd(
    weights_path: str | Path,
    image_dir: str | Path,
    annotation_file: str | Path,
    output_path: str | Path,
    score_threshold: float = 0.05,
) -> Path:
    """Evaluate an SSD checkpoint on a COCO test split."""
    try:
        import torch
        from PIL import Image
        from pipeline.SSD.train_SSD import create_ssd_model
    except ImportError as error:
        raise ImportError("Install pipeline/SSD/requirements.txt in the SSD environment.") from error

    samples, class_names = load_coco_samples(image_dir, annotation_file)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_ssd_model(len(class_names) + 1, device)
    checkpoint = torch.load(weights_path, map_location=device)
    model.load_state_dict(checkpoint.get("model_state_dict", checkpoint))
    model.eval()
    with torch.inference_mode():
        for sample in samples:
            image = Image.open(sample["path"]).convert("RGB")
            tensor = torch.from_numpy(np.asarray(image)).permute(2, 0, 1).float() / 255
            prediction = model([tensor.to(device)])[0]
            sample["predictions"] = [
                {
                    "box": [float(value) for value in box],
                    "class_id": int(label) - 1,
                    "score": float(score),
                }
                for box, label, score in zip(
                    prediction["boxes"].cpu(),
                    prediction["labels"].cpu(),
                    prediction["scores"].cpu(),
                )
                if float(score) >= score_threshold and 1 <= int(label) <= len(class_names)
            ]
    result = new_result("SSD", weights_path, annotation_file)
    result.update(detection_summary(samples, class_names))
    result["dataset"] = str(image_dir)
    result["class_names"] = class_names
    return save_result(result, output_path)


def measure_ssd_time(
    weights_path: str | Path,
    image_dir: str | Path,
    output_path: str | Path,
    limit: int | None = 100,
    warmup: int = 10,
) -> Path:
    """Measure SSD inference time on images from a directory."""
    import torch
    from PIL import Image
    from pipeline.SSD.train_SSD import create_ssd_model

    images = sorted(
        path for path in Path(image_dir).iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    )
    if limit is not None:
        images = images[:limit]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_ssd_model(2, device)
    checkpoint = torch.load(weights_path, map_location=device)
    model.load_state_dict(checkpoint.get("model_state_dict", checkpoint))
    model.eval()

    def predict(path: Path) -> None:
        image = torch.from_numpy(np.asarray(Image.open(path).convert("RGB"))).permute(2, 0, 1).float() / 255
        with torch.inference_mode():
            model([image.to(device)])

    synchronize = torch.cuda.synchronize if torch.cuda.is_available() else None
    return save_timing_result("SSD", measure_inference(predict, images, warmup, synchronize), output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SSD on a COCO test split.")
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.05)
    args = parser.parse_args()
    test_ssd(args.weights, args.images, args.annotations, args.output, args.threshold)


if __name__ == "__main__":
    main()
