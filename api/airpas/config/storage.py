"""
Local file storage configuration and helpers for uploaded receipt files.
"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

LOCAL_STORAGE_DIR = Path(__file__).resolve().parent.parent / "local"
LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

LOCAL_STORAGE_URL_PREFIX = "/local"

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def save_upload(upload: UploadFile) -> tuple[str, str, str]:
    """
    Validate and persist an uploaded file to local storage.
    Returns a tuple of (original_filename, content_type, url).
    """
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {upload.content_type}. Only PDF and image files are allowed.")

    original_filename = upload.filename or "upload"
    extension = Path(original_filename).suffix
    stored_filename = f"{uuid.uuid4()}{extension}"
    destination = LOCAL_STORAGE_DIR / stored_filename

    with destination.open("wb") as out_file:
        out_file.write(upload.file.read())

    url = f"{LOCAL_STORAGE_URL_PREFIX}/{stored_filename}"
    return original_filename, upload.content_type, url
