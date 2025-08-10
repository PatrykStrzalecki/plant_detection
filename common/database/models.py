import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON

from utils.defaults import TASK_STATUS_PENDING

from .database import Base


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True, index=True)

    original_image_path = Column(String, index=True, nullable=False)
    processed_image_path = Column(String, nullable=True)

    task_status = Column(String, default = TASK_STATUS_PENDING, index = True, nullable = False)
    uploaded_at = Column(DateTime, default = datetime.datetime.now, nullable = False)
    processed_at = Column(DateTime, nullable = True)

    num_flowers = Column(Integer, nullable = True)
    category = Column(Integer, nullable = True)
    bounding_boxes = Column(JSON, nullable = True)

    def __repr__(self):
        obj_name = f"<{self.__class__.__name__}>"
        result_id = f" - id = {self.id}"
        task_status = f" - task_status = {self.task_status}"
        image_path = f" - original_image_path = {self.original_image_path}"
        return f"{obj_name}\n{result_id}\n{task_status}\n{image_path}"
