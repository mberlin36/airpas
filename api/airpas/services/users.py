"""
User Service
"""

from sqlmodel import select
from sqlmodel import Session

from airpas.models.user import UserCreate, UserUpdate, User
from airpas.services.base import BaseService


class UserService(BaseService):
    def __init__(self, _db: Session, auto_commit: bool = True):
        self.auto_commit = auto_commit
        self._db = _db
        super().__init__(_db, User, UserCreate, UserUpdate, auto_commit)

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        statement = select(User).where(User.email == email)
        return self.first(statement)
