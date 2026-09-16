"""
Utility Schema

Pydantic schema for common, non-model use cases.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class HttpStatusSchema(BaseModel):
    ok: bool = Field(..., description="Status analysis for the application")
    ts: datetime = Field(..., description="Timestamp at which status request was performed")
    message: Optional[str] = Field(None, description="Optional message to end user.")


class SuccessSchema(BaseModel):
    ok: bool = Field(..., description="Status value")
