import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework.test import APIClient

u = User.objects.filter(role='operator').first()
client = APIClient()
client.force_authenticate(user=u)

data = {
    "company": "Ucell",
    "tariff": "Ucell_10",
    "count": 1,
    "bonus": 0
}
r = client.post('/api/v1/sales/', data, format='json')
print("Status Code Operator Create:", r.status_code)
if r.status_code != 201:
    print(r.data)
