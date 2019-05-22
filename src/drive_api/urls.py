from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.FileUploadView.as_view()),
    path('list/', views.ListFilesView.as_view()),
    path('download/', views.DownloadUrlView.as_view()),
    path('file-content/', views.FileContentView.as_view()),
    path('delete/', views.DeleteFileView.as_view()),
    path('user-details/', views.UserDetailsView.as_view()),
    path('share-file/', views.ShareFileView.as_view()),
    path('shared-files-list/', views.SharedFilesListView.as_view()),
    path('download-shared-file/', views.DownloadSharedFileView.as_view()),
    path('register-user/', views.RegisterUserView.as_view()),
    path('client-id/', views.ClientIdView.as_view()),
    path('authentication-token/', views.AuthenticationTokenView.as_view()),
    path('logout/', views.LogoutView.as_view()),
]

