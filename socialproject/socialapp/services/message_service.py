"""
Message Service

Handles messaging:
- Send messages
- Read receipts
- Block-aware messaging
- Conversation retrieval
"""

from django.db.models import Q
from django.utils import timezone
from ..models import Message, Block, User


class MessageService:
    """Direct messaging service"""

    @staticmethod
    def send_message(sender, recipient, content):
        """
        Send a message
        - Check if blocked
        - Create message
        - Return None if blocked
        """
        if sender == recipient:
            raise ValueError("Cannot message yourself")
        
        # Check if blocked
        if Block.objects.filter(
            Q(blocker=sender, blocked_user=recipient) |
            Q(blocker=recipient, blocked_user=sender)
        ).exists():
            raise ValueError("Cannot message this user")
        
        if not content.strip():
            raise ValueError("Message cannot be empty")
        
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=content
        )
        
        # Trigger WebSocket notification
        # In production: celery task
        
        return message

    @staticmethod
    def mark_as_read(message):
        """Mark message as read"""
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save(update_fields=['is_read', 'read_at'])

    @staticmethod
    def get_conversation(user1, user2, limit=50):
        """
        Get conversation between two users
        - Exclude soft-deleted messages
        - Ordered by date
        """
        messages = Message.objects.filter(
            Q(sender=user1, recipient=user2) |
            Q(sender=user2, recipient=user1)
        ).exclude(
            Q(is_deleted_by_sender=True, sender=user1) |
            Q(is_deleted_by_recipient=True, recipient=user1) |
            Q(is_deleted_by_sender=True, sender=user2) |
            Q(is_deleted_by_recipient=True, recipient=user2)
        ).order_by('-created_at')[:limit]
        
        return messages

    @staticmethod
    def get_conversations(user, limit=50):
        """
        Get user's conversation list
        - Latest message with each contact
        - Ordered by recency
        """
        from django.db.models import Max
        
        # Get latest message with each user
        conversations = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).values(
            'sender', 'recipient'
        ).annotate(
            latest=Max('created_at')
        ).order_by('-latest')[:limit]
        
        result = []
        for conv in conversations:
            other_user_id = conv['recipient'] if conv['sender'] == str(user.id) else conv['sender']
            try:
                other_user = User.objects.get(id=other_user_id)
                latest_message = Message.objects.filter(
                    Q(sender=user, recipient=other_user) |
                    Q(sender=other_user, recipient=user)
                ).order_by('-created_at').first()
                
                unread_count = Message.objects.filter(
                    sender=other_user,
                    recipient=user,
                    is_read=False
                ).count()
                
                result.append({
                    'user': other_user,
                    'latest_message': latest_message,
                    'unread_count': unread_count
                })
            except User.DoesNotExist:
                pass
        
        return result

    @staticmethod
    def delete_message(message, user):
        """
        Delete message for user
        - Soft delete
        - Only affects view for that user
        """
        if message.sender == user:
            message.is_deleted_by_sender = True
        elif message.recipient == user:
            message.is_deleted_by_recipient = True
        else:
            raise ValueError("User is not part of this message")
        
        message.save()

    @staticmethod
    def get_unread_count(user):
        """Get count of unread messages"""
        return Message.objects.filter(
            recipient=user,
            is_read=False
        ).count()

    @staticmethod
    def get_unread_conversation_count(user):
        """Get count of conversations with unread messages"""
        from django.db.models import Count, Q
        
        count = Message.objects.filter(
            recipient=user,
            is_read=False
        ).values('sender').distinct().count()
        
        return count

    @staticmethod
    def mark_conversation_as_read(user, other_user):
        """Mark all messages in conversation as read"""
        now = timezone.now()
        Message.objects.filter(
            recipient=user,
            sender=other_user,
            is_read=False
        ).update(is_read=True, read_at=now)
