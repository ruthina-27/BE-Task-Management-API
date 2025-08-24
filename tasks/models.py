from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

# Task model for our task management system
# Simple task tracker with basic CRUD operations
# Django models with user relationships

class Task(models.Model):
    # Priority choices - keeping it simple
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    # User association - each task belongs to a user
    # CASCADE means: if user gets deleted, delete all their tasks too
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    
    # Basic fields as required
    title = models.CharField(max_length=200, help_text="Enter task title")
    description = models.TextField(blank=True, help_text="Optional description")
    due_date = models.DateField(help_text="When is this due?")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # newest tasks first
        unique_together = ['user', 'title']  # prevent duplicate task names per user
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    # Basic validation
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.due_date and self.due_date < date.today():
            raise ValidationError('Due date cannot be in the past!')
    
    # Helper method to check if task is overdue
    def is_overdue(self):
        if self.status == 'completed':
            return False
        return self.due_date < date.today()
    
    # Method for Bootstrap CSS classes
    def get_priority_class(self):
        if self.priority == 'high':
            return 'danger'
        elif self.priority == 'medium':
            return 'warning'
        else:
            return 'info'
