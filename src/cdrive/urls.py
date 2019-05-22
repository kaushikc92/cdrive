from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/cdrive/', include('drive_api.urls')),
    path('admin/', admin.site.urls),
]
