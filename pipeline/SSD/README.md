# SSD

The `train_SSD.py` script trains an SSD300 model from torchvision.

## Separate environment

A separate environment should be created for this model. YOLO, SSD, and RF-DETR
may require different dependency versions, so sharing one environment can cause
library conflicts.

From the `pipeline/SSD` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Dataset preparation

Place the dataset in `pipeline/datasets/coco_dataset/` and prepare it in
COCO format:

```text
datasets/
└── coco_dataset/
    ├── train/
    │   ├── image_001.jpg
    │   └── _annotations.coco.json
    ├── valid/
    │   ├── image_101.jpg
    │   └── _annotations.coco.json
    └── test/
        ├── image_201.jpg
        └── _annotations.coco.json
```

The `_annotations.coco.json` file must contain `images`, `annotations`, and
`categories` sections. The `file_name` values in the JSON must match the actual
image files. The SSD script uses the `train` and `valid` splits; a `test` split
may be stored in the dataset but is not used during this training.

## Running the training

With the virtual environment activated, run:

```bash
python train_SSD.py
```

Checkpoints are saved in `pipeline/ssd_checkpoints/`, and the training history
is saved in `pipeline/ssd_results/training_history.json`.

## Evaluation

`evaluate.py` provides `test_ssd` and writes the shared JSON result format.
Run it in the SSD environment:

```bash
python3 -m pipeline.SSD.evaluate \
  --weights pipeline/ssd_checkpoints/ssd_model_best.pth \
  --images pipeline/datasets/coco_dataset/test \
  --annotations pipeline/datasets/coco_dataset/test/_annotations.coco.json \
  --output evaluation/results/ssd.json
```