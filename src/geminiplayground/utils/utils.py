import os
import typing
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import git
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


def get_timestamp_seconds(filename, prefix):
    """Extracts the frame count (as an integer) from a filename with the format
       'output_file_prefix_frame0000.jpg'.
    """
    parts = filename.split(prefix)
    if len(parts) != 2:
        return None  # Indicate that the filename might be incorrectly formatted

    frame_count_str = parts[1].split(".")[0]
    return int(frame_count_str)


def get_output_file_prefix(filename, prefix):
    """Extracts the output file prefix from a filename with the format
       'output_file_prefix_frame0000.jpg'.
    """
    parts = filename.split(prefix)
    if len(parts) != 2:
        return None  # Indicate that the filename might be incorrectly formatted

    return parts[0]


def normalize_url(url: str) -> str:
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
    http_uri = normalize_url(url)
    response = requests.get(http_uri)
    image_bytes = BytesIO(response.content)
    image_obj = PILImage.open(image_bytes)
    return image_obj


def get_image_from_path(path: str) -> PILImageType:
    """
    Read image from file and return it
    """
    return PILImage.open(path)


def is_url(uri: str) -> bool:
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


def get_image_from_anywhere(uri_or_path: typing.Union[str, Path]) -> PILImageType:
    """
    read an image from an url or local file and return it
    """
    uri_or_path = str(uri_or_path)
    if is_url(uri_or_path):
        return get_image_from_url(uri_or_path)
    else:
        return get_image_from_path(uri_or_path)


def get_gemini_playground_cache_dir() -> Path:
    """
    Get the cache directory for the playground
    :return:
    """
    cache_dir = os.environ.get("GEMINI_PLAYGROUND_CACHE_DIR", Path.home() / ".gemini_playground_cache")
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def create_image_thumbnail(image_path: typing.Union[str, Path], thumbnail_size: tuple = (128, 128)) -> PILImageType:
    """
    Create a thumbnail for an image
    :param image: The image
    :param thumbnail_size: The size of the thumbnail
    :return: The thumbnail
    """
    pil_image = PILImage.open(str(image_path))
    pil_image.thumbnail(thumbnail_size)
    pil_image = pil_image.convert('RGB')
    thumbnail_bytes = BytesIO()
    pil_image.save(thumbnail_bytes, format='JPEG')
    thumbnail_bytes.seek(0)
    return PILImage.open(thumbnail_bytes)


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


def folder_contains_git_repo(path):
    """
    Check if a given folder is a git repository
    :param path:
    :return: True if the given folder is a repor or false otherwise
    """
    try:
        _ = git.Repo(path).git_dir
        return True
    except (git.exc.InvalidGitRepositoryError, Exception):
        return False


def get_repo_name_from_url(url: str) -> str:
    """
    Get and return the repo name from a valid github url
    :rtype: str
    """
    last_slash_index = url.rfind("/")
    last_suffix_index = url.rfind(".git")
    if last_suffix_index < 0:
        last_suffix_index = len(url)
    if last_slash_index < 0 or last_suffix_index <= last_slash_index:
        raise Exception("invalid url format {}".format(url))
    return url[last_slash_index + 1: last_suffix_index]
