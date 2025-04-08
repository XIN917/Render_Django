from django.urls import path
from .views import PresentationDayView

urlpatterns = [
    path('day/', PresentationDayView.as_view(), name='presentation-day'),
]
