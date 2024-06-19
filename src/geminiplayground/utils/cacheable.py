import functools
from diskcache import Cache


class Cacheable:
    """
    Decorator to cache make classes cacheable.
    """

    def __init__(self, cache: Cache, cache_tag_attr: str):
        self._cache = cache
        self._cache_tag_attr = cache_tag_attr

    @staticmethod
    def cache_func(func):
        """
        Decorator to cache the results of a function.
        :param func: The function to be decorated
        :return: The decorated function
        """

        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            """
            Decorator to cache the results of a function implementation.
            :param self:
            :param args:
            :param kwargs:
            :return:
            """
            assert hasattr(self, "_cache_tag_attr"), (
                f"To use the `cache_func` decorator, you must make sure to decorate the class `{self.__class__.__name__}`"
                f"with the Cacheable decorator as follows: @Cacheable(cache, 'tag_attr')"
            )

            cache_entry_key = (
                f"{self.__class__.__name__}_{func.__name__}_{args}_{kwargs}"
            )
            cache_entry_tag = str(getattr(self, self._cache_tag_attr))
            print("cache_entry_tag", cache_entry_tag)
            cached_result, cached_result_tag = self._cache.get(cache_entry_key, tag=cache_entry_tag)

            if cache_entry_key in self._cache and cached_result_tag == cache_entry_tag:
                print(f"Loading cached results for {cache_entry_key}")
                return cached_result

            print(
                f"No cache found for {cache_entry_key}. Computing results and saving to cache. This may take a while."
            )
            result = func(self, *args, **kwargs)
            self._cache.set(cache_entry_key, result, tag=cache_entry_tag)
            return result

        return decorator

    def __call__(self, cls):
        def clear_cache(self):
            """
            Clear the cache for this file.
            """
            print(f"Clearing cache for {self.__class__.__name__}")
            cache_tag = str(getattr(self, self._cache_tag_attr))
            self._cache.evict(tag=cache_tag)

        def set_cache(self, key, value, **kwargs):
            """
            Add a value to the cache
            """
            cache_tag = str(getattr(self, self._cache_tag_attr))
            self._cache.set(str(key), value, tag=cache_tag, **kwargs)

        def get_cache(self, key):
            """
            Get a value from the cache
            """
            return self._cache.get(str(key))

        def del_cache(self, key):
            """
            Delete a value from the cache
            """
            del self._cache[str(key)]

        def in_cache(self, key):
            """
            Check if a value is in the cache
            """
            return str(key) in self._cache

        cls.clear_cache = clear_cache
        cls.set_cache = set_cache
        cls.get_cache = get_cache
        cls.del_cache = del_cache
        cls.in_cache = in_cache
        setattr(cls, "_cache", self._cache)
        setattr(cls, "_cache_tag_attr", self._cache_tag_attr)

        return cls
