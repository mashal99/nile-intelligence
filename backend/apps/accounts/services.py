import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import User, EmailVerificationToken, PasswordResetToken, UserActivity
from apps.subscriptions.models import Subscription


class UserService:
    @staticmethod
    def register(email: str, password: str, full_name: str, role: str, **kwargs) -> User:
        if User.objects.filter(email=email).exists():
            raise ValueError('A user with this email already exists.')

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            **kwargs,
        )

        Subscription.objects.create(user=user, plan='free')
        UserService._send_verification_email(user)

        UserActivity.objects.create(user=user, action='registered', metadata={'role': role})
        return user

    @staticmethod
    def _send_verification_email(user: User) -> None:
        token_value = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(token_value.encode()).hexdigest()

        EmailVerificationToken.objects.create(
            user=user,
            token=hashed,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={token_value}"
        send_mail(
            subject='Verify your Nile Intelligence account',
            message=f'Click to verify: {verification_url}',
            html_message=render_to_string('emails/verify_email.html', {
                'user': user,
                'verification_url': verification_url,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    @staticmethod
    def verify_email(token_value: str) -> bool:
        hashed = hashlib.sha256(token_value.encode()).hexdigest()
        try:
            token = EmailVerificationToken.objects.get(
                token=hashed,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
        except EmailVerificationToken.DoesNotExist:
            return False

        token.user.is_email_verified = True
        token.user.save(update_fields=['is_email_verified'])
        token.is_used = True
        token.save(update_fields=['is_used'])
        return True

    @staticmethod
    def initiate_password_reset(email: str) -> None:
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return  # Silent fail — don't leak user existence

        token_value = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(token_value.encode()).hexdigest()

        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
        PasswordResetToken.objects.create(
            user=user,
            token=hashed,
            expires_at=timezone.now() + timedelta(hours=2),
        )

        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token_value}"
        send_mail(
            subject='Reset your Nile Intelligence password',
            message=f'Reset link: {reset_url}',
            html_message=render_to_string('emails/reset_password.html', {
                'user': user,
                'reset_url': reset_url,
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    @staticmethod
    def reset_password(token_value: str, new_password: str) -> bool:
        hashed = hashlib.sha256(token_value.encode()).hexdigest()
        try:
            token = PasswordResetToken.objects.select_related('user').get(
                token=hashed,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
        except PasswordResetToken.DoesNotExist:
            return False

        token.user.set_password(new_password)
        token.user.save(update_fields=['password'])
        token.is_used = True
        token.save(update_fields=['is_used'])
        UserActivity.objects.create(user=token.user, action='password_reset')
        return True

    @staticmethod
    def update_profile(user: User, **fields) -> User:
        allowed = ['full_name', 'phone', 'company_name', 'avatar']
        for field in allowed:
            if field in fields:
                setattr(user, field, fields[field])
        user.save(update_fields=[f for f in allowed if f in fields])
        return user

    @staticmethod
    def log_activity(user: User, action: str, metadata: dict = None, ip_address: str = None) -> None:
        UserActivity.objects.create(
            user=user,
            action=action,
            metadata=metadata or {},
            ip_address=ip_address,
        )
