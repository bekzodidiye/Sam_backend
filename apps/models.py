import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')
        # Normalize phone: extract only digits
        normalized_phone = ''.join(filter(str.isdigit, str(phone)))
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')
    is_approved = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
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

class CheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    timestamp = models.DateTimeField(auto_now_add=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6)
    photo = models.ImageField(upload_to='checkins/', null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    working_hours_snapshot = models.JSONField(null=True, blank=True)

class Company(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales')
    count = models.IntegerField(default=1)
    bonus = models.IntegerField(default=0)
    tariff = models.ForeignKey("Tariff", on_delete=models.CASCADE, related_name='sales')
    date = models.DateField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.user} - {self.company} - {self.date}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True) # null for 'all'
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Rule(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tariff(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tariffs') # Ucell, Mobiuz, etc.
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'name')

class MonthlyTarget(models.Model):
    month = models.CharField(max_length=7) # YYYY-MM
    targets = models.JSONField(default=dict) # company -> target count
    office_counts = models.JSONField(default=dict)
    mobile_office_counts = models.JSONField(default=dict)

    class Meta:
        unique_together = ('month',)

class DailyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    date = models.DateField(auto_now_add=True)
    summary = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    photos = models.JSONField(default=list, blank=True) # List of image URLs

class SalesLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    mobile_url = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='sales_links/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
