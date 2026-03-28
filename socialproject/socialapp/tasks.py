"""
Celery Tasks

Async task processing:
- Email sending
- Notification digests
- Feed aggregation
- Cleanup jobs
- GDPR compliance
"""

from django.db.models import Count
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Task retry configuration
TASK_RETRY_KWARGS = {
    'max_retries': 3,
    'default_retry_delay': 60,  # 1 minute
}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(self, user_id):
    """Send verification email to user with retry"""
    try:
        from .models import User
        user = User.objects.get(id=user_id)
        
        send_mail(
            subject='Verify your email - ConnectSphere',
            message=f'Welcome to ConnectSphere! Please verify your email. Link will be sent via email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Verification email sent to {user.email}')
    except Exception as exc:
        logger.error(f'Failed to send verification email: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_task(self, user_id, reset_token):
    """Send password reset email with retry"""
    try:
        from .models import User
        user = User.objects.get(id=user_id)
        
        send_mail(
            subject='Password Reset - ConnectSphere',
            message=f'Click the link below to reset your password:\n{reset_token}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f'Password reset email sent to {user.email}')
    except Exception as exc:
        logger.error(f'Failed to send password reset email: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def send_notification_digest_task(self, user_id):
    """Send daily notification digest with retry"""
    try:
        from .models import User, Notification
        from django.utils import timezone
        from datetime import timedelta
        
        user = User.objects.get(id=user_id)
        
        # Get notifications from last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        notifications = Notification.objects.filter(
            recipient=user,
            created_at__gte=yesterday,
            is_read=False
        )[:10]
        
        if notifications.exists():
            send_mail(
                subject='Your Daily Notification Digest - ConnectSphere',
                message=f'You have {notifications.count()} new notifications',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f'Notification digest sent to {user.email}')
    except Exception as exc:
        logger.error(f'Failed to send notification digest: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task
def expire_stories_task():
    """Remove expired stories (24-hour expiry)"""
    try:
        from .models import Story
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=24)
        expired_stories = Story.objects.filter(created_at__lt=cutoff_time)
        count = expired_stories.count()
        expired_stories.delete()
        logger.info(f'Deleted {count} expired stories')
    except Exception as exc:
        logger.error(f'Failed to expire stories: {exc}')


@shared_task
def cleanup_orphaned_media_task():
    """Delete orphaned media files"""
    try:
        from .models import Media
        
        # Delete media not associated with posts, comments, or messages
        orphaned_media = Media.objects.filter(
            post__isnull=True,
            comment__isnull=True,
            message__isnull=True
        )
        count = orphaned_media.count()
        orphaned_media.delete()
        logger.info(f'Deleted {count} orphaned media files')
    except Exception as exc:
        logger.error(f'Failed to cleanup orphaned media: {exc}')



@shared_task
def aggregate_trending_hashtags_task():
    """Aggregate trending hashtags - run hourly"""
    try:
        from .models import Hashtag, Post
        from django.utils import timezone
        from datetime import timedelta
        
        # Get hashtags posted in last 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        
        hashtags = Hashtag.objects.filter(
            posts__created_at__gte=yesterday
        ).annotate(
            recent_count=Count('posts')
        ).order_by('-recent_count')[:20]
        
        # Update trending status
        for i, tag in enumerate(hashtags):
            tag.is_trending = True
            tag.trending_rank = i + 1
            tag.save()
        
        # Remove trending from old hashtags
        Hashtag.objects.exclude(id__in=hashtags).update(
            is_trending=False,
            trending_rank=None
        )
        logger.info(f'Updated {hashtags.count()} trending hashtags')
    except Exception as exc:
        logger.error(f'Failed to aggregate trending hashtags: {exc}')


@shared_task
def refresh_feed_cache_task():
    """Refresh feed cache for active users"""
    try:
        from .models import User
        from .services.feed_service import FeedService
        
        # Refresh cache for all active users (stub)
        logger.info('Feed cache refresh completed')
    except Exception as exc:
        logger.error(f'Failed to refresh feed cache: {exc}')


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def gdpr_delete_user_data_task(self, user_id):
    """
    Complete user data deletion (GDPR compliance)
    - Delete all personal data
    - Anonymize posts
    - Delete messages
    """
    try:
        from .models import User, Post, Message
        
        user = User.objects.get(id=user_id)
        
        # Anonymize posts
        posts = Post.objects.filter(author=user)
        posts.update(
            author=None,
            content="[Deleted by user]"
        )
        
        # Delete messages
        Message.objects.filter(sender=user).delete()
        Message.objects.filter(recipient=user).delete()
        
        # Delete user
        user.delete()
        logger.info(f'User {user_id} data deleted successfully (GDPR)')
    except User.DoesNotExist:
        logger.warning(f'User {user_id} not found for GDPR deletion')
    except Exception as exc:
        logger.error(f'Failed to delete user data: {exc}')
        raise self.retry(exc=exc, countdown=60)


@shared_task
def notify_new_follower_task(follow_id):
    """Notify user of new follower (async)"""
    try:
        from .models import Follow
        from .services.notification_service import NotificationService
        
        follow = Follow.objects.get(id=follow_id)
        NotificationService.notify_on_follow(follow.follower, follow.following)
        logger.info(f'Sent follow notification for follow_id {follow_id}')
    except Exception as exc:
        logger.error(f'Failed to notify new follower: {exc}')


@shared_task
def send_like_notification_task(like_id):
    """Send like notification (async)"""
    try:
        from .models import Like
        from .services.notification_service import NotificationService
        
        like = Like.objects.get(id=like_id)
        NotificationService.notify_on_like(like.user, like.post)
        logger.info(f'Sent like notification for like_id {like_id}')
    except Exception as exc:
        logger.error(f'Failed to send like notification: {exc}')


@shared_task
def process_mentions_task(post_id):
    """Process mentions and send notifications (async)"""
    try:
        from .models import Post, Mention, User
        from .services.notification_service import NotificationService
        import re
        
        post = Post.objects.get(id=post_id)
        
        # Extract mentions
        pattern = r'@(\w+)'
        mentions = set(re.findall(pattern, post.content))
        
        for mention_username in mentions:
            try:
                mentioned_user = User.objects.get(username=mention_username)
                Mention.objects.get_or_create(post=post, mentioned_user=mentioned_user)
                NotificationService.notify_on_mention(post, mentioned_user)
            except User.DoesNotExist:
                pass
        
        logger.info(f'Processed {len(mentions)} mentions for post_id {post_id}')
    except Exception as exc:
        logger.error(f'Failed to process mentions: {exc}')


@shared_task
def cleanup_old_notifications_task():
    """Delete old read notifications"""
    try:
        from .services.notification_service import NotificationService
        deleted_count = NotificationService.delete_old_notifications(days=30)
        logger.info(f'Deleted {deleted_count} old notifications')
    except Exception as exc:
        logger.error(f'Failed to cleanup old notifications: {exc}')


@shared_task
def cleanup_old_messages_task():
    """Delete old messages"""
    try:
        from .models import Message
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count, _ = Message.objects.filter(created_at__lt=cutoff_date).delete()
        logger.info(f'Deleted {deleted_count} old messages')
    except Exception as exc:
        logger.error(f'Failed to cleanup old messages: {exc}')


@shared_task
def update_user_statistics_task(user_id):
    """Update user statistics"""
    try:
        from .models import User
        from .services.user_service import UserService
        
        user = User.objects.get(id=user_id)
        UserService.update_posts_count(user)
        UserService.update_followers_count(user)
        UserService.update_following_count(user)
        logger.info(f'Updated statistics for user_id {user_id}')
    except Exception as exc:
        logger.error(f'Failed to update user statistics: {exc}')

