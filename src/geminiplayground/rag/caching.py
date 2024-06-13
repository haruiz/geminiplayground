import diskcache as dc
import logging

cache = dc.Cache(".cache")


def cache_func_results(func):
    """
    Decorator to cache results of a function.
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper function to cache results.
        """
        # Create a cache key based on the function name and arguments
        # ignore self argument for instance methods
        if len(args) > 0 and hasattr(args[0], "__class__"):
            cache_key = f"{func.__name__}_{args[1:]}_{kwargs}"
        else:
            cache_key = f"{func.__name__}_{args}_{kwargs}"

        if cache_key in cache:
            logging.info(f"Loading cached results for {cache_key}")
            return cache[cache_key]
        else:
            logging.warning(
                f"No cache found for {cache_key}. Computing results and saving to cache. be aware that this may take a while."
            )
            result = func(*args, **kwargs)
            cache[cache_key] = result
            return result

    return wrapper
