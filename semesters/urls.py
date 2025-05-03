from django.urls import path, include
from semesters.views import SemesterViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', SemesterViewSet, basename='semester')

urlpatterns = [
    path('', include(router.urls)),
]
