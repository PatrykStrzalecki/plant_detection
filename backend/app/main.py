from typing import Annotated
from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    status,
    Depends
)

from sqlalchemy.orm import Session

from common.database.database import engine, get_db
from common.database import models, schemas

from common.utils.api_utils import save_uploaded_file
from common.utils.defaults import SUPPORTED_IMAGE_EXTENSIONS

from common.worker.celery_worker import process_image_task

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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