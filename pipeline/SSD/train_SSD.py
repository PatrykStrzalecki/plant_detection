from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

import albumentations as A
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision.models.detection import SSD300_VGG16_Weights, _utils
from torchvision.models.detection import ssd300_vgg16
from torchvision.models.detection.ssd import SSDClassificationHead
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PIPELINE_DIR = Path(__file__).resolve().parents[1]
TRAIN_IMAGE_DIR = PIPELINE_DIR / "datasets" / "SSD_coco_dataset" / "train"
TRAIN_ANNOTATION_FILE = TRAIN_IMAGE_DIR / "_annotations.coco.json"
VALIDATION_IMAGE_DIR = PIPELINE_DIR / "datasets" / "coco_dataset" / "valid"
VALIDATION_ANNOTATION_FILE = VALIDATION_IMAGE_DIR / "_annotations.coco.json"

CHECKPOINT_DIR = PIPELINE_DIR / "ssd_checkpoints"
RESULTS_DIR = PIPELINE_DIR / "ssd_results"

INPUT_SIZE = (640, 640)
BATCH_SIZE = 16
NUM_WORKERS = 0
NUM_EPOCHS = 25
LEARNING_RATE = 0.0005
MAX_LEARNING_RATE = 0.001
WEIGHT_DECAY = 0.0001
SEED = 42
CHECKPOINT_PERIOD = 5


def set_seed(seed: int) -> None:
    """Set random seeds used by Python, NumPy and PyTorch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    """Return CUDA when available, otherwise CPU."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


class COCODetectionDataset(Dataset[tuple[torch.Tensor, dict[str, torch.Tensor]]]):
    """Read COCO annotations and return targets in torchvision SSD format."""

    def __init__(
        self,
        image_dir: Path,
        annotation_file: Path,
        category_id_to_label: dict[int, int] | None = None,
        transform: A.Compose | None = None,
    ) -> None:
        self.image_dir = image_dir
        self.transform = transform

        with annotation_file.open("r", encoding="utf-8") as file:
            coco = json.load(file)

        annotations_by_image: dict[int, list[dict[str, Any]]] = {}
        for annotation in coco["annotations"]:
            annotations_by_image.setdefault(annotation["image_id"], []).append(annotation)

        self.images = [
            image
            for image in coco["images"]
            if image["id"] in annotations_by_image
        ]
        if not self.images:
            raise ValueError(f"No annotated images found in {annotation_file}")

        used_category_ids = sorted(
            {
                int(annotation["category_id"])
                for annotation in coco["annotations"]
            }
        )
        self.category_id_to_label = category_id_to_label or {
            category_id: label
            for label, category_id in enumerate(used_category_ids, start=1)
        }
        self.annotations_by_image = annotations_by_image

        print(f"Loaded {len(self.images)} images from {annotation_file}")
        print(f"Category mapping: {self.category_id_to_label}")

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        image_info = self.images[index]
        image_path = self.image_dir / image_info["file_name"]

        try:
            image = Image.open(image_path).convert("RGB")
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Unable to load image: {image_path}") from error

        boxes: list[list[float]] = []
        labels: list[int] = []
        for annotation in self.annotations_by_image[image_info["id"]]:
            x, y, width, height = (float(value) for value in annotation["bbox"])
            x2 = x + width
            y2 = y + height
            if x2 <= x or y2 <= y:
                continue

            category_id = int(annotation["category_id"])
            if category_id not in self.category_id_to_label:
                raise ValueError(
                    f"Category {category_id} in {image_path} is not present "
                    "in the training category mapping."
                )
            boxes.append([x, y, x2, y2])
            labels.append(self.category_id_to_label[category_id])

        if not boxes:
            raise ValueError(f"No valid bounding boxes found in {image_path}")

        transformed = self.transform(
            image=np.asarray(image),
            bboxes=boxes,
            class_labels=labels,
        ) if self.transform else {"image": np.asarray(image), "bboxes": boxes, "class_labels": labels}

        transformed_image = transformed["image"]
        if not isinstance(transformed_image, torch.Tensor):
            transformed_image = torch.from_numpy(transformed_image).permute(2, 0, 1)

        target = {
            "boxes": torch.as_tensor(transformed["bboxes"], dtype=torch.float32),
            "labels": torch.as_tensor(transformed["class_labels"], dtype=torch.int64),
        }
        return transformed_image, target


