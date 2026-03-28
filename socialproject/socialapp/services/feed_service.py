"""
Feed Service

Handles feed generation:
- Home feed (personalized)
- Explore feed (trending)
- Cursor pagination
- Caching
"""

from django.db.models import Q, F, Count, Value, Window, DecimalField
from django.db.models.functions import DenseRank
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Post, Follow, Block, Mute, Like, Comment, FeedCache, TrendingCache
)
import json


class FeedService:
    """Feed generation service"""

    CACHE_TTL = 3600  # 1 hour

    @staticmethod
    def get_home_feed(user, cursor=None, limit=20):
        """
        Get personalized home feed
        - Posts from followed users
        - Exclude blocked/muted users
        - Cursor pagination
        - Cached with redis
        """
        # Check cache first
        cache_key = f"home_feed:{user.id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            post_ids = cached_data.get('post_ids', [])
        else:
            # Get following IDs
            following_ids = Follow.objects.filter(
                follower=user,
                is_deleted=False
            ).values_list('following_id', flat=True)
            
            # Get blocked/muted IDs
            blocked_ids = Block.objects.filter(
                blocker=user
            ).values_list('blocked_user_id', flat=True)
            
            muted_ids = Mute.objects.filter(
                user=user
            ).values_list('muted_user_id', flat=True)
            
            # Query posts
            posts = Post.objects.filter(
                author_id__in=following_ids,
                is_deleted=False
            ).exclude(
                author_id__in=list(blocked_ids) + list(muted_ids)
            ).order_by('-created_at').values_list('id', flat=True)[:1000]
            
            post_ids = list(posts)
            
            # Cache results
            cache.set(cache_key, {'post_ids': post_ids}, FeedService.CACHE_TTL)
        
        # Apply cursor pagination
        if cursor:
            try:
                cursor_index = post_ids.index(cursor)
                post_ids = post_ids[cursor_index + 1:]
            except (ValueError, IndexError):
                post_ids = []
        
        # Get paginated results
        paginated_ids = post_ids[:limit]
        
        # Fetch posts with optimizations
        posts = Post.objects.filter(
            id__in=paginated_ids
        ).select_related('author', 'author__profile').prefetch_related(
            'hashtags',
            'mentions__mentioned_user',
            'likes',
            'comments__author'
        ).order_by('-created_at')
        
        # Determine next cursor
        next_cursor = paginated_ids[-1] if len(paginated_ids) == limit else None
        
        return {
            'posts': posts,
            'next_cursor': str(next_cursor) if next_cursor else None
        }

    @staticmethod
    def get_explore_feed(cursor=None, limit=20):
        """
        Get trending/explore feed
        - Posts sorted by engagement
        - Score: (likes * 0.4) + (comments * 0.4) + (recency * 0.2)
        - Last 7 days
        """
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        # Score formula: (likes * 0.4) + (comments * 0.4)
        posts = Post.objects.filter(
            is_deleted=False,
            author__is_deleted=False,
            author__profile__is_private=False,
            created_at__gte=seven_days_ago
        ).annotate(
            engagement_score=(
                F('likes_count') * 0.4 +
                F('comments_count') * 0.4
            )
        ).order_by('-engagement_score', '-created_at')
        
        # Apply cursor pagination
        if cursor:
            try:
                cursor_post = posts.filter(id=cursor).first()
                if cursor_post:
                    posts = posts.filter(
                        created_at__lt=cursor_post.created_at
                    ).order_by('-created_at')
            except Post.DoesNotExist:
                pass
        
        paginated_posts = posts[:limit]
        
        # Optimize query
        paginated_posts = paginated_posts.select_related(
            'author', 'author__profile'
        ).prefetch_related(
            'hashtags',
            'mentions__mentioned_user',
            'likes',
            'comments__author'
        )
        
        post_list = list(paginated_posts)
        next_cursor = str(post_list[-1].id) if len(post_list) == limit else None
        
        return {
            'posts': post_list,
            'next_cursor': next_cursor
        }

    @staticmethod
    def get_trending_hashtags(limit=20):
        """
        Get trending hashtags
        - Based on post count in last 24 hours
        - Cached
        """
        cache_key = "trending_hashtags"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        from ..models import Hashtag
        
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        trending = Hashtag.objects.filter(
            posts__created_at__gte=twenty_four_hours_ago
        ).annotate(
            recent_count=Count('posts')
        ).order_by('-recent_count', '-posts_count')[:limit]
        
        result = [{
            'id': str(t.id),
            'name': t.name,
            'posts_count': t.posts_count
        } for t in trending]
        
        cache.set(cache_key, result, FeedService.CACHE_TTL)
        return result

    @staticmethod
    def get_trending_posts(limit=20):
        """Get trending posts"""
        cache_key = "trending_posts"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            post_ids = cached_data['post_ids']
            posts = Post.objects.filter(id__in=post_ids)
        else:
            seven_days_ago = timezone.now() - timedelta(days=7)
            
            posts = Post.objects.filter(
                is_deleted=False,
                author__is_deleted=False,
                created_at__gte=seven_days_ago
            ).annotate(
                score=F('likes_count') * 0.4 + F('comments_count') * 0.4
            ).order_by('-score')[:limit]
            
            post_ids = list(posts.values_list('id', flat=True))
            cache.set(cache_key, {'post_ids': post_ids}, FeedService.CACHE_TTL)
        
        return posts.select_related(
            'author', 'author__profile'
        ).prefetch_related('hashtags', 'mentions')

    @staticmethod
    def invalidate_feed_cache(user_id):
        """Invalidate user's feed cache"""
        cache_key = f"home_feed:{user_id}"
        cache.delete(cache_key)

    @staticmethod
    def invalidate_trending_cache():
        """Invalidate trending cache"""
        cache.delete("trending_hashtags")
        cache.delete("trending_posts")

    @staticmethod
    def get_user_feed(user_id, cursor=None, limit=20):
        """
        Get user's own posts
        - All posts from user
        - Ordered by date
        """
        from ..models import User
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return {'posts': [], 'next_cursor': None}
        
        posts = Post.objects.filter(
            author=target_user,
            is_deleted=False
        ).order_by('-created_at')
        
        # Cursor pagination
        if cursor:
            try:
                cursor_post = Post.objects.get(id=cursor)
                posts = posts.filter(created_at__lt=cursor_post.created_at)
            except Post.DoesNotExist:
                pass
        
        paginated = posts[:limit]
        post_list = list(paginated.select_related(
            'author', 'author__profile'
        ).prefetch_related('hashtags', 'mentions', 'likes', 'comments'))
        
        next_cursor = str(post_list[-1].id) if len(post_list) == limit else None
        
        return {
            'posts': post_list,
            'next_cursor': next_cursor
        }
