# RF-DETR

The `train_RF_DETR.py` script trains an RF-DETR Nano model.

## Separate environment

A separate environment should be created for this model. YOLO, SSD, and RF-DETR
may require different dependency versions, so sharing one environment can cause
library conflicts.

From the `pipeline/RFDETR` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Dataset preparation

Place the dataset in `pipeline/datasets/coco_dataset/` and prepare it in COCO
format:

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

Each split must contain one `_annotations.coco.json` file and the images listed
in its `images` section. The JSON file should contain `images`, `annotations`,
and `categories` sections. All three splits are required: `train`, `valid`, and
`test`.

## Running the training

With the virtual environment activated, run:

```bash
python train_RF_DETR.py
```

Checkpoints are saved in `pipeline/runs/rfdetr/`.

## Evaluation

`evaluate.py` provides `test_rfdetr` and writes the shared JSON result format.
Run it in the RF-DETR environment:

```bash
python3 -m pipeline.RFDETR.evaluate \
  --weights pipeline/runs/rfdetr/checkpoint_best_total.pth \
  --images pipeline/datasets/coco_dataset/test \
  --annotations pipeline/datasets/coco_dataset/test/_annotations.coco.json \
  --output evaluation/results/rfdetr.json
```