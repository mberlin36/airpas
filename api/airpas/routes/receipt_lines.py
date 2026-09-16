"""
Receipt Line Routes

API methods for CRUD operations on ReceiptLine models, nested under a receipt.
"""

import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Body
from pydantic import BaseModel, Field
from sqlmodel import Session

from airpas.config.database import request_db
from airpas.models.receipt import ReceiptLineRead, ReceiptLineNestedCreate, ReceiptLineCreate, ReceiptLineUpdate
from airpas.services.receipt_lines import ReceiptLineService
from airpas.lib.util_schemas import HttpStatusSchema

router = APIRouter()


class ReceiptLineListResponse(BaseModel):
    data: List[ReceiptLineRead] = Field(..., description="List of receipt lines.")
    count: int = Field(..., description="Total count of receipt lines for the receipt.")


###
# Receipt Line Index
# Get all lines for a receipt
###
@router.get("/", tags=["Receipt Lines"], response_model=ReceiptLineListResponse)
async def list_receipt_lines(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to list lines for"),
    skip: int = 0,
    limit: int = 200,
):
    """Return a list of lines for a receipt and total count."""
    service = ReceiptLineService(db)
    lines = service.get_by_receipt(receipt_id, skip=skip, limit=limit)
    return ReceiptLineListResponse(data=lines, count=len(lines))


###
# Receipt Line Get
# Get a single line by ID
###
@router.get("/{line_id}", tags=["Receipt Lines"], response_model=ReceiptLineRead)
async def get_receipt_line(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the line belongs to"),
    line_id: UUID = Path(..., description="The ID of the line to retrieve"),
):
    """Return a single receipt line by ID."""
    return ReceiptLineService(db).get(line_id)


###
# Receipt Line Create
# Create a new line on a receipt
###
@router.post("/", tags=["Receipt Lines"], response_model=ReceiptLineRead)
async def create_receipt_line(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to add the line to"),
    line: ReceiptLineNestedCreate = Body(..., description="The line data to create"),
):
    """Create a new line on the given receipt."""
    return ReceiptLineService(db).create(ReceiptLineCreate(receipt_id=receipt_id, **line.model_dump()))


###
# Receipt Line Update
# Update an existing line by ID
###
@router.patch("/{line_id}", tags=["Receipt Lines"], response_model=ReceiptLineRead)
async def update_receipt_line(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the line belongs to"),
    line_id: UUID = Path(..., description="The ID of the line to update"),
    line: ReceiptLineUpdate = Body(..., description="The line data to update"),
):
    """Update an existing receipt line."""
    return ReceiptLineService(db).update(line_id, line)


###
# Receipt Line Delete
# Delete a line by ID
###
@router.delete("/{line_id}", tags=["Receipt Lines"], response_model=HttpStatusSchema)
async def delete_receipt_line(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt the line belongs to"),
    line_id: UUID = Path(..., description="The ID of the line to delete"),
):
    """Delete a receipt line by ID."""
    ReceiptLineService(db).delete(line_id)
    return HttpStatusSchema(ok=True, ts=datetime.datetime.now(), message=f"Receipt line {line_id} deleted successfully")
