from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TribunalViewSet

router = DefaultRouter()
router.register(r'', TribunalViewSet, basename='tribunals')

urlpatterns = [
    path('', include(router.urls)),
]
