import datetime
from django.utils import timezone

def get_uz_now():
    """Returns joriy vaqt (current time) in Uzbekistan (UTC+5)."""
    # If using USE_TZ=True, this should respect the TIME_ZONE setting in settings.py
    return timezone.now()

def normalize_phone(phone: str) -> str:
    """Extracts only digits from a phone number string."""
    if not phone:
        return ""
    return ''.join(filter(str.isdigit, str(phone)))
