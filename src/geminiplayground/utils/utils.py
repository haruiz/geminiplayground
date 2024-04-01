import os
import subprocess
import typing
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import git
import requests
from PIL import Image as PILImage
from PIL.Image import Image as PILImageType

import cv2
import math
from tqdm import tqdm
import validators


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


def get_image_from_anywhere(uri_or_path: typing.Union[str, Path]) -> PILImageType:
    """
    read an image from an url or local file and return it
    """
    uri_or_path = str(uri_or_path)
    if validators.url(uri_or_path):
        return get_image_from_url(uri_or_path)
    else:
        return get_image_from_path(uri_or_path)


def get_file_name_from_path(path: str, include_extension=True):
    """
    Get the file name from a path
    :param path:
    :return:
    """
    if validators.url(path):
        file_path = Path(urlparse(path).path)
    else:
        file_path = Path(path)
    if include_extension:
        return file_path.name
    return file_path.stem


def get_gemini_playground_cache_dir() -> Path:
    """
    Get the cache directory for the playground
    :return:
    """
    cache_dir = os.environ.get(
        "GEMINI_PLAYGROUND_CACHE_DIR", Path.home() / ".gemini_playground_cache"
    )
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def create_image_thumbnail(
        image_path: typing.Union[str, Path], thumbnail_size: tuple = (128, 128)
) -> PILImageType:
    """
    Create a thumbnail for an image
    :param image: The image
    :param thumbnail_size: The size of the thumbnail
    :return: The thumbnail
    """
    pil_image = PILImage.open(str(image_path))
    pil_image.thumbnail(thumbnail_size)
    pil_image = pil_image.convert("RGB")
    thumbnail_bytes = BytesIO()
    pil_image.save(thumbnail_bytes, format="JPEG")
    thumbnail_bytes.seek(0)
    return PILImage.open(thumbnail_bytes)


def get_code_files_in_dir(
        root_dir: typing.Union[str, Path], files_extensions=None, exclude_dirs=None
) -> list:
    """
    Extract code files from the repo
    :return:
    """
    default_exclude_dirs = [
        ".git",
        "node_modules",
        ".venv",
        "__pycache__",
        ".idea",
        ".vscode",
        "build",
        "dist",
        "target",
    ]
    ignore_dirs = []
    if exclude_dirs is not None:
        ignore_dirs = default_exclude_dirs + exclude_dirs

    if files_extensions is None:
        files_extensions = [
            ".py",
            ".java",
            ".cpp",
            ".h",
            ".c",
            ".go",
            ".js",
            ".html",
            ".css",
            ".sh",
        ]
    code_files = []
    for path in Path(root_dir).rglob("*"):
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


import os
import shutil
import tempfile
from contextlib import contextmanager


@contextmanager
def TemporaryDirectory(suffix="tmp"):
    """
    Create a temporary directory
    """
    name = tempfile.mkdtemp(prefix=suffix)
    try:
        yield name
    finally:
        shutil.rmtree(name)


@contextmanager
def TemporaryFile(suffix="tmp"):
    """
    Create a temporary file
    :param suffix:
    """
    unique_name = next(tempfile._get_candidate_names())
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=unique_name)
    file_name = tmp.name
    try:
        yield file_name
    finally:
        os.unlink(file_name)


def extract_video_frames(
        video_path: typing.Union[str, Path], output_dir: typing.Union[str, Path]
) -> list:
    """
    Extract frames from the video
    :return:
    """
    output_dir = Path(output_dir)
    video_path = Path(video_path)
    vidcap = cv2.VideoCapture(video_path.as_posix())
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    duration = vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    video_file_name = video_path.stem

    frame_count = 0  # Initialize a frame counter
    count = 0
    frames_files = []
    with tqdm(total=math.ceil(duration), unit="sec", desc="Extracting frames") as pbar:
        while True:
            ret, frame = vidcap.read()
            if not ret:
                break
            if count % int(fps) == 0:  # Extract a frame every second

                frame_count += 1
                file_name_prefix = os.path.basename(video_file_name).replace(".", "_")
                frame_prefix = f"_frame"
                frame_image_filename = (
                    f"{file_name_prefix}{frame_prefix}{frame_count:04d}.jpg"
                )
                frame_image_path = output_dir.joinpath(frame_image_filename)
                frames_files.append(Path(frame_image_path))
                cv2.imwrite(frame_image_path.as_posix(), frame)
                pbar.update(1)
            count += 1
    vidcap.release()
    return frames_files


def extract_video_frame_count(video_path: typing.Union[str, Path]) -> int:
    """
    Extract the number of frames in a video
    :param video_path: The path to the video
    :return: The number of frames in the video
    """
    video_path = Path(video_path)
    vidcap = cv2.VideoCapture(video_path.as_posix())
    num_frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    vidcap.release()
    return int(num_frames)


def extract_video_duration(video_path: typing.Union[str, Path]) -> int:
    """
    Extract the duration of a video
    :param video_path: The path to the video
    :return: The duration of the video in seconds
    """
    video_path = Path(video_path)
    vidcap = cv2.VideoCapture(video_path.as_posix())
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    duration = vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    vidcap.release()
    return int(duration)


def extract_video_frame_at_t(
        video_path: typing.Union[str, Path], timestamp_seconds: int
) -> PILImageType:
    """
    Extract a frame at a specific timestamp
    :param timestamp_seconds: The timestamp in seconds
    :return:
    """
    video_path = Path(video_path)
    vidcap = cv2.VideoCapture(video_path.as_posix())
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    frame_number = int(fps * timestamp_seconds)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = vidcap.read()
    if not ret:
        raise ValueError(f"Could not extract frame at timestamp {timestamp_seconds}")
    vidcap.release()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return PILImage.fromarray(frame)


def beautify_file_size(size_in_bytes: int) -> str:
    """
    Convert size in bytes to human readable format
    :param size: Size in bytes
    :return: Human readable size
    """
    # Define the threshold for each size unit
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    size = size_in_bytes
    unit_index = 0

    while size > 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    # Format the size with two decimal places and the appropriate unit
    return f"{size:.2f} {units[unit_index]}"


def get_file_size(file_path: typing.Union[str, Path]):
    # Use os.path.getsize() to get the file size in bytes
    size_in_bytes = os.path.getsize(file_path)
    return size_in_bytes


def get_github_repo_available_branches(remote_url):
    """
    Get the available branches in a github repository
    :param remote_url:
    :return:
    """
    branches = subprocess.check_output(["git", "ls-remote", "--heads", remote_url])
    branches = branches.decode("utf-8").strip().split("\n")
    branches = [branch.split("refs/heads/")[1] for branch in branches]
    return branches


def check_github_repo_branch_exists(remote_url, branch_name):
    # List all branches from the remote repository
    branches = get_github_repo_available_branches(remote_url)

    # Check if the specified branch exists
    branch_exists = any(branch_name in branch for branch in branches)
    return branch_exists
