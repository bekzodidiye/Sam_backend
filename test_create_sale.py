import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models import User
from rest_framework.test import APIClient

u = User.objects.filter(role='operator').first()
if not u:
    u = User.objects.first()

client = APIClient()
client.force_authenticate(user=u)

data = {
    "company": "Ucell",
    "tariff": "Ucell_10",
    "count": 1,
    "bonus": 0
}

response = client.post('/api/v1/sales/', data, format='json')
print("Status Code:", response.status_code)
print("Response Data:", json.dumps(response.data))
