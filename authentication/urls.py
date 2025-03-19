from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('set-password/', SetPasswordView.as_view(), name='set_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
