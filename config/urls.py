"""URL configuration for BrainCheck project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('quiz.auth_urls')),
    path('', include('quiz.urls')),
]
