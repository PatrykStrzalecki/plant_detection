from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PIPELINE_DIR = Path(__file__).resolve().parents[1]

# RF-DETR expects the Roboflow/COCO directory layout:
# train/, valid/ and test/, each with _annotations.coco.json.
DATASET_DIR = PIPELINE_DIR / "datasets" / "coco_dataset"

OUTPUT_DIR = PIPELINE_DIR / "runs" / "rfdetr"
NUM_EPOCHS = 25
BATCH_SIZE = 4
GRAD_ACCUMULATION_STEPS = 4
NUM_WORKERS = 2
INPUT_RESOLUTION = 640
SEED = 42
CHECKPOINT_PERIOD = 5

# RF-DETR uses AdamW by default. Keep the optimizer and augmentation defaults
# unless an explicit override is added to one of the dictionaries below.
LEARNING_RATE = 0.0005
ENCODER_LEARNING_RATE = 0.0005
WEIGHT_DECAY = 0.0001

# RF-DETR applies this scheduler per optimizer step: linear warmup followed
# by cosine decay to LR_MIN_FACTOR * LEARNING_RATE.
LR_SCHEDULER_CONFIG: dict[str, object] = {
    "warmup_epochs": 3,
    "lr_scheduler": "cosine",
    "lr_min_factor": 0.02,
}

# Optional RF-DETR augmentation overrides. An empty dictionary preserves the
# package defaults: horizontal flip, random resize/crop/resize and normalize.
# Uncomment only options that should differ from those defaults.
CUSTOM_AUGMENTATION_CONFIG: dict[str, object] = {
    # "multi_scale": True,
    # "expanded_scales": True,
    # "do_random_resize_via_padding": True,
    # "square_resize_div_64": True,
}


def set_seed(seed: int) -> None:
    """Set seeds used by Python, NumPy and PyTorch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> str:
    """Use CUDA when available, otherwise CPU."""
    return "cuda" if torch.cuda.is_available() else "cpu"


def validate_configuration() -> None:
    """Fail before model creation when the configured dataset is incomplete."""
    required_paths = (
        DATASET_DIR / "train" / "_annotations.coco.json",
        DATASET_DIR / "valid" / "_annotations.coco.json",
        DATASET_DIR / "test" / "_annotations.coco.json",
    )
    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required RF-DETR dataset file does not exist: {path}"
            )


def build_training_arguments() -> dict[str, object]:
    """Build training arguments without changing RF-DETR defaults."""
    arguments: dict[str, object] = {
        "dataset_dir": str(DATASET_DIR),
        "epochs": NUM_EPOCHS,
        "batch_size": BATCH_SIZE,
        "grad_accum_steps": GRAD_ACCUMULATION_STEPS,
        "lr": LEARNING_RATE,
        "lr_encoder": ENCODER_LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "num_workers": NUM_WORKERS,
        "output_dir": str(OUTPUT_DIR),
        "checkpoint_interval": CHECKPOINT_PERIOD,
    }
    arguments.update(LR_SCHEDULER_CONFIG)
    arguments.update(CUSTOM_AUGMENTATION_CONFIG)
    return arguments


def train_model() -> Path:
    """Create RF-DETR Nano, train it and return the best checkpoint path."""
    validate_configuration()
    set_seed(SEED)

    try:
        from rfdetr import RFDETRNano
    except ImportError as error:
        raise ImportError(
            "RF-DETR is not installed in the selected Python environment. "
            "Install the package providing `from rfdetr import RFDETRNano` "
            "before running this script."
        ) from error

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print(f"Training RF-DETR Nano on {get_device()}")
    print(f"Dataset directory: {DATASET_DIR}")
    model = RFDETRNano(
        device=get_device(),
        resolution=INPUT_RESOLUTION,
    )
    model.train(**build_training_arguments())

    best_checkpoint = OUTPUT_DIR / "checkpoint_best_total.pth"
    if not best_checkpoint.exists():
        raise FileNotFoundError(
            f"Training finished but the best checkpoint was not found at "
            f"{best_checkpoint}"
        )
    return best_checkpoint


def main() -> None:
    """Run training and report the saved weights."""
    best_checkpoint = train_model()
    print(f"Training complete. Best weights saved at: {best_checkpoint}")


if __name__ == "__main__":
    main()
