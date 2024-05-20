import logging
import typing
from pathlib import Path

import validators

from geminiplayground.catching import cache
from geminiplayground.core.gemini_client import GeminiClient
from geminiplayground.schemas import TextPart, UploadFile
from geminiplayground.utils import (
    extract_video_frame_count,
    beautify_file_size,
    get_file_size,
    extract_video_duration,
    extract_video_frames,
    TemporaryDirectory,
    seconds_to_time_string,
    get_timestamp_seconds,
    get_expire_time,
    get_file_name_from_path

)
from .multimodal_part import MultimodalPart

logger = logging.getLogger("rich")


def upload_video(video_path: typing.Union[str, Path], gemini_client: GeminiClient = None):
    """
    Upload an image to Gemini
    :param gemini_client: The Gemini client
    :param video_path: The path to the image
    :return:
    """
    video_path = Path(video_path)
    num_frames = extract_video_frame_count(video_path)
    duration = extract_video_duration(video_path)
    logger.info(f"Uploading video {video_path}")
    logger.info(f"File size: {beautify_file_size(get_file_size(video_path))}")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"Number of frames: {num_frames}")

    with TemporaryDirectory(video_path.stem) as temp_dir:
        frames_files = extract_video_frames(video_path, temp_dir)
        frames_upload_files = [UploadFile.from_path(file_path, body={"file": {"displayName": file_path.name}}) for
                               file_path in frames_files]
        uploaded_files_timestamp = [
            seconds_to_time_string(get_timestamp_seconds(file_path.name, "_frame"))
            for file_path in frames_files]
        uploaded_files = gemini_client.upload_files(*frames_upload_files)
        return list(zip(uploaded_files, uploaded_files_timestamp))


class VideoFile(MultimodalPart):
    """
    Video part implementation
    """

    def __init__(self, video_path: typing.Union[str, Path], **kwargs):

        # Set the output directory for the frames
        if validators.url(video_path):
            raise ValueError("Videos from URLs are not supported yet")
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file {self.video_path} not found")
        self.video_name = get_file_name_from_path(video_path)
        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def upload(self):
        """
        Upload the image to Gemini
        :return:
        """
        if cache.get(self.video_name):
            return cache.get(self.video_name)

        delta_t = get_expire_time()
        uploaded_files = upload_video(self.video_path, self.gemini_client)
        cache.set(self.video_name, uploaded_files, expire=delta_t)
        return uploaded_files

    def clear_cache(self):
        """
        Clear the cache
        :return:
        """
        cache.delete(self.video_name)

    @property
    def files(self):
        """
        Get the files
        :return:
        """
        return self.upload()

    def delete(self):
        """
        Delete the image from Gemini
        :return:
        """
        if cache.get(self.video_name):
            cached_file = cache.get(self.video_name)
            files2delete = [file.name for file, _ in cached_file]
            self.gemini_client.delete_files(*files2delete)
            cache.delete(self.video_name)

    def force_upload(self):
        """
        Force upload the image to Gemini
        :return:
        """
        self.delete()
        self.upload()

    def content_parts(self):
        """
        Get the content parts for the video
        :return:
        """
        parts = []
        for file, timespan in self.files:
            parts.extend([TextPart(text=timespan), file.to_file_part()])
        return parts
