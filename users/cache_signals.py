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
