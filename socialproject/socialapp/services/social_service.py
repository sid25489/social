"""
Social Service

Handles social interactions:
- Follow/Unfollow
- Block/Unblock
- Mute/Unmute
- Follow requests
"""

from django.db import transaction
from django.db.models import F
from ..models import (
    User, Follow, FollowRequest, Block, Mute, Notification
)


class SocialService:
    """Social interactions service"""

    @staticmethod
    def follow_user(follower, following):
        """
        Follow a user
        - Check if already following
        - Check blocks
        - Handle private profiles
        """
        if follower == following:
            raise ValueError("Cannot follow yourself")
        
        if Block.objects.filter(
            blocker=following,
            blocked_user=follower
        ).exists():
            raise ValueError("You are blocked by this user")
        
        # Remove existing mute when following
        Mute.objects.filter(user=follower, muted_user=following).delete()
        
        if following.profile.is_private:
            # Create follow request for private profile
            follow_request, created = FollowRequest.objects.get_or_create(
                requester=follower,
                receiver=following,
                defaults={'status': 'pending'}
            )
            return follow_request
        else:
            # Directly create follow for public profile
            follow, created = Follow.objects.get_or_create(
                follower=follower,
                following=following,
                defaults={'is_deleted': False}
            )
            
            if created:
                # Update counters
                following.followers_count = F('followers_count') + 1
                following.save(update_fields=['followers_count'])
                
                follower.following_count = F('following_count') + 1
                follower.save(update_fields=['following_count'])
            elif follow.is_deleted:
                # Restore soft-deleted follow
                follow.is_deleted = False
                follow.save()
            
            return follow

    @staticmethod
    def unfollow_user(follower, following):
        """
        Unfollow a user
        - Soft delete follow relationship
        """
        try:
            follow = Follow.objects.get(follower=follower, following=following)
            follow.is_deleted = True
            follow.save()
            
            # Update counters
            following.followers_count = F('followers_count') - 1
            following.save(update_fields=['followers_count'])
            
            follower.following_count = F('following_count') - 1
            follower.save(update_fields=['following_count'])
        except Follow.DoesNotExist:
            pass

    @staticmethod
    def accept_follow_request(follow_request):
        """
        Accept a follow request
        - Create follow relationship
        - Update request status
        """
        with transaction.atomic():
            # Create follow
            follow, created = Follow.objects.get_or_create(
                follower=follow_request.requester,
                following=follow_request.receiver,
                defaults={'is_deleted': False}
            )
            
            # Update request
            follow_request.status = 'accepted'
            follow_request.save()
            
            # Update counters
            follow_request.receiver.followers_count = F('followers_count') + 1
            follow_request.receiver.save(update_fields=['followers_count'])
            
            follow_request.requester.following_count = F('following_count') + 1
            follow_request.requester.save(update_fields=['following_count'])
        
        return follow

    @staticmethod
    def reject_follow_request(follow_request):
        """Reject a follow request"""
        follow_request.status = 'rejected'
        follow_request.save()

    @staticmethod
    def block_user(blocker, blocked_user):
        """
        Block a user
        - Hard restriction
        - Remove follow relationships
        - Prevent messaging
        """
        if blocker == blocked_user:
            raise ValueError("Cannot block yourself")
        
        with transaction.atomic():
            # Create block
            block, created = Block.objects.get_or_create(
                blocker=blocker,
                blocked_user=blocked_user
            )
            
            # Remove follow relationships
            Follow.objects.filter(
                follower=blocker,
                following=blocked_user
            ).delete()
            
            Follow.objects.filter(
                follower=blocked_user,
                following=blocker
            ).delete()
            
            # Update counters
            if Follow.objects.filter(
                follower=blocker,
                following=blocked_user
            ).exists():
                blocker.following_count = F('following_count') - 1
                blocker.save(update_fields=['following_count'])
            
            if Follow.objects.filter(
                follower=blocked_user,
                following=blocker
            ).exists():
                blocked_user.followers_count = F('followers_count') - 1
                blocked_user.save(update_fields=['followers_count'])
        
        return block

    @staticmethod
    def unblock_user(blocker, blocked_user):
        """Unblock a user"""
        Block.objects.filter(blocker=blocker, blocked_user=blocked_user).delete()

    @staticmethod
    def mute_user(user, muted_user):
        """
        Mute a user
        - Soft restriction
        - Posts don't appear in feed
        """
        if user == muted_user:
            raise ValueError("Cannot mute yourself")
        
        mute, created = Mute.objects.get_or_create(
            user=user,
            muted_user=muted_user
        )
        return mute

    @staticmethod
    def unmute_user(user, muted_user):
        """Unmute a user"""
        Mute.objects.filter(user=user, muted_user=muted_user).delete()

    @staticmethod
    def get_followers(user, limit=100):
        """Get user's followers"""
        return Follow.objects.filter(
            following=user,
            is_deleted=False
        ).select_related('follower').values_list('follower', flat=True)[:limit]

    @staticmethod
    def get_following(user, limit=100):
        """Get users this user follows"""
        return Follow.objects.filter(
            follower=user,
            is_deleted=False
        ).select_related('following').values_list('following', flat=True)[:limit]

    @staticmethod
    def is_following(follower, following):
        """Check if follower is following"""
        return Follow.objects.filter(
            follower=follower,
            following=following,
            is_deleted=False
        ).exists()

    @staticmethod
    def is_blocked(blocker, blocked_user):
        """Check if blocked"""
        return Block.objects.filter(
            blocker=blocker,
            blocked_user=blocked_user
        ).exists()

    @staticmethod
    def is_muted(user, muted_user):
        """Check if muted"""
        return Mute.objects.filter(
            user=user,
            muted_user=muted_user
        ).exists()
