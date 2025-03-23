from rich import print

from dotenv import load_dotenv, find_dotenv
from pathlib import Path

from geminiplayground.parts import ImageFile
from geminiplayground.catching import cache

from geminiplayground.core import GeminiClient

load_dotenv(find_dotenv())

if __name__ == '__main__':
    cache.clear()

    gemini_client = GeminiClient()
    images = [ImageFile(image_file, gemini_client=gemini_client) for image_file in Path("./../data").glob("*.jpg")]
    prompt = ["Please describe the following images:"] + images

    model_name = "models/gemini-1.5-pro-latest"
    tokens_count = gemini_client.count_tokens(model_name, prompt)
    print(f"Tokens count: {tokens_count}")
    response = gemini_client.generate_response(model_name, prompt, stream=True)
    for message_chunk in response:
        if message_chunk:
            print(message_chunk.text, end="")
