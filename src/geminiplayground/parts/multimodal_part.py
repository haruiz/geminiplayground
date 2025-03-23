import time
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from yaspin import yaspin
from google.genai.types import GenerateContentConfig, GenerateContentConfigOrDict

from geminiplayground.core import GeminiClient
from geminiplayground.utils import FileUtils, LibUtils, Cacheable
from geminiplayground.utils.prompts import SUMMARIZATION_SYSTEM_INSTRUCTION
from geminiplayground.catching import cache

logger = logging.getLogger(__name__)


class MultimodalPart(ABC):
    """
    Abstract base class for multimodal parts used in Gemini interactions.

    Subclasses must implement `content_parts()`, which returns a list of multimodal input elements.
    """

    def __init__(self, gemini_client: GeminiClient = None, *args, **kwargs):
        self._gemini_client = gemini_client or GeminiClient(*args, **kwargs)

    def summarize(
            self,
            model: str,
            stream: bool = False,
            config: GenerateContentConfigOrDict = None
    ):
        """
        Generate a summary for this multimodal part.

        Args:
            model: Gemini model ID.
            stream: Whether to stream the response.
            config: Optional content generation config.

        Returns:
            The Gemini-generated summary (stream or single response).
        """
        prompt = ["Summarize the following content:"] + self.content_parts()
        config = config or {}
        if isinstance(config, GenerateContentConfig):
            config = config.to_json_dict()

        config.setdefault("system_instruction", SUMMARIZATION_SYSTEM_INSTRUCTION)
        return self._gemini_client.generate_response(model, prompt, config=config, stream=stream)

    @abstractmethod
    def content_parts(self, **kwargs) -> list:
        """
        Generate Gemini-compatible content parts from the multimodal input.

        Returns:
            A list of multimodal components.
        """
        raise NotImplementedError("Subclasses must implement the 'content_parts' method.")


@Cacheable(cache, "_file_path")
class MultiModalPartFile(MultimodalPart):
    """
    Concrete class for a single file input (image, audio, video, etc.).

    This class automatically uploads the file to Gemini and caches the upload result.
    """

    def __init__(self, file_path: Union[str, Path], gemini_client: GeminiClient = None):
        super().__init__(gemini_client)
        self._file_path = Path(file_path)

    @property
    def local_path(self) -> Path:
        """
        Return the resolved local path of the file.
        """
        return self._file_path

    @property
    def remote_file(self):
        """
        Get the uploaded Gemini file, using cache if available.

        Returns:
            The uploaded file object from Gemini.

        Raises:
            Exception: If the upload fails.
        """
        if self.in_cache(self._file_path):
            logger.info(f"[Cache Hit] Using cached Gemini file for {self._file_path}")
            return self.get_cache(self._file_path)

        return self.upload()

    def upload(self):
        """
        Upload the file to Gemini and cache the result.

        Returns:
            The uploaded file object from Gemini.

        Raises:
            Exception: If the upload fails.
        """
        with yaspin(text=f"Uploading file: {self._file_path}") as sp:
            with FileUtils.solve_file_path(self._file_path) as path:
                uploaded_file = self._gemini_client.upload_file(path)

                while uploaded_file.state.name == "PROCESSING":
                    logger.info(f"Waiting for Gemini to process file: {uploaded_file.name}")
                    time.sleep(10)
                    uploaded_file = self._gemini_client.get_file(uploaded_file.name)

                if uploaded_file.state.name == "FAILED":
                    sp.fail("❌")
                    raise Exception(f"Gemini failed to process file: {uploaded_file.name}")

                delta_t = LibUtils.get_uploaded_file_exp_date_delta_t(uploaded_file)
                self.set_cache(self._file_path, uploaded_file, expire=delta_t)
                sp.ok("✅")
                logger.info(f"Upload complete: {uploaded_file.name} (expires in {delta_t:.0f}s)")
                return uploaded_file

    def delete(self):
        """
        Delete the uploaded file from Gemini and clear local cache.
        """
        if self.in_cache(self._file_path):
            cached_file = self.get_cache(self._file_path)
            try:
                self._gemini_client.delete_file(cached_file.name)
                logger.info(f"Deleted file from Gemini: {cached_file.name}")
            except Exception as e:
                logger.warning(f"Failed to delete file from Gemini: {e}")

        self.clear_cache()
        logger.info(f"Cleared cache for: {self._file_path}")

    def content_parts(self, **kwargs) -> list:
        """
        Return this file as a content part for a Gemini prompt.

        Returns:
            A list containing the uploaded file.
        """
        return [self.remote_file]
