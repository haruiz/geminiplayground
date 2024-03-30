from rich import print

from geminiplayground import GenerateRequestParts, TextPart, GenerateRequest, GeminiClient, VideoFile


def talk_wit_your_video():
    """
    Get the content parts of a video and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    video_file_path = "BigBuckBunny_320x180.mp4"
    video_file = VideoFile(video_file_path, gemini_client=gemini_client)
    # video_file.upload()
    video_parts = video_file.content_parts()

    request_parts = GenerateRequestParts(parts=[
        TextPart(text="You see this video?:"),
        *video_parts,
        TextPart(text="Describe what you see"),
    ])
    request = GenerateRequest(
        contents=[
            request_parts
        ]
    )

    tokens_count = gemini_client.get_tokens_count(model, request)
    print("Tokens count: ", tokens_count)
    response = gemini_client.generate_response(model, request)

    # Print the response
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                print(part.text)


if __name__ == '__main__':
    talk_wit_your_video()
