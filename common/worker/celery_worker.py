import os
import redis
import logging
import datetime

from PIL import Image
from celery import Celery
from typing import Dict, Any
from ultralytics import YOLO
from dotenv import load_dotenv

from common.database.schemas import BoundingBox
from common.database.models import DetectionResult
from common.database.database import Base, get_db, engine

from common.utils.defaults import (
    IMAGE_SIZE,
    CONFIDENCE_THRESHOLD,
    MODEL_PATH,
    NMS_THRESHOLD,
    INPUT_DIR,
    OUTPUT_DIR,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    FLOWER_CATEGORY
)

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(__name__, broker = os.getenv("CELERY_BROKER_URL"))

celery_app.conf.update(
    result_backend = os.getenv("CELERY_RESULT_BACKEND"),
    task_track_started = True,
    broker_connection_retry_on_startup = True
)

try:
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except Exception as e:
    logger.error(f"Error occurred while setting up directories: {e}")

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    logger.error(f"Error occurred while loading model: {e}")
    model = None

Base.metadata.create_all(bind=engine)


@celery_app.task(name = "process_image_task")
def process_image_task(detection_id: int) -> Dict[str, Any]:
    logger.info(f"Starting task for detection ID: {detection_id}")
    try:
        db = next(get_db())
        detection_result = db.query(DetectionResult).filter(DetectionResult.id == detection_id).first()
        if not detection_result:
            logger.error(f"Detection result not found for ID: {detection_id}")
            redis_client.publish(f"task_status_{detection_id}", TASK_STATUS_FAILED)
            return {
                "status": TASK_STATUS_FAILED,
                "message": "Detection result not found."
            }

        detection_result.task_status = TASK_STATUS_IN_PROGRESS
        db.commit()
        db.refresh(detection_result)

        input_image_path = detection_result.original_image_path
        if not os.path.exists(input_image_path):
            logger.error(f"Input image not found at: {input_image_path}")
            raise FileNotFoundError(f"Input image not found at: {input_image_path}")
        
        logger.info(f"Processing image: {input_image_path}")
        image = Image.open(input_image_path)
        image = image.resize((IMAGE_SIZE, IMAGE_SIZE))

        results = model(image, conf=CONFIDENCE_THRESHOLD)
        logger.info(f"Processing finished for image: {input_image_path}")
        
        if not results:
            logger.warning(f"No detections found for image: {input_image_path}")
        
        output_image_path = os.path.join(OUTPUT_DIR, os.path.basename(input_image_path))
        results[0].save(output_image_path)
        logger.info(f"Output image saved to: {output_image_path}")

        bounding_boxes = results[0].boxes.xyxy.tolist()
        confidences = results[0].boxes.conf.tolist()

        formated_bounding_boxes = []
        for i, box in enumerate(bounding_boxes):
            formated_bounding_boxes.append(
                BoundingBox(
                    x1 = box[0],
                    y1 = box[1],
                    x2 = box[2],
                    y2 = box[3],
                    confidence = confidences[i]
                ).model_dump()
            )

        detection_result.processed_image_path = output_image_path
        detection_result.processed_at = datetime.datetime.now()
        detection_result.num_flowers = len(formated_bounding_boxes)
        detection_result.category = FLOWER_CATEGORY         # TODO
        detection_result.bounding_boxes = formated_bounding_boxes
        detection_result.task_status = TASK_STATUS_COMPLETED
        db.commit()
        db.refresh(detection_result)

        logger.info(f"Task completed for detection ID: {detection_id}")
        redis_client.publish(f"task_status_{detection_id}", TASK_STATUS_COMPLETED)
        return {
            "status": TASK_STATUS_COMPLETED,
            "detection_id": detection_id,
            "output_image_path": output_image_path,
            "num_flowers": len(bounding_boxes),
            "category": FLOWER_CATEGORY
        }
           
    except Exception as e:
        detection_result.task_status = TASK_STATUS_FAILED
        db.commit()
        logger.error(f"Error processing image for detection ID {detection_id}: {e}")
        redis_client.publish(f"task_status_{detection_id}", TASK_STATUS_FAILED)
        return {
            "status": TASK_STATUS_FAILED,
            "message": str(e)
        }