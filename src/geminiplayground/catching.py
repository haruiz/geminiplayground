import logging

from diskcache import Cache
from geminiplayground.utils import get_gemini_playground_cache_dir

logger = logging.getLogger("rich")

cached_dir = get_gemini_playground_cache_dir().joinpath(".cache").resolve()
logger.info(f"Using cache directory: {cached_dir}")
cache = Cache(directory=str(cached_dir))
