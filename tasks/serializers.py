from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Category
from datetime import date

# Django REST Framework serializers
# Convert between Python objects and JSON for the API

class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for registration and user info
    Only showing safe fields (no password in responses)
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Basic serializer for updating user stuff
    Just email and names - keeping it simple for now
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
    
    def validate_email(self, value):
        """Make sure email isnt taken by someone else"""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Someone already has this email")
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Includes password field and validation
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        """Check that passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match!")
        return data
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')  # remove confirmation field
        user = User.objects.create_user(**validated_data)
        return user

class CategorySerializer(serializers.ModelSerializer):
    """
    Category serializer for task organization
    Simple category management
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    """
    Main Task serializer for CRUD operations
    Automatically associates tasks with the logged-in user
    """
    user = UserSerializer(read_only=True)  # show user info but don't allow editing
    is_overdue = serializers.ReadOnlyField()  # include custom method
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 
            'priority', 'status', 'user', 'is_overdue',
            'created_at', 'updated_at', 'completed_at', 'category'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at']
    
    def validate_due_date(self, value):
        """Ensure due_date is not in the past."""
        from datetime import date
        # 'serializers' is imported at module level (rest_framework.serializers)
        if value and value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past!")
        return value
class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating tasks
    Doesn't include user info to keep it clean
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category']
    
    def validate_due_date(self, value):
        """Same validation as main serializer"""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past!")
        return value
