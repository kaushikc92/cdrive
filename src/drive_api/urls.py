from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadView.as_view()),
    path('initiate-chunked-upload/', views.InitiateChunkedUpload.as_view()),
    path('upload-chunk/', views.UploadChunk.as_view()),
    path('complete-chunked-upload/', views.CompleteChunkedUpload.as_view()),
    path('list/', views.ListView.as_view()),
    path('delete/', views.DeleteView.as_view()),
    path('download/', views.DownloadView.as_view()),
    path('content/', views.ContentView.as_view()),
    path('json-content/', views.JsonContentView.as_view()),
    path('share/', views.ShareView.as_view()),
    path('create/', views.CreateView.as_view()),
]
