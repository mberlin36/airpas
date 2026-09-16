"""
File Routes

API methods for CRUD operations on File models, nested under a receipt.
"""

import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Body, Form, UploadFile, File as UploadFileParam
from pydantic import BaseModel, Field
from sqlmodel import Session

from airpas.config.database import request_db
from airpas.config.storage import save_upload
from airpas.models.file import FileRead, FileNestedCreate, FileCreate, FileUpdate
from airpas.models.receipt import ReceiptRead
from airpas.services.files import FileService
from airpas.services.receipt_processing import ReceiptProcessingService
from airpas.lib.util_schemas import HttpStatusSchema

router = APIRouter()


class FileListResponse(BaseModel):
    data: List[FileRead] = Field(..., description="List of files.")
    count: int = Field(..., description="Total count of files for the receipt.")


###
# File Index
# Get all files for a receipt
###
@router.get("/", tags=["Files"], response_model=FileListResponse)
async def list_files(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to list files for"),
    skip: int = 0,
    limit: int = 200,
):
    """Return a list of files for a receipt and total count."""
    service = FileService(db)
    files = service.get_by_receipt(receipt_id, skip=skip, limit=limit)
    return FileListResponse(data=files, count=len(files))


###
# File Get
# Get a single file by ID
###
@router.get("/{file_id}", tags=["Files"], response_model=FileRead)
async def get_file(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the file belongs to"),
    file_id: UUID = Path(..., description="The ID of the file to retrieve"),
):
    """Return a single file by ID."""
    return FileService(db).get(file_id)


###
# File Create
# Create a new file on a receipt
###
@router.post("/", tags=["Files"], response_model=FileRead)
async def create_file(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to add the file to"),
    file: FileNestedCreate = Body(..., description="The file data to create"),
):
    """Create a new file on the given receipt."""
    return FileService(db).create(FileCreate(receipt_id=receipt_id, **file.model_dump()))


###
# File Upload
# Upload a PDF/image file to local storage and create its File record
###
@router.post("/upload", tags=["Files"], response_model=FileRead)
async def upload_file(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to attach the uploaded file to"),
    uploaded_by_id: UUID = Form(..., description="The ID of the user uploading the file"),
    upload: UploadFile = UploadFileParam(..., description="The PDF or image file to upload"),
):
    """Upload a PDF or image file to local storage and create a corresponding File record."""
    name, content_type, url = save_upload(upload)
    return FileService(db).create(
        FileCreate(receipt_id=receipt_id, uploaded_by_id=uploaded_by_id, name=name, type=content_type, url=url)
    )


###
# File Update
# Update an existing file by ID
###
@router.patch("/{file_id}", tags=["Files"], response_model=FileRead)
async def update_file(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the file belongs to"),
    file_id: UUID = Path(..., description="The ID of the file to update"),
    file: FileUpdate = Body(..., description="The file data to update"),
):
    """Update an existing file."""
    return FileService(db).update(file_id, file)


###
# File Delete
# Delete a file by ID
###
@router.delete("/{file_id}", tags=["Files"], response_model=HttpStatusSchema)
async def delete_file(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the file belongs to"),
    file_id: UUID = Path(..., description="The ID of the file to delete"),
):
    """Delete a file by ID."""
    FileService(db).delete(file_id)
    return HttpStatusSchema(ok=True, ts=datetime.datetime.now(), message=f"File {file_id} deleted successfully")


###
# File Process
# Run (mock) AI extraction on an uploaded file and apply results to the receipt
###
@router.post("/{file_id}/process", tags=["Files"], response_model=ReceiptRead)
async def process_file(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the file belongs to"),
    file_id: UUID = Path(..., description="The ID of the uploaded file to process"),
):
    """Send the uploaded file to the (mock) AI service and populate the receipt with the extracted data."""
    return ReceiptProcessingService(db).process(receipt_id, file_id)
