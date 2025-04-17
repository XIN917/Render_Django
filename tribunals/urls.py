from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TribunalViewSet, TribunalMemberViewSet

router = DefaultRouter()
router.register(r'', TribunalViewSet, basename='tribunals')
router.register(r'members', TribunalMemberViewSet, basename='tribunal-members') 

urlpatterns = [
    path('', include(router.urls)),
]
