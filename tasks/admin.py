from django.contrib import admin
from .models import Task

# Register Task model for admin interface
# Basic admin setup for testing

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'due_date']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    # Simple fieldsets for better organization
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description')
        }),
        ('Task Details', {
            'fields': ('due_date', 'priority', 'status')
        }),
    )