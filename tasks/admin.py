from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['status', 'priority']
    date_hierarchy = 'due_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'user')
        }),
        ('Task Details', {
            'fields': ('due_date', 'priority', 'status')
        }),
    )