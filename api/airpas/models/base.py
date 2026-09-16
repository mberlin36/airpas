from typing import Optional, Any, TypeVar
from datetime import datetime
from uuid import UUID

from pydantic import PrivateAttr, ConfigDict
from sqlmodel import Field, SQLModel, Session, select, DateTime
from sqlmodel.sql.expression import Select, SelectOfScalar
from sqlalchemy.sql import func
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import UUID as sa_UUID

from airpas.lib.exceptions import NoCurrentDbSession, UnexpectedIdChangeException
from airpas.config.database import UUID_SERVER_DEFAULT

# Set inherit cache for sqlmodel to avoid performance issues on SQLAlchemy queries
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


class BaseModelOps(SQLModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def class_name(self):
        return self.__class__.__name__

    _db: Session = PrivateAttr()
    _auto_commit: bool = PrivateAttr(default=True)

    @classmethod
    def session(cls, db: Session, auto_commit: bool = True, **kwargs):
        """
        Prepare a session for manipulating the model, pre-initialized with keys
        and values as specified via keyword arguments. You can provide a SQLAlchemy
        database session as the db parameter, and optionally change the auto-commit
        behavior of manipulations made during the session.

        Returns a model instance of the class, prepared as requested.
        """
        return cls(**kwargs).set_session(db, auto_commit)

    def set_session(self, db: Session, auto_commit: bool = True):
        """
        Add or change the SQLAlchemy session associated with this current model and
        session. Optionally set the auto commit mode.
        """
        self._db = db
        self._auto_commit = auto_commit
        return self

    def query(self, statement):
        """
        Return base SQLModel query object for the given statement.
        param: statement: SQLModel statement to execute, e.g. select(Model).where(Model.id == some_id)
          example: select(User).where(User.email == 'example@example.com').where(User.is_active == True)
                      .order_by(User.created_at.desc()).limit(10).offset(0)
        """
        return self._db.exec(statement)

    def select_all(self, statement):
        """
        Return all results for the given statement.
        param: statement: SQLModel statement to execute, e.g. select(Model).where(Model.id == some_id)
          example: select(User).where(User.email == 'example@example.com').where(User.is_active == True)
                      .order_by(User.created_at.desc()).limit(10).offset(0)
        """
        return self.query(statement).all()

    def first(self, statement):
        """
        Return the first result for the given statement.
        param: statement: SQLModel statement to execute, e.g. select(Model).where(Model.id == some_id)
          example: select(User).where(User.email == 'example@example.com').where(User.is_active == True)
        """
        return self.query(statement).first()

    def total(self, count_field="id", statement: Optional[Select] = None):
        """
        Return the total count of results for the given statement. If no statement is provided, it will
        count all records in the table.
        param: count_field: The field to count, default is 'id'.
        param: statement: SQLModel statement to execute, e.g. select(Model).where(Model.id == some_id)
          example: select(User).where(User.email == 'example@example.com').where(User.is_active == True)
        """
        if statement is None:
            return self.query(select(func.count(getattr(self.__class__, count_field)))).one()
        # Count rows via the subquery's own columns; referencing the original mapped column here
        # (e.g. Receipt.id) instead of the subquery's column creates an uncorrelated cartesian join.
        return self.query(select(func.count()).select_from(statement.subquery())).one()

    def get(self, instance_id: Any, id_field="id"):
        """
        Return the instance of the model with the given id. If no instance is found, return None.
        param: instance_id: The id of the instance to retrieve.
        param: id_field: The field to use as the id, default is 'id'.
        """
        return self.first(select(self.__class__).where(getattr(self.__class__, id_field) == instance_id))

    @classmethod
    def attribute_names(cls) -> list[str]:
        """Returns a list of this model's field/column names."""
        return [c_attr.key for c_attr in inspect(cls).c]

    def set_attribute(self, column_name: str, value: Any, force: bool = False):
        """
        Set the indicated record attribute to the given value. By default, None
        values will be ignored, unless force is set to True.
        """
        if column_name == "id":
            raise UnexpectedIdChangeException(model=self.__class__.__name__, id=getattr(self, "id"))
        if column_name in self.attribute_names():
            if force or value is not None:
                setattr(self, column_name, value)

    def set_attributes(self, force: bool = False, **kwargs):
        """
        Given as keyword arguments, set all record attributes to their matched
        values. By default, None values will be ignored, unless force is True.
        """
        for col, val in kwargs.items():
            if issubclass(type(val), (BaseModel, BaseCreate, BaseUpdate)):
                self.set_attributes(force, **val.model_dump())
            else:
                self.set_attribute(col, val, force=force)

    def commit(self):
        """
        Commit the current transaction history to the database. Depending on the
        configuration of self.auto_commit, persist immediately or queue for persist
        in future.
        """
        if self._auto_commit:
            self._db.commit()
        else:
            self._db.flush()

    def refresh(self):
        """
        Reload this record from the database.
        """
        self._db.refresh(self)

    def save(self):
        """
        Add this record to the database session and commit according to the
        configuration of self.auto_commit.
        Handles the update of updated_at timestamp if the model has an updated_at field.
        """
        if hasattr(self, "updated_at"):
            self.updated_at = datetime.now()
        self._db.add(self)
        self.commit()
        self.refresh()
        return self

    def create(self, create_instance: "BaseCreate"):
        """
        Create a new record in the database based on the given create model instance.
        """
        if not self._db:
            raise NoCurrentDbSession()
        new_instance = self.__class__(**create_instance.model_dump())
        if hasattr(new_instance, "created_at"):
            new_instance.created_at = datetime.now()
        new_instance.set_session(self._db, self._auto_commit)
        new_instance.save()
        return new_instance

    def update(self, update_instance: "BaseUpdate"):
        """
        Update this record in the database based on the given update model instance.
        Only fields explicitly provided in the update model are applied.
        """
        if not self._db:
            raise NoCurrentDbSession()
        self.set_attributes(force=True, **update_instance.model_dump(exclude_unset=True))
        return self.save()

    def delete(self):
        """
        Delete this record from the database.
        If the model has a deleted_at field, it will be treated as a soft delete and the deleted_at timestamp will
        be set to the current time. Otherwise, the record will be hard deleted from the database.
        """
        if not self._db:
            raise NoCurrentDbSession()
        if hasattr(self, "deleted_at"):
            self.deleted_at = datetime.now()
            return self.save()
        self.destroy()

    def destroy(self):
        """
        Hard delete this record from the database, regardless of whether the model has a deleted_at field or not.
        WARNING: Use with caution, as this will permanently delete the record from the database and cannot be undone.
        """
        if not self._db:
            raise NoCurrentDbSession()
        self._db.delete(self)
        self.commit()

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of this model instance, including only the fields defined in the model.
        """
        return {col: getattr(self, col) for col in self.attribute_names()}


class BaseModel(BaseModelOps):
    id: Optional[UUID] = Field(
        None,
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
        sa_type=sa_UUID,
        sa_column_kwargs={"server_default": UUID_SERVER_DEFAULT},
    )
    created_at: datetime = Field(
        default=datetime.now(),
        sa_type=DateTime,
        sa_column_kwargs={"nullable": False},
    )
    updated_at: datetime = Field(
        default=datetime.now(),
        sa_type=DateTime,
        sa_column_kwargs={"nullable": False, "onupdate": datetime.now()},
    )
    deleted_at: Optional[datetime] = Field(
        None,
        sa_type=DateTime,
        sa_column_kwargs={"nullable": True},
        description="Ability to Soft Delete relationship between a user and role",
    )


class BaseLineRead(SQLModel):
    id: UUID = Field(..., description="Primary Key, ID of the instance")


class BaseRead(BaseLineRead):
    created_at: datetime = Field(..., description="When the instance was created")
    updated_at: datetime = Field(..., description="Last time instance was updated")
    deleted_at: Optional[datetime] = Field(None, description="When the instance was deleted")
    class_name: Optional[str] = Field(None, description="Name of the class instance is associated with")


class BaseCreate(SQLModel):
    pass


class BaseUpdate(SQLModel):
    pass


ModelClass = TypeVar("ModelClass", bound=BaseModel)
CreateModelClass = TypeVar("CreateModelClass", bound=BaseCreate)
UpdateModelClass = TypeVar("UpdateModelClass", bound=BaseUpdate)
ReadModelClass = TypeVar("ReadModelClass", bound=BaseRead)
