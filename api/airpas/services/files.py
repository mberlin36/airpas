"""
File Service
"""

from uuid import UUID

from sqlmodel import select
from sqlmodel import Session

from airpas.models.file import File, FileCreate, FileUpdate
from airpas.services.base import BaseService


class FileService(BaseService):
    def __init__(self, _db: Session, auto_commit: bool = True):
        self.auto_commit = auto_commit
        self._db = _db
        super().__init__(_db, File, FileCreate, FileUpdate, auto_commit)

    def get_by_receipt(self, receipt_id: UUID, skip: int = 0, limit: int = 200):
        """Get all files belonging to the given receipt."""
        statement = select(File).where(File.receipt_id == receipt_id).offset(skip).limit(limit)
        return self.select_all(statement)
