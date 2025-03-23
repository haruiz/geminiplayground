import logging
import typing

from ..multimodal_part import MultiModalPartFile
from pathlib import Path


class PdfFile(MultiModalPartFile):
    """
    Pdf file part implementation
    """

    def __init__(self, file_path: typing.Union[str, Path], gemini_client=None, **kwargs):
        super().__init__(file_path, gemini_client)
