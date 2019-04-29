from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.FileUploadView.as_view()),
    path('list/', views.ListFilesView.as_view()),
]

