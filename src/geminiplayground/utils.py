import mimetypes
import os
import typing
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image as PILImage
from PIL.Image import Image as PILImageType


def rm_tree(pth: typing.Union[str, Path]):
    """
    Recursively remove a directory and its contents
    :param pth:
    :return:
    """
    pth = Path(pth)
    if not pth.exists():
        return
    for child in pth.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()


def seconds_to_time_string(seconds):
    """Converts an integer number of seconds to a string in the format '00:00'.
    Format is the expected format for Gemini 1.5.
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def solve_image_url(url: str) -> str:
    """
    converts gcs uri to url for image display.
    """
    url_parts = urlparse(url)
    scheme = url_parts.scheme
    if scheme == "gs":
        return "https://storage.googleapis.com/" + url.replace("gs://", "").replace(
            " ", "%20"
        )
    elif scheme in ["http", "https"]:
        return url
    raise Exception("Invalid scheme")


def get_image_from_url(url: str) -> PILImageType:
    """
    Create an image from url and return it
    """
    http_uri = solve_image_url(url)
    response = requests.get(http_uri)
    image_bytes = BytesIO(response.content)
    image_obj = PILImage.open(image_bytes)
    return image_obj


def get_image_from_path(path: str) -> PILImageType:
    """
    Read image from file and return it
    """
    return PILImage.open(path)


def is_valid_uri(uri: str) -> bool:
    """
    Check if a URI is valid.
    :param uri: URI
    :return: True if the URI is valid, False otherwise
    """
    try:
        result = urlparse(uri)
        # Check if the scheme and netloc are present
        return all([result.scheme, result.netloc])
    except:
        return False


def get_image_from_anywhere(uri_or_path: str) -> PILImageType:
    """
    read an image from an url or local file and return it
    """
    uri_or_path = str(uri_or_path)
    if is_valid_uri(uri_or_path):
        return get_image_from_url(uri_or_path)
    else:
        return get_image_from_path(uri_or_path)


def get_playground_cache_dir() -> Path:
    """
    Get the cache directory for the playground
    :return:
    """
    cache_dir = os.environ.get("GEMINI_PLAYGROUND_CACHE_DIR", Path.home() / ".gemini_playground_cache")
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_code_files_in_dir(root_dir: typing.Union[str, Path], files_extensions=None, exclude_dirs=None) -> list:
    """
    Extract code files from the repo
    :return:
    """
    default_exclude_dirs = [".git", "node_modules", ".venv", "__pycache__", ".idea", ".vscode", "build", "dist",
                            "target"]
    ignore_dirs = []
    if exclude_dirs is not None:
        ignore_dirs = default_exclude_dirs + exclude_dirs

    if files_extensions is None:
        files_extensions = ['.py', '.java', '.cpp', '.h', '.c', '.go', '.js', '.html', '.css', '.sh']
    code_files = []
    for path in Path(root_dir).rglob('*'):
        if path.is_file() and path.suffix in files_extensions:
            # Check if any part of the path is in the ignore list
            if not any([ignore_dir in path.parts for ignore_dir in ignore_dirs]):
                code_files.append(path)

    return code_files


class UploadFile:
    def __init__(
            self,
            file_path: str,
            display_name: str = None,
            timestamp_seconds: int = None,
            mimetype: str = None,
            uri=None,
    ):
        self.file_path = file_path
        self.display_name = display_name
        self.timestamp = (
            seconds_to_time_string(timestamp_seconds) if timestamp_seconds else None
        )
        self.mimetype = mimetype if mimetype else mimetypes.guess_type(file_path)[0]
        self.uri = uri

    def set_file_uri(self, uri):
        self.uri = uri
