from pathlib import Path

from geminiplayground import GeminiClient
from geminiplayground.multi_modal_part import MultimodalPart
from geminiplayground.utils import get_image_from_anywhere, UploadFile


class ImageFile(MultimodalPart):

    def __init__(self, image_path: str, **kwargs):
        self.image_path = image_path
        self.gemini_client = kwargs.get("gemini_client", GeminiClient())

    def upload(self):
        """
        Upload an image to Gemini
        """
        image = get_image_from_anywhere(self.image_path)
        image_filename = Path(self.image_path).name
        print(f"Uploading image {image_filename} to Gemini...")
        image.save(image_filename)
        upload_file = UploadFile(file_path=image_filename, display_name=image_filename)
        return self.gemini_client.upload_file(
            upload_file
        )

    def content_parts(self):
        """
        Get the content parts for the image
        :return:
        """
        image_file = self.gemini_client.get_file_by_display_name(Path(self.image_path).name)
        return [image_file.to_file_part()]
