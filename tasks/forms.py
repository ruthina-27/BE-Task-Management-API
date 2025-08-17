from django import forms
from .models import Task
from datetime import date

class TaskForm(forms.ModelForm):
    """Basic form for creating/editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Optional description...'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    # Basic validation - student style
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():
            raise forms.ValidationError("Due date cannot be in the past!")
        return due_date
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long!")
        return title.strip()
