from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from api_v1.utils import normalize_phone

User = get_user_model()

class PhoneOrNicknameBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        # Depending on the view, the username_field might be passed as username, phone, or in kwargs
        username = phone or kwargs.get(User.USERNAME_FIELD) or kwargs.get('username')
        if not username:
            return None
            
        username_str = str(username)
        user = None
        
        # 1. Try exact nickname match
        user = User.objects.filter(nickname=username_str).first()
        
        if not user:
            # 2. Try normalized phone match
            normalized = normalize_phone(username_str)
            if normalized:
                # Exact match
                user = User.objects.filter(**{User.USERNAME_FIELD: normalized}).first()
                if not user:
                    # Match with '+' prefix (in case DB has it differently)
                    user = User.objects.filter(**{User.USERNAME_FIELD: f"+{normalized}"}).first()
                if not user:
                    # Contains match
                    user = User.objects.filter(**{f"{User.USERNAME_FIELD}__icontains": normalized}).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None
