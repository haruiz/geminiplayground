import functools
import logging
from diskcache import Cache

logger = logging.getLogger("rich")


class Cacheable:
    """
    A class decorator to make methods and objects cache-aware using `diskcache.Cache`.

    Usage:
        @Cacheable(cache, "tag_attr")
        class MyClass:
            ...
            @Cacheable.cache_func
            def expensive_computation(self, ...):
                ...
    """

    def __init__(self, cache: Cache, cache_tag_attr: str):
        """
        Initialize a cacheable class wrapper.

        Args:
            cache: A `diskcache.Cache` instance.
            cache_tag_attr: Name of the instance attribute used to tag cache entries.
        """
        self._cache = cache
        self._cache_tag_attr = cache_tag_attr

    @staticmethod
    def cache_func(func):
        """
        Method decorator for caching function outputs based on arguments and instance tag.

        Args:
            func: The method to cache.

        Returns:
            The wrapped method with caching.
        """

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            assert hasattr(self, "_cache_tag_attr") and hasattr(self, "_cache"), (
                f"To use @cache_func, decorate the class `{self.__class__.__name__}` with "
                f"`@Cacheable(cache, 'tag_attr')` first."
            )

            # Generate a stable key
            sorted_kwargs = tuple(sorted(kwargs.items()))
            cache_key = f"{self.__class__.__name__}:{func.__name__}:{args}:{sorted_kwargs}"
            cache_tag = str(getattr(self, self._cache_tag_attr))

            # Attempt to retrieve cached result
            entry = self._cache.get(cache_key, tag=cache_tag)
            if entry is not None:
                logger.info(f"[Cache Hit] {cache_key}")
                return entry

            logger.info(f"[Cache Miss] {cache_key} — computing and caching result.")
            result = func(self, *args, **kwargs)
            self._cache.set(cache_key, result, tag=cache_tag)
            return result

        return decorator

    def __call__(self, cls):
        """
        Wrap the class with cache-aware methods and attributes.

        Adds instance methods: clear_cache, set_cache, get_cache, del_cache, in_cache.

        Args:
            cls: The class to decorate.

        Returns:
            The decorated class.
        """

        def clear_cache(self):
            """Clear all cache entries tagged with this instance's tag."""
            tag = str(getattr(self, self._cache_tag_attr))
            logger.info(f"[Cache Clear] Tag: {tag}")
            self._cache.evict(tag=tag)

        def set_cache(self, key, value, **kwargs):
            """Manually set a value in cache under the given key."""
            tag = str(getattr(self, self._cache_tag_attr))
            self._cache.set(str(key), value, tag=tag, **kwargs)

        def get_cache(self, key):
            """Retrieve a value from cache."""
            return self._cache.get(str(key))

        def del_cache(self, key):
            """Remove a value from the cache."""
            try:
                del self._cache[str(key)]
            except KeyError:
                logger.warning(f"[Cache Delete] Key not found: {key}")

        def in_cache(self, key):
            """Check if a value is cached."""
            return str(key) in self._cache

        # Attach cache methods and attributes
        cls.clear_cache = clear_cache
        cls.set_cache = set_cache
        cls.get_cache = get_cache
        cls.del_cache = del_cache
        cls.in_cache = in_cache
        setattr(cls, "_cache", self._cache)
        setattr(cls, "_cache_tag_attr", self._cache_tag_attr)

        return cls
