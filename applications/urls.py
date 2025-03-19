from django.urls import path
from .views import SubmitApplicationView, AdminManageApplicationView, ListApplicationsView

urlpatterns = [
    path('', ListApplicationsView.as_view(), name='list-applications'),
    path('apply/', SubmitApplicationView.as_view(), name='apply-teacher'),
    path('<int:pk>/', AdminManageApplicationView.as_view(), name='manage-application'),
]
