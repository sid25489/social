"""
ConnectSphere REST Serializers

Production-grade serializers with:
- Nested relationships
- Validation
- Optimized queries (select_related, prefetch_related)
- Custom fields
- Error handling
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction, models
from django.db.models import Q
from .models import (
    User, UserProfile, Post, Comment, Like, Follow, FollowRequest,
    Block, Mute, Notification, Message, Report, ModeratorAction,
    Hashtag, Mention, Bookmark, CommentLike
)
import re


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User registration with email and password validation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': "Password fields didn't match."
            })
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': "This email is already registered."
            })
        
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({
                'username': "This username is already taken."
            })
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # UserProfile is automatically created by the post_save signal in signals.py
        # No need to create it manually here
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    JWT token obtain with custom claims
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token


class UserListSerializer(serializers.ModelSerializer):
    """
    Minimal user serializer for lists
    """
    is_following = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'followers_count', 'is_following', 'is_blocked')

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(
            follower=request.user,
            following=obj,
            is_deleted=False
        ).exists()

    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Block.objects.filter(
            blocker=request.user,
            blocked_user=obj
        ).exists()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User profile with relationship status
    """
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    followers_count = serializers.IntegerField(source='user.followers_count', read_only=True)
    following_count = serializers.IntegerField(source='user.following_count', read_only=True)
    posts_count = serializers.IntegerField(source='user.posts_count', read_only=True)
    
    is_following = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    can_message = serializers.SerializerMethodField()
    pending_follow_request = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user_id', 'username', 'email', 'display_name', 'bio',
            'avatar_url', 'cover_image_url', 'website', 'location',
            'is_private', 'followers_count', 'following_count', 'posts_count',
            'is_following', 'is_blocked', 'can_message', 'pending_follow_request'
        )

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user == obj.user:
            return False
        return Follow.objects.filter(
            follower=request.user,
            following=obj.user,
            is_deleted=False
        ).exists()

    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Block.objects.filter(
            blocker=request.user,
            blocked_user=obj.user
        ).exists() or Block.objects.filter(
            blocker=obj.user,
            blocked_user=request.user
        ).exists()

    def get_can_message(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Cannot message if blocked either way
        return not Block.objects.filter(
            Q(blocker=request.user, blocked_user=obj.user) |
            Q(blocker=obj.user, blocked_user=request.user)
        ).exists()

    def get_pending_follow_request(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user == obj.user:
            return None
        fr = FollowRequest.objects.filter(
            requester=request.user,
            receiver=obj.user,
            status='pending'
        ).first()
        return str(fr.id) if fr else None


class HashtagSerializer(serializers.ModelSerializer):
    """
    Hashtag with trending information
    """
    class Meta:
        model = Hashtag
        fields = ('id', 'name', 'posts_count', 'is_trending', 'trending_rank')


class MentionSerializer(serializers.ModelSerializer):
    """
    Mention information
    """
    mentioned_user = UserListSerializer(read_only=True)

    class Meta:
        model = Mention
        fields = ('id', 'mentioned_user', 'created_at')


class CommentListSerializer(serializers.ModelSerializer):
    """
    Minimal comment serializer for lists
    """
    author = UserListSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'likes_count', 'replies_count', 'created_at')


class CommentDetailSerializer(serializers.ModelSerializer):
    """
    Complete comment serializer with replies
    """
    author = UserListSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id', 'author', 'post', 'parent_comment', 'content',
            'likes_count', 'replies_count', 'is_liked', 'is_own',
            'created_at', 'edited_at', 'edit_count'
        )

    def get_replies(self, obj):
        if obj.depth >= 1:  # Max depth is 2
            return []
        replies = obj.replies.filter(is_deleted=False).select_related('author')
        return CommentListSerializer(replies, many=True, context=self.context).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return CommentLike.objects.filter(user=request.user, comment=obj).exists()

    def get_is_own(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.author_id == request.user.id


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Comment creation with mention extraction
    """
    class Meta:
        model = Comment
        fields = ('post', 'parent_comment', 'content')

    def validate_parent_comment(self, value):
        if value and value.depth >= 1:
            raise serializers.ValidationError("Cannot nest comments beyond 2 levels")
        return value

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Comment cannot be empty")
        return value


class PostListSerializer(serializers.ModelSerializer):
    """
    Post list serializer with minimal author info
    """
    author = UserListSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'content', 'likes_count', 'comments_count',
            'reposts_count', 'bookmarks_count', 'is_liked', 'is_bookmarked',
            'is_own', 'image_urls', 'created_at'
        )

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Like.objects.filter(user=request.user, post=obj).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Bookmark.objects.filter(user=request.user, post=obj).exists()

    def get_is_own(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.author_id == request.user.id


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Complete post serializer with comments and engagement
    """
    author = UserProfileSerializer(source='author.profile', read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    mentions = MentionSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'content', 'image_urls', 'hashtags', 'mentions',
            'likes_count', 'comments_count', 'reposts_count', 'bookmarks_count',
            'is_liked', 'is_bookmarked', 'is_own', 'comments',
            'created_at', 'edited_at', 'edit_count'
        )

    def get_comments(self, obj):
        comments = obj.comments.filter(
            parent_comment__isnull=True,
            is_deleted=False
        ).select_related('author').prefetch_related('replies')[:10]
        return CommentDetailSerializer(comments, many=True, context=self.context).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Like.objects.filter(user=request.user, post=obj).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Bookmark.objects.filter(user=request.user, post=obj).exists()

    def get_is_own(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.author_id == request.user.id


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Post creation with hashtag and mention extraction
    """
    class Meta:
        model = Post
        fields = ('content', 'image_urls')

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Post content cannot be empty")
        if len(value) > 2000:
            raise serializers.ValidationError("Post content exceeds 2000 characters")
        return value

    def extract_hashtags(self, content):
        """Extract hashtags from post content"""
        pattern = r'#(\w+)'
        return re.findall(pattern, content)

    def extract_mentions(self, content):
        """Extract mentions from post content"""
        pattern = r'@(\w+)'
        return re.findall(pattern, content)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        
        with transaction.atomic():
            post = Post.objects.create(**validated_data)
            
            # Extract and link hashtags
            hashtags = self.extract_hashtags(validated_data['content'])
            for hashtag_name in hashtags:
                hashtag, _ = Hashtag.objects.get_or_create(
                    name_lower=hashtag_name.lower(),
                    defaults={'name': hashtag_name}
                )
                post.hashtags.add(hashtag)
            
            # Extract and link mentions
            mentions = self.extract_mentions(validated_data['content'])
            for mention_username in mentions:
                try:
                    mentioned_user = User.objects.get(username=mention_username)
                    Mention.objects.create(post=post, mentioned_user=mentioned_user)
                except User.DoesNotExist:
                    pass
        
        return post


class FollowSerializer(serializers.ModelSerializer):
    """
    Follow relationship serializer
    """
    follower = UserListSerializer(read_only=True)
    following = UserListSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'following', 'created_at')


class FollowRequestSerializer(serializers.ModelSerializer):
    """
    Follow request with user details
    """
    requester = UserListSerializer(read_only=True)
    receiver = UserListSerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ('id', 'requester', 'receiver', 'status', 'created_at')


class BlockSerializer(serializers.ModelSerializer):
    """
    Block relationship serializer
    """
    blocker = UserListSerializer(read_only=True)
    blocked_user = UserListSerializer(read_only=True)

    class Meta:
        model = Block
        fields = ('id', 'blocker', 'blocked_user', 'created_at')


class MuteSerializer(serializers.ModelSerializer):
    """
    Mute relationship serializer
    """
    user = UserListSerializer(read_only=True)
    muted_user = UserListSerializer(read_only=True)

    class Meta:
        model = Mute
        fields = ('id', 'user', 'muted_user', 'created_at')


class NotificationSerializer(serializers.ModelSerializer):
    """
    Notification with related object info
    """
    actor = UserListSerializer(read_only=True)
    post = PostListSerializer(read_only=True)
    comment = CommentListSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'notification_type', 'message', 'actor', 'post', 'comment',
            'is_read', 'created_at'
        )


class MessageListSerializer(serializers.ModelSerializer):
    """
    Message list serializer
    """
    sender = UserListSerializer(read_only=True)
    recipient = UserListSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            'id', 'sender', 'recipient', 'content', 'is_read',
            'read_at', 'created_at'
        )


class MessageDetailSerializer(serializers.ModelSerializer):
    """
    Message detail serializer
    """
    sender = UserListSerializer(read_only=True)
    recipient = UserListSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            'id', 'sender', 'recipient', 'content', 'is_read',
            'read_at', 'created_at', 'updated_at'
        )


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Message creation serializer
    """
    class Meta:
        model = Message
        fields = ('recipient', 'content')

    def validate_content(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message cannot be empty")
        return value


class ReportSerializer(serializers.ModelSerializer):
    """
    Report creation and listing
    """
    reporter = UserListSerializer(read_only=True)

    class Meta:
        model = Report
        fields = (
            'id', 'reporter', 'post', 'comment', 'reported_user',
            'reason', 'description', 'status', 'created_at'
        )
        read_only_fields = ('reporter', 'status')


class BookmarkSerializer(serializers.ModelSerializer):
    """
    Bookmark serializer
    """
    post = PostListSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ('id', 'post', 'created_at')


class LikeSerializer(serializers.ModelSerializer):
    """
    Like serializer
    """
    user = UserListSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'created_at')
