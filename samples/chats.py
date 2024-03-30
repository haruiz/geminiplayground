from pathlib import Path

from rich import print

from geminiplayground import GeminiClient
from geminiplayground.gemini_client import CandidatesSchema


def make_video_prompt(prompt, files):
    """
    Make a prompt for the model.
    :param prompt:
    :param files:
    :return:
    """
    generate_content = {"contents": [{"parts": [{"text": prompt}]}]}
    for file in files:
        generate_content["contents"][0]["parts"].extend(make_video_part(file))
    return generate_content


def make_image_prompt(prompt, files):
    """
    Make a prompt for the model.
    :param prompt:
    :param files:
    :return:
    """
    generate_content = {"contents": [{"parts": [{"text": prompt}]}]}
    for file in files:
        generate_content["contents"][0]["parts"].extend(make_image_part(file))
    return generate_content


def make_video_part(file):
    """
    Make a video part.
    :param file:
    :return:
    """
    return [
        {"text": file.display_name},
        {"file_data": {"file_uri": str(file.uri), "mime_type": file.mime_type}},
    ]


def make_text_part(file):
    """
    Make a text file part.
    :param file:
    :return:
    """
    with open(file, "r") as f:
        return [{"text": f.read()}]


def make_text_prompt(prompt, files):
    """
    Make a prompt for the model.
    :param prompt:
    :param files:
    :return:
    """
    generate_content = {"contents": [{"parts": [{"text": prompt}]}]}
    for file in files:
        generate_content["contents"][0]["parts"].extend(make_text_part(file))
    return generate_content


def make_image_part(file):
    """
    Make an image part.
    :param file:
    :return:
    """
    return [{"file_data": {"file_uri": str(file.uri), "mime_type": file.mime_type}}]


def initiate_video_chat():
    """
    Initiate a video chat with the model.
    :return:
    """
    model = "models/gemini-1.5-pro-latest"
    video_files = gemini_client.find_files_by_display_name_prefix(file_name_prefix="BigBuckBunny")

    while True:
        # prompt = "Tell me about this video."
        prompt = input("Enter a prompt: ")
        if not prompt:
            break
        video_prompt = make_video_prompt(prompt, video_files)
        print(video_prompt)
        response = (
            gemini_client.genai_service.models()
            .generateContent(model=model, body=video_prompt)
            .execute()
        )
        response = CandidatesSchema.parse_obj(response)
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.text:
                    print(part.text)


def initiate_image_chat():
    """
    Initiate a chat with the model.
    :return:
    """
    model = "models/gemini-1.5-pro-latest"
    file = gemini_client.get_file_by_display_name(
        "PNG_transparency_demonstration_1.png"
    )
    print(file)
    while True:
        # prompt = "Tell me about this video."
        prompt = input("Enter a prompt: ")
        if not prompt:
            break
        image_prompt = make_image_prompt(prompt, [file])
        print(image_prompt)
        response = (
            gemini_client.genai_service.models()
            .generateContent(model=model, body=image_prompt)
            .execute()
        )
        response = CandidatesSchema.parse_obj(response)
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.text:
                    print(part.text)


def initiate_code_chat():
    """
    Initiate a chat with the model.
    :return:
    """

    model = "models/gemini-1.5-pro-latest"
    code_files = [
        path for path in Path("..").rglob("*.py") if ".venv" not in path.as_posix()
    ]
    while True:
        # prompt = "Tell me about this video."
        prompt = input("Enter a prompt: ")
        if not prompt:
            break
        text_prompt = make_text_prompt(prompt, code_files)
        print(text_prompt)
        response = (
            gemini_client.genai_service.models()
            .generateContent(model=model, body=text_prompt)
            .execute()
        )
        response = CandidatesSchema.parse_obj(response)
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    # List files uploaded in the API
    gemini_client = GeminiClient()

    # video_file_path = "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4"
    # video_uploader = VideoUploader(video_file_path, gemini_client=gemini_client)
    # video_uploader.upload()

    # image_file_path = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
    # image_uploader = ImageUploader(image_file_path, gemini_client=gemini_client)
    # image_uploader.upload()

    # gemini_client.print_models()
    # gemini_client.remove_all_files()

    # initiate_code_chat()
    ##initiate_video_chat()
    # initiate_image_chat()
