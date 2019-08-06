from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('drive_api.urls')),
    path('', include('apps_api.urls')),
    path('', include('user_mgmt.urls')),
    path('admin/', admin.site.urls),
]
