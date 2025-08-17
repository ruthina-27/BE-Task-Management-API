from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Task
from .forms import TaskForm

# Basic CRUD views for Task Management
# Using function-based views because they're easier to understand

def task_list(request):
    """Display all tasks - READ operation"""
    tasks = Task.objects.all()
    # Simple filtering by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    context = {
        'tasks': tasks,
        'current_filter': status_filter,
    }
    return render(request, 'tasks/task_list.html', context)

def task_detail(request, task_id):
    """Show single task details"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_detail.html', {'task': task})

def task_create(request):
    """Create new task - CREATE operation"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Create New Task'
    })

def task_update(request, task_id):
    """Update existing task - UPDATE operation"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_detail', task_id=task.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': f'Edit Task: {task.title}'
    })

def task_delete(request, task_id):
    """Delete task - DELETE operation"""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('task_list')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

# Simple home page
def home(request):
    """Basic home page with task summary"""
    total_tasks = Task.objects.count()
    pending_tasks = Task.objects.filter(status='pending').count()
    completed_tasks = Task.objects.filter(status='completed').count()
    
    # Count overdue tasks (basic logic)
    from datetime import date
    overdue_tasks = Task.objects.filter(
        status='pending',
        due_date__lt=date.today()
    ).count()
    
    context = {
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'tasks/home.html', context)
