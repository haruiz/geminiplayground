from dotenv import load_dotenv, find_dotenv
from rich.logging import RichHandler

from .gemini_client import *
from .git_repo_part import GitRepo
from .image_part import ImageFile
from .video_part import VideoFile

load_dotenv(find_dotenv())

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=False)],
)