def get_transforms(train: bool) -> A.Compose:
    """Create annotation-aware transforms for training or validation."""
    if train:
        transforms: list[Any] = [
            A.HorizontalFlip(p=0.5),
            A.RandomResizedCrop(
                size=INPUT_SIZE,
                scale=(0.8, 1.0),
                ratio=(0.9, 1.1),
            ),
            A.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.1,
                hue=0.05,
                p=0.7,
            ),
        ]
    else:
        transforms = [
            A.Resize(height=INPUT_SIZE[0], width=INPUT_SIZE[1]),
        ]

    transforms.extend([A.ToFloat(max_value=255.0), ToTensorV2()])
    return A.Compose(
        transforms,
        bbox_params=A.BboxParams(
            format="pascal_voc",
            label_fields=["class_labels"],
            min_visibility=0.3 if train else 0.0,
        ),
    )


def collate_fn(
    batch: list[tuple[torch.Tensor, dict[str, torch.Tensor]]],
) -> tuple[tuple[torch.Tensor, ...], tuple[dict[str, torch.Tensor], ...]]:
    """Keep images and targets as separate variable-length tuples."""
    return tuple(zip(*batch))


def build_dataloaders() -> tuple[
    DataLoader[tuple[torch.Tensor, dict[str, torch.Tensor]]],
    DataLoader[tuple[torch.Tensor, dict[str, torch.Tensor]]],
    int,
]:
    """Create training and validation loaders and return the class count."""
    train_dataset = COCODetectionDataset(
        TRAIN_IMAGE_DIR,
        TRAIN_ANNOTATION_FILE,
        transform=get_transforms(train=True),
    )
    validation_dataset = COCODetectionDataset(
        VALIDATION_IMAGE_DIR,
        VALIDATION_ANNOTATION_FILE,
        category_id_to_label=train_dataset.category_id_to_label,
        transform=get_transforms(train=False),
    )

    loader_kwargs = {
        "batch_size": BATCH_SIZE,
        "num_workers": NUM_WORKERS,
        "collate_fn": collate_fn,
        "pin_memory": torch.cuda.is_available(),
    }
    train_loader = DataLoader(train_dataset, shuffle=True, **loader_kwargs)
    validation_loader = DataLoader(validation_dataset, shuffle=False, **loader_kwargs)
    return train_loader, validation_loader, len(train_dataset.category_id_to_label) + 1


def create_ssd_model(num_classes: int, device: torch.device) -> nn.Module:
    """Create an SSD300 model with a classification head for this dataset."""
    model = ssd300_vgg16(weights=SSD300_VGG16_Weights.DEFAULT)
    in_channels = _utils.retrieve_out_channels(model.backbone, INPUT_SIZE)
    num_anchors = model.anchor_generator.num_anchors_per_location()
    model.head.classification_head = SSDClassificationHead(
        in_channels=in_channels,
        num_anchors=num_anchors,
        num_classes=num_classes,
    )
    model.transform.min_size = (INPUT_SIZE[0],)
    model.transform.max_size = INPUT_SIZE[0]
    return model.to(device)


def create_optimizer_and_scheduler(
    model: nn.Module,
    train_loader: DataLoader[tuple[torch.Tensor, dict[str, torch.Tensor]]],
) -> tuple[torch.optim.Optimizer, torch.optim.lr_scheduler.OneCycleLR]:
    """Create the optimizer and the OneCycle learning-rate scheduler."""
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=MAX_LEARNING_RATE,
        total_steps=NUM_EPOCHS * len(train_loader),
        pct_start=0.1,
        div_factor=10,
        final_div_factor=100,
        anneal_strategy="cos",
    )
    return optimizer, scheduler


def move_batch_to_device(
    images: tuple[torch.Tensor, ...],
    targets: tuple[dict[str, torch.Tensor], ...],
    device: torch.device,
) -> tuple[list[torch.Tensor], list[dict[str, torch.Tensor]]]:
    """Move a detection batch to the selected device."""
    device_images = [image.to(device) for image in images]
    device_targets = [
        {key: value.to(device) for key, value in target.items()}
        for target in targets
    ]
    return device_images, device_targets


def calculate_batch_loss(
    model: nn.Module,
    images: list[torch.Tensor],
    targets: list[dict[str, torch.Tensor]],
) -> torch.Tensor:
    """Calculate the sum of torchvision's SSD loss components."""
    loss_dict = model(images, targets)
    return sum(loss_dict.values())


