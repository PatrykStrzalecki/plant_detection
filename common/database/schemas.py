import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.utils.defaults import TASK_STATUS_PENDING


class BoundingBox(BaseModel):
    x1: float = Field(..., description = "Top left X coordinate of the bounding box")
    y1: float = Field(..., description = "Top left Y coordinate of the bounding box")
    x2: float = Field(..., description = "Bottom right X coordinate of the bounding box")
    y2: float = Field(..., description = "Bottom right Y coordinate of the bounding box")
    confidence: Optional[float] = Field(None, description = "Confidence score of the detection")

class DetectionResultBase(BaseModel):
    num_flowers: Optional[int] = Field(None, description = "Number of flowers detected in the image")
    category: Optional[int] = Field(None, description = "Category of the detected flowers")
    bounding_boxes: Optional[List[BoundingBox]] = Field(None, description = "List of bounding boxes for detected flowers")

class DetectionResultCreate(BaseModel):
    original_image_path: str = Field(..., description = "Path to the original uploaded image")
    
class DetectionResultUpdate(DetectionResultBase):
    processed_image_path: str = Field(..., description = "Path to the processed image after detection")
    task_status: str = Field(..., description = "Current status of the detection task")
    processed_at: datetime.datetime = Field(default_factory = datetime.datetime.now, description = "Timestamp when the image was processed")

class DetectionResult(DetectionResultBase):
    id: Optional[int] = Field(None, description = "Unique identifier for the detection result")
    original_image_path: str = Field(..., description = "Path to the original uploaded image")
    processed_image_path: Optional[str] = Field(None, description = "Path to the processed image after detection")
    task_status: str = Field(TASK_STATUS_PENDING, description = "Current status of the detection task")
    uploaded_at: datetime.datetime = Field(default_factory = datetime.datetime.now, description = "Timestamp when the image was uploaded")
    processed_at: Optional[datetime.datetime] = Field(None, description = "Timestamp when the image was processed")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "original_image_path": "/images/original.jpg",
                "processed_image_path": "/images/processed.jpg",
                "task_status": "completed",
                "uploaded_at": "2025-10-01T12:00:00Z",
                "processed_at": "2025-10-01T12:05:00Z",
                "num_flowers": 5,
                "category": 2,
                "bounding_boxes": [
                    {
                        "x1": 100.0,
                        "y1": 150.0,
                        "x2": 200.0,
                        "y2": 250.0,
                        "confidence": 0.95
                    }
                ]
            }
        }