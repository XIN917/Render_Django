from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PresentationDayViewSet

router = DefaultRouter()
router.register(r'day', PresentationDayViewSet, basename='presentation-day')

urlpatterns = [
    path('', include(router.urls)),
]