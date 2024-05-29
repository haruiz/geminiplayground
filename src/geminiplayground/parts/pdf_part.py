import logging
import typing
import validators
import urllib.request
from geminiplayground.parts import ImageFile
from geminiplayground.core.gemini_client import GeminiClient
from geminiplayground.schemas import TextPart
from .multimodal_part import MultimodalPart
from geminiplayground.utils import normalize_url
from geminiplayground.utils import get_file_name_from_path
from pathlib import Path
from urllib.error import HTTPError
from typing import List
import pymupdf
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger("rich")


def get_pdf_from_url(url: str) -> str:
    """
    Create a pdf from url and return it
    """
    logging.info(f"getting pdf from url: {url}")
    http_uri = normalize_url(url)
    try:
        assert validators.url(http_uri), "invalid url"
        file_name, _ = urllib.request.urlretrieve(url)
        logger.info(f"Temporary file was saved in {file_name}")
        return file_name
    except HTTPError as err:
        if err.strerror == 404:
            raise Exception("PDF not found")
        elif err.code in [403, 406]:
            raise Exception("PDF document, it can not be reached")
        else:
            raise


def get_pdf_from_anywhere(uri_or_path: typing.Union[str, Path]) -> str:
    """
    read a pdf from an url or local file and return it
    """
    logging.info(f"getting pdf from anywhere: {uri_or_path}")
    uri_or_path = str(uri_or_path)
    if validators.url(uri_or_path):
        return get_pdf_from_url(uri_or_path)
    return uri_or_path


class PdfFile(MultimodalPart):
    """
    PDF file part implementation
    """

    def __init__(self, pdf_path: typing.Union[str, Path], **kwargs):
        self.pdf_path = pdf_path
        self.pdf_name = get_file_name_from_path(pdf_path)
        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def __get_pdf_parts(self) -> List[TextPart]:
        """
        Get the content parts for the pdf
        :return: List[TextPart]
        """
        parts = []
        pdf_path = get_pdf_from_anywhere(self.pdf_path)
        pdf = pymupdf.open(pdf_path)
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            part_page = TextPart(text=(f'## Page {page_index} ##'))
            parts.append(part_page)
            parts.append(self._extract_text_from_page(page))
            parts.extend(self._extract_images(pdf, page, page_index))
        return parts

    def content_parts(self):
        """
        Get the content parts for the pdf
        :return:
        """
        return self.__get_pdf_parts()

    def _extract_images(self, pdf, page, page_index: int):
        image_list = page.get_images()
        images = []
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = pymupdf.Pixmap(pdf, xref)
            if pix.n - pix.alpha > 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            file_name = f"./images/page_{page_index}-image_{image_index}.png"
            print(file_name)
            pix.save(file_name)
            pix = None
            image_file = ImageFile(file_name, gemini_client=self.gemini_client)
            images.extend(image_file.content_parts())
        return images

    def _extract_text_from_page(self, page):
        return TextPart(text=page.get_text().encode("utf8"))
