# Evaluation from JSON

The model pipelines produce JSON files with one stable format. Detection
results contain `metrics`, `curves.precision_recall` and optionally
`confusion_matrix`; timing results contain `timing.samples_ms` and summary
statistics. The plotting code does not import PyTorch, Ultralytics or RF-DETR.

Generate all detection plots:

```bash
python3 -m evaluation.generate_plots results/
```

Generate detection and timing plots from separate directories:

```bash
python3 -m evaluation.generate_plots results/ --timing-results timing/
```

The model-specific commands are intentionally run in their existing isolated
environments:

```bash
python3 -m pipeline.YOLO.evaluate --model yolov11 \
  --weights path/to/best.pt --dataset path/to/data.yaml \
  --output results/yolov11.json

python3 -m pipeline.SSD.evaluate \
  --weights path/to/ssd_model_best.pth \
  --images pipeline/datasets/coco_dataset/test \
  --annotations pipeline/datasets/coco_dataset/test/_annotations.coco.json \
  --output results/ssd.json

python3 -m pipeline.RFDETR.evaluate \
  --weights path/to/checkpoint_best_total.pth \
  --images pipeline/datasets/coco_dataset/test \
  --annotations pipeline/datasets/coco_dataset/test/_annotations.coco.json \
  --output results/rfdetr.json
```

Timing is stored separately so it can be repeated without recalculating
accuracy. For example, call `measure_yolo_time`, `measure_ssd_time` or
`measure_rfdetr_time` from a short Python script and pass the produced
directory to `--timing-results`.

## End-to-end system performance

The [`performance/`](./performance/) folder contains a separate test suite for
measuring the performance of the complete system, rather than only the model
inference time. `perf_test.py` sends images to the backend through
`POST /upload-image` and measures the time until a successful result is
published by the worker on Redis channels matching `task_status_*`.

This test requires a running backend, worker and Redis instance, as well as a
folder containing test images. The client reads the following environment
variables (defaults are suitable for a local Docker setup):

```bash
export BACKEND_URL=http://localhost:8000
export REDIS_URL=redis://localhost:6379
```

Run it from the repository root after starting the application stack:

```bash
python3 -m evaluation.performance.perf_test
```

The suite includes baseline single-image latency, constant conveyor-belt
speed, burst throughput and queue-buildup series tests. It reports sent,
completed and lost requests together with minimum, maximum, average, median
and p95 latency where enough samples are available. The graph-oriented tests
also save JSON and PNG output in the current working directory.
