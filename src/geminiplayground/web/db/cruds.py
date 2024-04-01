# import typing
# import uuid

import typing

from geminiplayground.utils import Singleton
from .models import FileEntry
from .orm_utils import with_db_session

if typing.TYPE_CHECKING:
    from .orm_session import SessionMaker


class AppCrud(metaclass=Singleton):
    """
    This module contains the CRUD operations for the Project model.
    """

    def __init__(self):
        super().__init__()

    @with_db_session
    def save_image(self, file: FileEntry, session: "SessionMaker") -> FileEntry:
        """
        Get a project by name
        :param name: The name of the project
        :param session: The database session
        :return: The project with the given name
        """
        session.add(file)
        return file


files = AppCrud()
