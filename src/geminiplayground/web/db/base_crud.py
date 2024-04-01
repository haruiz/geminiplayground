from typing import Generic, get_args, Any, TypeVar

from .orm_utils import with_db_session

M = TypeVar("M")
S = TypeVar("S")


class BaseCrud(Generic[M, S]):
    """
    This module contains the base class for all CRUD operations.
    """

    @classmethod
    def model_cls(cls) -> M:
        """
        resolve the model class from the generic type
        :return:
        """
        model_cls, _ = get_args(cls.__orig_bases__[0])
        return model_cls

    @classmethod
    def schema_cls(cls) -> S:
        """
        resolve the schema class from the generic type
        :return:
        """
        _, schema_cls = get_args(cls.__orig_bases__[0])
        return schema_cls

    @with_db_session
    def get(self, model_id: Any, session):
        """
        Get a model by id
        :param session: The database session
        :param model_id: The id of the model
        :return: The model with the given id
        """
        model_cls = self.model_cls()
        return session.query(model_cls).get(model_id)

    @with_db_session
    def list(self, session):
        """
        Get all models
        :param session: The database session
        :return: The models
        """
        model_cls = self.model_cls()
        return session.query(model_cls).all()

    @with_db_session
    def create(self, model, session):
        """
        Save a model
        :param session: The database session
        :param model: The model to save
        :return: The saved model
        """
        session.add(model)
        return model

    @with_db_session
    def delete(self, model_id: Any, session):
        """
        Delete a model by id
        :param session: The database session
        :param model_id: The id of the model
        :return: The deleted model
        """
        model = self.get(model_id)
        session.delete(model)
        return model
