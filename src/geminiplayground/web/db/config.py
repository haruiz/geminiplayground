import os

from geminiplayground.utils import get_gemini_playground_cache_dir
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    echo_sql: bool = True


cache_dir = get_gemini_playground_cache_dir()
database_file = os.path.join(cache_dir, "data.db")
database_uri = f"sqlite+aiosqlite:///{database_file}"
settings = Settings(database_url=database_uri, echo_sql=False)
