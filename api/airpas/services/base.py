import re
from typing import Type
from uuid import UUID
from sqlmodel import Session, select

from airpas.models.base import ModelClass, CreateModelClass, UpdateModelClass
from airpas.lib.exceptions import NotFoundException


class BaseService:
    def __init__(
        self,
        _db: Session,
        model_class: Type[ModelClass],
        create_class: Type[CreateModelClass],
        update_class: Type[UpdateModelClass],
        auto_commit: bool = True,
    ):
        self._db = _db
        self._auto_commit = auto_commit
        self.model_class = model_class
        self.create_class = create_class
        self.update_class = update_class

    def __session(self):
        return self.model_class.session(self._db, self._auto_commit)

    def create(
        self,
        create_instance: CreateModelClass,
    ):
        return self.__session().create(create_instance)

    def delete(self, instance_id: UUID):
        instance = self.get(instance_id)
        return instance.delete()

    def destroy(self, instance_id: UUID):
        instance = self.get(instance_id)
        return instance.destroy()

    def get(self, instance_id: UUID):
        instance = self.__session().get(instance_id=instance_id)
        if instance is None:
            raise NotFoundException(model=self.model_class.__name__, id=instance_id)
        instance.set_session(self._db, self._auto_commit)
        return instance

    def get_all(self, skip: int = 0, limit: int = 100, sort=None, order=None):
        order_by_clause = None

        if order is not None and not isinstance(order, str):
            order_by_clause = order

        if sort is not None:
            sort_field = getattr(self.model_class, str(sort), None)

            if sort_field is None and isinstance(sort, str):
                snake_sort = re.sub(r"(?<!^)(?=[A-Z])", "_", sort).lower()
                sort_field = getattr(self.model_class, snake_sort, None)

            if sort_field is not None:
                sort_order = str(order).lower() if order is not None else "asc"
                order_by_clause = sort_field.desc() if sort_order == "desc" else sort_field.asc()

        statement = select(self.model_class)
        if order_by_clause is not None:
            statement = statement.order_by(order_by_clause)
        statement = statement.offset(skip).limit(limit)
        return self.__session().select_all(statement)

    def save(self, instance_id: UUID):
        instance = self.get(instance_id)
        return instance.save()

    def update(self, instance_id: UUID, update_instance: UpdateModelClass):
        instance = self.get(instance_id)
        return instance.update(update_instance)

    def total(self, count_field: str = "id", statement=None):
        return self.__session().total(count_field=count_field, statement=statement)

    def first(self, statement):
        return self.__session().first(statement)

    def select_all(self, statement):
        return self.__session().select_all(statement)
