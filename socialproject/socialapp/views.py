"""
ConnectSphere API Views

Production-grade DRF ViewSets:
- Authentication viewsets
- User viewsets
- Post viewsets
- Social interaction viewsets
- Feed viewsets
- Notification viewsets
- Message viewsets
- Search and moderation endpoints
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied

from .models import (
    User, UserProfile, Post, Comment, Like, Follow, FollowRequest,
    Block, Mute, Notification, Message, Report, Hashtag, Bookmark
)
from .serializers import (
    UserRegisterSerializer, CustomTokenObtainPairSerializer,
    UserProfileSerializer, UserListSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    CommentListSerializer, CommentDetailSerializer, CommentCreateSerializer,
    FollowSerializer, FollowRequestSerializer, 
    BlockSerializer, MuteSerializer,
    NotificationSerializer, MessageListSerializer, MessageCreateSerializer,
    BookmarkSerializer, ReportSerializer, HashtagSerializer
)
from .permissions import (
    IsOwnerOrReadOnly, IsOwner, IsNotBlocked, CanViewProfile,
    CanMessage, IsModerator
)
from .services.auth_service import AuthService
from .services.user_service import UserService
from .services.post_service import PostService
from .services.social_service import SocialService
from .services.feed_service import FeedService
from .services.notification_service import NotificationService
from .services.message_service import MessageService
from .services.search_service import SearchService
from .services.moderation_service import ModerationService


# ============================================================================
# AUTH VIEWSETS
# ============================================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    """Login with email and password"""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterViewSet(viewsets.ViewSet):
    """User registration"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = AuthService.get_tokens_for_user(user)
            return Response({
                'user': UserListSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# USER VIEWSETS
# ============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """User management"""
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'profile__display_name']
    
    def get_permissions(self):
        if self.action in ('retrieve', 'by_username'):
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserProfileSerializer
        return UserListSerializer
    
    def get_queryset(self):
        return User.objects.filter(is_deleted=False).select_related('profile')
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        profile = user.profile
        perm = CanViewProfile()
        if not perm.has_object_permission(request, self, profile):
            raise PermissionDenied('You cannot view this profile.')
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path=r'by-username/(?P<username>[^/.]+)')
    def by_username(self, request, username=None):
        user = get_object_or_404(
            User.objects.select_related('profile'),
            username__iexact=username,
            is_deleted=False
        )
        profile = user.profile
        perm = CanViewProfile()
        if not perm.has_object_permission(request, self, profile):
            raise PermissionDenied('You cannot view this profile.')
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        from django.contrib.auth.password_validation import validate_password
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response(
                {'detail': 'old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(new_password, user=request.user)
            AuthService.change_password(request.user, old_password, new_password)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DjangoValidationError as e:
            return Response({'new_password': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'password changed'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def blocked_accounts(self, request):
        blocks = Block.objects.filter(blocker=request.user).select_related('blocked_user')
        users = [b.blocked_user for b in blocks]
        serializer = UserListSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current authenticated user"""
        serializer = UserProfileSerializer(
            request.user.profile,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get user recommendations"""
        users = UserService.get_user_recommendations(request.user, limit=20)
        serializer = UserListSerializer(
            users,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """Get user's followers"""
        user = self.get_object()
        followers = SocialService.get_followers(user, limit=100)
        follower_users = User.objects.filter(id__in=followers)
        serializer = UserListSerializer(
            follower_users,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """Get users this user follows"""
        user = self.get_object()
        following = SocialService.get_following(user, limit=100)
        following_users = User.objects.filter(id__in=following)
        serializer = UserListSerializer(
            following_users,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """User profile CRUD"""
    queryset = UserProfile.objects.filter(is_deleted=False)
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return UserProfile.objects.select_related('user').filter(is_deleted=False)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        profile = request.user.profile
        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# POST VIEWSETS
# ============================================================================

class PostViewSet(viewsets.ModelViewSet):
    """Post CRUD and interactions"""
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['author']
    ordering_fields = ['created_at', 'likes_count']
    pagination_class = None
    
    def get_queryset(self):
        return Post.objects.filter(
            is_deleted=False,
            author__is_deleted=False
        ).select_related('author', 'author__profile').prefetch_related(
            'hashtags', 'mentions', 'likes', 'comments'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def create(self, request, *args, **kwargs):
        """Create new post"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            post = Post.objects.get(id=serializer.data['id'])
            detail_serializer = PostDetailSerializer(post, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a post"""
        post = self.get_object()
        
        if request.user == post.author:
            return Response(
                {'detail': 'Cannot like own post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({'status': 'post liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        """Unlike a post"""
        post = self.get_object()
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({'status': 'post unliked'}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """Bookmark a post"""
        post = self.get_object()
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({'status': 'post bookmarked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already bookmarked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def unbookmark(self, request, pk=None):
        """Unbookmark a post"""
        post = self.get_object()
        Bookmark.objects.filter(user=request.user, post=post).delete()
        return Response({'status': 'post removed from bookmarks'}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def home_feed(self, request):
        """Get personalized home feed"""
        cursor = request.query_params.get('cursor')
        result = FeedService.get_home_feed(request.user, cursor=cursor, limit=20)
        
        serializer = PostListSerializer(
            result['posts'],
            many=True,
            context={'request': request}
        )
        return Response({
            'results': serializer.data,
            'next': result['next_cursor']
        })
    
    @action(detail=False, methods=['get'])
    def explore(self, request):
        """Get explore/trending feed"""
        cursor = request.query_params.get('cursor')
        result = FeedService.get_explore_feed(cursor=cursor, limit=20)
        
        serializer = PostListSerializer(
            result['posts'],
            many=True,
            context={'request': request}
        )
        return Response({
            'results': serializer.data,
            'next': result['next_cursor']
        })
    
    @action(detail=False, methods=['get'])
    def bookmarks(self, request):
        """Get user's bookmarked posts"""
        bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
        posts = [b.post for b in bookmarks]
        
        serializer = PostListSerializer(
            posts,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """Comment CRUD"""
    serializer_class = CommentListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post']
    
    def get_queryset(self):
        return Comment.objects.filter(is_deleted=False).select_related('author')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action == 'retrieve':
            return CommentDetailSerializer
        return CommentListSerializer
    
    def create(self, request, *args, **kwargs):
        """Create comment"""
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(author=request.user)
            
            detail_serializer = CommentDetailSerializer(comment, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like a comment"""
        from .models import CommentLike
        
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        
        if created:
            return Response({'status': 'comment liked'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        """Unlike a comment"""
        from .models import CommentLike
        
        comment = self.get_object()
        CommentLike.objects.filter(user=request.user, comment=comment).delete()
        return Response({'status': 'comment unliked'}, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# SOCIAL INTERACTION VIEWSETS
# ============================================================================

class FollowViewSet(viewsets.ViewSet):
    """Follow/Unfollow operations"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def follow(self, request):
        """Follow a user"""
        following_id = request.data.get('user_id')
        
        try:
            following_user = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            result = SocialService.follow_user(request.user, following_user)
            serializer = FollowRequestSerializer(result) if isinstance(result, FollowRequest) else FollowSerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        """Unfollow a user"""
        following_id = request.data.get('user_id')
        
        try:
            following_user = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        SocialService.unfollow_user(request.user, following_user)
        return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def block(self, request):
        """Block a user"""
        blocked_id = request.data.get('user_id')
        
        try:
            blocked_user = User.objects.get(id=blocked_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            block = SocialService.block_user(request.user, blocked_user)
            serializer = BlockSerializer(block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def unblock(self, request):
        """Unblock a user"""
        blocked_id = request.data.get('user_id')
        
        try:
            blocked_user = User.objects.get(id=blocked_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        SocialService.unblock_user(request.user, blocked_user)
        return Response({'status': 'unblocked'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def mute(self, request):
        """Mute a user"""
        muted_id = request.data.get('user_id')
        
        try:
            muted_user = User.objects.get(id=muted_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            mute = SocialService.mute_user(request.user, muted_user)
            serializer = MuteSerializer(mute)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def unmute(self, request):
        """Unmute a user"""
        muted_id = request.data.get('user_id')
        
        try:
            muted_user = User.objects.get(id=muted_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        SocialService.unmute_user(request.user, muted_user)
        return Response({'status': 'unmuted'}, status=status.HTTP_200_OK)


class FollowRequestViewSet(viewsets.ViewSet):
    """Follow request management"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def pending_requests(self, request):
        """Get pending follow requests"""
        requests = FollowRequest.objects.filter(
            receiver=request.user,
            status='pending'
        ).select_related('requester')
        
        serializer = FollowRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def accept(self, request):
        """Accept follow request"""
        request_id = request.data.get('request_id')
        
        try:
            follow_request = FollowRequest.objects.get(id=request_id, receiver=request.user)
        except FollowRequest.DoesNotExist:
            return Response({'detail': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        follow = SocialService.accept_follow_request(follow_request)
        serializer = FollowSerializer(follow)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reject(self, request):
        """Reject follow request"""
        request_id = request.data.get('request_id')
        
        try:
            follow_request = FollowRequest.objects.get(id=request_id, receiver=request.user)
        except FollowRequest.DoesNotExist:
            return Response({'detail': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        SocialService.reject_follow_request(follow_request)
        return Response({'status': 'rejected'}, status=status.HTTP_200_OK)


# ============================================================================
# NOTIFICATION VIEWSETS
# ============================================================================

class NotificationViewSet(viewsets.ViewSet):
    """Notification management"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def list_notifications(self, request):
        """Get user's notifications"""
        notification_type = request.query_params.get('type')
        notifications = NotificationService.get_notifications(
            request.user,
            notification_type=notification_type,
            limit=50
        )
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = NotificationService.get_unread_count(request.user)
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Mark notification as read"""
        notification_id = request.data.get('id')
        
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        
        NotificationService.mark_as_read(notification)
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        NotificationService.mark_all_as_read(request.user)
        return Response({'status': 'all marked as read'})


# ============================================================================
# MESSAGE VIEWSETS
# ============================================================================

class MessageViewSet(viewsets.ViewSet):
    """Direct messaging"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """Send message"""
        recipient_id = request.data.get('recipient_id')
        content = request.data.get('content')
        
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            message = MessageService.send_message(request.user, recipient, content)
            serializer = MessageListSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get conversation list"""
        conversations = MessageService.get_conversations(request.user, limit=50)
        
        result = [{
            'user': UserListSerializer(conv['user'], context={'request': request}).data,
            'latest_message': MessageListSerializer(conv['latest_message']).data if conv['latest_message'] else None,
            'unread_count': conv['unread_count']
        } for conv in conversations]
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation with user"""
        user_id = request.query_params.get('user_id')
        
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        messages = MessageService.get_conversation(request.user, other_user, limit=50)
        
        # Mark as read
        MessageService.mark_conversation_as_read(request.user, other_user)
        
        serializer = MessageListSerializer(messages, many=True)
        return Response(serializer.data)


# ============================================================================
# SEARCH VIEWSETS
# ============================================================================

class SearchViewSet(viewsets.ViewSet):
    """Search functionality"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def global_search(self, request):
        """Global search"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'detail': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        requesting_user = request.user if request.user.is_authenticated else None
        result = SearchService.global_search(query, requesting_user=requesting_user, limit=10)
        
        return Response({
            'users': UserListSerializer(result['users'], many=True, context={'request': request}).data,
            'posts': PostListSerializer(result['posts'], many=True, context={'request': request}).data,
            'hashtags': HashtagSerializer(result['hashtags'], many=True).data,
        })
    
    @action(detail=False, methods=['get'])
    def hashtags(self, request):
        """Search hashtags"""
        query = request.query_params.get('q', '')
        
        hashtags = SearchService.search_hashtags(query, limit=20)
        serializer = HashtagSerializer(hashtags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending hashtags"""
        hashtags = FeedService.get_trending_hashtags(limit=20)
        return Response(hashtags)


# ============================================================================
# MODERATION VIEWSETS
# ============================================================================

class ReportViewSet(viewsets.ViewSet):
    """Content reporting"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_report(self, request):
        """Create report"""
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """Get user's reports"""
        reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)


class ModerationViewSet(viewsets.ViewSet):
    """Moderation panel (admin only)"""
    permission_classes = [IsAuthenticated, IsModerator]
    
    @action(detail=False, methods=['get'])
    def pending_reports(self, request):
        """Get pending reports"""
        reports = ModerationService.get_reports(status='submitted')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def approve_report(self, request):
        """Approve report"""
        report_id = request.data.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        action = ModerationService.approve_report(report, request.user)
        return Response({'status': 'report approved'})
    
    @action(detail=False, methods=['post'])
    def reject_report(self, request):
        """Reject report"""
        report_id = request.data.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({'detail': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ModerationService.reject_report(report)
        return Response({'status': 'report rejected'})
