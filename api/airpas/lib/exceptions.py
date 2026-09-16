"""
Exception Handling
"""

from typing import Any, Optional

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse


class NotFoundException(Exception):
    """Data record could not be found."""

    def __init__(self, model: Optional[str] = None, id: Optional[Any] = None, message: Optional[str] = None):
        self.model = model
        self.id = id
        self.message = f"Unable to locate {self.model} with ID {self.id}." if not message else message


class NoCurrentDbSession(Exception):
    """Unable to perform actions without a database session attached."""

    def __init__(self):
        self.message = "Unable to perform action without database session attached."


class AuthenticationError(Exception):
    def __init__(self):
        self.message = "Not Authenticated"


class AuthorizationError(Exception):
    def __init__(self, model: str, id: str):
        self.message = "Not Authorized"
        self.model = model
        self.id = id


class UnexpectedIdChangeException(Exception):
    """Unexpected attempt to change the ID of a database record."""

    def __init__(self, model: Optional[str] = None, id: Optional[int] = None, message: Optional[str] = None):
        self.model = model
        self.id = id
        if message is None:
            self.message = f"Unexpected attempt change ID of {self.model} with ID {self.id}."
        else:
            self.message = message


class InvalidReviewerException(Exception):
    """The assigned reviewer is not an admin user."""

    def __init__(self, reviewer_id: Optional[Any] = None, message: Optional[str] = None):
        self.reviewer_id = reviewer_id
        self.message = message or f"User {reviewer_id} is not an admin and cannot be assigned as a reviewer."


class InvalidRejectionException(Exception):
    """A receipt cannot be rejected without review notes explaining why."""

    def __init__(self, message: Optional[str] = None):
        self.message = message or "Notes are required to reject a receipt."


def attach_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundException)
    def _not_found_exception_handler(request: Request, exc: NotFoundException):
        return JSONResponse(status_code=404, content={"detail": exc.message or f"Unable to locate {exc.model}"})

    @app.exception_handler(AuthorizationError)
    def _not_authorized_exception_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(status_code=403, content={"detail": exc.message or "Not Authorized"})

    @app.exception_handler(InvalidReviewerException)
    def _invalid_reviewer_exception_handler(request: Request, exc: InvalidReviewerException):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(InvalidRejectionException)
    def _invalid_rejection_exception_handler(request: Request, exc: InvalidRejectionException):
        return JSONResponse(status_code=400, content={"detail": exc.message})