from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JudgeViewSet

router = DefaultRouter()
router.register(r'', JudgeViewSet, basename='judges')

urlpatterns = [
    path('', include(router.urls)),
]
