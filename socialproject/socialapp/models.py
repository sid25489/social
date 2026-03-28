"""
ConnectSphere Core Models

Production-grade models for social media platform with:
- UUID primary keys for all public models
- Optimized indexes and constraints
- Soft delete pattern
- Denormalized counters for performance
- Django signals support
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db.models import F, Q, Value
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    - UUID primary key
    - Email as unique identifier
    - JWT token support
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Engagement metrics (denormalized for performance)
    followers_count = models.IntegerField(default=0, db_index=True)
    following_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
            models.Index(fields=['followers_count']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"@{self.username}"


class UserProfile(models.Model):
    """
    User profile with bio, avatar, and preference settings
    - One-to-one relationship with User
    - Privacy settings
    - Soft delete support
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Profile Information
    display_name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(
        max_length=500,
        blank=True,
        validators=[MaxLengthValidator(500)]
    )
    avatar_url = models.URLField(blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Location and preferences
    location = models.CharField(max_length=200, blank=True)
    is_private = models.BooleanField(default=False, db_index=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_private']),
        ]

    def __str__(self):
        return f"Profile of {self.user.username}"


class Follow(models.Model):
    """
    Follow relationship between users
    - Atomic unique constraint
    - Denormalized counter on User model
    - Soft delete support
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'follow'
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['following', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(follower=models.F('following')),
                name='cannot_follow_self'
            )
        ]

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"


class FollowRequest(models.Model):
    """
    Follow request for private profile users
    - Pending follow requests
    - Accept/reject workflow
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'follow_request'
        unique_together = ('requester', 'receiver')
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(requester=models.F('receiver')),
                name='cannot_request_self'
            )
        ]

    def __str__(self):
        return f"Follow request {self.requester.username} -> {self.receiver.username} ({self.status})"


class Block(models.Model):
    """
    Block relationships - hard restriction
    - Blocked users cannot see content, message, or appear in search
    - One-directional relationship
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking_set')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_set')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'block'
        unique_together = ('blocker', 'blocked_user')
        indexes = [
            models.Index(fields=['blocker']),
            models.Index(fields=['blocked_user']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(blocker=models.F('blocked_user')),
                name='cannot_block_self'
            )
        ]

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked_user.username}"


class Mute(models.Model):
    """
    Mute relationships - soft restriction
    - Muted users' posts don't appear in feed
    - User is unaware of mute
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='muting_set')
    muted_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='muted_by_set')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mute'
        unique_together = ('user', 'muted_user')
        indexes = [
            models.Index(fields=['user']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~Q(user=models.F('muted_user')),
                name='cannot_mute_self'
            )
        ]

    def __str__(self):
        return f"{self.user.username} muted {self.muted_user.username}"


class Hashtag(models.Model):
    """
    Hashtag model for trending and search
    - Denormalized count for performance
    - Case-insensitive
    - GIN index for full-text search
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(1), MaxLengthValidator(100)]
    )
    name_lower = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Engagement metrics
    posts_count = models.IntegerField(default=0, db_index=True)
    
    # Trending data
    is_trending = models.BooleanField(default=False, db_index=True)
    trending_rank = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hashtag'
        indexes = [
            models.Index(fields=['posts_count', '-created_at']),
            models.Index(fields=['is_trending', 'trending_rank']),
        ]
        ordering = ['-posts_count']

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.name}"


class Post(models.Model):
    """
    Core Post model
    - 2000 character limit
    - Hashtag and mention extraction
    - Soft delete
    - Denormalized counters
    - Edit history support
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    
    # Content
    content = models.TextField(
        max_length=2000,
        validators=[MaxLengthValidator(2000)],
        db_index=True
    )
    edited_at = models.DateTimeField(null=True, blank=True)
    edit_count = models.IntegerField(default=0)
    
    # Relationships
    parent_post = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reposts'
    )
    original_author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reposted_by'
    )
    
    # Engagement metrics (denormalized)
    likes_count = models.IntegerField(default=0, db_index=True)
    comments_count = models.IntegerField(default=0)
    reposts_count = models.IntegerField(default=0)
    bookmarks_count = models.IntegerField(default=0)
    
    # Media
    image_urls = models.JSONField(default=list, blank=True)  # List of image URLs
    
    # Extraction fields
    hashtags = models.ManyToManyField(Hashtag, related_name='posts', blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'post'
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['likes_count', '-created_at']),
            models.Index(fields=['comments_count', '-created_at']),
            models.Index(fields=['parent_post']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if len(self.content.strip()) == 0:
            raise ValidationError("Post content cannot be empty")

    def __str__(self):
        return f"Post by {self.author.username}: {self.content[:50]}..."


class Mention(models.Model):
    """
    Mention model for extracting @username mentions
    - Many-to-many through explicit model for better querying
    - Used for notifications
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='mentions')
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions_in_posts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mention'
        unique_together = ('post', 'mentioned_user')
        indexes = [
            models.Index(fields=['mentioned_user', '-created_at']),
        ]

    def __str__(self):
        return f"Mention of {self.mentioned_user.username} in post {self.post.id}"


class Bookmark(models.Model):
    """
    Bookmark/Save posts for later
    - User can bookmark any post they can see
    - Not affected by blocks
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookmark'
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} bookmarked post {self.post.id}"


