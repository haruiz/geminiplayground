import logging
import ssl
import typing
import urllib.request
from pathlib import Path
from typing import List
from urllib.error import HTTPError

import validators
from geminiplayground.catching import cache
from geminiplayground.core.gemini_client import GeminiClient
from geminiplayground.schemas import TextPart
from geminiplayground.utils import get_expire_time
from geminiplayground.utils import get_file_name_from_path
from geminiplayground.utils import normalize_url
from PyPDF2 import PdfReader

from .multimodal_part import MultimodalPart

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


def read_file(path_file: str) -> List[str]:
    logger.info(f"reading file: {path_file}")
    text = []
    pdf_path = get_pdf_from_anywhere(path_file)
    with open(pdf_path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text.append(page.extract_text())
    return text


class PdfFile(MultimodalPart):
    """
    PDF file part implementation
    """

    def __init__(self, pdf_path: typing.Union[str, Path], **kwargs):
        self.pdf_path = pdf_path
        self.pdf_name = get_file_name_from_path(pdf_path)
        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def upload(self):
        """
        Read the pdf to Gemini
        :return:
        """
        if cache.get(self.pdf_name):
            cached_file = cache.get(self.pdf_name)
            return cached_file

        delta_t = get_expire_time()
        text = read_file(self.pdf_path)
        cache.set(self.pdf_name, text, expire=delta_t)
        return text

    @property
    def files(self):
        """
        Get the files
        :return:
        """
        return self.upload()

    def force_upload(self):
        """
        Force the upload of the pdf
        :return:
        """
        self.delete()
        self.upload()

    def delete(self):
        """
        Delete the pdf from Gemini
        :return:
        """
        if cache.get(self.pdf_name):
            cached_file = cache.get(self.pdf_name)
            self.gemini_client.delete_file(cached_file.name)
            # remove the cached file
            cache.delete(self.pdf_name)

    def clear_cache(self):
        """
        Clear the cache
        :return:
        """
        cache.delete(self.pdf_name)

    def content_parts(self):
        """
        Get the content parts for the pdf
        :return:
        """
        return [TextPart(text=text) for text in self.files]
