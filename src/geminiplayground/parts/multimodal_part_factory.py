import mimetypes
import typing
from pathlib import Path

from .image_part import ImageFile
from .video_part import VideoFile
from .audio_part import AudioFile
from .pdf_part import PdfFile


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
            mime_type: str = mimetypes.guess_type(path.as_posix())[0]
            if "image" in mime_type:
                return ImageFile(path, **kwargs)
            if "video" in mime_type:
                return VideoFile(path, **kwargs)
            if "audio" in mime_type:
                return AudioFile(path, **kwargs)
            if "pdf" in mime_type:
                return PdfFile(path, **kwargs)
        raise ValueError(f"Unsupported file type: {path}")
