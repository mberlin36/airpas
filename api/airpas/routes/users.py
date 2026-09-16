"""
User Routes

API methods for CRUD operations on User models
"""

import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Body
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from airpas.config.database import request_db
from airpas.models.user import User, UserRead, UserLineRead, UserCreate, UserUpdate
from airpas.services.users import UserService
from airpas.lib.util_schemas import HttpStatusSchema

router = APIRouter()


class UserListResponse(BaseModel):
    data: List[UserLineRead] = Field(..., description="List of users.")
    count: int = Field(..., description="Total count of users.")


###
# User Index
# Get all users, with optional pagination and sorting. Pass `email` to look up a single user by email,
# or `is_admin` to filter to admin/non-admin users (e.g. for a reviewer picker).
###
@router.get("/", tags=["Users"], response_model=UserListResponse)
async def list_users(
    *,
    db: Session = Depends(request_db),
    skip: int = 0,
    limit: int = 200,
    sort: str = "last_name",
    order: str = "asc",
    email: Optional[str] = None,
    is_admin: Optional[bool] = None,
):
    """Return a list of users and total count, optionally filtered by email or admin status."""
    service = UserService(db)
    if email is not None:
        user = service.get_by_email(email)
        users = [user] if user else []
        return UserListResponse(data=users, count=len(users))

    if is_admin is not None:
        statement = select(User).where(User.is_admin == is_admin)
        sort_field = getattr(User, sort, User.last_name)
        statement = statement.order_by(sort_field.desc() if order == "desc" else sort_field.asc())
        users = service.select_all(statement.offset(skip).limit(limit))
        count = service.total("id", statement)
        return UserListResponse(data=users, count=count)

    users = service.get_all(skip=skip, limit=limit, sort=sort, order=order)
    count = service.total("id")
    return UserListResponse(data=users, count=count)


###
# User Get
# Get a single user by ID
###
@router.get("/{user_id}", tags=["Users"], response_model=UserRead)
async def get_user(
    *,
    db: Session = Depends(request_db),
    user_id: UUID = Path(..., description="The ID of the user to retrieve"),
):
    """Return a single user by ID."""
    return UserService(db).get(user_id)


###
# User Create
# Create a new user
###
@router.post("/", tags=["Users"], response_model=UserRead)
async def create_user(
    *,
    db: Session = Depends(request_db),
    user: UserCreate = Body(..., description="The user data to create"),
):
    """Create a new user."""
    return UserService(db).create(user)


###
# User Update
# Update an existing user by ID
###
@router.patch("/{user_id}", tags=["Users"], response_model=UserRead)
async def update_user(
    *,
    db: Session = Depends(request_db),
    user_id: UUID = Path(..., description="The ID of the user to update"),
    user: UserUpdate = Body(..., description="The user data to update"),
):
    """Update an existing user."""
    return UserService(db).update(user_id, user)


###
# User Delete
# Delete a user by ID
###
@router.delete("/{user_id}", tags=["Users"], response_model=HttpStatusSchema)
async def delete_user(
    *,
    db: Session = Depends(request_db),
    user_id: UUID = Path(..., description="The ID of the user to delete"),
):
    """Delete a user by ID."""
    UserService(db).delete(user_id)
    return HttpStatusSchema(ok=True, ts=datetime.datetime.now(), message=f"User {user_id} deleted successfully")
