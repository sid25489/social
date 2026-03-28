from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

# Initialize router for ViewSet auto-routing
router = DefaultRouter()

# Authentication
router.register(r'auth/register', views.RegisterViewSet, basename='register')

# Users and Profiles
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

# Posts
router.register(r'posts', views.PostViewSet, basename='post')

# Comments
router.register(r'comments', views.CommentViewSet, basename='comment')

# Social (Follow, Block, Mute)
router.register(r'social/follow', views.FollowViewSet, basename='follow')
router.register(r'social/follow-requests', views.FollowRequestViewSet, basename='follow-request')

# Notifications
router.register(r'notifications', views.NotificationViewSet, basename='notification')

# Messages
router.register(r'messages', views.MessageViewSet, basename='message')

# Search
router.register(r'search', views.SearchViewSet, basename='search')

# Reports (User Reporting)
router.register(r'reports', views.ReportViewSet, basename='report')

# Moderation (Admin)
router.register(r'moderation', views.ModerationViewSet, basename='moderation')

# URL patterns - versioned API
urlpatterns = [
    # JWT Token endpoints
    path('api/v1/auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # All other API endpoints via router
    path('api/v1/', include(router.urls)),
    
    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]
