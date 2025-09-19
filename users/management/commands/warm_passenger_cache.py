from django.core.management.base import BaseCommand
from django.core.cache import cache
from users.models import Passenger
from users.serializers import PassengerSerializer

def get_cache_key(prefix, identifier=None):
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix

class Command(BaseCommand):
    help = 'Warm up the cache with frequently accessed passenger data'

    def handle(self, *args, **options):
        passengers = Passenger.objects.select_related('user').all()
        serializer = PassengerSerializer(passengers, many=True)
        cache.set(get_cache_key('passenger_list'), serializer.data, timeout=3600)
        for passenger in passengers:
            passenger_data = PassengerSerializer(passenger).data
            cache.set(get_cache_key('passenger', passenger.id), passenger_data, timeout=3600)
        self.stdout.write(self.style.SUCCESS(f'Successfully cached {len(passengers)} passengers'))
