from rich import print

from geminiplayground import GeminiClient, VideoFile, HarmCategory, HarmBlockThreshold, GitRepo

if __name__ == "__main__":
    gemini_client = GeminiClient()

    video_path = "transformers-explained.mp4"
    video = VideoFile(video_path, gemini_client=gemini_client)
    # video.upload()

    repo_url = "https://github.com/karpathy/ng-video-lecture"
    codebase = GitRepo.from_repo_url(repo_url, branch="master", config={
        "content": "code-files",  # "code-files" or "issues"
        "file_extensions": ["*.py"]
    })

    prompt = [
        "Use this video:",
        video,
        "and this codebase:",
        codebase,
        "To create a short tutorial about transformers. "
        "Include some code snippets. Create the code snippets from the code provided. "
    ]

    response = gemini_client.generate_response("models/gemini-1.5-pro-latest", prompt,
                                               generation_config={"temperature": 0.0, "top_p": 1.0},
                                               safety_settings={
                                                   "category": HarmCategory.DANGEROUS_CONTENT,
                                                   "threshold": HarmBlockThreshold.BLOCK_NONE
                                               })
    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)
