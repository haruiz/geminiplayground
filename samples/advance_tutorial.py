from rich import print

from geminiplayground import GeminiClient, VideoFile, GitRepo

if __name__ == "__main__":
    gemini_client = GeminiClient()

    video_path = "transformers-explained.mp4"
    video = VideoFile(video_path, gemini_client=gemini_client)
    # video.upload()

    repo_url = "https://github.com/karpathy/ng-video-lecture"
    codebase = GitRepo.from_repo_url(repo_url, branch="master", config={
        "content": "code-files",  # "code-files" or "issues"
        "file_extensions": [".py"]
    })

    prompt = [
        "Use this code:",
        codebase,
        "Generate some code snippets"
    ]
    model = "models/gemini-1.5-pro-latest"
    token_count = gemini_client.get_tokens_count(model, prompt)
    print("Tokens count: ", token_count)
    response = gemini_client.generate_response(model, prompt)
    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)
