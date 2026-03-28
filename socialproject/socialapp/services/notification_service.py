"""
Notification Service

Handles notifications:
- Creating notifications from events
- Reading notifications
- Filtering by type
- Bulk operations
"""

from django.db.models import F
from django.utils import timezone
from ..models import Notification, User, Post, Comment, Follow, FollowRequest


class NotificationService:
    """Notification management service"""

    @staticmethod
    def create_notification(recipient, notification_type, actor=None, post=None,
                           comment=None, follow_request=None, message=""):
        """
        Create a notification
        Event types: like, comment, follow, mention, repost, follow_request
        """
        if recipient == actor:
            # Don't notify user about own actions
            return None
        
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            actor=actor,
            post=post,
            comment=comment,
            follow_request=follow_request,
            message=message or NotificationService._get_default_message(
                notification_type, actor
            )
        )
        
        # Trigger async task to send notification via WebSocket
        # In production: celery task to push to WebSocket
        
        return notification

    @staticmethod
    def _get_default_message(notification_type, actor):
        """Generate default notification message"""
        if notification_type == 'like':
            return f"{actor.username} liked your post"
        elif notification_type == 'comment':
            return f"{actor.username} commented on your post"
        elif notification_type == 'follow':
            return f"{actor.username} followed you"
        elif notification_type == 'mention':
            return f"{actor.username} mentioned you"
        elif notification_type == 'repost':
            return f"{actor.username} reposted your post"
        elif notification_type == 'follow_request':
            return f"{actor.username} requested to follow you"
        return "New notification"

    @staticmethod
    def mark_as_read(notification):
        """Mark single notification as read"""
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])

    @staticmethod
    def mark_all_as_read(user):
        """Mark all user's notifications as read"""
        now = timezone.now()
        Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(is_read=True, read_at=now)

    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications"""
        return Notification.objects.filter(
            recipient=user,
            is_read=False,
            is_deleted=False
        ).count()

    @staticmethod
    def get_notifications(user, notification_type=None, limit=20):
        """
        Get user's notifications
        Optional filter by type
        """
        notifications = Notification.objects.filter(
            recipient=user,
            is_deleted=False
        )
        
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        
        return notifications.select_related(
            'actor', 'post', 'comment', 'follow_request'
        ).order_by('-created_at')[:limit]

    @staticmethod
    def delete_notification(notification):
        """Soft delete notification"""
        notification.is_deleted = True
        notification.save()

    @staticmethod
    def delete_old_notifications(days=30):
        """Delete notifications older than X days"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).update(is_deleted=True)

    @staticmethod
    def notify_on_like(user, post):
        """Notify post author on like"""
        if user != post.author:
            NotificationService.create_notification(
                recipient=post.author,
                notification_type='like',
                actor=user,
                post=post
            )

    @staticmethod
    def notify_on_comment(comment):
        """Notify post author on comment"""
        if comment.author != comment.post.author:
            NotificationService.create_notification(
                recipient=comment.post.author,
                notification_type='comment',
                actor=comment.author,
                post=comment.post,
                comment=comment
            )
        
        # Notify parent comment author if replying
        if comment.parent_comment and comment.author != comment.parent_comment.author:
            NotificationService.create_notification(
                recipient=comment.parent_comment.author,
                notification_type='comment',
                actor=comment.author,
                post=comment.post,
                comment=comment
            )

    @staticmethod
    def notify_on_follow(follower, following):
        """Notify user on follow"""
        NotificationService.create_notification(
            recipient=following,
            notification_type='follow',
            actor=follower
        )

    @staticmethod
    def notify_on_mention(post, mentioned_user):
        """Notify user on mention"""
        if post.author != mentioned_user:
            NotificationService.create_notification(
                recipient=mentioned_user,
                notification_type='mention',
                actor=post.author,
                post=post
            )

    @staticmethod
    def notify_on_repost(user, original_post):
        """Notify original author on repost"""
        if user != original_post.author:
            NotificationService.create_notification(
                recipient=original_post.author,
                notification_type='repost',
                actor=user,
                post=original_post
            )

    @staticmethod
    def notify_on_follow_request(follow_request):
        """Notify user on follow request"""
        NotificationService.create_notification(
            recipient=follow_request.receiver,
            notification_type='follow_request',
            actor=follow_request.requester,
            follow_request=follow_request
        )
