import os
import shutil
from uuid import uuid4
from fastapi import UploadFile

from pathlib import Path

from .defaults import INPUT_DIR

def save_uploaded_file(upload_file: UploadFile) -> str:
    file_id = str(uuid4())
    file_extension = Path(upload_file.filename).suffix
    file_path = os.path.join(INPUT_DIR, f"{file_id}{file_extension}")

    try:
        os.makedirs(INPUT_DIR, exist_ok = True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path
    except Exception as e:
        raise IOError(f"Failed to save uploaded file: {e}")