from django.urls import path
from . import views

urlpatterns = [
    path('install-application/', views.InstallApplicationView.as_view()),
    path('start-application/', views.StartApplicationView.as_view()),
    path('app-status/', views.AppStatusView.as_view()),
    path('stop-applications/', views.StopApplicationsView.as_view()),
    path('applications-list/', views.ApplicationsListView.as_view()),
    path('delete-application/', views.DeleteApplicationView.as_view()),
]

