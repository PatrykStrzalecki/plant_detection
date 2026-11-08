from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_coco_samples(
    image_dir: str | Path,
    annotation_file: str | Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Load COCO images and annotations into the shared sample representation."""
    image_dir = Path(image_dir)
    coco = json.loads(Path(annotation_file).read_text(encoding="utf-8"))
    categories = sorted(coco.get("categories", []), key=lambda item: int(item["id"]))
    category_to_class = {int(item["id"]): index for index, item in enumerate(categories)}
    class_names = [str(item.get("name", item["id"])) for item in categories]
    grouped: dict[int, list[dict[str, Any]]] = {}
    for annotation in coco.get("annotations", []):
        x, y, width, height = (float(value) for value in annotation["bbox"])
        if width > 0 and height > 0:
            grouped.setdefault(int(annotation["image_id"]), []).append(
                {"box": [x, y, x + width, y + height], "class_id": category_to_class[int(annotation["category_id"])]}
            )
    samples = []
    for image in coco.get("images", []):
        path = image_dir / str(image["file_name"])
        if not path.exists():
            raise FileNotFoundError(f"Image referenced by COCO does not exist: {path}")
        samples.append(
            {
                "image_id": int(image["id"]),
                "path": str(path),
                "ground_truth": grouped.get(int(image["id"]), []),
                "predictions": [],
            }
        )
    return samples, class_names
