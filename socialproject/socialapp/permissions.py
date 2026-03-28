"""
ConnectSphere Custom Permissions

Production-grade permission classes:
- IsOwner - only owner can edit/delete
- IsOwnerOrReadOnly - owner can edit, others can read
- IsAuthenticatedOrReadOnly - authenticated can edit
- IsNotBlocked - user is not blocked
- IsPrivateProfileAllowed - can view private profile
- CanMessage - allowed to message user
"""

from typing import cast
from django.contrib.auth.models import User
from rest_framework import permissions
from .models import Block, Follow


class IsOwner(permissions.BasePermission):
    """
    Only allow owner to access object
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow owner to edit/delete
    Others can read
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Authenticated users can perform actions
    Anonymous can only read
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsNotBlocked(permissions.BasePermission):
    """
    Check if user is not blocked by target user
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return True
        
        # Get target user from object
        target_user = None
        if hasattr(obj, 'author'):
            target_user = obj.author
        elif hasattr(obj, 'user'):
            target_user = obj.user
        
        if not target_user:
            return True
        
        # Check if blocked
        is_blocked = Block.objects.filter(
            blocker=target_user,
            blocked_user=request.user
        ).exists()
        
        return not is_blocked


class CanViewProfile(permissions.BasePermission):
    """
    Check if user can view target profile
    - Not blocked
    - Not private, or is following, or is owner
    """
    def has_object_permission(self, request, view, obj):
        # obj is UserProfile
        if obj.user == request.user:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return not obj.is_private
        
        # Check if blocked
        if Block.objects.filter(
            blocker=obj.user,
            blocked_user=request.user
        ).exists():
            return False
        
        # Check if can view private profile
        if obj.is_private:
            is_following = Follow.objects.filter(
                follower=request.user,
                following=obj.user,
                is_deleted=False
            ).exists()
            return is_following
        
        return True


class CanMessage(permissions.BasePermission):
    """
    Check if user can message target user
    - Not blocked either way
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # obj should be target User
        target_user = obj if hasattr(obj, 'id') else obj.user
        
        is_blocked = Block.objects.filter(
            blocker=target_user,
            blocked_user=request.user
        ).exists() or Block.objects.filter(
            blocker=request.user,
            blocked_user=target_user
        ).exists()
        
        return not is_blocked


class IsPrivateProfileAllowed(permissions.BasePermission):
    """
    Allow access to private profile if:
    - Own profile
    - Following user
    """
    def has_object_permission(self, request, view, obj):
        if not obj.is_private:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        if obj.user == request.user:
            return True
        
        is_following = Follow.objects.filter(
            follower=request.user,
            following=obj.user,
            is_deleted=False
        ).exists()
        
        return is_following


class IsNotDeleted(permissions.BasePermission):
    """
    Check if object is not soft-deleted
    """
    def has_object_permission(self, request, view, obj):
        return not getattr(obj, 'is_deleted', False)


class CanEditPost(permissions.BasePermission):
    """
    User can edit post if:
    - Is author
    - Post is not deleted
    - Post is not too old (optional: can edit within 24 hours)
    """
    def has_object_permission(self, request, view, obj):
        if obj.author != request.user:
            return False
        
        return not obj.is_deleted


class IsReportAuthor(permissions.BasePermission):
    """
    Only report author can view their own report
    """
    def has_object_permission(self, request, view, obj):
        return obj.reporter == request.user or (request.user.is_authenticated and cast(User, request.user).is_staff)


class IsModerator(permissions.BasePermission):
    """
    Only moderators/admins can access moderation endpoints
    """
    def has_permission(self, request, view):
        user = cast(User, request.user)
        return request.user.is_authenticated and (user.is_staff or user.is_superuser)
