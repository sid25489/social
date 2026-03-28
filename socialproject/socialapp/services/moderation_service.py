"""
Moderation Service

Handles moderation:
- Report handling
- Moderator actions
- Content removal
- User bans/suspensions
"""

from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Report, ModeratorAction, Post, Comment, User, Notification
)


class ModerationService:
    """Moderation service"""

    @staticmethod
    def create_report(reporter, reason, description="", post=None,
                     comment=None, reported_user=None):
        """
        Create a content report
        - Validate that atleast one entity is provided
        - Store report for moderation queue
        """
        if not any([post, comment, reported_user]):
            raise ValueError("Must report a post, comment, or user")
        
        if reporter == reported_user:
            raise ValueError("Cannot report yourself")
        
        report = Report.objects.create(
            reporter=reporter,
            post=post,
            comment=comment,
            reported_user=reported_user,
            reason=reason,
            description=description,
            status='submitted'
        )
        
        # Notify moderators (via email or dashboard)
        # In production: send notification to moderator queue
        
        return report

    @staticmethod
    def get_reports(status='submitted', limit=50):
        """Get reports by status"""
        reports = Report.objects.filter(
            status=status
        ).order_by('-created_at')[:limit]
        
        return reports

    @staticmethod
    def approve_report(report, moderator, action_type='remove_content'):
        """
        Approve a report and take action
        """
        report.status = 'approved'
        report.save()
        
        # Execute moderation action
        if action_type == 'remove_content':
            if report.post:
                report.post.is_deleted = True
                report.post.save()
            elif report.comment:
                report.comment.is_deleted = True
                report.comment.save()
        
        # Create moderation action record
        action = ModeratorAction.objects.create(
            moderator=moderator,
            action_type=action_type,
            post=report.post,
            comment=report.comment,
            affected_user=report.reported_user or (report.post.author if report.post else report.comment.author),
            report=report,
            reason=f"Approved report: {report.reason}"
        )
        
        return action

    @staticmethod
    def reject_report(report):
        """Reject a report"""
        report.status = 'rejected'
        report.save()

    @staticmethod
    def warn_user(moderator, user, reason):
        """Issue a warning to user"""
        action = ModeratorAction.objects.create(
            moderator=moderator,
            action_type='warn_user',
            affected_user=user,
            reason=reason
        )
        
        # Notify user
        # In production: send email notification
        
        return action

    @staticmethod
    def suspend_user(moderator, user, reason, duration_days=7):
        """
        Suspend user temporarily
        - Cannot post/comment
        - Cannot login
        """
        expires_at = timezone.now() + timedelta(days=duration_days)
        
        action = ModeratorAction.objects.create(
            moderator=moderator,
            action_type='suspend_user',
            affected_user=user,
            reason=reason,
            duration_days=duration_days,
            expires_at=expires_at
        )
        
        # Update user account (can add is_suspended field if needed)
        # For now, track via ModeratorAction
        
        return action

    @staticmethod
    def ban_user(moderator, user, reason, permanent=True):
        """
        Ban user permanently or temporarily
        """
        if permanent:
            duration_days = None
            expires_at = None
        else:
            duration_days = 30
            expires_at = timezone.now() + timedelta(days=duration_days)
        
        action = ModeratorAction.objects.create(
            moderator=moderator,
            action_type='ban_user',
            affected_user=user,
            reason=reason,
            duration_days=duration_days,
            expires_at=expires_at
        )
        
        # Soft delete user
        user.is_deleted = True
        user.save()
        
        return action

    @staticmethod
    def remove_content(moderator, content, reason, post=None, comment=None):
        """
        Remove post or comment
        """
        if post:
            post.is_deleted = True
            post.save()
            affected_user = post.author
        elif comment:
            comment.is_deleted = True
            comment.save()
            affected_user = comment.author
        else:
            raise ValueError("Must specify post or comment")
        
        action = ModeratorAction.objects.create(
            moderator=moderator,
            action_type='remove_content',
            post=post,
            comment=comment,
            affected_user=affected_user,
            reason=reason
        )
        
        return action

    @staticmethod
    def is_user_suspended(user):
        """Check if user is currently suspended"""
        suspension = ModeratorAction.objects.filter(
            affected_user=user,
            action_type='suspend_user',
            expires_at__gt=timezone.now()
        ).exists()
        
        return suspension

    @staticmethod
    def is_user_banned(user):
        """Check if user is permanently banned"""
        ban = ModeratorAction.objects.filter(
            affected_user=user,
            action_type='ban_user',
            duration_days=None  # Permanent ban
        ).exists()
        
        return ban

    @staticmethod
    def get_moderation_log(user=None, limit=50):
        """Get moderation activity log"""
        actions = ModeratorAction.objects.all()
        
        if user:
            actions = actions.filter(affected_user=user)
        
        return actions.order_by('-created_at')[:limit]

    @staticmethod
    def auto_flag_spam(post):
        """
        Auto-flag potential spam
        Simple heuristic: duplicate content, excessive links, etc.
        In production: use ML model
        """
        # Check for excessive links
        link_count = post.content.count('http')
        if link_count > 5:
            return {
                'is_spam': True,
                'reason': 'Excessive links'
            }
        
        # Check for all caps
        if len(post.content) > 10 and post.content.isupper():
            return {
                'is_spam': True,
                'reason': 'All caps message'
            }
        
        return {'is_spam': False}
