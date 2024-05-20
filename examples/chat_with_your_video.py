from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts import VideoFile
from geminiplayground.schemas import GenerateRequestParts, TextPart, GenerateRequest
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def chat_wit_your_video():
    """
    Get the content parts of a video and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    video_file_path = "./../data/transformers-explained.mp4"
    video_file = VideoFile(video_file_path, gemini_client=gemini_client)
    video_parts = video_file.content_parts()

    for part in video_parts[:5]:
        print(part)

    request_parts = GenerateRequestParts(
        parts=[
            TextPart(text="What is the following video about?"),
            *video_parts
        ]
    )
    request = GenerateRequest(
        contents=[request_parts]
    )
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == "__main__":
    chat_wit_your_video()
