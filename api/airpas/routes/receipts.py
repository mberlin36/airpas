"""
Receipt Routes

API methods for CRUD operations on Receipt models
"""

import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Body
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from airpas.config.database import request_db
from airpas.models.receipt import Receipt, ReceiptRead, ReceiptCreate, ReceiptUpdate, ReceiptStatus
from airpas.services.receipts import ReceiptService
from airpas.lib.util_schemas import HttpStatusSchema

router = APIRouter()


class ReceiptListResponse(BaseModel):
    data: List[ReceiptRead] = Field(..., description="List of receipts.")
    count: int = Field(..., description="Total count of receipts.")


###
# Receipt Index
# Get all receipts, with optional pagination, sorting, and submitter/reviewer/status filters
###
@router.get("/", tags=["Receipts"], response_model=ReceiptListResponse)
async def list_receipts(
    *,
    db: Session = Depends(request_db),
    skip: int = 0,
    limit: int = 200,
    sort: str = "created_at",
    order: str = "desc",
    submitter_id: Optional[UUID] = None,
    reviewer_id: Optional[UUID] = None,
    status: Optional[ReceiptStatus] = None,
):
    """Return a list of receipts and total count, optionally filtered by submitter, reviewer, or status."""
    service = ReceiptService(db)

    if submitter_id is not None or reviewer_id is not None or status is not None:
        statement = select(Receipt)
        if submitter_id is not None:
            statement = statement.where(Receipt.submitter_id == submitter_id)
        if reviewer_id is not None:
            statement = statement.where(Receipt.reviewer_id == reviewer_id)
        if status is not None:
            statement = statement.where(Receipt.status == status)
        sort_field = getattr(Receipt, sort, Receipt.created_at)
        statement = statement.order_by(sort_field.desc() if order == "desc" else sort_field.asc())
        receipts = service.select_all(statement.offset(skip).limit(limit))
        count = service.total("id", statement)
        return ReceiptListResponse(data=receipts, count=count)

    receipts = service.get_all(skip=skip, limit=limit, sort=sort, order=order)
    count = service.total("id")
    return ReceiptListResponse(data=receipts, count=count)


###
# Receipt Get
# Get a single receipt by ID
###
@router.get("/{receipt_id}", tags=["Receipts"], response_model=ReceiptRead)
async def get_receipt(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to retrieve"),
):
    """Return a single receipt by ID."""
    return ReceiptService(db).get(receipt_id)


###
# Receipt Create
# Create a new receipt, optionally with lines
###
@router.post("/", tags=["Receipts"], response_model=ReceiptRead)
async def create_receipt(
    *,
    db: Session = Depends(request_db),
    receipt: ReceiptCreate = Body(..., description="The receipt data to create"),
):
    """Create a new receipt."""
    return ReceiptService(db).create(receipt)


###
# Receipt Update
# Update an existing receipt by ID
###
@router.patch("/{receipt_id}", tags=["Receipts"], response_model=ReceiptRead)
async def update_receipt(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to update"),
    receipt: ReceiptUpdate = Body(..., description="The receipt data to update"),
):
    """Update an existing receipt."""
    return ReceiptService(db).update(receipt_id, receipt)


###
# Receipt Delete
# Delete a receipt by ID (cascades to its lines)
###
@router.delete("/{receipt_id}", tags=["Receipts"], response_model=HttpStatusSchema)
async def delete_receipt(
    *,
    db: Session = Depends(request_db),
    receipt_id: UUID = Path(..., description="The ID of the receipt to delete"),
):
    """Delete a receipt by ID."""
    ReceiptService(db).delete(receipt_id)
    return HttpStatusSchema(ok=True, ts=datetime.datetime.now(), message=f"Receipt {receipt_id} deleted successfully")
