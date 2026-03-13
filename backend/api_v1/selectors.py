from typing import TYPE_CHECKING
from django.db.models import QuerySet, Q
from apps.models import CheckIn, Sale, Message, DailyReport

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    User = AbstractBaseUser
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()

def get_checkins(user: User) -> QuerySet[CheckIn]:
    """Retrieve check-ins with optimized related fields."""
    qs = CheckIn.objects.select_related('user')
    if user.role == 'manager':
        return qs
    return qs.filter(user=user)

def get_sales() -> QuerySet[Sale]:
    """Retrieve sales with optimized related fields to prevent N+1 issues."""
    return Sale.objects.select_related('user', 'company', 'tariff')

def get_messages(user: User) -> QuerySet[Message]:
    """Retrieve messages for a specific user with optimized related fields."""
    qs = Message.objects.select_related('sender', 'recipient')
    if user.role == 'manager':
        # Managers see: messages to them, sent by them, or to "all" (recipients is null)
        return qs.filter(
            Q(recipient=user) | 
            Q(recipient__isnull=True) | 
            Q(sender=user)
        )
    else:
        # Operators see: messages to them, sent by them, or broadcasts from managers
        return qs.filter(
            Q(recipient=user) | 
            Q(sender=user) |
            Q(recipient__isnull=True, sender__role='manager')
        )

def get_daily_reports(user: User) -> QuerySet[DailyReport]:
    """Retrieve daily reports with optimized related fields."""
    qs = DailyReport.objects.select_related('user')
    if user.role == 'manager':
        return qs
    return qs.filter(user=user)
