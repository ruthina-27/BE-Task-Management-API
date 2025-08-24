from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import models
from .models import Task
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
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    except:
        return Response({'error': 'Error logging out'}, 
                       status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [permissions.IsAuthenticated]
    
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
