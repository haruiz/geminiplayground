from functools import wraps

from .orm_registry import mapper_registry
from .orm_session import SessionMaker, engine


def with_db_session(func):
    """
    Create a database session
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        wrapper function
        :param args:
        :param kwargs:
        :return:
        """
        session = SessionMaker()
        try:
            result = func(*args, session=session, **kwargs)
            session.commit()
            return result
        except:
            session.rollback()
            raise
        finally:
            session.close()

    return wrapper


def create_db():
    """
    Create all tables in the database
    :return:
    """
    print("Creating all tables")
    mapper_registry.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables in the database
    :return:
    """
    print("Dropping all tables")
    mapper_registry.metadata.drop_all(bind=engine)


def pre_populate_db():
    """
    Load initial data
    :return:
    """
