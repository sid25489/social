# ConnectSphere API v1.0 Documentation

**Base URL:** `https://api.connectsphere.com/api/v1/`

## Authentication

### JWT Token Authentication
```
Authorization: Bearer <access_token>
```

### Endpoints

#### 1. Obtain JWT Token
```
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: {
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. Refresh Access Token
```
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response: {
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 3. Register New User
```
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}

Response: {
  "id": "uuid-here",
  "username": "newuser",
  "email": "newuser@example.com",
  "access": "jwt-token",
  "refresh": "jwt-refresh-token"
}
```

---

## User Management

### 1. List All Users (Paginated)
```
GET /api/v1/users/?search=john&ordering=-created_at
Query Parameters:
  - search: Search by username/email
  - ordering: created_at, followers_count, username
  - page: Page number (cursor pagination)

Response: {
  "next": "http://...",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "avatar": "https://...",
      "bio": "Developer and designer",
      "followers_count": 150,
      "following_count": 100,
      "posts_count": 45,
      "is_verified": true,
      "is_following": false,
      "is_followed_by": true
    }
  ]
}
```

### 2. Get User Detail
```
GET /api/v1/users/{user_id}/

Response: {
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "avatar": "https://...",
  "bio": "Developer and designer",
  "website": "https://example.com",
  "location": "San Francisco, CA",
  "followers_count": 150,
  "following_count": 100,
  "posts_count": 45,
  "is_verified": true,
  "is_following": false,
  "is_blocked": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get Current User
```
GET /api/v1/users/me/
Authentication: Required

Response: {
  "id": "uuid",
  "username": "current_user",
  "email": "user@example.com",
  "first_name": "John",
  ...
  (full user object)
}
```

### 4. Get User Followers
```
GET /api/v1/users/{user_id}/followers/?page=1

Response: {
  "results": [
    {
      "id": "uuid",
      "username": "follower1",
      "avatar": "https://...",
      "is_following": false
    }
  ]
}
```

### 5. Get User Following
```
GET /api/v1/users/{user_id}/following/?page=1

Response: {
  "results": [
    {
      "id": "uuid",
      "username": "following1",
      "avatar": "https://...",
      "is_following": true
    }
  ]
}
```

### 6. Get User Recommendations
```
GET /api/v1/users/recommendations/?limit=10
Query Parameters:
  - limit: Number of recommendations (default: 10)

Response: {
  "results": [
    {
      "id": "uuid",
      "username": "suggested_user",
      "avatar": "https://...",
      "bio": "Suggested based on interests",
      "reason": "Followed by people you follow"
    }
  ]
}
```

---

## User Profiles

### 1. Get Current User Profile
```
GET /api/v1/profiles/
Authentication: Required

Response: {
  "id": "uuid",
  "user": "uuid",
  "avatar": "https://...",
  "banner": "https://...",
  "bio": "I'm a developer",
  "website": "https://example.com",
  "location": "San Francisco",
  "is_private": false,
  "is_verified": false,
  "birth_date": "1990-01-15",
  "theme": "dark",
  "notifications_enabled": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2. Update User Profile
```
PUT /api/v1/profiles/
PATCH /api/v1/profiles/
Content-Type: multipart/form-data
Authentication: Required

{
  "avatar": <file>,
  "banner": <file>,
  "bio": "Updated bio",
  "website": "https://newsite.com",
  "location": "New York",
  "is_private": false
}

Response: (Updated profile object)
```

### 3. Update Profile (Alternative Endpoint)
```
PUT /api/v1/profiles/update_profile/
PATCH /api/v1/profiles/update_profile/
Authentication: Required

(Same as above)
```

---

## Posts

### 1. Create Post
```
POST /api/v1/posts/
Content-Type: multipart/form-data
Authentication: Required

{
  "content": "This is my first post!",
  "images": [<file1>, <file2>],
  "mentions": ["@user1", "@user2"],
  "hashtags": ["#python", "#django"]
}

Response: {
  "id": "uuid",
  "author": {
    "id": "uuid",
    "username": "john_doe",
    "avatar": "https://..."
  },
  "content": "This is my first post!",
  "images": ["https://...", "https://..."],
  "likes_count": 0,
  "comments_count": 0,
  "shares_count": 0,
  "is_liked": false,
  "is_bookmarked": false,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-03-15T10:30:00Z"
}
```

### 2. List Posts (Feed)
```
GET /api/v1/posts/?ordering=-created_at&page=1
Query Parameters:
  - search: Search in post content
  - ordering: created_at, likes_count, comments_count
  - page: Page number

Response: {
  "results": [
    {
      "id": "uuid",
      "author": {...},
      "content": "Post content",
      "images": ["https://..."],
      "likes_count": 45,
      "comments_count": 12,
      "is_liked": false,
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

### 3. Get Post Detail
```
GET /api/v1/posts/{post_id}/

Response: {
  "id": "uuid",
  "author": {...},
  "content": "Post content",
  "images": [...],
  "likes_count": 45,
  "comments": [
    {
      "id": "uuid",
      "author": {...},
      "content": "Great post!",
      "likes_count": 5,
      "created_at": "2024-03-15T11:00:00Z"
    }
  ],
  "is_liked": false,
  "is_bookmarked": false,
  "created_at": "2024-03-15T10:30:00Z"
}
```

### 4. Update Post
```
PATCH /api/v1/posts/{post_id}/
Authentication: Required (must be author)

{
  "content": "Updated content"
}

Response: (Updated post object)
```

### 5. Delete Post
```
DELETE /api/v1/posts/{post_id}/
Authentication: Required (must be author)

Response: 204 No Content
```

### 6. Like Post
```
POST /api/v1/posts/{post_id}/like/
Authentication: Required

Response: {
  "id": "uuid",
  "status": "liked",
  "likes_count": 46
}
```

### 7. Unlike Post
```
DELETE /api/v1/posts/{post_id}/like/
Authentication: Required

Response: {
  "id": "uuid",
  "status": "unliked",
  "likes_count": 45
}
```

### 8. Bookmark Post
```
POST /api/v1/posts/{post_id}/bookmark/
Authentication: Required

Response: {
  "id": "uuid",
  "status": "bookmarked"
}
```

### 9. Unbookmark Post
```
DELETE /api/v1/posts/{post_id}/unbookmark/
Authentication: Required

Response: {
  "id": "uuid",
  "status": "unbookmarked"
}
```

### 10. Home Feed (For Logged-in User)
```
GET /api/v1/posts/home_feed/?page=1
Authentication: Required

Response: (Posts from following users, paginated)
```

### 11. Explore Feed
```
GET /api/v1/posts/explore/?page=1

Response: (Trending posts globally)
```

### 12. User Bookmarks
```
GET /api/v1/posts/bookmarks/?page=1
Authentication: Required

Response: (User's bookmarked posts)
```

---

## Comments

### 1. Create Comment
```
POST /api/v1/comments/
Content-Type: application/json
Authentication: Required

{
  "post": "post-uuid",
  "content": "Great post!",
  "parent": null  // For nested replies, set parent comment UUID
}

Response: {
  "id": "uuid",
  "post": "post-uuid",
  "author": {...},
  "content": "Great post!",
  "likes_count": 0,
  "replies_count": 0,
  "is_liked": false,
  "created_at": "2024-03-15T11:00:00Z"
}
```

### 2. List Comments on Post
```
GET /api/v1/comments/?post={post_id}&ordering=-created_at

Response: {
  "results": [
    {
      "id": "uuid",
      "author": {...},
      "content": "Comment text",
      "likes_count": 2,
      "replies": [
        {
          "id": "uuid",
          "author": {...},
          "content": "Reply text"
        }
      ]
    }
  ]
}
```

### 3. Get Comment Detail
```
GET /api/v1/comments/{comment_id}/

Response: {
  "id": "uuid",
  "post": "post-uuid",
  "author": {...},
  "content": "Comment text",
  "likes_count": 2,
  "created_at": "2024-03-15T11:00:00Z"
}
```

### 4. Update Comment
```
PATCH /api/v1/comments/{comment_id}/
Authentication: Required (must be author)

{
  "content": "Updated comment"
}
```

### 5. Delete Comment
```
DELETE /api/v1/comments/{comment_id}/
Authentication: Required (must be author)

Response: 204 No Content
```

### 6. Like Comment
```
POST /api/v1/comments/{comment_id}/like/
Authentication: Required

Response: {
  "id": "uuid",
  "likes_count": 3
}
```

### 7. Unlike Comment
```
DELETE /api/v1/comments/{comment_id}/like/
Authentication: Required

Response: {
  "id": "uuid",
  "likes_count": 2
}
```

---

## Social Interactions

### 1. Follow User
```
POST /api/v1/social/follow/follow/
Content-Type: application/json
Authentication: Required

{
  "user_to_follow": "user-uuid"
}

Response: {
  "id": "uuid",
  "follower": "current-user-uuid",
  "following": "user-uuid",
  "status": "following",
  "created_at": "2024-03-15T10:30:00Z"
}
```

### 2. Unfollow User
```
POST /api/v1/social/follow/unfollow/
Content-Type: application/json
Authentication: Required

{
  "user_to_unfollow": "user-uuid"
}

Response: {
  "status": "unfollowed"
}
```

### 3. Block User
```
POST /api/v1/social/follow/block/
Content-Type: application/json
Authentication: Required

{
  "user_to_block": "user-uuid"
}

Response: {
  "id": "uuid",
  "blocker": "current-user-uuid",
  "blocked_user": "user-uuid",
  "status": "blocked",
  "created_at": "2024-03-15T10:30:00Z"
}
```

### 4. Unblock User
```
POST /api/v1/social/follow/unblock/
Content-Type: application/json
Authentication: Required

{
  "user_to_unblock": "user-uuid"
}

Response: {
  "status": "unblocked"
}
```

### 5. Mute User
```
POST /api/v1/social/follow/mute/
Content-Type: application/json
Authentication: Required

{
  "user_to_mute": "user-uuid"
}

Response: {
  "status": "muted"
}
```

### 6. Unmute User
```
POST /api/v1/social/follow/unmute/
Content-Type: application/json
Authentication: Required

{
  "user_to_unmute": "user-uuid"
}

Response: {
  "status": "unmuted"
}
```

### 7. Get Pending Follow Requests
```
GET /api/v1/social/follow-requests/?status=pending
Authentication: Required (for private profiles)

Response: {
  "results": [
    {
      "id": "uuid",
      "from_user": {...},
      "to_user": "current-user-uuid",
      "status": "pending",
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

### 8. Accept Follow Request
```
POST /api/v1/social/follow-requests/accept/
Content-Type: application/json
Authentication: Required

{
  "request_id": "request-uuid"
}

Response: {
  "status": "accepted",
  "from_user": {...}
}
```

### 9. Reject Follow Request
```
POST /api/v1/social/follow-requests/reject/
Content-Type: application/json
Authentication: Required

{
  "request_id": "request-uuid"
}

Response: {
  "status": "rejected"
}
```

---

## Notifications

### 1. List Notifications
```
GET /api/v1/notifications/?filter=unread&ordering=-created_at
Query Parameters:
  - filter: all, read, unread
  - ordering: created_at, type

Authentication: Required

Response: {
  "results": [
    {
      "id": "uuid",
      "type": "like",
      "actor": {...},
      "content_type": "post",
      "action_object_id": "post-uuid",
      "description": "user liked your post",
      "is_read": false,
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

### 2. Get Notification Count
```
GET /api/v1/notifications/unread_count/
Authentication: Required

Response: {
  "unread_count": 5
}
```

### 3. Mark Notification as Read
```
POST /api/v1/notifications/{notification_id}/mark_as_read/
Authentication: Required

Response: {
  "id": "uuid",
  "is_read": true
}
```

### 4. Mark All as Read
```
POST /api/v1/notifications/mark_all_as_read/
Authentication: Required

Response: {
  "marked_count": 5
}
```

### 5. List Notifications (Alternative)
```
GET /api/v1/notifications/list_notifications/
Authentication: Required

Response: (Same as #1)
```

---

## Messaging

### 1. Send Message
```
POST /api/v1/messages/send/
Content-Type: application/json
Authentication: Required

{
  "recipient": "user-uuid",
  "content": "Hello! How are you?"
}

Response: {
  "id": "uuid",
  "sender": "current-user-uuid",
  "recipient": "user-uuid",
  "content": "Hello! How are you?",
  "is_read": false,
  "created_at": "2024-03-15T10:30:00Z"
}
```

### 2. Get Conversations
```
GET /api/v1/messages/conversations/?ordering=-updated_at
Authentication: Required

Response: {
  "results": [
    {
      "id": "uuid",
      "other_user": {...},
      "last_message": "Last message content",
      "unread_count": 2,
      "updated_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

### 3. Get Conversation Messages
```
GET /api/v1/messages/conversation/?user={user_id}&page=1
Authentication: Required

Response: {
  "results": [
    {
      "id": "uuid",
      "sender": {...},
      "recipient": {...},
      "content": "Message text",
      "is_read": true,
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

---

## Search & Discovery

### 1. Global Search
```
GET /api/v1/search/global_search/?q=python&type=posts
Query Parameters:
  - q: Search query (required)
  - type: posts, users, hashtags (default: all)
  - page: Page number

Response: {
  "posts": [
    {
      "id": "uuid",
      "content": "Python is awesome",
      "author": {...}
    }
  ],
  "users": [
    {
      "id": "uuid",
      "username": "python_dev",
      "avatar": "https://..."
    }
  ],
  "hashtags": [
    {
      "id": "uuid",
      "name": "python",
      "posts_count": 1500
    }
  ]
}
```

### 2. Hashtag Search
```
GET /api/v1/search/hashtags/?q=python&ordering=-posts_count
Query Parameters:
  - q: Hashtag query
  - ordering: posts_count, created_at

Response: {
  "results": [
    {
      "id": "uuid",
      "name": "python",
      "posts_count": 1500,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Trending Hashtags
```
GET /api/v1/search/trending/?limit=10
Query Parameters:
  - limit: Number of trending hashtags (default: 10)

Response: {
  "results": [
    {
      "id": "uuid",
      "name": "trending_topic",
      "posts_count": 5000,
      "growth": 250
    }
  ]
}
```

---

## Reports & Moderation

### 1. Create Report
```
POST /api/v1/reports/create_report/
Content-Type: application/json
Authentication: Required

{
  "content_type": "post",  // post, comment, user
  "object_id": "uuid",
  "reason": "spam",  // spam, harassment, violence, etc.
  "description": "This post violates guidelines"
}

Response: {
  "id": "uuid",
  "reporter": "current-user-uuid",
  "content_type": "post",
  "object_id": "post-uuid",
  "reason": "spam",
  "status": "pending",
  "created_at": "2024-03-15T10:30:00Z"
}
```

### 2. Get User's Reports
```
GET /api/v1/reports/my_reports/?ordering=-created_at
Authentication: Required

Response: {
  "results": [
    {
      "id": "uuid",
      "content_type": "post",
      "reason": "spam",
      "status": "pending"
    }
  ]
}
```

### 3. Get Pending Reports (Admin Only)
```
GET /api/v1/moderation/pending_reports/?status=pending
Authentication: Required (admin)
Permission: IsModerator

Response: {
  "results": [
    {
      "id": "uuid",
      "reporter": {...},
      "content": "Post or comment content",
      "reason": "spam",
      "status": "pending",
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

### 4. Approve Report (Admin Only)
```
POST /api/v1/moderation/approve_report/
Content-Type: application/json
Authentication: Required (admin)
Permission: IsModerator

{
  "report_id": "report-uuid",
  "action": "delete"  // delete, suspend, warn
}

Response: {
  "id": "uuid",
  "status": "approved",
  "action_taken": "post_deleted"
}
```

### 5. Reject Report (Admin Only)
```
POST /api/v1/moderation/reject_report/
Content-Type: application/json
Authentication: Required (admin)
Permission: IsModerator

{
  "report_id": "report-uuid",
  "reason": "Does not violate guidelines"
}

Response: {
  "id": "uuid",
  "status": "rejected"
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE"
}
```

### Common Status Codes
- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests (Rate Limited)
- `500` - Internal Server Error

### Rate Limiting
- **Anonymous Users:** 100 requests/hour
- **Authenticated Users:** 1000 requests/hour

---

## Pagination

All list endpoints use cursor-based pagination:

```
GET /api/v1/posts/?page=1

Response: {
  "next": "http://...?cursor=cD0yMDIzLTAxLTE1",
  "previous": null,
  "results": [...]
}
```

---

## Versioning

API Version: **v1.0**

Future versions will be available at:
- `/api/v2/` (when released)
- `/api/v3/` (when released)

---

**Last Updated:** March 2026
**Compatibility:** Django 6.0.3, Python 3.12.13
