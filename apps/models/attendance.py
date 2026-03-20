from django.db import models
from .utils import validate_image_size
from .user import User

class CheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    timestamp = models.DateTimeField(auto_now_add=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6)
    photo = models.ImageField(upload_to='checkins/', null=True, blank=True, validators=[validate_image_size])
    date = models.DateField(auto_now_add=True, db_index=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    working_hours_snapshot = models.JSONField(null=True, blank=True)
