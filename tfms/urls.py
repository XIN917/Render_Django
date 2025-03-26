from django.urls import path
from . import views

urlpatterns = [
    path('', views.AllTFMsAdminView.as_view(), name='all_tfms'),
    path('upload/', views.StudentUploadTFMView.as_view(), name='upload_tfm'),
    path('create/', views.AdminOrTeacherCreateTFMView.as_view(), name='create_tfm'),
    path('my-tfms/', views.MyTFMsView.as_view(), name='my_tfms'),
    path('<int:pk>/', views.TFMDetailUpdateView.as_view(), name='tfm_detail_update'),
    path('review/<int:pk>/', views.ReviewTFMView.as_view(), name='review_tfm'),
]
