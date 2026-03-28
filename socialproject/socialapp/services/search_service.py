"""
Search Service

Handles search operations:
- Search users
- Search posts
- Search hashtags
- Full-text search with PostgreSQL
"""

from django.db.models import Q, Count
from ..models import User, Post, Hashtag, Block


class SearchService:
    """Search service"""

    @staticmethod
    def search_users(query, requesting_user=None, limit=20):
        """
        Search users by username or display name
        - Case-insensitive
        - Exclude blocked users
        - Exclude deleted users
        """
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__display_name__icontains=query),
            is_deleted=False
        ).distinct()
        
        # Exclude blocked
        if requesting_user:
            blocked_ids = Block.objects.filter(
                Q(blocker=requesting_user) | Q(blocked_user=requesting_user)
            ).values_list('blocker_id', 'blocked_user_id')
            blocked_ids = set([item for tup in blocked_ids for item in tup])
            users = users.exclude(id__in=blocked_ids)
        
        return users.select_related('profile')[:limit]

    @staticmethod
    def search_posts(query, requesting_user=None, limit=20):
        """
        Search posts by content
        - Case-insensitive
        - Exclude deleted posts
        - Respect visibility settings
        """
        posts = Post.objects.filter(
            content__icontains=query,
            is_deleted=False,
            author__is_deleted=False
        ).distinct()
        
        # Apply visibility filters
        if requesting_user:
            blocked_ids = Block.objects.filter(
                blocker=requesting_user
            ).values_list('blocked_user_id', flat=True)
            
            posts = posts.exclude(author_id__in=blocked_ids)
        else:
            # Only public posts for anonymous
            posts = posts.filter(author__profile__is_private=False)
        
        return posts.select_related('author', 'author__profile')[:limit]

    @staticmethod
    def search_hashtags(query, limit=20):
        """
        Search hashtags by name
        - Case-insensitive
        - Sort by popularity
        """
        hashtags = Hashtag.objects.filter(
            name_lower__icontains=query.lower()
        ).order_by('-posts_count')[:limit]
        
        return hashtags

    @staticmethod
    def global_search(query, requesting_user=None, limit=10):
        """
        Global search across all entities
        - Users
        - Posts
        - Hashtags
        """
        return {
            'users': SearchService.search_users(query, requesting_user, limit),
            'posts': SearchService.search_posts(query, requesting_user, limit),
            'hashtags': SearchService.search_hashtags(query, limit),
        }

    @staticmethod
    def autocomplete_hashtag(prefix, limit=10):
        """Autocomplete hashtags"""
        hashtags = Hashtag.objects.filter(
            name_lower__istartswith=prefix.lower()
        ).order_by('-posts_count')[:limit]
        
        return hashtags

    @staticmethod
    def autocomplete_username(prefix, limit=10):
        """Autocomplete usernames"""
        users = User.objects.filter(
            username__istartswith=prefix,
            is_deleted=False
        ).order_by('username')[:limit]
        
        return users

    @staticmethod
    def get_posts_by_hashtag(hashtag, limit=20):
        """Get all posts with specific hashtag"""
        posts = hashtag.posts.filter(
            is_deleted=False,
            author__is_deleted=False
        ).select_related('author', 'author__profile').order_by('-created_at')[:limit]
        
        return posts

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        try:
            return User.objects.select_related('profile').get(
                username=username,
                is_deleted=False
            )
        except User.DoesNotExist:
            return None
