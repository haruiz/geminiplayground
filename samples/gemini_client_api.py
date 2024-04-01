from pathlib import Path

from geminiplayground import GeminiClient
from geminiplayground.schemas import UploadFile

if __name__ == '__main__':
    gemini_client = GeminiClient()

    image_file = UploadFile.from_path("./../data/roses.jpg", body={
        "file": {
            "displayName": "roses.jpg"
        }
    })
    image_file = gemini_client.upload_file(image_file)
    image_file = gemini_client.get_file(image_file.name)
    print(image_file)
    gemini_client.delete_file(image_file.name)

    # list all files
    files = gemini_client.query_files()
    print(files)

    # search files  by query function
    files = gemini_client.query_files(query_fn=lambda x: "roses" in x.display_name, limit=3)
    print(files)

    images = Path("./../data").glob("*.jpg")
    files = [UploadFile.from_path(image) for image in images]
    gemini_client.upload_files(*files)

    # delete all files
    files = gemini_client.query_files()
    gemini_client.delete_files(*files)
