FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-runtime

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/.config/Ultralytics && chmod -R 777 /app/.config/Ultralytics

ENV YOLO_CONFIG_DIR=/app/.config/Ultralytics
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./common ./common
COPY ./models ./models
COPY ./worker/app ./app

CMD ["celery", "-A", "common.worker.celery_worker", "worker", "--loglevel=info", "--pool=solo"]