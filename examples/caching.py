from pathlib import Path

from geminiplayground.core import GeminiClient
from geminiplayground.parts import ImageFile, VideoFile
from rich import print


def test_image_file():
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


def test_video_file():
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


if __name__ == '__main__':
    test_image_file()
    test_video_file()
