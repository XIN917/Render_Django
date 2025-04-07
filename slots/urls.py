from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SlotViewSet

router = DefaultRouter()
router.register(r'', SlotViewSet, basename='slots')

urlpatterns = [
    path('', include(router.urls)),
]
