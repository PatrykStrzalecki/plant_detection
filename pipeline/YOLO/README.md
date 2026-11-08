# YOLO

The `train_YOLO.py` script trains YOLOv11n or YOLOv12n models using
Ultralytics.

## Separate environment

A separate environment should be created for this model. YOLO, SSD, and RF-DETR
may require different dependency versions, so sharing one environment can cause
library conflicts.

From the `pipeline/YOLO` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Dataset preparation

Place the dataset in `pipeline/datasets/` and prepare it in YOLO format. The
script expects one of the following directories:

```text
datasets/
├── YOLOv11_dataset/
│   ├── data.yaml
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   │   ├── images/
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
└── YOLOv12_dataset/
     ├── data.yaml
     ├── train/
     │   ├── images/
     │   └── labels/
     ├── valid/
     │   ├── images/
     │   └── labels/
     └── test/
         ├── images/
         └── labels/
```

Each image must have a corresponding `.txt` file containing YOLO annotations.
The `data.yaml` file must define the `train` and `val` paths and, optionally,
the `test` path. It must also contain `nc` and `names`. If the directory is
named `valid`, reference it as `val` in the YAML file.

## Running the training

Before running the script, set `MODEL_VARIANT` in `train_YOLO.py` to `yolo11n`
or `yolo12n`, then run:

```bash
python train_YOLO.py
```

Results are saved in `pipeline/runs/detect/<model>_<iteration>/`.

## Evaluation

`evaluate.py` exposes `test_yolov11` and `test_yolov12`. Both save the same
JSON schema used by the SSD and RF-DETR pipelines:

```bash
python3 -m pipeline.YOLO.evaluate --model yolov11 \
  --weights pipeline/runs/detect/yolo11n_1/weights/best.pt \
  --dataset pipeline/datasets/YOLOv11_dataset/data.yaml \
  --output evaluation/results/yolov11.json
```