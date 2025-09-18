from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User

import functools
import time
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    # What caches should be cleared?
    cache.delete('user_list')
    cache.delete(f'user_{instance.id}')

@receiver(post_delete, sender=User)  
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    # What caches should be cleared?
    cache.delete('user_list')
    cache.delete(f'user_{instance.id}')

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

@cache_performance("user_list_cache")
def list(self, request, *args, **kwargs):
    # Your existing cached implementation
    cache_key = get_cache_key('user_list')
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return Response(cached_data)
    
    response = super().list(request, *args, **kwargs)
    cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
    return response


