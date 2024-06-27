from abc import ABC, abstractmethod
from geminiplayground.core import GeminiClient
import time
import typing
from pathlib import Path

from geminiplayground.utils import FileUtils, LibUtils, Cacheable
from geminiplayground.utils.prompts import SUMMARIZATION_SYSTEM_INSTRUCTION
from geminiplayground.catching import cache
from yaspin import yaspin


class MultimodalPart(ABC):
    """
    Abstract class for multimodal part
    """

    def __init__(self, gemini_client=None):
        self._gemini_client = gemini_client if gemini_client else GeminiClient()

    def summarize(self, model: str, **kwargs):
        """
        Summarize the multimodal part
        :return:
        """
        summarization_prompt = ["Summarize the following content: "] + self.content_parts()
        summarization_instructions = kwargs.get("summarization_instructions", SUMMARIZATION_SYSTEM_INSTRUCTION)
        response = self._gemini_client.generate_response(model, summarization_prompt,
                                                         system_instruction=summarization_instructions, **kwargs)
        return response.text

    @abstractmethod
    def content_parts(self, **kwargs):
        """
        transform a multimodal part into a list of content parts
        :param kwargs:
        :return:
        """
        raise NotImplementedError("Subclasses must implement the 'content_parts' method")


@Cacheable(cache, "_file_path")
class MultiModalPartFile(MultimodalPart):
    """
    A class representing a cacheable file.
    """

    def __init__(self, file_path: typing.Union[str, Path], gemini_client=None):
        super().__init__(gemini_client)
        self._file_path = file_path

    @property
    def local_path(self):
        return self._file_path

    @property
    def remote_file(self):
        """
        Get the uploaded file from cache or upload it if not cached.
        :return: The uploaded file
        :raises ValueError: If the file type is not supported
        """
        if self.in_cache(self._file_path):
            cached_file = self.get_cache(self._file_path)
            return cached_file

        return self.upload()

    def upload(self):
        """
        Upload the audio to Gemini
        :return:
        """
        with yaspin(text=f"Uploading file {self._file_path}") as sp:
            with FileUtils.solve_file_path(self._file_path) as file:
                uploaded_file = self._gemini_client.upload_file(file)
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(10)
                    uploaded_file = self._gemini_client.get_file(uploaded_file.name)
                if uploaded_file.state.name == "FAILED":
                    sp.fail("❌")
                    raise Exception("File upload failed")
                delta_t = LibUtils.get_uploaded_file_exp_date_delta_t(uploaded_file)
                # this unction is injected by the Cacheable decorator
                self.set_cache(
                    self._file_path, uploaded_file, expire=delta_t
                )
                sp.ok("✅")
                return uploaded_file

    def delete(self):
        """
        Delete the image from Gemini
        :return:
        """
        if self.in_cache(self._file_path):
            cached_file = self.get_cache(self._file_path)
            self._gemini_client.delete_file(cached_file.name)
        # this function remove any cache entry for the file
        self.clear_cache()

    def content_parts(self, **kwargs):
        return [self.remote_file]
