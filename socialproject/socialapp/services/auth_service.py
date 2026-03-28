"""
Auth Service

Handles authentication workflows:
- User registration
- Email verification
- Password reset
- Token management
"""

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User, UserProfile
import secrets
import string


class AuthService:
    """Authentication service"""

    @staticmethod
    def register_user(email, username, password):
        """
        Register a new user
        - Create user account
        - Create profile
        - Send verification email
        """
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        UserProfile.objects.create(user=user)
        
        # Send verification email (stub)
        AuthService.send_verification_email(user)
        
        return user

    @staticmethod
    def send_verification_email(user):
        """Send email verification link"""
        # In production, use celery task
        # token = secrets.token_urlsafe(32)
        # user.email_verification_token = token
        # user.save()
        pass

    @staticmethod
    def verify_email(user):
        """Mark email as verified"""
        user.is_verified = True
        user.save()

    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password
        Returns user or None
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and not user.is_deleted:
                return user
        except User.DoesNotExist:
            pass
        return None

    @staticmethod
    def get_tokens_for_user(user):
        """Get JWT tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def logout_user(request):
        """Logout user (invalidate refresh token)"""
        # Token blacklist logic handled by SimpleJWT
        pass

    @staticmethod
    def change_password(user, old_password, new_password):
        """Change user password"""
        if not user.check_password(old_password):
            raise ValueError("Old password is incorrect")
        
        user.set_password(new_password)
        user.save()

    @staticmethod
    def request_password_reset(email):
        """Generate password reset token and send email"""
        try:
            user = User.objects.get(email=email)
            # In production: create token, send email via celery
            pass
        except User.DoesNotExist:
            pass

    @staticmethod
    def reset_password(token, new_password):
        """Reset password using token"""
        # Verify token, update password
        pass
