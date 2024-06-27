import logging
import typing

from pathlib import Path
from ..multimodal_part import MultiModalPartFile

logger = logging.getLogger("rich")


class ImageFile(MultiModalPartFile):
    """
    Audio file part implementation
    """

    def __init__(self, file_path: typing.Union[str, Path], gemini_client=None, **kwargs):
        super().__init__(file_path, gemini_client)
