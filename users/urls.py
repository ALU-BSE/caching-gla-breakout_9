from django.urls import path, include
from rest_framework import routers

from users.views import UserViewSet, cache_stats, PassengerViewSet

router = routers.DefaultRouter()
router.register(r'passengers', PassengerViewSet)
router.register(r'', UserViewSet)

urlpatterns = [
    path('cache-stats/', cache_stats, name='cache-stats'),
] + router.urls