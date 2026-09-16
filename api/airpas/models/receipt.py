"""
SQLModel models for the Receipt and ReceiptLine tables.
"""

import enum
from typing import Optional, List
from uuid import UUID

from sqlmodel import Field, Column, Relationship
from sqlalchemy.types import String, Text, Numeric, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as sa_UUID
from sqlalchemy import ForeignKey

from airpas.models.base import BaseCreate, BaseLineRead, BaseModel, BaseRead, BaseUpdate
from airpas.models.file import File, FileRead


class ReceiptStatus(str, enum.Enum):
    """Workflow status of a receipt."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    REVIEW = "review"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReceiptLineBase:
    item: str = Field(
        ...,
        sa_column=Column(String(255), nullable=False),
        description="Name/description of the line item.",
    )
    value: float = Field(
        ...,
        sa_column=Column(Numeric(12, 2), nullable=False),
        description="Monetary value of the line item.",
    )
    note: Optional[str] = Field(
        None,
        sa_column=Column(Text, nullable=True),
        description="Optional note for the line item.",
    )
    receipt_id: UUID = Field(
        ...,
        sa_column=Column(sa_UUID, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
        description="ID of the receipt this line belongs to.",
    )


class ReceiptLine(BaseModel, ReceiptLineBase, table=True):
    __tablename__ = "receipt_lines"  # type: ignore[assignment]

    receipt: "Receipt" = Relationship(back_populates="receipt_lines")

    # override methods

    # model specific methods


class ReceiptLineLineRead(BaseLineRead, ReceiptLineBase):
    pass


class ReceiptLineRead(BaseRead, ReceiptLineLineRead):
    pass


class ReceiptLineCreate(BaseCreate, ReceiptLineBase):
    pass


class ReceiptLineNestedCreate(BaseCreate):
    """Line payload used when submitting lines alongside a new receipt (receipt_id is implied)."""

    item: str
    value: float
    note: Optional[str] = None


class ReceiptLineUpdate(BaseUpdate):
    item: Optional[str] = None
    value: Optional[float] = None
    note: Optional[str] = None


class ReceiptBase:
    vendor_name: str = Field(
        ...,
        sa_column=Column(String(255), nullable=False),
        description="Name of the vendor on the receipt.",
    )
    notes: Optional[str] = Field(
        None,
        sa_column=Column(Text, nullable=True),
        description="Optional notes about the receipt.",
    )
    submitter_id: UUID = Field(
        ...,
        sa_column=Column(sa_UUID, ForeignKey("users.id"), nullable=False),
        description="ID of the user who submitted the receipt.",
    )
    reviewer_id: UUID = Field(
        ...,
        sa_column=Column(sa_UUID, ForeignKey("users.id"), nullable=False),
        description="ID of the admin user assigned to review the receipt.",
    )
    status: ReceiptStatus = Field(
        default=ReceiptStatus.UPLOADED,
        sa_column=Column(
            SAEnum(ReceiptStatus, name="receipt_status", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
            nullable=False,
            server_default=ReceiptStatus.UPLOADED.value,
        ),
        description="Current workflow status of the receipt.",
    )


class Receipt(BaseModel, ReceiptBase, table=True):
    __tablename__ = "receipts"  # type: ignore[assignment]

    receipt_lines: List["ReceiptLine"] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    files: List["File"] = Relationship(
        back_populates="receipt",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # override methods

    # model specific methods


class ReceiptRead(BaseRead, ReceiptBase):
    receipt_lines: List[ReceiptLineRead] = []
    files: List[FileRead] = []


class ReceiptCreate(BaseCreate, ReceiptBase):
    receipt_lines: List[ReceiptLineNestedCreate] = []


class ReceiptUpdate(BaseUpdate):
    vendor_name: Optional[str] = None
    notes: Optional[str] = None
    submitter_id: Optional[UUID] = None
    reviewer_id: Optional[UUID] = None
    status: Optional[ReceiptStatus] = None