def validate(
    model: nn.Module,
    validation_loader: DataLoader[tuple[torch.Tensor, dict[str, torch.Tensor]]],
    device: torch.device,
) -> float:
    """Calculate mean validation loss."""
    model.train()
    total_loss = 0.0
    batch_count = 0
    with torch.no_grad():
        for images, targets in tqdm(validation_loader, desc="Validation"):
            device_images, device_targets = move_batch_to_device(images, targets, device)
            total_loss += calculate_batch_loss(model, device_images, device_targets).item()
            batch_count += 1
    model.eval()
    return total_loss / max(batch_count, 1)


def save_checkpoint(
    path: Path,
    epoch: int,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.OneCycleLR,
    train_loss: float,
    validation_loss: float,
) -> None:
    """Save model and optimizer state needed to resume training."""
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "train_loss": train_loss,
            "val_loss": validation_loss,
        },
        path,
    )


def train_model(
    model: nn.Module,
    train_loader: DataLoader[tuple[torch.Tensor, dict[str, torch.Tensor]]],
    validation_loader: DataLoader[tuple[torch.Tensor, dict[str, torch.Tensor]]],
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.OneCycleLR,
    device: torch.device,
) -> dict[str, Any]:
    """Train SSD, validate after each epoch and save best/final weights."""
    best_validation_loss = float("inf")
    history: dict[str, Any] = {
        "train_losses": [],
        "val_losses": [],
        "learning_rates": [],
        "epochs": [],
        "best_val_loss": best_validation_loss,
        "best_epoch": 0,
    }
    start_time = time.time()

    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        total_train_loss = 0.0
        batch_count = 0
        progress = tqdm(train_loader, desc=f"Epoch {epoch}/{NUM_EPOCHS}")

        for images, targets in progress:
            device_images, device_targets = move_batch_to_device(images, targets, device)
            optimizer.zero_grad(set_to_none=True)
            loss = calculate_batch_loss(model, device_images, device_targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()

            total_train_loss += loss.item()
            batch_count += 1
            progress.set_postfix(
                loss=f"{loss.item():.4f}",
                lr=f"{optimizer.param_groups[0]['lr']:.6f}",
            )

        train_loss = total_train_loss / max(batch_count, 1)
        validation_loss = validate(model, validation_loader, device)
        history["epochs"].append(epoch)
        history["train_losses"].append(train_loss)
        history["val_losses"].append(validation_loss)
        history["learning_rates"].append(optimizer.param_groups[0]["lr"])

        print(
            f"Epoch {epoch}/{NUM_EPOCHS}: "
            f"train_loss={train_loss:.4f}, val_loss={validation_loss:.4f}"
        )

        if epoch % CHECKPOINT_PERIOD == 0:
            save_checkpoint(
                CHECKPOINT_DIR / f"ssd_model_epoch_{epoch}.pth",
                epoch,
                model,
                optimizer,
                scheduler,
                train_loss,
                validation_loss,
            )

        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            history["best_val_loss"] = validation_loss
            history["best_epoch"] = epoch
            save_checkpoint(
                CHECKPOINT_DIR / "ssd_model_best.pth",
                epoch,
                model,
                optimizer,
                scheduler,
                train_loss,
                validation_loss,
            )

    torch.save({"model_state_dict": model.state_dict()}, CHECKPOINT_DIR / "ssd_model_final.pth")
    (RESULTS_DIR / "training_history.json").write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )
    print(f"Training completed in {(time.time() - start_time) / 60:.2f} minutes")
    return history


def main() -> None:
    """Configure resources, train the model and persist its weights."""
    set_seed(SEED)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    for required_path in (
        TRAIN_IMAGE_DIR,
        TRAIN_ANNOTATION_FILE,
        VALIDATION_IMAGE_DIR,
        VALIDATION_ANNOTATION_FILE,
    ):
        if not required_path.exists():
            raise FileNotFoundError(f"Required dataset path does not exist: {required_path}")

    device = get_device()
    print(f"Using device: {device}")
    if device.type == "cuda":
        torch.cuda.empty_cache()

    train_loader, validation_loader, num_classes = build_dataloaders()
    model = create_ssd_model(num_classes, device)
    optimizer, scheduler = create_optimizer_and_scheduler(model, train_loader)
    history = train_model(
        model,
        train_loader,
        validation_loader,
        optimizer,
        scheduler,
        device,
    )
    print(
        f"Best validation loss: {history['best_val_loss']:.4f} "
        f"(epoch {history['best_epoch']})"
    )
    print(f"Best weights: {CHECKPOINT_DIR / 'ssd_model_best.pth'}")


if __name__ == "__main__":
    main()
