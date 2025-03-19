from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CurrentUserView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('', include(router.urls)),
]
