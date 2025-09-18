from django.core.management.base import BaseCommand
from django.core.cache import cache
from users.models import User
from users.serializers import UserSerializer

class Command(BaseCommand):
    help = 'Warm up the cache with frequently accessed data'

    def handle(self, *args, **options):
        # Pre-cache user list
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        cache.set('user_list', serializer.data, timeout=3600)
        
        # Pre-cache individual users
        for user in users:
            user_data = UserSerializer(user).data
            cache.set(f'user_{user.id}', user_data, timeout=3600)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cached {len(users)} users')
        )

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
