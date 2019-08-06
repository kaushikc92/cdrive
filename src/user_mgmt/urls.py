from django.urls import path
from . import views

urlpatterns = [
    path('user-details/', views.UserDetailsView.as_view()),
    path('register-user/', views.RegisterUserView.as_view()),
    path('client-id/', views.ClientIdView.as_view()),
    path('authentication-token/', views.AuthenticationTokenView.as_view()),
    path('logout/', views.LogoutView.as_view()),
]

