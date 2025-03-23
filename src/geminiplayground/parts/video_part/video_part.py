import json
import logging
from pathlib import Path
from typing import Union

from google.genai.types import GenerateContentConfig
from pydantic import BaseModel, ValidationError

from ..multimodal_part import MultiModalPartFile

logger = logging.getLogger("rich")


class VideoKeyFrame(BaseModel):
    """
    A keyframe segment identified in the video.
    """
    timespan: str
    description: str


class VideoFile(MultiModalPartFile):
    """
    Represents a video file used in multimodal prompting.

    Provides utilities to extract keyframes using Gemini.
    """

    def __init__(self, file_path: Union[str, Path], gemini_client=None, **kwargs):
        super().__init__(file_path, gemini_client)

    def extract_keyframes(
            self,
            model: str = "models/gemini-1.5-flash-latest"
    ) -> list[VideoKeyFrame]:
        """
        Use Gemini to extract keyframes from a video.

        Args:
            model: Gemini model to use (default: Gemini 1.5 Flash).

        Returns:
            A list of VideoKeyFrame objects.

        Raises:
            ValueError: If the response is not valid JSON or doesn't match the expected schema.
        """
        system_instruction = (
            "You are a video processing system. Extract the keyframes in the provided video. "
            "Each keyframe should include a timespan and a description (max 100 characters). "
            "Respond using JSON."
        )

        prompt = ["Return the keyframes in the following video:"] + self.content_parts()

        logger.info(f"Sending video to Gemini model: {model}")
        raw_response = self._gemini_client.generate_response(
            model=model,
            prompt=prompt,
            stream=False,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=list[VideoKeyFrame],
                system_instruction=system_instruction
            ),
        )

        try:
            data = json.loads(raw_response.text)
            return [VideoKeyFrame(**frame) for frame in data]
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            logger.error(f"Failed to parse keyframes: {e}")
            raise ValueError("Invalid response format received from Gemini.")
