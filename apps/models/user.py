import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .utils import validate_image_size

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')
        # Normalize phone: extract only digits, but keep + at the start
        clean_digits = ''.join(filter(str.isdigit, str(phone)))
        normalized_phone = f'+{clean_digits}' if clean_digits else ''
        user = self.model(phone=normalized_phone, **extra_fields)
        user.set_password(password)
        if password:
            user.plain_password = password
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'manager')
        extra_fields.setdefault('is_approved', True)
        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('operator', 'Operator'),
        ('manager', 'Manager'),
        ('navbatchi_operator', 'Duty Operator'),
    )
    LEAGUE_CHOICES = (
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator', db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[validate_image_size])
    league = models.CharField(max_length=10, choices=LEAGUE_CHOICES, default='bronze', null=True, blank=True)
    inventory = models.JSONField(default=dict, blank=True)
    working_hours = models.JSONField(default=dict, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    work_location = models.JSONField(null=True, blank=True) # {lat, lng, address}
    work_radius = models.IntegerField(default=100) # in meters
    work_type = models.CharField(max_length=20, default='office')
    achievements = models.JSONField(default=list, blank=True)
    league_history = models.JSONField(default=list, blank=True)
    plain_password = models.CharField(max_length=128, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"