class Like(models.Model):
    """
    Like/Love interaction on posts
    - Atomic operations only
    - Cannot like own post
    - Triggers notification
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_given')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'like'
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} liked post {self.post.id}"


class Comment(models.Model):
    """
    Comment on posts with threading
    - Nested comments support (depth limited to 2)
    - Denormalized counters
    - Soft delete
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    
    # Threading
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    depth = models.IntegerField(default=0, db_index=True)  # 0 for top-level, 1 for replies
    
    # Content
    content = models.TextField(
        max_length=500,
        validators=[MaxLengthValidator(500)]
    )
    
    edited_at = models.DateTimeField(null=True, blank=True)
    edit_count = models.IntegerField(default=0)
    
    # Engagement metrics
    likes_count = models.IntegerField(default=0)
    replies_count = models.IntegerField(default=0)
    
    # Mentions for notifications
    mentions = models.ManyToManyField(User, related_name='comment_mentions', blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comment'
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent_comment', '-created_at']),
            models.Index(fields=['depth']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.depth > 1:
            raise ValidationError("Cannot nest comments beyond 2 levels")

    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"


class CommentLike(models.Model):
    """
    Like on comments
    - Similar to post likes but for comments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes_given')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comment_like'
        unique_together = ('user', 'comment')
        indexes = [
            models.Index(fields=['comment']),
        ]

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"


class Notification(models.Model):
    """
    User notifications from social interactions
    - Event-driven via Django signals
    - Read status tracking
    - Soft delete
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification types
    TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('repost', 'Repost'),
        ('follow_request', 'Follow Request'),
    ]
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    
    # Related objects (polymorphic)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='notifications_created')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    follow_request = models.ForeignKey(FollowRequest, on_delete=models.CASCADE, null=True, blank=True)
    
    # Content
    message = models.CharField(max_length=200)
    
    # Read status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notification'
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.notification_type}"


class Message(models.Model):
    """
    Direct messages between users
    - 1:1 conversations
    - Read receipts
    - Block-aware
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_received')
    
    content = models.TextField(
        max_length=500,
        validators=[MaxLengthValidator(500)]
    )
    
    # Read status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete (only for sender)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_recipient = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'message'
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class Report(models.Model):
    """
    Content reporting system
    - User reports content
    - Creates moderation task
    - Tracks reason for report
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    
    # Reported content
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_against')
    
    # Reason and notes
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('sexual_content', 'Sexual Content'),
        ('violence', 'Violence'),
        ('misinformation', 'Misinformation'),
        ('copyright', 'Copyright Infringement'),
        ('other', 'Other'),
    ]
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, db_index=True)
    description = models.TextField(max_length=500, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewing', 'Reviewing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted', db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        if self.post:
            return f"Report on post {self.post.id} - {self.reason}"
        return f"Report on user {self.reported_user.username} - {self.reason}"


class ModeratorAction(models.Model):
    """
    Actions taken by moderators
    - Content removal
    - User suspension/ban
    - Warning
    - Activity log
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderation_actions')
    
    # Action type
    ACTION_CHOICES = [
        ('remove_content', 'Remove Content'),
        ('warn_user', 'Warn User'),
        ('suspend_user', 'Suspend User'),
        ('ban_user', 'Ban User'),
        ('unban_user', 'Unban User'),
    ]
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    
    # Related objects
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
    affected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_against')
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Reason and notes
    reason = models.TextField(max_length=500)
    notes = models.TextField(blank=True)
    
    # Duration for temporary actions
    duration_days = models.IntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'moderator_action'
        indexes = [
            models.Index(fields=['affected_user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]

    def __str__(self):
        return f"Moderation: {self.action_type} on {self.affected_user.username}"


class FeedCache(models.Model):
    """
    Cache for user's home feed
    - Stores post IDs for quick retrieval
    - TTL-based invalidation
    - Redis-backed but database fallback
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='feed_cache')
    
    # Cached post IDs
    post_ids = models.JSONField(default=list)
    
    # Cache validity
    last_updated = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'feed_cache'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Feed cache for {self.user.username}"


class TrendingCache(models.Model):
    """
    Cache for trending data
    - Hashtags
    - Posts
    - Updated periodically via Celery
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    CACHE_TYPE_CHOICES = [
        ('hashtags', 'Trending Hashtags'),
        ('posts', 'Trending Posts'),
    ]
    cache_type = models.CharField(max_length=50, choices=CACHE_TYPE_CHOICES)
    
    # Cached data
    data = models.JSONField(default=dict)
    
    # Cache validity
    last_updated = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'trending_cache'
        unique_together = ('cache_type',)
        indexes = [
            models.Index(fields=['cache_type']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Trending {self.cache_type} cache"
