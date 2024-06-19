from rich import print

from geminiplayground.core import GeminiClient
from geminiplayground.parts import GitRepo
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def chat_wit_your_code():
    """
    Get the content parts of a github repo and generate a request.
    :return:
    """
    repo = GitRepo.from_url(
        "https://github.com/mhdawson/node-core-utils.git",
        branch="main",
        config={
            "content": "code-files"
        },
    )
    prompt = [
        "Describe the following codebase:",
        repo
    ]
    model = "models/gemini-1.5-flash-latest"
    gemini_client = GeminiClient()
    tokens_count = gemini_client.count_tokens(model, prompt)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, prompt, stream=True)

    # Print the response
    for message_chunk in response:
        if message_chunk.parts:
            print(message_chunk.text, "")


if __name__ == "__main__":
    chat_wit_your_code()
