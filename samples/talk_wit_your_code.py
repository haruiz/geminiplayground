from rich import print

from geminiplayground import GitRepo, GenerateRequestParts, TextPart, GenerateRequest, GeminiClient


def talk_wit_your_code():
    """
    Get the content parts of a github repo and generate a request.
    :return:
    """

    repo = GitRepo.from_folder("../", config={
        "content": "code-files",  # "code-files" or "issues"
        "exclude_dirs": ["frontend", "ui"],
        "file_extensions": ["*.py"]
    })
    repo_parts = repo.content_parts()

    request_parts = GenerateRequestParts(parts=[
        TextPart(text="use this codebase:"),
        *repo_parts,
        TextPart(
            text="Help me to write a Readme file for this codebase."),
    ])
    request = GenerateRequest(
        contents=[
            request_parts
        ]
    )
    model = "models/gemini-1.5-pro-latest"
    gemini_client = GeminiClient()
    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == '__main__':
    talk_wit_your_code()
