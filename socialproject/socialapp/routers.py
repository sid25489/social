"""
API URL Router Configuration

Configure all ViewSet routes for the REST API.
Add these to your socialapp/urls.py:

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from . import views
from .routers import urlpatterns as api_urlpatterns

router = DefaultRouter()

# Auth
router.register(r'auth/register', views.RegisterViewSet, basename='register')

# Users
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

# Posts
router.register(r'posts', views.PostViewSet, basename='post')

# Comments
router.register(r'comments', views.CommentViewSet, basename='comment')

# Social
router.register(r'social/follow', views.FollowViewSet, basename='follow')
router.register(r'social/follow-requests', views.FollowRequestViewSet, basename='follow-request')

# Notifications
router.register(r'notifications', views.NotificationViewSet, basename='notification')

# Messages
router.register(r'messages', views.MessageViewSet, basename='message')

# Search
router.register(r'search', views.SearchViewSet, basename='search')

# Reports & Moderation
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'moderation', views.ModerationViewSet, basename='moderation')

urlpatterns = [
    # JWT Auth Endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Routes
    path('api/', include(router.urls)),
]
"""

# This file is for documentation only
# Configure the actual routes in socialapp/urls.py
