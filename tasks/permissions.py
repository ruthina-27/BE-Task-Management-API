from rest_framework import permissions

class IsTaskOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task to view/edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read and write permissions are only allowed to the owner of the task
        return obj.user == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit, but allow read access to all authenticated users.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user
