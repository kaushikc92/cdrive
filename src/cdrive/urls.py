from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('drive_api.urls')),
    path('admin/', admin.site.urls),
]
