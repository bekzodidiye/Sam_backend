from django.db import models
from .user import User
from .utils import validate_image_size

class Company(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Tariff(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tariffs')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'name')

    def __str__(self):
        return f"{self.company.name} - {self.name}"

class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sales')
    count = models.IntegerField(default=1)
    bonus = models.IntegerField(default=0)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField(auto_now_add=True, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True) 

    def __str__(self):
        return f"{self.user} - {self.company} - {self.date}"

class SalesLink(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    mobile_url = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='sales_links/', null=True, blank=True, validators=[validate_image_size])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
