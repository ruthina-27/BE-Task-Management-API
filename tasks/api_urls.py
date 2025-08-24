from django.urls import path
from . import api_views

# API URL patterns for Task Management
# Basic REST API endpoints

urlpatterns = [
    # Authentication endpoints
    path('register/', api_views.register_user, name='api_register'),
    path('login/', api_views.login_user, name='api_login'),
    path('logout/', api_views.logout_user, name='api_logout'),
    path('profile/', api_views.user_profile, name='api_profile'),
    path('profile/delete/', api_views.delete_user_account, name='api_delete_account'),
    path('profile/change-password/', api_views.change_password, name='api_change_password'),
    
    # Task CRUD endpoints
    path('tasks/', api_views.TaskListCreateView.as_view(), name='api_task_list'),
    path('tasks/<int:pk>/', api_views.TaskDetailView.as_view(), name='api_task_detail'),
    path('tasks/<int:task_id>/toggle/', api_views.toggle_task_status, name='api_task_toggle'),
    path('tasks/stats/', api_views.task_statistics, name='api_task_stats'),
    path('tasks/bulk/update/', api_views.bulk_update_tasks, name='api_bulk_update'),
    path('tasks/bulk/delete/', api_views.bulk_delete_tasks, name='api_bulk_delete'),
]
