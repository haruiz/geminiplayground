import mimetypes
import typing
from pathlib import Path

from .audio_part import AudioFile
from .image_part import ImageFile
from .pdf_part import PdfFile
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
                return ImageFile(path, **kwargs)
            if mime_type.startswith("video"):
                return VideoFile(path, **kwargs)
            if mime_type.startswith("audio"):
                return AudioFile(path, **kwargs)
            if mime_type.startswith("pdf"):
                return PdfFile(path, **kwargs)
        raise ValueError(f"Unsupported file type: {path}")
