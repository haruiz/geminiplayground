import logging

from dotenv import load_dotenv, find_dotenv
from rich.logging import RichHandler

from geminiplayground.core import GeminiClient

load_dotenv(find_dotenv())

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=False)],
)
