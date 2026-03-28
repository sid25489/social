"""
ConnectSphere Django Signals

Event-driven side effects:
- Update denormalized counters
- Create notifications
- Trigger async tasks
- Sync related data
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F
from .models import (
    Post, Like, Comment, CommentLike, Follow, Block, Mention, 
    UserProfile, Notification, User, FollowRequest
)
from .services.notification_service import NotificationService
from .services.feed_service import FeedService
from .services.user_service import UserService


# ============================================================================
# Post Signals
# ============================================================================

@receiver(post_delete, sender=Post)
def update_hashtag_count_on_post_delete(sender, instance, **kwargs):
    """Update hashtag counts when post is deleted"""
    for hashtag in instance.hashtags.all():
        from django.db.models import Count
        count = hashtag.posts.count()
        hashtag.posts_count = count
        hashtag.save(update_fields=['posts_count'])


# ============================================================================
# Like Signals
# ============================================================================

@receiver(post_save, sender=Like)
def update_post_likes_count(sender, instance, created, **kwargs):
    """Update post likes count and create notification"""
    if created:
        # Update post likes_count
        instance.post.likes_count = F('likes_count') + 1
        instance.post.save(update_fields=['likes_count'])
        instance.post.refresh_from_db()
        
        # Invalidate feed cache
        FeedService.invalidate_feed_cache(instance.user.id)
        FeedService.invalidate_trending_cache()
        
        # Create notification
        NotificationService.notify_on_like(instance.user, instance.post)


@receiver(post_delete, sender=Like)
def decrement_post_likes_count(sender, instance, **kwargs):
    """Decrement post likes count when like is removed"""
    instance.post.likes_count = F('likes_count') - 1
    instance.post.save(update_fields=['likes_count'])
    
    # Invalidate caches
    FeedService.invalidate_trending_cache()


# ============================================================================
# Comment Signals
# ============================================================================

@receiver(post_save, sender=Comment)
def update_post_comments_count(sender, instance, created, **kwargs):
    """Update post comments count and create notification"""
    if created:
        # Update post comments_count
        instance.post.comments_count = F('comments_count') + 1
        instance.post.save(update_fields=['comments_count'])
        
        # Update parent comment replies_count if reply
        if instance.parent_comment:
            instance.parent_comment.replies_count = F('replies_count') + 1
            instance.parent_comment.save(update_fields=['replies_count'])
        
        # Invalidate feed cache
        FeedService.invalidate_trending_cache()
        
        # Create notification
        NotificationService.notify_on_comment(instance)
        
        # Create notifications for mentions
        for mention in instance.mentions.all():
            NotificationService.notify_on_mention(instance.post, mention)


@receiver(post_delete, sender=Comment)
def decrement_post_comments_count(sender, instance, **kwargs):
    """Decrement post comments count"""
    instance.post.comments_count = F('comments_count') - 1
    instance.post.save(update_fields=['comments_count'])
    
    if instance.parent_comment:
        instance.parent_comment.replies_count = F('replies_count') - 1
        instance.parent_comment.save(update_fields=['replies_count'])


# ============================================================================
# CommentLike Signals
# ============================================================================

@receiver(post_save, sender=CommentLike)
def update_comment_likes_count(sender, instance, created, **kwargs):
    """Update comment likes count"""
    if created:
        instance.comment.likes_count = F('likes_count') + 1
        instance.comment.save(update_fields=['likes_count'])


@receiver(post_delete, sender=CommentLike)
def decrement_comment_likes_count(sender, instance, **kwargs):
    """Decrement comment likes count"""
    instance.comment.likes_count = F('likes_count') - 1
    instance.comment.save(update_fields=['likes_count'])


# ============================================================================
# Follow Signals
# ============================================================================

@receiver(post_save, sender=Follow)
def update_follower_counts_on_follow(sender, instance, created, **kwargs):
    """Update follower/following counts and create notification"""
    if created and not instance.is_deleted:
        # Update counters
        instance.following.followers_count = F('followers_count') + 1
        instance.following.save(update_fields=['followers_count'])
        
        instance.follower.following_count = F('following_count') + 1
        instance.follower.save(update_fields=['following_count'])
        
        # Invalidate feed cache
        FeedService.invalidate_feed_cache(instance.follower.id)
        
        # Create notification
        NotificationService.notify_on_follow(instance.follower, instance.following)


@receiver(post_delete, sender=Follow)
def update_follower_counts_on_unfollow(sender, instance, **kwargs):
    """Update follower/following counts when unfollowed"""
    instance.following.followers_count = F('followers_count') - 1
    instance.following.save(update_fields=['followers_count'])
    
    instance.follower.following_count = F('following_count') - 1
    instance.follower.save(update_fields=['following_count'])
    
    # Invalidate feed cache
    FeedService.invalidate_feed_cache(instance.follower.id)


# ============================================================================
# FollowRequest Signals
# ============================================================================

@receiver(post_save, sender=FollowRequest)
def notify_on_follow_request(sender, instance, created, **kwargs):
    """Create notification on follow request"""
    if created:
        NotificationService.notify_on_follow_request(instance)


# ============================================================================
# Block Signals
# ============================================================================

@receiver(post_save, sender=Block)
def handle_block_creation(sender, instance, created, **kwargs):
    """
    Handle block creation:
    - Remove follow relationships
    - Invalidate feed caches
    """
    if created:
        # Remove follows
        Follow.objects.filter(
            follower=instance.blocker,
            following=instance.blocked_user
        ).delete()
        
        Follow.objects.filter(
            follower=instance.blocked_user,
            following=instance.blocker
        ).delete()
        
        # Remove follow requests
        FollowRequest.objects.filter(
            requester=instance.blocker,
            receiver=instance.blocked_user
        ).delete()
        
        FollowRequest.objects.filter(
            requester=instance.blocked_user,
            receiver=instance.blocker
        ).delete()
        
        # Invalidate caches
        FeedService.invalidate_feed_cache(instance.blocker.id)
        FeedService.invalidate_feed_cache(instance.blocked_user.id)


# ============================================================================
# Mention Signals
# ============================================================================

@receiver(post_save, sender=Mention)
def notify_on_mention(sender, instance, created, **kwargs):
    """Create notification on mention"""
    if created:
        NotificationService.notify_on_mention(instance.post, instance.mentioned_user)


# ============================================================================
# UserProfile Signals
# ============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


# ============================================================================
# Post Repost Signals
# ============================================================================

@receiver(post_save, sender=Post)
def handle_repost_creation(sender, instance, created, **kwargs):
    """Create notification on repost"""
    if created and instance.parent_post:
        # Increment repost count
        instance.parent_post.reposts_count = F('reposts_count') + 1
        instance.parent_post.save(update_fields=['reposts_count'])
        
        # Create notification
        NotificationService.notify_on_repost(instance.author, instance.parent_post)
        
        # Invalidate trending cache
        FeedService.invalidate_trending_cache()


# Connect all signals
from django.apps import AppConfig

class SocialappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialapp'
    
    def ready(self):
        # Import signals
        import socialapp.signals  # noqa
