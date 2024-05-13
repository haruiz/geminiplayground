import logging
import typing
import validators
import urllib.request
from geminiplayground.catching import cache
from geminiplayground.core.gemini_client import GeminiClient
from geminiplayground.schemas import UploadFile
from .multimodal_part import MultimodalPart
from geminiplayground.utils import normalize_url
from geminiplayground.utils import get_file_name_from_path
from geminiplayground.utils import get_expire_time
from pathlib import Path
from urllib.error import HTTPError

logger = logging.getLogger("rich")


def get_audio_from_url(url: str) -> str:
    """
    Create an audio from url and return it
    """
    http_uri = normalize_url(url)
    try:
        assert validators.url(http_uri), "invalid url"
        file_name, _ = urllib.request.urlretrieve(url)
        logger.info(f"Temporary file was saved in {file_name}")
        return file_name
    except HTTPError as err:
        if err.strerror == 404:
            raise Exception("Audio not found")
        elif err.code in [403, 406]:
            raise Exception("Audio image, it can not be reached")
        else:
            raise


def get_audio_from_anywhere(uri_or_path: typing.Union[str, Path]) -> str:
    """
    read an audio from an url or local file and return it
    """
    uri_or_path = str(uri_or_path)
    if validators.url(uri_or_path):
        return get_audio_from_url(uri_or_path)
    return uri_or_path


def upload_audio(
        audio_path: typing.Union[str, Path],
        gemini_client: GeminiClient = None):
    """
    Upload an audio to Gemini
    :param gemini_client: The Gemini client
    :param audio_path: The path to the audio
    :return:
    """
    audio_path = get_audio_from_anywhere(audio_path)
    audio_filename = get_file_name_from_path(audio_path)

    if audio_path:
        upload_file = UploadFile.from_path(audio_path,
                                           body={"file": {"displayName": audio_filename}})
        uploaded_file = gemini_client.upload_file(upload_file)
        return uploaded_file


class AudioFile(MultimodalPart):
    """
    Audio file part implementation
    """

    def __init__(self, audio_path: typing.Union[str, Path], **kwargs):
        self.audio_path = audio_path
        self.audio_name = get_file_name_from_path(audio_path)
        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def upload(self):
        """
        Upload the audio to Gemini
        :return:
        """
        if cache.get(self.audio_name):
            cached_file = cache.get(self.audio_name)
            return [cached_file]

        delta_t = get_expire_time()
        uploaded_file = upload_audio(self.audio_path, self.gemini_client)
        cache.set(self.audio_name, uploaded_file, expire=delta_t)
        return [uploaded_file]

    @property
    def files(self):
        """
        Get the files
        :return:
        """
        return self.upload()

    def force_upload(self):
        """
        Force the upload of the audio
        :return:
        """
        self.delete()
        self.upload()

    def delete(self):
        """
        Delete the image from Gemini
        :return:
        """
        if cache.get(self.audio_name):
            cached_file = cache.get(self.audio_name)
            self.gemini_client.delete_file(cached_file.name)
            # remove the cached file
            cache.delete(self.audio_name)

    def clear_cache(self):
        """
        Clear the cache
        :return:
        """
        cache.delete(self.audio_name)

    def content_parts(self):
        """
        Get the content parts for the audio
        :return:
        """
        return list(map(lambda f: f.to_file_part(), self.files))
