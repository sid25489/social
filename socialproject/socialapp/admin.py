"""
ConnectSphere Django Admin Configuration

Register all models with admin panel for management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, UserProfile, Post, Comment, Like, Follow, FollowRequest,
    Block, Mute, Notification, Message, Report, ModeratorAction,
    Hashtag, Mention, Bookmark, CommentLike, FeedCache, TrendingCache
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    list_display = ('username', 'email', 'is_verified', 'followers_count', 'posts_count', 'created_at')
    list_filter = ('is_verified', 'is_deleted', 'created_at')
    search_fields = ('username', 'email')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ConnectSphere Fields', {'fields': ('is_verified', 'is_deleted', 'followers_count', 'following_count', 'posts_count')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile admin"""
    list_display = ('user', 'display_name', 'is_private', 'created_at')
    list_filter = ('is_private', 'is_deleted')
    search_fields = ('user__username', 'display_name', 'bio')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin"""
    list_display = ('author', 'content_preview', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('author__username', 'content')
    readonly_fields = ('likes_count', 'comments_count', 'reposts_count', 'bookmarks_count')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...'
    content_preview.short_description = 'Content'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment admin"""
    list_display = ('author', 'post', 'content_preview', 'likes_count', 'created_at')
    list_filter = ('is_deleted', 'created_at', 'depth')
    search_fields = ('author__username', 'content')
    readonly_fields = ('likes_count', 'replies_count')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...'
    content_preview.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Like admin"""
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Comment like admin"""
    list_display = ('user', 'comment', 'created_at')
    list_filter = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Follow admin"""
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('follower__username', 'following__username')


@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    """Follow request admin"""
    list_display = ('requester', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'receiver__username')


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    """Block admin"""
    list_display = ('blocker', 'blocked_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked_user__username')


@admin.register(Mute)
class MuteAdmin(admin.ModelAdmin):
    """Mute admin"""
    list_display = ('user', 'muted_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'muted_user__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin"""
    list_display = ('recipient', 'notification_type', 'actor', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'actor__username', 'message')
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin"""
    list_display = ('sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'content')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Report admin"""
    list_display = ('reporter', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('reporter__username', 'description')


@admin.register(ModeratorAction)
class ModeratorActionAdmin(admin.ModelAdmin):
    """Moderator action admin"""
    list_display = ('moderator', 'action_type', 'affected_user', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('moderator__username', 'affected_user__username', 'reason')


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    """Hashtag admin"""
    list_display = ('name', 'posts_count', 'is_trending', 'trending_rank')
    list_filter = ('is_trending', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('posts_count',)


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    """Mention admin"""
    list_display = ('mentioned_user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('mentioned_user__username', 'post__content')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """Bookmark admin"""
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')


@admin.register(FeedCache)
class FeedCacheAdmin(admin.ModelAdmin):
    """Feed cache admin"""
    list_display = ('user', 'last_updated', 'expires_at')
    list_filter = ('expires_at',)
    search_fields = ('user__username',)


@admin.register(TrendingCache)
class TrendingCacheAdmin(admin.ModelAdmin):
    """Trending cache admin"""
    list_display = ('cache_type', 'last_updated', 'expires_at')
    list_filter = ('cache_type', 'expires_at')
