from django.contrib import admin
from django.urls import path, include

# Main URL configuration for task management project
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),  # Include task app URLs
]