from django.shortcuts import render
from rest_framework import viewsets

from users.models import User
from users.serializers import UserSerializer

from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def cache_stats(request):
    return Response({
        'cache_keys': list(cache.keys()),  # List current cache keys
        'total_keys': cache.count(),       # Count of cached items
        'cache_timeout': settings.CACHES['default']['TIMEOUT'],  # Default timeout
    })

def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

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
