# URL Configuration Setup Guide

This guide will help you set up the URL routing to make all API endpoints accessible.

## Step 1: Update socialapp/urls.py

Replace the contents of `socialapp/urls.py` with the following:

```python
"""
ConnectSphere API URL Configuration

All endpoints are prefixed with /api/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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

# URL patterns
urlpatterns = [
    # JWT Token endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # All other API endpoints via router
    path('api/', include(router.urls)),
    
    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]
```

## Step 2: Update socialproject/urls.py

Make sure your main `socialproject/urls.py` includes the socialapp URLs:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('socialapp.urls')),
]
```

## Step 3: Run Database Migrations

```bash
# Create migration files based on your models
python manage.py makemigrations socialapp

# Apply migrations to database
python manage.py migrate
```

## Step 4: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser

# You'll be prompted:
# Email: admin@example.com
# Username: admin
# Password: (enter secure password)
```

## Step 5: Run Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Access Points

- **API Documentation**: http://127.0.0.1:8000/api/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Browsable Views**: http://127.0.0.1:8000/api/{endpoint}/

## Testing the API

### Option 1: Using Postman/Insomnia

1. Import the base URL: `http://127.0.0.1:8000/api/`
2. Create folder structure matching the endpoints
3. Use the auth endpoints to get a JWT token

### Option 2: Using cURL

```bash
# Register a new user
curl -X POST http://127.0.0.1:8000/api/auth/register/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "TestPass123!",
    "password2": "TestPass123!"
  }'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "TestPass123!"
  }'

# Use the returned access token in Authorization header
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://127.0.0.1:8000/api/users/me/
```

### Option 3: Using Python

```python
import requests

BASE_URL = 'http://127.0.0.1:8000/api'

# Register
register_data = {
    'email': 'user@example.com',
    'username': 'johndoe',
    'password': 'TestPass123!',
    'password2': 'TestPass123!'
}
response = requests.post(f'{BASE_URL}/auth/register/register/', json=register_data)
print(response.json())

# Login
login_data = {
    'email': 'user@example.com',
    'password': 'TestPass123!'
}
response = requests.post(f'{BASE_URL}/auth/token/', json=login_data)
tokens = response.json()
access_token = tokens['access']

# Use token
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(f'{BASE_URL}/users/me/', headers=headers)
print(response.json())
```

## Endpoint Quick Reference

### Authentication
- `POST /api/auth/register/register/` - Register new user
- `POST /api/auth/token/` - Login (get JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh access token

### Users
- `GET /api/users/` - List all users
- `GET /api/users/me/` - Get current authenticated user
- `GET /api/users/{id}/` - Get specific user profile
- `PUT /api/profiles/update_profile/` - Update own profile

### Posts
- `GET /api/posts/` - List posts
- `POST /api/posts/` - Create a new post
- `GET /api/posts/{id}/` - Get post details
- `POST /api/posts/{id}/like/` - Like a post
- `POST /api/posts/{id}/unlike/` - Unlike a post
- `GET /api/posts/home_feed/` - Get personalized home feed
- `GET /api/posts/explore/` - Get trending explore feed

### Social
- `POST /api/social/follow/follow/` - Follow a user
- `POST /api/social/follow/unfollow/` - Unfollow a user
- `POST /api/social/follow/block/` - Block a user
- `POST /api/social/follow/unblock/` - Unblock a user
- `POST /api/social/follow/mute/` - Mute a user's posts
- `POST /api/social/follow/unmute/` - Unmute a user

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/mark_as_read/` - Mark notification as read
- `POST /api/notifications/mark_all_as_read/` - Mark all as read

### Messages
- `POST /api/messages/send/` - Send a direct message
- `GET /api/messages/conversations/` - Get all conversations
- `GET /api/messages/conversation/?user_id=<user_id>` - Get specific conversation

### Search
- `GET /api/search/global_search/?q=query` - Global search
- `GET /api/search/hashtags/?q=hashtag` - Search hashtags
- `GET /api/search/trending/` - Get trending hashtags

## Troubleshooting

### "No module named 'rest_framework'"
```bash
pip install djangorestframework
```

### "No module named 'rest_framework_simplejwt'"
```bash
pip install djangorestframework-simplejwt
```

### "django-cors-headers not found"
```bash
pip install django-cors-headers
```

### Migration errors
```bash
# Reset database (development only!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### CORS errors from frontend
Make sure `CORS_ALLOWED_ORIGINS` in settings.py includes your frontend URL:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]
```

## Next Steps

1. ✅ Setup URL routing (this guide)
2. ✅ Run migrations
3. ✅ Create superuser
4. ✅ Start development server
5. Test all endpoints with Postman/cURL
6. Setup frontend to consume the API
7. Deploy to production

Happy coding! 🚀
