import os
import redis.asyncio as aioredis
import asyncio

from contextlib import asynccontextmanager

from typing import Annotated, Dict, Set
from fastapi import (
    FastAPI, UploadFile, HTTPException, status,
    File, Depends, WebSocket, WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from common.database.database import engine, get_db
from common.database import models, schemas

from common.utils.api_utils import save_uploaded_file
from common.utils.defaults import (
    INPUT_DIR, OUTPUT_DIR, SUPPORTED_IMAGE_EXTENSIONS,
    TASK_STATUS_COMPLETED, TASK_STATUS_FAILED
)

from common.worker.celery_worker import process_image_task

load_dotenv()

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

REDIS_URL = os.getenv("REDIS_URL")
redis_client = aioredis.from_url(REDIS_URL, decode_responses = True)

active_connections: Dict[int, WebSocket] = {}
frontend_connections: Set[WebSocket] = set()

async def redis_listener():
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("task_status_*")
    try:
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                channel = message["channel"]
                task_id = int(channel.split("_")[-1])
                status = message["data"]

                if task_id in active_connections:
                    websocket = active_connections[task_id]
                    try:
                        await websocket.send_json({"task_id": task_id, "status": status})
                        if status in [TASK_STATUS_COMPLETED, TASK_STATUS_FAILED]:
                            await websocket.close(code = 1000)
                            del active_connections[task_id]
                    except WebSocketDisconnect:
                        if task_id in active_connections:
                            del active_connections[task_id]
                    except Exception as e:
                        print(f"Error sending message to websocket: {e}")
                        if task_id in active_connections:
                            del active_connections[task_id]
                
                if status == TASK_STATUS_COMPLETED:
                    await notify_all_frontends({"task_id": task_id, "status": status})

    except Exception as e:
        print(f"Error in redis listener: {e}")

async def notify_all_frontends(message: dict):
    disconnected = set()
    for websocket in frontend_connections:
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error notifying frontend: {e}")
            disconnected.add(websocket)
    frontend_connections.difference_update(disconnected)

@asynccontextmanager
async def startup_event(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    asyncio.create_task(redis_listener())
    yield

app = FastAPI(lifespan = startup_event)

origins = [
    "http://localhost",
    "http://localhost:80"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.mount("/data", StaticFiles(directory="data"), name="data")

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

@app.websocket("/ws/frontend")
async def frontend_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    frontend_connections.add(websocket)
    print(f"Frontend connected. Total: {len(frontend_connections)}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        frontend_connections.discard(websocket)
        print(f"Frontend disconnected. Total: {len(frontend_connections)}")