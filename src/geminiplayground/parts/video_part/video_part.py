import json
import logging
import typing

from pydantic import BaseModel

from ..multimodal_part import MultiModalPartFile
from pathlib import Path
import google.generativeai as genai

logger = logging.getLogger("rich")


class VideoFile(MultiModalPartFile):
    """
    Audio file part implementation
    """

    def __init__(self, file_path: typing.Union[str, Path], gemini_client=None, **kwargs):
        super().__init__(file_path, gemini_client)

    def extract_keyframes(self, model: str = "models/gemini-1.5-flash-latest"):
        """
        Get the timeline of the video
        :return:
        """

        class VideoKeyFrame(BaseModel):
            """
            Video key frame
            """

            timespan: str
            description: str

        system_instruction = """you are a video processing system, follow the instructions and extract the key frames 
        in the provided video, your response should include a description of max 100 characters and the timespan of 
        each key frame"""
        prompt = ["return the key frames in the following video"] + self.prompt_parts()
        raw_response = self._gemini_client.generate_response(
            model,
            prompt,
            stream=False,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=list[VideoKeyFrame],
            ),
        )
        response = json.loads(raw_response.text)
        return response["key_frames"]
