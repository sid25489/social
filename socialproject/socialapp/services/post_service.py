"""
Post Service

Handles post operations:
- Create, edit, delete posts
- Hashtag and mention processing
- Post visibility
- Repost logic
"""

from django.db import transaction
from django.utils import timezone
from django.db.models import F
from ..models import (
    Post, User, Hashtag, Mention, Comment, Like, Bookmark, Block, Mute
)
import re


class PostService:
    """Post management service"""

    @staticmethod
    def create_post(author, content, image_urls=None):
        """
        Create a new post
        - Extract hashtags and mentions
        - Store relationships
        """
        if not content.strip():
            raise ValueError("Post content cannot be empty")
        
        if len(content) > 2000:
            raise ValueError("Post exceeds 2000 character limit")
        
        with transaction.atomic():
            post = Post.objects.create(
                author=author,
                content=content,
                image_urls=image_urls or []
            )
            
            # Extract and link hashtags
            PostService._extract_and_link_hashtags(post, content)
            
            # Extract and link mentions
            PostService._extract_and_link_mentions(post, content)
            
            # Update author's posts count
            author.posts_count = F('posts_count') + 1
            author.save(update_fields=['posts_count'])
            author.refresh_from_db()
        
        return post

    @staticmethod
    def edit_post(post, new_content):
        """
        Edit post content
        - Update content
        - Re-extract hashtags and mentions
        - Track edit history
        """
        if post.is_deleted:
            raise ValueError("Cannot edit deleted post")
        
        if not new_content.strip():
            raise ValueError("Post content cannot be empty")
        
        with transaction.atomic():
            post.content = new_content
            post.edited_at = timezone.now()
            post.edit_count = F('edit_count') + 1
            post.save()
            
            # Clear old relationships
            post.hashtags.clear()
            post.mentions.all().delete()
            
            # Re-extract
            PostService._extract_and_link_hashtags(post, new_content)
            PostService._extract_and_link_mentions(post, new_content)
        
        return post

    @staticmethod
    def _extract_and_link_hashtags(post, content):
        """Extract hashtags from content and link to post"""
        pattern = r'#(\w+)'
        hashtags = set(re.findall(pattern, content))
        
        for hashtag_name in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(
                name_lower=hashtag_name.lower(),
                defaults={'name': hashtag_name}
            )
            post.hashtags.add(hashtag)
            
            if not created:
                # Update hashtag count
                Hashtag.objects.filter(id=hashtag.id).update(
                    posts_count=F('posts_count') + 1
                )

    @staticmethod
    def _extract_and_link_mentions(post, content):
        """Extract mentions from content and link to post"""
        pattern = r'@(\w+)'
        mentions = set(re.findall(pattern, content))
        
        for mention_username in mentions:
            try:
                mentioned_user = User.objects.get(username=mention_username)
                Mention.objects.get_or_create(
                    post=post,
                    mentioned_user=mentioned_user
                )
            except User.DoesNotExist:
                pass

    @staticmethod
    def delete_post(post):
        """
        Soft delete post
        - Mark as deleted
        - Preserve data
        """
        post.is_deleted = True
        post.save()

    @staticmethod
    def hard_delete_post(post):
        """Hard delete post (for compliance)"""
        post.delete()

    @staticmethod
    def repost(user, original_post):
        """
        Create a repost
        - User reposts another user's post
        - Creates new post with parent reference
        """
        if user == original_post.author:
            raise ValueError("Cannot repost own post")
        
        if original_post.is_deleted:
            raise ValueError("Cannot repost deleted post")
        
        with transaction.atomic():
            repost = Post.objects.create(
                author=user,
                parent_post=original_post,
                original_author=original_post.author,
                content=f"Repost: {original_post.content[:100]}..."
            )
            
            # Update repost count
            original_post.reposts_count = F('reposts_count') + 1
            original_post.save(update_fields=['reposts_count'])
        
        return repost

    @staticmethod
    def get_post_visibility(post, requesting_user=None):
        """
        Check if post is visible to requesting user
        - Check soft delete
        - Check author is not deleted
        - Check block status
        - Check private profile
        """
        if post.is_deleted or post.author.is_deleted:
            return False
        
        if not requesting_user or requesting_user == post.author:
            return True
        
        # Check if blocked
        if Block.objects.filter(
            blocker=post.author,
            blocked_user=requesting_user
        ).exists():
            return False
        
        # Check if blocked by requester
        if Block.objects.filter(
            blocker=requesting_user,
            blocked_user=post.author
        ).exists():
            return False
        
        # Check if private profile and not following
        if post.author.profile.is_private:
            from ..models import Follow
            is_following = Follow.objects.filter(
                follower=requesting_user,
                following=post.author,
                is_deleted=False
            ).exists()
            if not is_following:
                return False
        
        return True

    @staticmethod
    def get_filtered_posts(queryset, requesting_user=None):
        """
        Filter posts based on visibility rules
        """
        if not requesting_user:
            # Anonymous user - only public posts from public profiles
            return queryset.filter(
                is_deleted=False,
                author__is_deleted=False,
                author__profile__is_private=False
            )
        
        # Get blocked user IDs
        blocked_ids = Block.objects.filter(
            blocker=requesting_user
        ).values_list('blocked_user_id', flat=True)
        
        blocked_by_ids = Block.objects.filter(
            blocked_user=requesting_user
        ).values_list('blocker_id', flat=True)
        
        # Get muted user IDs
        muted_ids = Mute.objects.filter(
            user=requesting_user
        ).values_list('muted_user_id', flat=True)
        
        # Filter with visibility rules
        return queryset.filter(
            is_deleted=False,
            author__is_deleted=False
        ).exclude(
            author_id__in=list(blocked_ids) + list(blocked_by_ids) + list(muted_ids)
        )
