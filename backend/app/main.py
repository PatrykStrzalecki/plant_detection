import os
import redis
import asyncio

from contextlib import asynccontextmanager

from typing import Annotated, List, Dict
from fastapi import (
    FastAPI, UploadFile, HTTPException, status,
    File, Depends, WebSocket, WebSocketDisconnect
)

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from common.database.database import engine, get_db
from common.database import models, schemas

from common.utils.api_utils import save_uploaded_file
from common.utils.defaults import (
    INPUT_DIR, OUTPUT_DIR, SUPPORTED_IMAGE_EXTENSIONS, DECODING
)

from common.worker.celery_worker import process_image_task

load_dotenv()

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL)

active_connections: Dict[int, WebSocket] = {}

async def redis_listener():
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("task_status_*")
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages = True)
        if message:
            channel = message["channel"].decode(DECODING)
            task_id = int(channel.split("_")[-1])
            status = message["data"].decode(DECODING)
            if task_id in active_connections:
                websocket = active_connections[task_id]
                try:
                    await websocket.send_json({"task_id": task_id, "status": status})
                    await websocket.close(code = 1000)
                    del active_connections[task_id]
                except WebSocketDisconnect:
                    del active_connections[task_id]
        await asyncio.sleep(0.1)

@asynccontextmanager
async def startup_event(app: FastAPI):
    asyncio.create_task(redis_listener())
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan = startup_event)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Plant Detection API"}

@app.post("/upload-image", response_model = schemas.DetectionResult, status_code = status.HTTP_202_ACCEPTED)
async def upload_file(
    file: Annotated[UploadFile, File(..., description="Image file to upload")],
    db: Session = Depends(get_db)
) -> schemas.DetectionResult:
    if not file.filename.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Invalid file type. Only {', '.join(SUPPORTED_IMAGE_EXTENSIONS)} are allowed."
        ) 
    try:
        file_path = save_uploaded_file(file)
    except IOError as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"Error saving file: {e}"
        )

    detection_result = schemas.DetectionResultCreate(
        original_image_path = file_path
    )

    db_result = models.DetectionResult(**detection_result.model_dump())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    process_image_task.delay(db_result.id)

    return db_result

@app.get("/detection-result/{detection_id}", response_model = schemas.DetectionResult)
async def get_detection_result(
    detection_id: int,
    db: Session = Depends(get_db)
) -> schemas.DetectionResult:
    db_result = db.query(models.DetectionResult).filter(models.DetectionResult.id == detection_id).first()
    if not db_result:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Detection result not found"
        )
    return db_result

@app.get("/task-status/{task_id}", response_model = schemas.DetectionResult)
async def get_task_status(
    task_id: int,
    db: Session = Depends(get_db)
) -> schemas.DetectionResult:
    db_result = db.query(models.DetectionResult).filter(models.DetectionResult.id == task_id).first()
    if not db_result:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Detection result not found"
        )
    return db_result

@app.websocket("/ws/task-status/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    await websocket.accept()
    active_connections[task_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if task_id in active_connections:
            del active_connections[task_id]