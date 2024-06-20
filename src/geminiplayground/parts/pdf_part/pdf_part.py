import logging
import typing

import pymupdf
import validators

from geminiplayground.core import GeminiClient
from .. import MultimodalPart, ImageFile
from geminiplayground.utils import FileUtils, Cacheable
from pathlib import Path
from geminiplayground.catching import cache
from slugify import slugify
from langchain_core.documents import Document

logger = logging.getLogger("rich")


@Cacheable(cache, "_file_path")
class PdfFile(MultimodalPart):
    """
    PDF file part implementation
    """

    def __init__(self, file_path: typing.Union[str, Path], gemini_client: GeminiClient = None, **kwargs):
        super().__init__(gemini_client)
        self._file_path = file_path

    @Cacheable.cache_func
    def __get_pdf_parts(self) -> typing.List[typing.Any]:
        """
        Get the content parts for the pdf
        :return: list of text parts
        """
        parts = []
        with FileUtils.solve_file_path(self._file_path) as pdf_path:
            pdf = pymupdf.open(pdf_path)
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                parts.append(self._extract_page_content(page))
                parts.extend(self._extract_page_images(pdf, page))
            pdf.close()
        return parts

    def _extract_page_content(self, page):
        """
        Extract text from a page
        :param page: The page to extract text from
        :return: The extracted text
        """
        return Document(
            page_content=page.get_text(),
            metadata={
                "file_path": str(self._file_path),
                "page_number": page.number,
                "category": "Text",
            },
        )

    def _extract_page_images(self, pdf, page):
        """
        Extract images from a page
        :param page: The page to extract images from
        :return: The extracted images
        """
        file_path = str(self._file_path)
        if validators.url(file_path):
            images_folder = Path(slugify(file_path))
        else:
            file_path = Path(file_path)
            images_folder = file_path.parent / file_path.stem

        images_folder.mkdir(exist_ok=True, parents=True)
        images = []
        for image in page.get_images(full=True):
            # get the XREF of the image
            xref = image[0]
            pix = pymupdf.Pixmap(pdf, xref)
            if pix.n - pix.alpha > 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            image_path = images_folder / f"image{page.number}.png"
            pix.save(image_path)
            image = ImageFile(image_path)
            images.append(image)
            del pix
        return images

    def content_parts(self):
        """
        Get the content parts for the pdf
        :return:
        """
        return self.__get_pdf_parts()
