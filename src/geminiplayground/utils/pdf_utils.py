from pathlib import Path
from typing import Union
from PIL import Image as PILImage
from PIL.Image import Image as PILImageType
import fitz  # PyMuPDF


class PDFUtils:
    """
    Utility class for working with PDF files.
    """

    @staticmethod
    def create_pdf_thumbnail(
            pdf_path: Union[str, Path],
            thumbnail_size: tuple[int, int] = (128, 128),
            zoom: float = 0.2,
    ) -> PILImageType:
        """
        Create a thumbnail image from the first page of a PDF.

        Args:
            pdf_path: Path to the PDF file.
            thumbnail_size: Size of the thumbnail (width, height).
            zoom: Zoom factor to control rendered resolution.

        Returns:
            A PIL.Image thumbnail of the first PDF page.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the PDF has no pages or cannot be opened.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            with fitz.open(pdf_path) as document:
                if len(document) == 0:
                    raise ValueError(f"The PDF at {pdf_path} has no pages.")

                page = document[0]
                matrix = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=matrix)

                image = PILImage.frombytes("RGB", (pix.width, pix.height), pix.samples)
                image.thumbnail(thumbnail_size)
                return image

        except Exception as e:
            raise RuntimeError(f"Failed to create PDF thumbnail: {e}") from e


if __name__ == '__main__':
    pdf_path = "./../../../data/vis-language-model.pdf"
    thumbnail = PDFUtils.create_pdf_thumbnail(pdf_path)
    thumbnail.show()
