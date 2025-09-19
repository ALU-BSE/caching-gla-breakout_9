import functools
import time
import logging

logger = logging.getLogger(__name__)

def cache_performance(cache_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            logger.info(f"{cache_name}: {end_time - start_time:.4f}s")
            return result
        return wrapper
    return decorator
