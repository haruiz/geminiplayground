from geminiplayground.core import GeminiClient
from geminiplayground.parts import VideoFile, ImageFile
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
if __name__ == "__main__":
    gemini_client = GeminiClient()

    video_file_path = "./../data/BigBuckBunny_320x180.mp4"
    video_file = VideoFile(video_file_path, gemini_client=gemini_client)
    image_file_path = "./../data/daisy.jpg"
    image_file = ImageFile(image_file_path, gemini_client=gemini_client)

    multimodal_prompt = [
        "See this video",
        video_file,
        "and this image",
        image_file,
        "Explain what you see.",
    ]
    response = gemini_client.generate_response(
        "models/gemini-1.5-pro-latest",
        multimodal_prompt,
        stream=True
    )

    for chunk in response:
        print(chunk.text, end="")
