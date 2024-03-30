from rich import print

from geminiplayground import GenerateRequestParts, TextPart, GenerateRequest, GeminiClient, ImageFile


def talk_wit_your_images():
    """
    Get the content parts of an image and generate a request.
    :return:
    """
    gemini_client = GeminiClient()
    model = "models/gemini-1.5-pro-latest"

    image_file_path = "PNG_transparency_demonstration_1.png"
    image_file = ImageFile(image_file_path, gemini_client=gemini_client)
    # video_file.upload()
    image_parts = image_file.content_parts()

    request_parts = GenerateRequestParts(parts=[
        TextPart(text="You see this image?:"),
        *image_parts,
        TextPart(text="Describe what you see"),
    ])
    request = GenerateRequest(
        contents=[
            request_parts
        ],

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
    talk_wit_your_images()
