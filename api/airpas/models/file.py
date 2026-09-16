"""
SQLModel model for the File table.
"""

from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Column, Relationship
from sqlalchemy.types import String
from sqlalchemy.dialects.postgresql import UUID as sa_UUID
from sqlalchemy import ForeignKey

from airpas.models.base import BaseCreate, BaseLineRead, BaseModel, BaseRead, BaseUpdate

if TYPE_CHECKING:
    from airpas.models.receipt import Receipt


class FileBase:
    name: str = Field(
        ...,
        sa_column=Column(String(255), nullable=False),
        description="Original name of the uploaded file.",
    )
    type: str = Field(
        ...,
        sa_column=Column(String(100), nullable=False),
        description="MIME type of the uploaded file.",
    )
    url: str = Field(
        ...,
        sa_column=Column(String(2048), nullable=False),
        description="Storage URL/path where the file can be retrieved.",
    )
    receipt_id: UUID = Field(
        ...,
        sa_column=Column(sa_UUID, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
        description="ID of the receipt this file belongs to.",
    )
    uploaded_by_id: UUID = Field(
        ...,
        sa_column=Column(sa_UUID, ForeignKey("users.id"), nullable=False),
        description="ID of the user who uploaded the file.",
    )


class File(BaseModel, FileBase, table=True):
    __tablename__ = "files"  # type: ignore[assignment]

    receipt: "Receipt" = Relationship(back_populates="files")

    # override methods

    # model specific methods


class FileLineRead(BaseLineRead, FileBase):
    pass


class FileRead(BaseRead, FileLineRead):
    pass


class FileCreate(BaseCreate, FileBase):
    pass


class FileNestedCreate(BaseCreate):
    """File payload used when submitting files alongside a new receipt (receipt_id is implied)."""

    name: str
    type: str
    url: str
    uploaded_by_id: UUID


class FileUpdate(BaseUpdate):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
