from django.db import models
from django.utils import timezone
from datetime import date

# Task model for our task management system
# This is my capstone project - basic CRUD operations

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
    
    # Basic fields as required
    title = models.CharField(max_length=200, help_text="Enter task title")
    description = models.TextField(blank=True, help_text="Optional description")
    due_date = models.DateField(help_text="When is this due?")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Auto timestamps (good practice I learned)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # newest first
    
    def __str__(self):
        return self.title
    
    # Basic validation - due date should be in future
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.due_date and self.due_date < date.today():
            raise ValidationError('Due date cannot be in the past!')
    
    # Helper method to check if task is overdue
    def is_overdue(self):
        if self.status == 'completed':
            return False
        return self.due_date < date.today()
    
    # Simple method to get priority display with color (for templates)
    def get_priority_class(self):
        if self.priority == 'high':
            return 'danger'
        elif self.priority == 'medium':
            return 'warning'
        else:
            return 'info'
