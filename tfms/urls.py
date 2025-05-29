from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TFMViewSet

router = DefaultRouter()
router.register(r'', TFMViewSet, basename='tfm')

urlpatterns = [
    path('', include(router.urls)),
]
