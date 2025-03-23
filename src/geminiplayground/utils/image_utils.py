from pathlib import Path
from typing import Union

from PIL import Image as PILImage
from PIL.Image import Image as PILImageType


class ImageUtils:
    """
    Utility class for performing common image processing tasks.
    """

    @staticmethod
    def create_image_thumbnail(
            image_path: Union[str, Path],
            thumbnail_size: tuple[int, int] = (128, 128)
    ) -> PILImageType:
        """
        Create a thumbnail from an image file.

        Args:
            image_path: Path to the image file.
            thumbnail_size: Desired thumbnail size as (width, height).

        Returns:
            A PIL.Image object containing the thumbnail.

        Raises:
            FileNotFoundError: If the image file does not exist.
            OSError: If the file is not a valid image.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        pil_image = PILImage.open(image_path)
        pil_image.thumbnail(thumbnail_size)

        # Convert RGBA to RGB with white background if necessary
        if pil_image.mode == "RGBA":
            background = PILImage.new("RGB", pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.getchannel("A"))
            pil_image = background

        return pil_image
