from dotenv import find_dotenv
from dotenv import load_dotenv
from geminiplayground.core import GeminiClient
from geminiplayground.parts.git_repo_part import GitRepo
from geminiplayground.schemas import GenerateRequest
from geminiplayground.schemas import GenerateRequestParts
from geminiplayground.schemas import TextPart
from rich import print

load_dotenv(find_dotenv())


def chat_wit_your_code():
    """
    Get the content parts of a github repo and generate a request.
    :return:
    """

    repo = GitRepo.from_url(
        "https://github.com/karpathy/ng-video-lecture",
        branch="master",
        config={
            "content": "code-files",  # "code-files" or "issues"
            "file_extensions": [".py"],
        },
    )
    repo_parts = repo.content_parts()
    request_parts = GenerateRequestParts(
        parts=[
            TextPart(text="use this codebase:"),
            *repo_parts,
            TextPart(
                text="Describe the `bigram.py` file, and generate some code snippets"
            ),
        ]
    )
    request = GenerateRequest(contents=[request_parts])
    model = "models/gemini-1.5-pro-latest"

    gemini_client = GeminiClient()
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                with open("output.txt", "a") as f:
                    f.write(part.text + "\n")
                print(part.text)


if __name__ == "__main__":
    chat_wit_your_code()
