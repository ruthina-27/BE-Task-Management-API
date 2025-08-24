from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from .models import Task
from .permissions import IsTaskOwner
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    TaskSerializer, 
    TaskCreateSerializer
)

# Django REST Framework API views
# Handle HTTP requests and return JSON responses

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Anyone can register
def register_user(request):
    """
    User registration endpoint
    POST /api/register/
    """
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create authentication token for immediate login
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Registration successful!',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Registration failed',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': 'Registration failed due to server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Anyone can login
def login_user(request):
    """
    User login endpoint
    POST /api/login/
    Expects: username, password
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful!',
            'user': UserSerializer(user).data,
            'token': token.key
        })
    
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_user(request):
    """
    User logout endpoint - deletes the auth token
    POST /api/logout/
    """
    try:
        # Delete the user's token to log them out
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
    except AttributeError:
        return Response({
            'error': 'No active session found'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Logout failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_profile(request):
    """
    Get current user's profile
    GET /api/profile/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# Task CRUD API Views
# Complete REST API for task management

class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET /api/tasks/ - List all tasks for the current user
    POST /api/tasks/ - Create a new task
    
    Query parameters:
    - status: filter by 'pending' or 'completed'
    - priority: filter by 'low', 'medium', or 'high'
    - search: search in title and description
    - due_date: filter by specific date (YYYY-MM-DD)
    - overdue: show overdue tasks (true/false)
    - due_today: show tasks due today (true/false)
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only show tasks belonging to the current user
        queryset = Task.objects.filter(user=self.request.user)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        # Due date filtering
        due_date = self.request.query_params.get('due_date')
        if due_date:
            queryset = queryset.filter(due_date=due_date)
        
        # Overdue tasks
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            from datetime import date
            queryset = queryset.filter(
                status='pending',
                due_date__lt=date.today()
            )
        
        # Due today
        due_today = self.request.query_params.get('due_today')
        if due_today == 'true':
            from datetime import date
            queryset = queryset.filter(due_date=date.today())
        
        return queryset
    
    def get_serializer_class(self):
        # Use different serializer for creation
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        # Automatically assign the task to the current user
        serializer.save(user=self.request.user)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/tasks/{id}/ - Get specific task
    PUT /api/tasks/{id}/ - Update specific task
    DELETE /api/tasks/{id}/ - Delete specific task
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskOwner]
    
    def get_queryset(self):
        # Users can only access their own tasks
        return Task.objects.filter(user=self.request.user)

@api_view(['PATCH'])
def toggle_task_status(request, task_id):
    """
    Toggle task between pending and completed
    PATCH /api/tasks/{id}/toggle/
    """
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    # Toggle status
    if task.status == 'pending':
        task.status = 'completed'
        message = 'Task marked as completed!'
    else:
        task.status = 'pending'
        message = 'Task marked as pending!'
    
    task.save()
    
    return Response({
        'message': message,
        'task': TaskSerializer(task).data
    })

@api_view(['GET'])
def task_statistics(request):
    """
    Get task statistics for the current user
    GET /api/tasks/stats/
    """
    from datetime import date
    user_tasks = Task.objects.filter(user=request.user)
    
    # Basic counts
    total_tasks = user_tasks.count()
    pending_tasks = user_tasks.filter(status='pending').count()
    completed_tasks = user_tasks.filter(status='completed').count()
    
    # Priority breakdown
    high_priority = user_tasks.filter(priority='high').count()
    medium_priority = user_tasks.filter(priority='medium').count()
    low_priority = user_tasks.filter(priority='low').count()
    
    # Overdue tasks
    overdue_tasks = user_tasks.filter(
        status='pending',
        due_date__lt=date.today()
    ).count()
    
    # Due today
    due_today = user_tasks.filter(
        due_date=date.today()
    ).count()
    
    return Response({
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks,
        'due_today': due_today,
        'priority_breakdown': {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority
        },
        'completion_rate': round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
    })

@api_view(['PATCH'])
def bulk_update_tasks(request):
    """
    Bulk update multiple tasks
    PATCH /api/tasks/bulk/
    Body: {"task_ids": [1, 2, 3], "status": "completed"}
    """
    task_ids = request.data.get('task_ids', [])
    update_data = {}
    
    # Extract update fields
    if 'status' in request.data:
        update_data['status'] = request.data['status']
    if 'priority' in request.data:
        update_data['priority'] = request.data['priority']
    
    if not task_ids or not update_data:
        return Response({
            'error': 'task_ids and update fields required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update tasks belonging to current user
    updated_count = Task.objects.filter(
        id__in=task_ids,
        user=request.user
    ).update(**update_data)
    
    return Response({
        'message': f'{updated_count} tasks updated successfully',
        'updated_count': updated_count
    })

@api_view(['DELETE'])
def bulk_delete_tasks(request):
    """
    Bulk delete multiple tasks
    DELETE /api/tasks/bulk/
    Body: {"task_ids": [1, 2, 3]}
    """
    task_ids = request.data.get('task_ids', [])
    
    if not task_ids:
        return Response({
            'error': 'task_ids required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete tasks belonging to current user
    deleted_count, _ = Task.objects.filter(
        id__in=task_ids,
        user=request.user
    ).delete()
    
    return Response({
        'message': f'{deleted_count} tasks deleted successfully',
        'deleted_count': deleted_count
    })
