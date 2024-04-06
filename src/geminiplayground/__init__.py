import logging
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from rich.logging import RichHandler

from geminiplayground.core import GeminiClient

env_path = Path('.', '.env')
load_dotenv(dotenv_path=env_path)

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=False)],
)
