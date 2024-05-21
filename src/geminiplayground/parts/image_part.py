import logging
import typing
from pathlib import Path
from tempfile import TemporaryFile

from geminiplayground.catching import cache
from geminiplayground.core import GeminiClient
from geminiplayground.schemas import UploadFile
from geminiplayground.utils import get_expire_time
from geminiplayground.utils import get_file_name_from_path
from geminiplayground.utils import get_image_from_anywhere

from .multimodal_part import MultimodalPart

logger = logging.getLogger("rich")


def upload_image(
    image_path: typing.Union[str, Path], gemini_client: GeminiClient = None
):
    """
    Upload an image to Gemini
    :param gemini_client: The Gemini client
    :param image_path: The path to the image
    :return:
    """
    pil_image = get_image_from_anywhere(image_path)
    image_filename = get_file_name_from_path(image_path)

    with TemporaryFile(image_filename) as temp_file:
        pil_image.save(temp_file)
        upload_file = UploadFile.from_path(
            temp_file, body={"file": {"displayName": image_filename}}
        )
        uploaded_file = gemini_client.upload_file(upload_file)
        return uploaded_file


class ImageFile(MultimodalPart):
    """
    Image File Part implementation
    """

    def __init__(self, image_path: typing.Union[str, Path], **kwargs):
        self.image_path = image_path
        self.image_name = get_file_name_from_path(image_path)
        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def upload(self):
        """
        Upload the image to Gemini
        :return:
        """
        if cache.get(self.image_name):
            cached_file = cache.get(self.image_name)
            return [cached_file]

        delta_t = get_expire_time()
        uploaded_file = upload_image(self.image_path, self.gemini_client)
        cache.set(self.image_name, uploaded_file, expire=delta_t)
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
        Force the upload of the image
        :return:
        """
        self.delete()
        self.upload()

    def delete(self):
        """
        Delete the image from Gemini
        :return:
        """
        if cache.get(self.image_name):
            cached_file = cache.get(self.image_name)
            self.gemini_client.delete_file(cached_file.name)
            # remove the cached file
            cache.delete(self.image_name)

    def clear_cache(self):
        """
        Clear the cache
        :return:
        """
        cache.delete(self.image_name)

    def content_parts(self):
        """
        Get the content parts for the image
        :return:
        """
        return list(map(lambda f: f.to_file_part(), self.files))
