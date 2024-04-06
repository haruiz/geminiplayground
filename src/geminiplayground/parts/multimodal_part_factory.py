import mimetypes
import typing
from pathlib import Path

from .image_part import ImageFile
from .video_part import VideoFile


class MultimodalPartFactory:
    """
    Factory class for multimodal parts
    """

    @staticmethod
    def from_path(path: typing.Union[str, Path], **kwargs):
        """
        Create a multimodal part from a path
        :param path:
        :param kwargs:
        :return:
        """
        path = Path(path)
        if path.is_file():
            mime_type = mimetypes.guess_type(path.as_posix())[0]
            if mime_type.startswith("image"):
                return ImageFile(image_path=path, **kwargs)
            elif mime_type.startswith("video"):
                return VideoFile(video_path=path, **kwargs)
        raise ValueError(f"Unsupported file type: {path}")
