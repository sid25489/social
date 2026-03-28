"""
User Service

Handles user profile operations:
- Profile CRUD
- User search
- User recommendations
- Privacy settings
"""

from django.db.models import Q, Count, Prefetch
from ..models import User, UserProfile, Follow, Block, Post


class UserService:
    """User profile management service"""

    @staticmethod
    def get_user_profile(user_id, requesting_user=None):
        """
        Get user profile with visibility checks
        - Check privacy settings
        - Check blocks
        """
        try:
            user = User.objects.select_related('profile').get(id=user_id)
            
            if user.is_deleted:
                return None
            
            # Check if blocked
            if requesting_user and UserService._is_blocked(user, requesting_user):
                return None
            
            return user.profile
        except User.DoesNotExist:
            return None

    @staticmethod
    def update_profile(user, **kwargs):
        """Update user profile"""
        profile = user.profile
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        profile.save()
        return profile

    @staticmethod
    def search_users(query, requesting_user=None, limit=20):
        """
        Search users by username or display name
        - Exclude blocked users
        - Exclude self
        """
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__display_name__icontains=query),
            is_deleted=False
        ).exclude(
            id=requesting_user.id if requesting_user else None
        ).prefetch_related('profile')[:limit]
        
        # Filter out blocked users
        if requesting_user:
            blocked_ids = Block.objects.filter(
                Q(blocker=requesting_user) | Q(blocked_user=requesting_user)
            ).values_list('blocked_user_id', 'blocker_id')
            blocked_ids = set([item for tup in blocked_ids for item in tup])
            users = [u for u in users if u.id not in blocked_ids]
        
        return users

    @staticmethod
    def get_user_recommendations(requesting_user, limit=20):
        """
        Get user recommendations
        - Users with mutual followers
        - Popular users
        - Exclude already following and blocked users
        """
        # Get users this user follows
        following_ids = Follow.objects.filter(
            follower=requesting_user,
            is_deleted=False
        ).values_list('following_id', flat=True)
        
        # Get users blocked by this user
        blocked_ids = Block.objects.filter(
            blocker=requesting_user
        ).values_list('blocked_user_id', flat=True)
        
        # Find users followed by people this user follows
        recommendations = User.objects.filter(
            followers_set__follower__in=following_ids,
            is_deleted=False
        ).exclude(
            id__in=following_ids
        ).exclude(
            id=requesting_user.id
        ).exclude(
            id__in=blocked_ids
        ).annotate(
            mutual_followers=Count('followers_set')
        ).order_by('-mutual_followers').distinct()[:limit]
        
        return recommendations

    @staticmethod
    def _is_blocked(user, requesting_user):
        """Check if user is blocked by requesting user or vice versa"""
        return Block.objects.filter(
            Q(blocker=requesting_user, blocked_user=user) |
            Q(blocker=user, blocked_user=requesting_user)
        ).exists()

    @staticmethod
    def update_followers_count(user):
        """
        Update denormalized followers count
        Called via signals when Follow is created/deleted
        """
        count = Follow.objects.filter(
            following=user,
            is_deleted=False
        ).count()
        user.followers_count = count
        user.save(update_fields=['followers_count'])

    @staticmethod
    def update_following_count(user):
        """Update denormalized following count"""
        count = Follow.objects.filter(
            follower=user,
            is_deleted=False
        ).count()
        user.following_count = count
        user.save(update_fields=['following_count'])

    @staticmethod
    def update_posts_count(user):
        """Update denormalized posts count"""
        count = Post.objects.filter(
            author=user,
            is_deleted=False
        ).count()
        user.posts_count = count
        user.save(update_fields=['posts_count'])

    @staticmethod
    def soft_delete_user(user):
        """
        Soft delete user account
        - Mark as deleted
        - Preserve data for compliance
        """
        user.is_deleted = True
        user.save()
        
        # Soft delete profile
        user.profile.is_deleted = True
        user.profile.save()

    @staticmethod
    def hard_delete_user(user):
        """
        Hard delete user account
        Only for GDPR compliance
        """
        user.delete()
