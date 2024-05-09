from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts import AudioFile
from geminiplayground.schemas import GenerateRequestParts, TextPart, GenerateRequest
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def chat_wit_your_audios():
    """
    Get the content parts of an audio file and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    audio_file_path = "https://d3ctxlq1ktw2nl.cloudfront.net/staging/2024-3-20/375002170-44100-2-2bb0f483b9938.m4a"
    audio_file = AudioFile(audio_file_path, gemini_client=gemini_client)
    audio_parts = audio_file.content_parts()
    audio_files = audio_parts.files
    print("Audio files: ", audio_files)

    request_parts = GenerateRequestParts(
        parts=[
            TextPart(text="You can listen to this audio?:"),
            *audio_parts,
            TextPart(text="Describe what you heard:"),
        ]
    )
    request = GenerateRequest(
        contents=[request_parts],
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
    chat_wit_your_audios()
