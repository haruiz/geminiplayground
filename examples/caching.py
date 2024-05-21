from pathlib import Path

from dotenv import find_dotenv
from dotenv import load_dotenv
from geminiplayground.catching import cache
from geminiplayground.core import GeminiClient
from geminiplayground.parts import ImageFile
from geminiplayground.parts import VideoFile
from rich import print

load_dotenv(find_dotenv())


def cache_image_file():
    """
    code snippet to cache image file
    """
    gemini_client = GeminiClient()
    image_path = "./data/daisy.jpg"
    print(str(Path(image_path).resolve()))
    image_file = ImageFile(image_path, gemini_client=gemini_client)
    image_file.upload()
    image_file.force_upload()
    # image_file.delete()
    # image_file.clear_cache()
    parts = image_file.content_parts()
    for part in parts:
        print(part)


def cache_video_file():
    """
    code snippet to cache video file
    """
    gemini_client = GeminiClient()
    video_path = "./data/transformers-explained.mp4"
    print(str(Path(video_path).resolve()))
    video_file = VideoFile(video_path, gemini_client=gemini_client)
    # video_file.delete()
    # video_file.force_upload()
    # video_file.clear_cache()
    parts = video_file.content_parts()
    for part in parts:
        print(part)


if __name__ == "__main__":
    # clear cache
    cache.clear()
    # cache_image_file()
    # cache_video_file()
