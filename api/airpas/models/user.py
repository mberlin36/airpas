"""
SQLModel model for the User table.
"""

from typing import Optional

from sqlmodel import Field, Column
from sqlalchemy.types import String, Boolean

from airpas.models.base import BaseCreate, BaseLineRead, BaseModel, BaseRead, BaseUpdate


class UserBase:
    first_name: str = Field(
        ...,
        sa_column=Column(String(50), nullable=False),
        description="First Name of user.",
    )
    last_name: str = Field(
        ...,
        sa_column=Column(String(50), nullable=False),
        description="Last Name of user.",
    )
    email: str = Field(
        ...,
        sa_column=Column(String(128), nullable=False, unique=True),
        description="User email. Will be used to login with. Must be valid",
    )
    is_admin: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
        description="Flag indicating whether the user is an admin.",
    )


class User(BaseModel, UserBase, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    # override methods

    # model specific methods

class UserLineRead(BaseLineRead, UserBase):
    pass


class UserRead(BaseRead, UserLineRead):
    pass


class UserCreate(BaseCreate, UserBase):
    pass


class UserUpdate(BaseUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None
