from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from ultralytics import YOLO


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PIPELINE_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = PIPELINE_DIR.parent

# Change only this value to train the other model.
MODEL_VARIANT = "yolo11n"
ITERATION = 1

MODEL_WEIGHTS = {
    "yolo11n": REPOSITORY_DIR / "models" / "yolo11n.pt",
    "yolo12n": REPOSITORY_DIR / "models" / "yolo12n.pt",
}
DATASET_CONFIGS = {
    "yolo11n": PIPELINE_DIR / "datasets" / "YOLOv11_dataset" / "data.yaml",
    "yolo12n": PIPELINE_DIR / "datasets" / "YOLOv12_dataset" / "data.yaml",
}

OUTPUT_DIR = PIPELINE_DIR / "runs" / "detect"
RUN_NAME = f"{MODEL_VARIANT}_{ITERATION}"

INPUT_SIZE = 640
BATCH_SIZE = 4
NUM_EPOCHS = 25
NUM_WORKERS = 8
SEED = 42

# Keep the optimizer and augmentation values at Ultralytics defaults.
OPTIMIZER = "auto"
FINAL_LR_FACTOR = 0.02
WARMUP_EPOCHS = 3.0

# Optional custom augmentations. By default this dictionary is not passed to
# model.train(), so Ultralytics' default augmentation configuration is used.
# To enable custom values, set CUSTOM_AUGMENTATION_CONFIG and keep the
# **CUSTOM_AUGMENTATION_CONFIG line in build_training_arguments().
CUSTOM_AUGMENTATION_CONFIG: dict[str, float] = {
    # "hsv_h": 0.014,
    # "hsv_s": 0.20,
    # "hsv_v": 0.20,
    # "translate": 0.10,
    # "scale": 0.20,
    # "fliplr": 0.5,
}


def set_seed(seed: int) -> None:
    """Set seeds used by Python, NumPy and PyTorch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> int | str:
    """Use the first CUDA device when available, otherwise CPU."""
    return 0 if torch.cuda.is_available() else "cpu"


def validate_configuration() -> None:
    """Fail early when the selected model or dataset is unavailable."""
    if MODEL_VARIANT not in MODEL_WEIGHTS:
        raise ValueError(
            f"Unsupported MODEL_VARIANT={MODEL_VARIANT!r}. "
            f"Choose one of: {', '.join(MODEL_WEIGHTS)}."
        )

    required_paths = (
        MODEL_WEIGHTS[MODEL_VARIANT],
        DATASET_CONFIGS[MODEL_VARIANT],
    )
    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"Required training file does not exist: {path}")


def build_training_arguments() -> dict[str, object]:
    """Return explicit Ultralytics arguments for the comparable training setup."""
    return {
        "data": str(DATASET_CONFIGS[MODEL_VARIANT]),
        "epochs": NUM_EPOCHS,
        "imgsz": INPUT_SIZE,
        "batch": BATCH_SIZE,
        "workers": NUM_WORKERS,
        "device": get_device(),
        "optimizer": OPTIMIZER,
        "lrf": FINAL_LR_FACTOR,
        "cos_lr": True,
        "warmup_epochs": WARMUP_EPOCHS,
        "seed": SEED,
        "deterministic": True,
        "project": str(OUTPUT_DIR),
        "name": RUN_NAME,
        "exist_ok": True,
        "pretrained": True,
        "save": True,
        "plots": True,
        "val": True,
        **CUSTOM_AUGMENTATION_CONFIG,
    }


def train_model() -> Path:
    """Train the selected YOLO model and return the path to best.pt."""
    validate_configuration()
    set_seed(SEED)

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model_path = MODEL_WEIGHTS[MODEL_VARIANT]
    print(f"Training {MODEL_VARIANT} on {get_device()}")
    print(f"Dataset configuration: {DATASET_CONFIGS[MODEL_VARIANT]}")

    model = YOLO(str(model_path))
    model.train(**build_training_arguments())

    best_weights = OUTPUT_DIR / RUN_NAME / "weights" / "best.pt"
    if not best_weights.exists():
        raise FileNotFoundError(
            f"Training finished but best weights were not found at {best_weights}"
        )
    return best_weights


def main() -> None:
    """Run training and report the saved weights."""
    best_weights = train_model()
    print(f"Training complete. Best weights saved at: {best_weights}")


if __name__ == "__main__":
    main()
