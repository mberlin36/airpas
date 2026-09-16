"""
Receipt Processing Service

Mocks sending an uploaded receipt image/PDF to an AI/OCR service and parsing
the response into the vendor, notes, and line item data used by the Receipt
and ReceiptLine tables.
"""

import random
from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Session

from airpas.models.file import File
from airpas.models.receipt import Receipt, ReceiptStatus, ReceiptLineNestedCreate, ReceiptLineCreate
from airpas.services.receipts import ReceiptService
from airpas.services.receipt_lines import ReceiptLineService
from airpas.services.files import FileService


class ExtractedReceiptData(BaseModel):
    """Structured data shaped like the Receipt/ReceiptLine tables, as returned by the AI service."""

    vendor_name: str
    receipt_lines: List[ReceiptLineNestedCreate]


# Mock vendor pool and lorem-ipsum word pool used to simulate varied AI OCR responses.
_MOCK_VENDORS = ["Office Depot", "Home Depot", "Staples", "Costco", "Best Buy"]
_LOREM_WORDS = [
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
    "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
    "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
    "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
    "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
    "velit", "esse", "cillum", "eu", "fugiat", "nulla", "pariatur",
]


def _mock_item_name() -> str:
    """Generate a plausible line item name from random lorem-ipsum words."""
    return " ".join(random.sample(_LOREM_WORDS, random.randint(1, 3))).title()


def mock_extract_receipt_data(file: File) -> ExtractedReceiptData:
    """
    Stand-in for a real call to an AI/OCR service: instead of reading the
    uploaded image/PDF, generate plausible mock vendor and line item data.
    """
    line_count = random.randint(2, 15)
    lines = [
        ReceiptLineNestedCreate(item=_mock_item_name(), value=round(random.uniform(1.50, 2000), 2), note=None)
        for _ in range(line_count)
    ]
    return ExtractedReceiptData(
        vendor_name=random.choice(_MOCK_VENDORS),
        receipt_lines=lines,
    )


class ReceiptProcessingService:
    """Coordinates running (mock) AI extraction against a receipt's uploaded file."""

    def __init__(self, _db: Session, auto_commit: bool = True):
        self._db = _db
        self._auto_commit = auto_commit
        self.receipt_service = ReceiptService(_db, auto_commit)
        self.receipt_line_service = ReceiptLineService(_db, auto_commit)
        self.file_service = FileService(_db, auto_commit)

    def process(self, receipt_id: UUID, file_id: UUID) -> Receipt:
        """
        Run mock AI extraction on the given file and apply the results to
        the receipt, moving its workflow status from processing to review.
        """
        receipt = self.receipt_service.get(receipt_id)
        file = self.file_service.get(file_id)

        receipt.set_attribute("status", ReceiptStatus.PROCESSING, force=True)
        receipt.save()

        extracted = mock_extract_receipt_data(file)

        # notes is reserved for the manager's review comments, so only vendor_name is applied here.
        receipt.set_attributes(force=True, vendor_name=extracted.vendor_name)
        receipt.set_attribute("status", ReceiptStatus.REVIEW, force=True)
        receipt.save()

        for line in extracted.receipt_lines:
            self.receipt_line_service.create(ReceiptLineCreate(receipt_id=receipt.id, **line.model_dump()))

        receipt.refresh()
        return receipt
