import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework.test import APIClient

# Find an operator User
u = User.objects.filter(first_name='Bekzod', role='operator').first()
if not u: u = User.objects.exclude(id=User.objects.filter(first_name='Jaloliddin').first().id).first()

client = APIClient()
client.force_authenticate(user=u)

data = {
    "company": "Uztelecom",
    "tariff": "Milliy_10",
    "count": 5,
    "bonus": 1
}
r = client.post('/api/v1/sales/', data, format='json')
print("Status Code:", r.status_code)
print("Created sale for:", u.get_full_name())
