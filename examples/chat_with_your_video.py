from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts import VideoFile
from geminiplayground.schemas import GenerateRequestParts, TextPart, GenerateRequest


def chat_wit_your_video():
    """
    Get the content parts of a video and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    video_file_path = "./../data/BigBuckBunny_320x180.mp4"
    video_file = VideoFile(video_file_path, gemini_client=gemini_client)
    video_parts = video_file.content_parts()
    video_files = video_file.files[-4:]
    for part in video_parts[:5]:
        print(part)

    request_parts = GenerateRequestParts(
        parts=[
            TextPart(text="check this video?:"),
            *video_parts,
            TextPart(text="list the object you see in the video"),
        ]
    )
    request = GenerateRequest(
        contents=[request_parts], generation_config={"temperature": 0.0, "top_p": 1.0}
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
