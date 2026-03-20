from django.db import models
from .user import User

class MonthlyTarget(models.Model):
    month = models.CharField(max_length=7, db_index=True) # YYYY-MM
    targets = models.JSONField(default=dict) # company -> target count
    office_counts = models.JSONField(default=dict)
    mobile_office_counts = models.JSONField(default=dict)

    class Meta:
        unique_together = ('month',)

    def __str__(self):
        return f"Targets for {self.month}"

class DailyReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    date = models.DateField(auto_now_add=True, db_index=True)
    summary = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    photos = models.JSONField(default=list, blank=True) # List of image URLs

    def __str__(self):
        return f"Report by {self.user} on {self.date}"

class OperatorRating(models.Model):
    operator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    date = models.DateField(db_index=True)
    stars = models.IntegerField() # 1 to 5
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('operator', 'date')
        indexes = [
            models.Index(fields=['operator', 'date']),
            models.Index(fields=['rated_by', 'date']),
        ]

    def __str__(self):
        return f"Rating for {self.operator} - {self.date}"
