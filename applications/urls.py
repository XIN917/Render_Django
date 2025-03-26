from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListApplicationsView.as_view(), name='list-applications'),
    path('submit/', views.SubmitApplicationView.as_view(), name='apply-teacher'),
    path('<int:pk>/', views.ManageTApplicationView.as_view(), name='manage-application'),
    path('my/', views.MyApplicationView.as_view(), name='my-application'),
]
