from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('auth/', include('authentication.urls')),
    path('applications/', include('applications.urls')),
    path('profiles/', include('profiles.urls')),
    path('tfms/', include('tfms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)