from django.shortcuts import render
from rest_framework import viewsets

from users.models import User, Passenger
from users.serializers import UserSerializer, PassengerSerializer

from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.decorators import cache_performance

def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix

def cache_with_tags(key, data, tags, timeout=300):
    cache.set(key, data, timeout)
    for tag in tags:
        tagged_keys = cache.get(f'tag_{tag}', set())
        tagged_keys.add(key)
        cache.set(f'tag_{tag}', tagged_keys, timeout)

def invalidate_by_tag(tag):
    tagged_keys = cache.get(f'tag_{tag}', set())
    for key in tagged_keys:
        cache.delete(key)
    cache.delete(f'tag_{tag}')

@api_view(['GET'])
def cache_stats(request):
    # How would you check what's in cache?
    redis_client = cache.client.get_client()
    # Get all keys in Redis
    keys = redis_client.keys('*')
    keys = [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys]
    total_keys = len(keys)
    key_ttls = {k: redis_client.ttl(k) for k in keys}

    return Response({
        'cache_keys': keys,
        'total_keys': total_keys,
        'key_ttls': key_ttls,
    })

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @cache_performance("user_list_cache")
    def list(self, request, *args, **kwargs):
        # Step 1: Create cache key
        cache_key = get_cache_key('user_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Step 3: Get fresh data
        response = super().list(request, *args, **kwargs)
        
        # Step 4: Store in cache
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        
        return response

    @cache_performance("user_detail_cache")    
    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        cache_key = get_cache_key('user', user_id)
        
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        response = super().retrieve(request, *args, **kwargs)
        
        cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
        
        return response

    def perform_create(self, serializer):
        # Clear relevant caches
        cache.delete('user_list')
        super().perform_create(serializer)

    def perform_update(self, serializer):
        # Clear both list and individual caches
        user_id = serializer.instance.id
        cache.delete('user_list')  # List cache
        cache.delete(f'user_{user_id}')  # Individual cache
        super().perform_update(serializer)

        # Write-through: immediately update cache
        user_data = self.get_serializer(serializer.instance).data
        cache_key = f"user_{serializer.instance.id}"
        cache.set(cache_key, user_data, timeout=300)
    
    def perform_destroy(self, instance):
        passenger_id = instance.id
        result = super().perform_destroy(instance)
        cache.delete(get_cache_key('passenger_list'))
        cache.delete(get_cache_key('passenger', passenger_id))

class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.select_related('user').all()
    serializer_class = PassengerSerializer

    @cache_performance("passenger_list_cache")
    def list(self, request, *args, **kwargs):
        cache_key = get_cache_key('passenger_list')
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    @cache_performance("passenger_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        passenger_id = kwargs.get('pk')
        cache_key = get_cache_key('passenger', passenger_id)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        return response

    def perform_create(self, serializer):
        cache.delete('passenger_list')
        super().perform_create(serializer)

    def perform_update(self, serializer):
        passenger_id = serializer.instance.id
        cache.delete('passenger_list')
        cache.delete(f'passenger_{passenger_id})')
        super().perform_update(serializer)

        passenger_data = self.get_serializer(serializer.instance).data
        cache_key = f"passenger_{serializer.instance.id}"
        cache.set(cache_key, passenger_data, timeout=300)

    def perform_destroy(self, instance):
        passenger_id = instance.id
        super().perform_destroy(instance)
        cache.delete(get_cache_key('passenger_list'))
        cache.delete(get_cache_key('passenger', passenger_id))