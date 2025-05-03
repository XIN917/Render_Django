from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyProfileView, ProfileViewSet

router = DefaultRouter()
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('me/', MyProfileView.as_view(), name='my-profile'),
    path('', include(router.urls)),
]