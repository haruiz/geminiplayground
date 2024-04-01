import mimetypes
import typing
from pathlib import Path


class UploadFile:
    def __init__(self, file_path: str, mimetype: str = None, body: dict = None):
        self.file_path = file_path
        self.mimetype = mimetype
        self.body = body

    @classmethod
    def from_path(cls, file_path: typing.Union[str, Path], **kwargs):
        """
        Create an UploadFile instance from a file
        :param file_path:
        :param kwargs:
        :return:
        """
        return cls(
            file_path=str(file_path),
            mimetype=mimetypes.guess_type(file_path)[0],
            **kwargs
        )

    def __str__(self):
        data_obj = vars(self)
        return str(data_obj)
