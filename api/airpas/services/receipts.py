"""
Receipt Service
"""

from uuid import UUID

from sqlmodel import Session

from airpas.models.receipt import Receipt, ReceiptCreate, ReceiptUpdate, ReceiptLineCreate, ReceiptStatus
from airpas.models.user import User
from airpas.lib.exceptions import InvalidReviewerException, InvalidRejectionException, NotFoundException
from airpas.services.base import BaseService
from airpas.services.receipt_lines import ReceiptLineService


class ReceiptService(BaseService):
    def __init__(self, _db: Session, auto_commit: bool = True):
        self.auto_commit = auto_commit
        self._db = _db
        super().__init__(_db, Receipt, ReceiptCreate, ReceiptUpdate, auto_commit)

    def create(self, create_instance: ReceiptCreate) -> Receipt:
        """Create a receipt, confirming the assigned reviewer is an admin, along with any lines submitted alongside it."""
        self._validate_reviewer(create_instance.reviewer_id)

        data = create_instance.model_dump()
        lines_data = data.pop("receipt_lines", [])
        receipt = super().create(ReceiptCreate(**data))

        line_service = ReceiptLineService(self._db, self._auto_commit)
        for line in lines_data:
            line_service.create(ReceiptLineCreate(receipt_id=receipt.id, **line))

        receipt.refresh()
        return receipt

    def update(self, instance_id: UUID, update_instance: ReceiptUpdate) -> Receipt:
        """Update a receipt, confirming the reviewer is an admin if changed, and notes are present if rejecting."""
        fields_set = update_instance.model_fields_set
        if fields_set and "reviewer_id" in fields_set:
            self._validate_reviewer(update_instance.reviewer_id)

        if update_instance.status == ReceiptStatus.REJECTED:
            existing = self.get(instance_id)
            effective_notes = update_instance.notes if "notes" in fields_set else existing.notes
            if not effective_notes or not effective_notes.strip():
                raise InvalidRejectionException()

        return super().update(instance_id, update_instance)

    def _validate_reviewer(self, reviewer_id) -> None:
        """Confirm the given reviewer_id belongs to an admin user."""
        reviewer = self._db.get(User, reviewer_id)
        if reviewer is None:
            raise NotFoundException(model="User", id=reviewer_id)
        if not reviewer.is_admin:
            raise InvalidReviewerException(reviewer_id=reviewer_id)
