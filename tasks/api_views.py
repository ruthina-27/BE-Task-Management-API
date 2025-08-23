from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Task
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    TaskSerializer, 
    TaskCreateSerializer
)

# Student project: Learning Django REST Framework API views
# These handle HTTP requests and return JSON responses

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
